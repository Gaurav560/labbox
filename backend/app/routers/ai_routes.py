from fastapi import APIRouter, Depends

from .. import code_complete
from ..slots import lab_open
from ..auth import get_current_user
from ..config import get_settings
from ..labs import get_lab
from ..models import User

router = APIRouter(prefix="/api", tags=["ai"])


@router.get("/ai/config")
def ai_config(user: User = Depends(get_current_user)) -> dict[str, bool]:
    return {"completion": get_settings().AI_COMPLETION and code_complete.ALIAS in get_settings().llm_models}


@router.post("/labs/{lab_id}/complete", response_model=code_complete.CompleteOut, dependencies=[Depends(lab_open)])
async def complete(lab_id: str, body: code_complete.CompleteBody, user: User = Depends(get_current_user)) -> code_complete.CompleteOut:
    """Ghost-text code completion at the cursor (its own daily limit, separate from the tutor)."""
    assert user.id is not None
    return await code_complete.complete(user.id, get_lab(lab_id), body)
