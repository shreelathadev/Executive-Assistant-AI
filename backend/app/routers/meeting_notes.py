#backend/app/routers/meeting_notes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.meeting_note import ExtractRequest, ExtractResponse, SaveRequest, SaveResponse
from app.agent.notes_extraction import extract_meeting_notes
from app.services import meeting_note_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/meeting-notes", tags=["meeting-notes"])


@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest, current_user: User = Depends(get_current_user)):
    # current_user isn't used in the body -- extract() is a stateless AI
    # call with no DB lookup -- but it still requires login. Without this,
    # anyone could hit this endpoint and burn Gemini quota with zero
    # accountability, since there'd be nothing tying the call to an account.
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
        raise HTTPException(status_code=502, detail=f"The model's response didn't match the expected format: {e}")


@router.post("", response_model=SaveResponse, status_code=201)
def save(payload: SaveRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = meeting_note_service.save_meeting_notes(db, current_user.id, payload)
    return result