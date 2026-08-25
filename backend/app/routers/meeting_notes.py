from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.meeting_note import ExtractRequest, ExtractResponse, SaveRequest, SaveResponse
from app.agent.notes_extraction import extract_meeting_notes
from app.services import meeting_note_service
from app.config import settings

router = APIRouter(prefix="/api/meeting-notes", tags=["meeting-notes"])


@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest):
    if not payload.raw_text.strip():
        raise HTTPException(status_code=400, detail="Paste some meeting notes first.")
    try:
        raw = extract_meeting_notes(payload.raw_text)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"Couldn't extract from those notes: {e}")

    try:
        return ExtractResponse(**raw)
    except Exception as e:
        # Model returned valid JSON but not in the shape we asked for —
        # surface it clearly rather than a raw 500 from Pydantic.
        raise HTTPException(status_code=502, detail=f"The model's response didn't match the expected format: {e}")


@router.post("", response_model=SaveResponse, status_code=201)
def save(payload: SaveRequest, db: Session = Depends(get_db)):
    result = meeting_note_service.save_meeting_notes(db, settings.DEMO_USER_ID, payload)
    return result
