"""Make (once) a separate author account and print a gateway token for it, for capturing AI lab output.

    cd backend && .venv/bin/python ../tools/authoring/author_token.py atlas-author spring-ai > SCRATCH/token.txt

The token is what a lab machine gets as OPENAI_API_KEY: valid only at the LabBox LLM gateway, for this
account and lab, never the provider's key. Captures then count against the author account's own daily
budget (not the owner's or a learner's) and show in `lab requests`. Keep the token in the session scratchpad,
never in the repo or chat. The account gets a random password nobody knows and is never made admin.
See COURSE_PRODUCTION.md, "Capturing real output".
"""
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from sqlmodel import Session, select  # noqa: E402

from app.auth import hash_password  # noqa: E402
from app.db import engine  # noqa: E402
from app.llm_gateway import create_lab_token  # noqa: E402
from app.models import User  # noqa: E402


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    username, lab = sys.argv[1], sys.argv[2]
    with Session(engine) as s:
        user = s.exec(select(User).where(User.username == username)).first()
        if user is None:
            user = User(username=username, password_hash=hash_password(secrets.token_urlsafe(16)))
            s.add(user)
            s.commit()
            s.refresh(user)
        print(create_lab_token(user.id, lab))


if __name__ == "__main__":
    main()
