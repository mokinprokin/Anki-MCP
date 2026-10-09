import json

from mcp.server import MCPServer

from anki_mcp_server.anki.schemas import (
    NoteCreateRequest,
    NoteUpdateRequest,
    TagsAddRequest,
)
from anki_mcp_server.anki.service import anki_service
from anki_mcp_server.core.logger import logger
from anki_mcp_server.decorators import handle_anki_errors


def register_anki_tools(mcp: MCPServer) -> None:
    """
    Registers all Anki management tools to the MCP Server.
    """

    @mcp.tool()
    @handle_anki_errors
    async def add_card_to_anki(data: NoteCreateRequest) -> str:
        """
        Create a new vocabulary flashcard (Note) in Anki.
        Use this when the user asks to save a new word, phrase, or concept.
        Automatically uses the default deck if not explicitly provided.
        """
        logger.info("Executing add_card_to_anki for deck: '%s'", data.deck_name)
        note_id = await anki_service.add_note(data)
        return (
            f"Success: Flashcard added to deck '{data.deck_name}'. Note ID: {note_id}"
        )

    @mcp.tool()
    @handle_anki_errors
    async def update_note(data: NoteUpdateRequest) -> str:
        """
        Update fields of an existing Anki flashcard (Note).
        Use this to fix typos, add synonyms, or update translations on an already existing card.
        Requires the exact Note ID.
        """
        logger.info("Updating fields for note ID: %s", data.note_id)
        await anki_service.update_note_fields(data)
        return f"Success: Fields updated for Note ID {data.note_id}."

    @mcp.tool()
    @handle_anki_errors
    async def delete_notes(note_ids: list[int]) -> str:
        """
        Permanently delete specific notes (and their associated cards) from Anki.
        Use this to clean up duplicates or remove unwanted vocabulary.
        """
        logger.info("Deleting notes: %s", note_ids)
        await anki_service.delete_notes(note_ids)
        return f"Success: Deleted {len(note_ids)} notes."

    @mcp.tool()
    @handle_anki_errors
    async def add_tags(data: TagsAddRequest) -> str:
        """
        Attach tags to specific flashcards.
        Tags help categorize words (e.g., 'hard', 'learned', 'idiom').
        """
        logger.info("Adding tags '%s' to %s notes", data.tags, len(data.note_ids))
        await anki_service.add_tags(data)
        return f"Success: Tags '{data.tags}' added to the specified notes."

    @mcp.tool()
    @handle_anki_errors
    async def list_decks() -> str:
        """
        Retrieve a list of all existing deck names in the user's Anki.
        Use this to check where to save cards if the target deck is ambiguous.
        """
        decks = await anki_service.get_deck_names()
        return json.dumps(decks, ensure_ascii=False, indent=2)

    @mcp.tool()
    @handle_anki_errors
    async def create_deck(deck_name: str) -> str:
        """
        Create a new empty deck in Anki.
        Use this if the user wants to start learning a new language or topic.
        """
        deck_id = await anki_service.create_deck(deck_name)
        return f"Success: Deck '{deck_name}' created. Deck ID: {deck_id}"

    @mcp.tool()
    @handle_anki_errors
    async def get_notes_in_deck(deck_name: str, limit: int = 50) -> str:
        """
        Fetch the vocabulary content (Notes) stored in a specific deck.
        Use this to check for existing words/duplicates before adding new ones,
        or to review the deck's contents.
        Returns clean data without spaced repetition statistics.
        """
        notes = await anki_service.get_deck_notes(deck_name=deck_name, limit=limit)
        if not notes:
            return f"Deck '{deck_name}' is empty or does not exist."

        return json.dumps([n.model_dump() for n in notes], ensure_ascii=False, indent=2)

    @mcp.tool()
    @handle_anki_errors
    async def get_cards_in_deck(deck_name: str, limit: int = 50) -> str:
        """
        Fetch the physical study items (Cards) in a specific deck.
        Unlike get_notes_in_deck, this includes spaced repetition scheduling data
        such as 'interval' (days until next review) and 'due' status.
        Use this to analyze learning progress.
        """
        cards = await anki_service.get_deck_cards(deck_name=deck_name, limit=limit)
        if not cards:
            return f"Deck '{deck_name}' is empty or does not exist."

        return json.dumps([c.model_dump() for c in cards], ensure_ascii=False, indent=2)

    @mcp.tool()
    @handle_anki_errors
    async def sync_anki() -> str:
        """
        Synchronize the local Anki database with the AnkiWeb cloud.
        Use this to backup data after adding a large batch of new flashcards.
        """
        await anki_service.sync()
        return "Success: Local Anki collection synced with AnkiWeb."
