"""Certificates (owner, 27 November): "a certificate, automatically, with a URL to share on LinkedIn, X and other
social media once a lab is passed and completed".

- A learner earns one per lab when 80% of its tasks have passed (slots.is_finished, the moment the lab's slot frees).
- The name on it is the full name the learner types once, for their first certificate (user_profile.certificate_name);
  after that, finishing a lab issues the next certificate by itself, right after the check that finished it.
- Each certificate has a public page, /certificates/<id> in the app. The address to share is /c/<id>: a small HTML
  page with the Open Graph and X card tags that LinkedIn, X, WhatsApp and Facebook read (their bots run no
  JavaScript), which sends people on to the app's page. The card's picture is /api/certificates/<id>/image.jpg.
- The learner may hide a certificate (its page then says it is not available) and correct its name once.
"""
import html
import io
import math
import re
import secrets
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from . import metrics, slots
from .config import BACKEND_DIR
from .labs import LabConfig, all_labs, get_lab
from .models import Certificate, User, UserProfile

ISSUER = "LabBox by Telusko"
ID_ALPHABET = "23456789ABCDEFGHJKMNPQRSTVWXYZ"  # no 0, 1, I, L, O or U: easy to read and type
ID_LENGTH = 8
# Letters (Latin, with accents), spaces, dots, apostrophes and hyphens: what the certificate's fonts can draw.
NAME_RE = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ .'\-]{0,58}[A-Za-zÀ-ÖØ-öø-ÿ.]$")
FONTS = Path(__file__).resolve().parent / "assets" / "fonts"
PRINTS = BACKEND_DIR.parent / "frontend" / "public" / "ukiyo" / "labs"  # Ukiyo's woodblock print for each lab


class CertificateOut(BaseModel):
    id: str
    lab_id: str
    lab_title: str
    lab_subtitle: str = ""
    track: str = ""
    name: str
    tasks_passed: int
    tasks_total: int
    chapters_total: int
    skills: list[str]  # the lab's course parts, in order
    issued_at: datetime
    issuer: str = ISSUER
    hidden: bool = False
    name_corrected: bool = False
    mine: bool = False  # the viewer is the learner (shows the hide switch and the name correction)


class LabCertificateStatus(BaseModel):
    """What the course page and the lab show about a lab's certificate."""
    eligible: bool  # 80% of the lab's tasks passed
    tasks_passed: int
    tasks_total: int
    tasks_needed: int  # how many passed tasks earn it
    certificate: CertificateOut | None = None
    saved_name: str | None = None  # the name typed for an earlier certificate (then claiming needs no typing)


class CheckCertificate(BaseModel):
    """Added to a check's answer when that check finished the lab: the certificate issued, or a prompt to claim it."""
    id: str | None = None
    needs_name: bool = False


def clean_name(raw: str) -> str:
    name = " ".join(raw.split())
    if not NAME_RE.match(name):
        raise HTTPException(422, "Type your name as it should appear: 2 to 60 letters, with spaces, dots, apostrophes or hyphens.")
    return name


def _skills(lab: LabConfig) -> list[str]:
    seen: list[str] = []
    for c in lab.chapters:
        if c.part and c.part not in seen:
            seen.append(c.part)
    return seen


def _task_ids(lab: LabConfig) -> set[str]:
    return {t.id for c in lab.chapters for t in c.tasks}


def _passed(session: Session, user_id: int, lab: LabConfig) -> set[str]:
    return slots._passed_by_lab(session, user_id).get(lab.id, set()) & _task_ids(lab)


def to_out(cert: Certificate, viewer: User | None = None) -> CertificateOut:
    lab = get_lab(cert.lab_id)
    return CertificateOut(
        id=cert.id, lab_id=cert.lab_id, lab_title=lab.title, lab_subtitle=lab.subtitle or lab.description,
        track=lab.track, name=cert.name, tasks_passed=cert.tasks_passed,
        tasks_total=cert.tasks_total, chapters_total=cert.chapters_total, skills=_skills(lab), issued_at=cert.issued_at,
        hidden=cert.hidden, name_corrected=cert.name_corrected, mine=viewer is not None and viewer.id == cert.user_id,
    )


def _profile(session: Session, user_id: int) -> UserProfile:
    p = session.get(UserProfile, user_id)
    if p is None:
        p = UserProfile(user_id=user_id)
        session.add(p)
    return p


def _new_id(session: Session) -> str:
    while True:
        cid = "".join(secrets.choice(ID_ALPHABET) for _ in range(ID_LENGTH))
        if session.get(Certificate, cid) is None:
            return cid


def find(session: Session, user_id: int, lab_id: str) -> Certificate | None:
    return session.exec(select(Certificate).where(Certificate.user_id == user_id, Certificate.lab_id == lab_id)).first()


def status(session: Session, user: User, lab: LabConfig) -> LabCertificateStatus:
    assert user.id is not None
    total = len(_task_ids(lab))
    passed = len(_passed(session, user.id, lab))
    cert = find(session, user.id, lab.id)
    p = session.get(UserProfile, user.id)
    return LabCertificateStatus(
        eligible=slots.is_finished(lab, _passed(session, user.id, lab)), tasks_passed=passed, tasks_total=total,
        tasks_needed=math.ceil(slots.FINISH_SHARE * total), certificate=to_out(cert, user) if cert else None,
        saved_name=p.certificate_name if p else None,
    )


def issue(session: Session, user: User, lab: LabConfig, name: str | None) -> Certificate:
    """The learner's certificate for this lab: the one they have, or a new one. 409 until 80% of the tasks passed;
    422 when no name was ever given (the first certificate asks for it)."""
    assert user.id is not None
    existing = find(session, user.id, lab.id)
    if existing is not None:
        return existing
    passed = _passed(session, user.id, lab)
    if not slots.is_finished(lab, passed):
        need = math.ceil(slots.FINISH_SHARE * len(_task_ids(lab)))
        raise HTTPException(409, f"The certificate comes when {need} of this lab's {len(_task_ids(lab))} tasks have passed "
                                 f"(you have {len(passed)}).")
    profile = _profile(session, user.id)
    if name:
        profile.certificate_name = clean_name(name)
    if not profile.certificate_name:
        raise HTTPException(422, "Type your full name as it should appear on your certificates.")
    cert = Certificate(id=_new_id(session), user_id=user.id, lab_id=lab.id, name=profile.certificate_name,
                       tasks_passed=len(passed), tasks_total=len(_task_ids(lab)), chapters_total=len(lab.chapters))
    session.add(profile)
    session.add(cert)
    session.commit()
    session.refresh(cert)
    metrics.count("labbox_certificates_total")
    return cert


def after_check(session: Session, user: User, lab: LabConfig) -> CheckCertificate | None:
    """Right after a check: when the lab is finished and has no certificate yet, issue it (the name is known) or
    ask for the name. None otherwise, so a finished lab with its certificate never nags."""
    assert user.id is not None
    if find(session, user.id, lab.id) is not None or not slots.is_finished(lab, _passed(session, user.id, lab)):
        return None
    p = session.get(UserProfile, user.id)
    if p is None or not p.certificate_name:
        return CheckCertificate(needs_name=True)
    return CheckCertificate(id=issue(session, user, lab, None).id)


def mine(session: Session, user: User) -> list[CertificateOut]:
    rows = session.exec(select(Certificate).where(Certificate.user_id == user.id).order_by(Certificate.issued_at.desc())).all()  # type: ignore[attr-defined]
    known = {lab.id for lab in all_labs()}
    return [to_out(c, user) for c in rows if c.lab_id in known]


def public(session: Session, cert_id: str, viewer: User | None = None) -> Certificate:
    cert = session.get(Certificate, cert_id.upper())
    if cert is None or (cert.hidden and (viewer is None or viewer.id != cert.user_id)):
        raise HTTPException(404, "This certificate is not available.")
    try:
        get_lab(cert.lab_id)
    except HTTPException:
        raise HTTPException(404, "This certificate is not available.")
    return cert


def change(session: Session, user: User, cert_id: str, name: str | None, hidden: bool | None) -> Certificate:
    cert = session.get(Certificate, cert_id.upper())
    if cert is None or cert.user_id != user.id:
        raise HTTPException(404, "This certificate is not available.")
    if name is not None and clean_name(name) != cert.name:
        if cert.name_corrected:
            raise HTTPException(409, "The name on this certificate was already corrected once.")
        cert.name = clean_name(name)
        cert.name_corrected = True
        _profile(session, user.id).certificate_name = cert.name  # the next certificates use it too
    if hidden is not None:
        cert.hidden = hidden
    session.add(cert)
    session.commit()
    session.refresh(cert)
    return cert


# ---------- what LinkedIn, X and others read ----------

def share_page(cert: Certificate, base: str) -> str:
    """The page behind /c/<id>: card tags for the bots, then on to the app's certificate page for people."""
    lab = get_lab(cert.lab_id)
    e = html.escape
    url = f"{base}/c/{cert.id}"
    image = f"{base}/api/certificates/{cert.id}/image.jpg?v={_image_version(cert)}"
    title = f"{cert.name} completed {lab.title}"
    desc = (f"Certificate {cert.id} from {ISSUER}: {cert.tasks_passed} of {cert.tasks_total} hands-on tasks passed "
            f"on real machines, {cert.issued_at:%d %B %Y}.")
    app_page = f"/certificates/{cert.id}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} | {ISSUER}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{ISSUER}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{e(image)}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="627">
<meta property="og:image:alt" content="{e(f'Certificate: {title}')}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{e(image)}">
<script>location.replace({app_page!r});</script>
</head>
<body><p><a href="{e(app_page)}">View the certificate: {e(title)}</a></p></body>
</html>"""


def missing_page() -> str:
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>Certificate not available | "
            f"{ISSUER}</title><meta name=\"robots\" content=\"noindex\"></head><body><p>This certificate is not available."
            "</p></body></html>")


def _image_version(cert: Certificate) -> str:
    return f"{int(cert.issued_at.timestamp())}{int(cert.name_corrected)}"


def image(cert: Certificate) -> bytes:
    return _render(cert.id, cert.name, cert.lab_id, cert.tasks_passed, cert.tasks_total, cert.chapters_total,
                   cert.issued_at.strftime("%d %B %Y"))


@lru_cache(maxsize=128)
def _render(cid: str, name: str, lab_id: str, passed: int, total: int, chapters: int, date: str) -> bytes:
    """The 1200 x 627 card: cream paper, the lab's woodblock print on the left (Ukiyo), the text, a red seal."""
    from PIL import Image, ImageDraw, ImageFont

    W, H = 1200, 627
    paper, ink, muted, red = (246, 240, 227), (28, 26, 23), (106, 99, 88), (184, 50, 39)
    img = Image.new("RGB", (W, H), paper)
    d = ImageDraw.Draw(img)

    def font(file: str, size: int):
        return ImageFont.truetype(str(FONTS / file), size)

    left = 0
    art = PRINTS / f"{lab_id}.webp"
    if art.is_file():
        try:
            pic = Image.open(art).convert("RGB")
            pw = 380
            scale = max(pw / pic.width, H / pic.height)
            pic = pic.resize((math.ceil(pic.width * scale), math.ceil(pic.height * scale)))
            x0, y0 = (pic.width - pw) // 2, max(0, (pic.height - H) // 5)
            img.paste(pic.crop((x0, y0, x0 + pw, y0 + H)), (0, 0))
            left = pw
        except OSError:
            left = 0
    if not left:
        d.rectangle((0, 0, 24, H), fill=ink)
        left = 24

    # A fine double rule around the text, like a printed certificate.
    x, top = left + 56, 54
    d.rectangle((left + 24, 24, W - 24, H - 24), outline=(210, 198, 176), width=2)
    d.rectangle((left + 32, 32, W - 32, H - 32), outline=(225, 215, 196), width=1)

    def fit(text: str, file: str, size: int, width: int):
        while size > 20 and d.textlength(text, font=font(file, size)) > width:
            size -= 2
        return font(file, size)

    usable = W - 32 - 40 - x
    d.text((x, top), "CERTIFICATE OF COMPLETION", font=font("inter-latin-600-normal.woff", 19), fill=red)
    d.text((x, top + 44), "This certifies that", font=font("inter-latin-400-normal.woff", 22), fill=muted)
    f_name = fit(name, "fraunces-latin-600-normal.woff", 64, usable)
    d.text((x, top + 82), name, font=f_name, fill=ink)
    d.text((x, top + 182), "completed the hands-on lab", font=font("inter-latin-400-normal.woff", 22), fill=muted)
    lab = get_lab(lab_id).title
    d.text((x, top + 218), lab, font=fit(lab, "fraunces-latin-400-italic.woff", 46, usable), fill=ink)
    facts = f"{passed} of {total} tasks passed on a real machine  ·  {chapters} chapters"
    d.text((x, top + 298), facts, font=font("inter-latin-400-normal.woff", 21), fill=muted)

    d.line((x, H - 150, W - 72, H - 150), fill=(210, 198, 176), width=1)
    d.text((x, H - 128), date, font=font("inter-latin-600-normal.woff", 21), fill=ink)
    d.text((x, H - 98), f"Certificate {cid}", font=font("inter-latin-400-normal.woff", 19), fill=muted)
    d.text((x, H - 72), ISSUER, font=font("fraunces-latin-600-normal.woff", 24), fill=ink)

    # The red seal: a square stamp with the product's name.
    s = 112
    sx, sy = W - 72 - s, H - 72 - s
    d.rounded_rectangle((sx, sy, sx + s, sy + s), radius=10, fill=red)
    d.rounded_rectangle((sx + 7, sy + 7, sx + s - 7, sy + s - 7), radius=6, outline=(240, 214, 200), width=2)
    for i, word in enumerate(("Lab", "Box")):
        f = font("fraunces-latin-600-normal.woff", 34)
        tw = d.textlength(word, font=f)
        d.text((sx + (s - tw) / 2, sy + 16 + i * 38), word, font=f, fill=(250, 240, 230))

    out = io.BytesIO()
    img.save(out, "JPEG", quality=88, optimize=True, progressive=True)  # a quarter of a PNG's size, for a photo-like print
    return out.getvalue()
