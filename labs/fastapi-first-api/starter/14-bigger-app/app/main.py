"""Lostdesk, chapter 14: the app, assembled from its parts. Start it with: fastapi dev app/main.py"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from sqlmodel import select

from .database import SessionDep, create_db_and_tables
from .models import Report, ReportCreate, ReportPublic
from .routers import items


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


# TODO (task app_metadata): give the app its title "Lostdesk", version "1.0.0" and a one-line summary, for /docs.
app = FastAPI(lifespan=lifespan)

app.include_router(items.router)


@app.get("/", tags=["status"])
def home():
    return {"message": "Lostdesk is open. Try /items"}


# TODO (task reports_router): move these three report routes into app/routers/reports.py, on an APIRouter with the
# prefix /reports and the tag "reports", and include that router here, like items.


@app.post("/reports", status_code=status.HTTP_201_CREATED)
def create_report(report: ReportCreate, session: SessionDep) -> ReportPublic:
    db_report = Report.model_validate(report)
    session.add(db_report)
    session.commit()
    session.refresh(db_report)
    return db_report


@app.get("/reports")
def list_reports(session: SessionDep) -> list[ReportPublic]:
    return session.exec(select(Report).order_by(Report.id)).all()


@app.get("/reports/{report_id}")
def read_report(report_id: int, session: SessionDep) -> ReportPublic:
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="No report with that id")
    return report
