from pydantic import BaseModel, Field


class NoteCreateRequest(BaseModel):
    deck_name: str = Field(..., description="Target Anki deck name")
    front: str = Field(..., description="Content for the Front field")
    back: str = Field(..., description="Content for the Back field")
    tags: list[str] = Field(default_factory=lambda: ["mcp-auto"])


class NoteUpdateRequest(BaseModel):
    note_id: int = Field(..., description="Internal Anki Note ID")
    fields: dict[str, str] = Field(
        ..., description="Key-value map of fields to update (e.g. {'Front': 'new'})"
    )


class TagsAddRequest(BaseModel):
    note_ids: list[int] = Field(..., description="List of note IDs to tag")
    tags: str = Field(..., description="Space-separated string of tags")


class AnkiNote(BaseModel):
    note_id: int = Field(alias="note_id")
    model_name: str
    fields: dict[str, str]
    tags: list[str]


class AnkiCard(BaseModel):
    card_id: int
    note_id: int
    interval: int = Field(description="Days until next review")
    reps: int = Field(description="Total number of reviews")
    due: int = Field(description="Due date or queue state")
    fields: dict[str, str]
