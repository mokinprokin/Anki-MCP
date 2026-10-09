from typing import Any

from anki_mcp_server.core.config import settings
from anki_mcp_server.core.exceptions import AnkiAPIError, AnkiConnectionError
from anki_mcp_server.core.http_client import HttpClient, http_client
from anki_mcp_server.core.logger import logger
from anki_mcp_server.core.utils import clean_html

from .schemas import (
    AnkiCard,
    AnkiNote,
    NoteCreateRequest,
    NoteUpdateRequest,
    TagsAddRequest,
)


class AnkiService:
    """
    High-level domain service for Anki operations via AnkiConnect.
    Strictly typed using Pydantic models for inputs and outputs.
    """

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    async def invoke(self, action: str, **params: Any) -> Any:
        """Base method to execute an AnkiConnect RPC action."""
        payload = {"action": action, "version": 6, "params": params}

        async with self._client.request(
            "POST", settings.anki_connect_url, json=payload
        ) as response:
            if response.status != 200:
                raise AnkiConnectionError(f"HTTP status {response.status}")
            body: dict[str, Any] = await response.json()

        error_message = body.get("error")
        if error_message:
            logger.error("AnkiConnect rejected '%s': %s", action, error_message)
            raise AnkiAPIError(f"AnkiConnect API error: {error_message}")

        return body.get("result")

    # ==========================================
    # DECK MANAGEMENT
    # ==========================================

    async def get_deck_names(self) -> list[str]:
        decks = await self.invoke("deckNames")
        return [str(d) for d in decks]

    async def create_deck(self, deck_name: str) -> int:
        logger.info("Creating new deck: '%s'", deck_name)
        return int(await self.invoke("createDeck", deck=deck_name))

    async def sync(self) -> None:
        logger.info("Triggering AnkiWeb sync...")
        await self.invoke("sync")

    # ==========================================
    # NOTES MANAGEMENT
    # ==========================================

    async def add_note(self, request: NoteCreateRequest) -> int:
        """Adds a note using the NoteCreateRequest Pydantic model."""
        note_params = {
            "note": {
                "deckName": request.deck_name,
                "modelName": "Basic",
                "fields": {"Front": request.front, "Back": request.back},
                "tags": request.tags,
            }
        }
        result = await self.invoke("addNote", **note_params)
        return int(result)

    async def update_note_fields(self, request: NoteUpdateRequest) -> None:
        """Updates a note using the NoteUpdateRequest Pydantic model."""
        logger.info("Updating fields for note ID: %s", request.note_id)
        note_params = {"note": {"id": request.note_id, "fields": request.fields}}
        await self.invoke("updateNoteFields", **note_params)

    async def delete_notes(self, note_ids: list[int]) -> None:
        logger.info("Deleting %s notes...", len(note_ids))
        await self.invoke("deleteNotes", notes=note_ids)

    async def add_tags(self, request: TagsAddRequest) -> None:
        """Adds tags using the TagsAddRequest Pydantic model."""
        logger.info(
            "Adding tags '%s' to %s notes.", request.tags, len(request.note_ids)
        )
        await self.invoke("addTags", notes=request.note_ids, tags=request.tags)

    async def get_deck_notes(self, deck_name: str, limit: int = 100) -> list[AnkiNote]:
        """Returns a list of validated AnkiNote Pydantic models."""
        query = f'deck:"{deck_name}"'
        note_ids: list[int] = await self.invoke("findNotes", query=query)

        if not note_ids:
            return []

        notes_info: list[dict[str, Any]] = await self.invoke(
            "notesInfo", notes=note_ids[:limit]
        )
        extracted_notes: list[AnkiNote] = []

        for note in notes_info:
            clean_fields = {
                k: clean_html(v.get("value", ""))
                for k, v in note.get("fields", {}).items()
            }

            anki_note = AnkiNote(
                note_id=note["noteId"],
                model_name=note["modelName"],
                fields=clean_fields,
                tags=note.get("tags", []),
            )
            extracted_notes.append(anki_note)

        return extracted_notes

    async def get_deck_cards(self, deck_name: str, limit: int = 100) -> list[AnkiCard]:
        """Returns a list of validated AnkiCard Pydantic models."""
        query = f'deck:"{deck_name}"'
        card_ids: list[int] = await self.invoke("findCards", query=query)

        if not card_ids:
            return []

        cards_info: list[dict[str, Any]] = await self.invoke(
            "cardsInfo", cards=card_ids[:limit]
        )
        extracted_cards: list[AnkiCard] = []

        for card in cards_info:
            clean_fields = {
                k: clean_html(v.get("value", ""))
                for k, v in card.get("fields", {}).items()
            }

            anki_card = AnkiCard(
                card_id=card["cardId"],
                note_id=card["note"],
                interval=card["interval"],
                reps=card["reps"],
                due=card["due"],
                fields=clean_fields,
            )
            extracted_cards.append(anki_card)

        return extracted_cards


anki_service = AnkiService(client=http_client)
