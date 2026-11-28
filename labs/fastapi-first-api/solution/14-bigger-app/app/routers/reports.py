"""Every route about passengers' reports. main.py includes this router under /reports."""
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from ..database import SessionDep
from ..models import Report, ReportCreate, ReportPublic

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_report(report: ReportCreate, session: SessionDep) -> ReportPublic:
    db_report = Report.model_validate(report)
    session.add(db_report)
    session.commit()
    session.refresh(db_report)
    return db_report


@router.get("")
def list_reports(session: SessionDep) -> list[ReportPublic]:
    return session.exec(select(Report).order_by(Report.id)).all()


@router.get("/{report_id}")
def read_report(report_id: int, session: SessionDep) -> ReportPublic:
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="No report with that id")
    return report
