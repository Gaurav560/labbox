#!/usr/bin/env python3
"""Create a Telusko user from the command line (handy when ALLOW_SIGNUP=false).

Usage (from the repo root):
    backend/.venv/bin/python scripts/create_user.py <username> [password]
If the password is left out you are prompted for it.
"""
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from fastapi import HTTPException  # noqa: E402
from sqlmodel import Session  # noqa: E402

from app.auth import create_user  # noqa: E402
from app.db import engine, init_db  # noqa: E402


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        return 2
    username = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) == 3 else getpass.getpass("Password: ")
    if len(password) < 6:
        print("Password must be at least 6 characters")
        return 1
    init_db()
    with Session(engine) as session:
        try:
            user = create_user(session, username, password)
        except HTTPException as e:
            print(f"Error: {e.detail}")
            return 1
    print(f"Created user {user.username} (id {user.id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
