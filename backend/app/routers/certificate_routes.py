"""Certificates (owner, 27 November; rules in app/certificates.py). Learner routes need a login; the certificate's
page data, its picture and the share page /c/<id> are public, as a certificate must be."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlmodel import Session

from .. import certificates
from ..auth import _bearer, get_current_user, user_from_token
from ..db import get_session
from ..labs import get_lab
from ..models import User

router = APIRouter(tags=["certificates"])


def viewer(creds: HTTPAuthorizationCredentials | None = Depends(_bearer), session: Session = Depends(get_session)) -> User | None:
    """The logged-in viewer, if any (a public page shows its owner the hide switch)."""
    return user_from_token(creds.credentials, session) if creds else None


class ClaimBody(BaseModel):
    name: str | None = Field(default=None, max_length=80)  # needed for the first certificate only


class ChangeBody(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    hidden: bool | None = None


@router.get("/api/labs/{lab_id}/certificate", response_model=certificates.LabCertificateStatus)
def lab_certificate(lab_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return certificates.status(session, user, get_lab(lab_id))


@router.post("/api/labs/{lab_id}/certificate", response_model=certificates.CertificateOut)
def claim(lab_id: str, body: ClaimBody, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return certificates.to_out(certificates.issue(session, user, get_lab(lab_id), body.name), user)


@router.get("/api/certificates", response_model=list[certificates.CertificateOut])
def my_certificates(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return certificates.mine(session, user)


@router.get("/api/certificates/{cert_id}", response_model=certificates.CertificateOut)
def certificate(cert_id: str, me: User | None = Depends(viewer), session: Session = Depends(get_session)):
    return certificates.to_out(certificates.public(session, cert_id, me), me)


@router.patch("/api/certificates/{cert_id}", response_model=certificates.CertificateOut)
def change(cert_id: str, body: ChangeBody, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return certificates.to_out(certificates.change(session, user, cert_id, body.name, body.hidden), user)


@router.get("/api/certificates/{cert_id}/image.jpg", include_in_schema=False)
def certificate_image(cert_id: str, session: Session = Depends(get_session)) -> Response:
    cert = certificates.public(session, cert_id)
    return Response(certificates.image(cert), media_type="image/jpeg",
                    headers={"Cache-Control": "public, max-age=86400"})


@router.get("/c/{cert_id}", include_in_schema=False, response_class=HTMLResponse)
def share_page(cert_id: str, request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    """The address learners share: card tags for LinkedIn, X and others, then on to the certificate page."""
    try:
        cert = certificates.public(session, cert_id)
    except Exception:
        return HTMLResponse(certificates.missing_page(), status_code=404)
    # The address the visitor used: Caddy and Vite's proxy say it in X-Forwarded-Host (Vite rewrites Host).
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
    base = f"{request.url.scheme}://{host.split(',')[0].strip()}"
    return HTMLResponse(certificates.share_page(cert, base), headers={"Cache-Control": "public, max-age=300"})
