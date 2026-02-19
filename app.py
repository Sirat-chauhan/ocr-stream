import streamlit as st
import requests
import cv2
import numpy as np
import os
import re
import json
import base64
from datetime import datetime
from PIL import Image, ImageEnhance
import io
from supabase import create_client, Client

# ================================================================
# 1. PAGE CONFIG
# ================================================================
st.set_page_config(page_title="OCR Stream", page_icon="📝", layout="centered")

# ================================================================
# 2. CUSTOM CSS
# ================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }

    .stApp {
        background: #0c0f1a;
        color: #e8eaf0;
    }

    h1, h2, h3 {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
    }

    .ocr-header {
        background: linear-gradient(135deg, #1a1f35 0%, #0f1320 100%);
        border: 1px solid #2a3060;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .ocr-header::before {
        content: '';
        position: absolute;
        top: -40px; right: -40px;
        width: 140px; height: 140px;
        background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .ocr-header h1 {
        font-size: 2rem;
        margin: 0;
        color: #f0f2ff;
        letter-spacing: -0.5px;
    }
    .ocr-header p {
        margin: 6px 0 0;
        color: #6b7280;
        font-size: 0.9rem;
        font-family: 'JetBrains Mono', monospace;
    }

    .info-card {
        background: #141729;
        border: 1px solid #1e2448;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }

    .kv-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }
    .kv-table th {
        text-align: left;
        padding: 10px 14px;
        background: #0f1320;
        color: #6366f1;
        font-weight: 600;
        font-size: 0.78rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        border-bottom: 1px solid #1e2448;
    }
    .kv-table td {
        padding: 10px 14px;
        border-bottom: 1px solid #1a1f35;
        color: #d1d5db;
        vertical-align: top;
    }
    .kv-table td:first-child {
        color: #9ca3af;
        width: 36%;
        font-weight: 500;
    }
    .kv-table tr:hover td {
        background: #1a1f35;
    }

    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .badge-aadhaar { background: #1a2a1a; color: #4ade80; border: 1px solid #166534; }
    .badge-pan     { background: #1a1a2a; color: #818cf8; border: 1px solid #3730a3; }
    .badge-unknown { background: #2a1a1a; color: #f87171; border: 1px solid #991b1b; }
    .badge-normal  { background: #1a2030; color: #60a5fa; border: 1px solid #1e3a5f; }
    .badge-dl      { background: #1a2a2a; color: #34d399; border: 1px solid #065f46; }
    .badge-voter   { background: #2a1a2a; color: #c084fc; border: 1px solid #6b21a8; }

    .fail-log {
        background: #100a0a;
        border: 1px solid #3b1515;
        border-radius: 12px;
        padding: 18px;
        margin-top: 16px;
    }
    .fail-log-title {
        color: #ef4444;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .fail-entry {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #9ca3af;
        padding: 6px 0;
        border-bottom: 1px solid #1c0f0f;
        display: flex;
        gap: 12px;
    }
    .fail-entry:last-child { border-bottom: none; }
    .fail-ts { color: #6b7280; flex-shrink: 0; }
    .fail-msg { color: #fca5a5; }

    .conf-bar-wrap { display: flex; align-items: center; gap: 10px; margin-top: 6px; }
    .conf-bar-bg { flex: 1; background: #1a1f35; border-radius: 4px; height: 6px; overflow: hidden; }
    .conf-bar-fill { height: 100%; border-radius: 4px; }
    .conf-high  { background: #4ade80; }
    .conf-mid   { background: #facc15; }
    .conf-low   { background: #f87171; }

    .photo-card {
        background: #141729;
        border: 1px solid #1e2448;
        border-radius: 12px;
        padding: 20px;
        display: flex;
        align-items: flex-start;
        gap: 20px;
        margin-bottom: 16px;
    }
    .photo-frame {
        width: 100px;
        height: 120px;
        border-radius: 8px;
        border: 2px solid #2a3060;
        overflow: hidden;
        flex-shrink: 0;
        background: #0c0f1a;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .photo-frame img { width: 100%; height: 100%; object-fit: cover; }
    .photo-placeholder {
        width: 100px;
        height: 120px;
        border-radius: 8px;
        border: 2px dashed #2a3060;
        flex-shrink: 0;
        background: #0c0f1a;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 6px;
        color: #374151;
        font-size: 0.72rem;
        font-family: 'JetBrains Mono', monospace;
        text-align: center;
    }
    .photo-meta { flex: 1; display: flex; flex-direction: column; gap: 6px; }
    .photo-label { font-size: 0.72rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: #4b5563; }
    .photo-name { font-size: 1.1rem; font-weight: 700; color: #f0f2ff; }
    .photo-sub { font-size: 0.8rem; color: #6b7280; font-family: 'JetBrains Mono', monospace; }

    .section-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #4b5563;
        margin: 20px 0 8px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 28px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover { opacity: 0.88 !important; }

    .stTextArea textarea {
        background: #0f1320 !important;
        color: #d1d5db !important;
        border: 1px solid #1e2448 !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem !important;
    }

    .stDownloadButton > button {
        background: #141729 !important;
        color: #818cf8 !important;
        border: 1px solid #2a3060 !important;
        border-radius: 8px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
    }

    .stSelectbox > div > div {
        background: #141729 !important;
        border-color: #1e2448 !important;
        color: #d1d5db !important;
    }

    .stFileUploader {
        background: #141729 !important;
        border: 2px dashed #2a3060 !important;
        border-radius: 12px !important;
    }

    .stAlert { border-radius: 10px !important; }
    hr { border-color: #1e2448 !important; }
</style>
""", unsafe_allow_html=True)

# ================================================================
# 3. CONFIG & SUPABASE INIT
# ================================================================
OCR_API_KEY = os.getenv("OCR_API_KEY", "")
OCR_URL = "https://api.ocr.space/parse/image"

def _get_secret(key: str, default: str = "") -> str:
    """Safely read from env vars first, then st.secrets, with fallback."""
    val = os.getenv(key)
    if val:
        return val
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default

SUPABASE_URL = _get_secret("SUPABASE_URL")
SUPABASE_KEY = _get_secret("SUPABASE_ANON_KEY")

@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# ================================================================
# 4. SESSION STATE INIT
# ================================================================
if "user" not in st.session_state:
    st.session_state.user = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "failure_log" not in st.session_state:
    st.session_state.failure_log = []
if "ocr_mode" not in st.session_state:
    st.session_state.ocr_mode = "Normal"
# Camera: store raw bytes so they survive button-click reruns
if "camera_bytes" not in st.session_state:
    st.session_state.camera_bytes = None
if "camera_fsize" not in st.session_state:
    st.session_state.camera_fsize = 0

# ================================================================
# 5. ALL FUNCTION DEFINITIONS
# ================================================================

def log_failure(context: str, message: str):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.failure_log.append({"ts": ts, "ctx": context, "msg": message})


# ── Auth helpers ─────────────────────────────────────────────────
def auth_login(email: str, password: str):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = res.user
        st.session_state.access_token = res.session.access_token
        supabase.postgrest.auth(res.session.access_token)
        return True, None
    except Exception as e:
        return False, str(e)

def auth_signup(email: str, password: str):
    try:
        supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "email_redirect_to": "https://ocr-stream-nhjd5pbhtxcm99hfgncbre.streamlit.app"
            }
        })
        return True, None
    except Exception as e:
        return False, str(e)

def auth_logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.access_token = None

def save_extraction(doc_type: str, fields: dict, raw_text: str = "",
                    file_name: str = "", file_size_bytes: int = 0):
    """Save to single extractions table."""
    if not st.session_state.user:
        return False, "Not logged in"
    try:
        supabase.postgrest.auth(st.session_state.access_token)
        size_kb = round(file_size_bytes / 1024, 1) if file_size_bytes else 0
        row = {
            "user_id":              st.session_state.user.id,
            "user_email":           st.session_state.user.email,
            "doc_type":             doc_type if doc_type in ("aadhaar","pan","dl","voter") else "other",
            "file_name":            file_name,
            "file_size_kb":         size_kb,
            "holder_name":          fields.get("Name", ""),
            "dob":                  fields.get("Date of Birth", ""),
            # Aadhaar
            "aadhaar_number":       fields.get("Aadhaar Number", ""),
            "gender":               fields.get("Gender", ""),
            "address":              fields.get("Address", ""),
            "pincode":              fields.get("Pincode", ""),
            "state":                fields.get("State", ""),
            "vid":                  fields.get("VID", ""),
            # PAN
            "pan_number":           fields.get("PAN Number", ""),
            "father_name":          fields.get("Father's Name", ""),
            "account_type":         fields.get("Account Type", ""),
            "issued_by":            fields.get("Issued By", ""),
            # DL
            "dl_number":            fields.get("DL Number", ""),
            "valid_till":           fields.get("Valid Till", ""),
            "vehicle_class":        fields.get("Vehicle Class", ""),
            "blood_group":          fields.get("Blood Group", ""),
            "issuing_authority":    fields.get("Issuing Authority", ""),
            # Voter
            "epic_number":          fields.get("EPIC Number", ""),
            "father_husband_name":  fields.get("Father/Husband Name", ""),
            "constituency":         fields.get("Constituency", ""),
            "part_no":              fields.get("Part No", ""),
            "raw_text":             raw_text[:4000],
        }
        supabase.table("extractions").insert(row).execute()
        return True, None
    except Exception as e:
        return False, str(e)

def load_extractions():
    """Load all extractions for current user, newest first."""
    if not st.session_state.user:
        return []
    try:
        supabase.postgrest.auth(st.session_state.access_token)
        res = (supabase.table("extractions")
               .select("*")
               .eq("user_id", st.session_state.user.id)
               .order("created_at", desc=True)
               .execute())
        return res.data or []
    except Exception as e:
        log_failure("Supabase Fetch", str(e))
        return []


# ── Auth UI ───────────────────────────────────────────────────────
def render_auth_ui():
    st.markdown("""
    <div class="ocr-header">
        <h1>📝 OCR Stream</h1>
        <p>Sign in to securely extract &amp; store document data</p>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔐 Login", "✍ Sign Up"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login", use_container_width=True, key="btn_login"):
            ok, err = auth_login(email, password)
            if ok:
                st.success("Logged in!")
                st.rerun()
            else:
                st.error(f"Login failed: {err}")

    with tab_signup:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password (min 6 chars)", type="password", key="signup_pw")
        if st.button("Create Account", use_container_width=True, key="btn_signup"):
            ok, err = auth_signup(email, password)
            if ok:
                st.success("Account created! Check your email to confirm, then log in.")
            else:
                st.error(f"Sign up failed: {err}")


# ── OCR / Image helpers ───────────────────────────────────────────

def get_file_type(f) -> str:
    """
    Safely get MIME type — works for both st.file_uploader and st.camera_input objects.
    Camera captures sometimes have an unreliable or missing .type attribute.
    """
    try:
        t = getattr(f, "type", None)
        if t and isinstance(t, str) and t.strip():
            return t.strip()
        # Fallback: infer from file name
        name = getattr(f, "name", "") or ""
        if name.lower().endswith(".pdf"):
            return "application/pdf"
        # Camera captures are always JPEG
        return "image/jpeg"
    except Exception:
        return "image/jpeg"


def detect_blur(file) -> float:
    try:
        file.seek(0)
        image = Image.open(file).convert("L")
        image_np = np.array(image)
        score = cv2.Laplacian(image_np, cv2.CV_64F).var()
        file.seek(0)
        return score
    except Exception as e:
        log_failure("Blur Detection", str(e))
        return 999


def preprocess_image(file, max_width: int = 1200) -> io.BytesIO:
    """
    Resize + enhance + compress image.
    Camera photos from phones can be 3-8 MB; OCR.space free tier times out
    on anything over ~500 KB. We target <300 KB aggressively.
    """
    try:
        file.seek(0)
        image = Image.open(file).convert("L")  # greyscale shrinks size a lot

        # Resize: cap at max_width (1200px is plenty for OCR)
        if image.width > max_width:
            ratio = max_width / image.width
            new_h = int(image.height * ratio)
            image = image.resize((max_width, new_h), Image.LANCZOS)

        # Enhance for OCR readability
        image = ImageEnhance.Contrast(image).enhance(1.5)
        image = ImageEnhance.Sharpness(image).enhance(1.5)

        # Compress: try quality levels until under 300 KB
        target_bytes = 300 * 1024  # 300 KB
        for quality in [60, 45, 30, 20]:
            buf = io.BytesIO()
            image.save(buf, format="JPEG", quality=quality, optimize=True)
            size = buf.tell()
            if size <= target_bytes:
                buf.seek(0)
                log_failure("Preprocess Info", f"Compressed to {round(size/1024)}KB at quality={quality}") if quality < 45 else None
                return buf
            # If still too big at quality=20, just return it anyway
            if quality == 20:
                buf.seek(0)
                return buf

        buf.seek(0)
        return buf
    except Exception as e:
        log_failure("Image Preprocessing", str(e))
        file.seek(0)
        return file


def extract_face_photo(file):
    try:
        file.seek(0)
        img_pil = Image.open(file).convert("RGB")
        img_np  = np.array(img_pil)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        h, w    = img_bgr.shape[:2]
        gray    = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        cascade_paths = [
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml",
            "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml",
            "/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml",
        ]
        face_cascade = None
        for cp in cascade_paths:
            if os.path.exists(cp):
                face_cascade = cv2.CascadeClassifier(cp)
                break

        face_rect = None
        if face_cascade is not None and not face_cascade.empty():
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4,
                                                  minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
            if len(faces) > 0:
                best, best_score = None, -1
                for (fx, fy, fw, fh) in faces:
                    right_bonus = 1 if fx > w * 0.4 else 0
                    score = right_bonus + (fw * fh) / (w * h)
                    if score > best_score:
                        best_score = score
                        best = (fx, fy, fw, fh)
                face_rect = best

        if face_rect is not None:
            fx, fy, fw, fh = face_rect
            pad_x, pad_y = int(fw * 0.20), int(fh * 0.20)
            face_crop = img_pil.crop((max(0, fx - pad_x), max(0, fy - pad_y),
                                      min(w, fx + fw + pad_x), min(h, fy + fh + pad_y)))
        else:
            face_crop = img_pil.crop((int(w * 0.60), int(h * 0.10),
                                      int(w * 0.85), int(h * 0.70)))
            log_failure("Face Detection", "No face detected — using ROI heuristic fallback")

        face_crop = face_crop.resize((100, 120), Image.LANCZOS)
        buf = io.BytesIO()
        face_crop.save(buf, format="JPEG", quality=85)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception as e:
        log_failure("Face Extraction", str(e))
        return None


def photo_html(b64, name="", doc_type=""):
    if b64:
        photo_div = f'<div class="photo-frame"><img src="data:image/jpeg;base64,{b64}" alt="Photo"/></div>'
    else:
        photo_div = '<div class="photo-placeholder">👤<br/>No photo<br/>found</div>'
    sub_lines = []
    if doc_type == "aadhaar":
        sub_lines = ["Aadhaar Card Holder", "भारत सरकार"]
    elif doc_type == "pan":
        sub_lines = ["PAN Card Holder", "Income Tax Department"]
    elif doc_type == "dl":
        sub_lines = ["Driving Licence Holder", "Transport Department"]
    elif doc_type == "voter":
        sub_lines = ["Voter ID Card Holder", "Election Commission of India"]
    sub_html = "".join(f'<div class="photo-sub">{s}</div>' for s in sub_lines)
    return f"""
    <div class="photo-card">
        {photo_div}
        <div class="photo-meta">
            <div class="photo-label">Identity Card Photo</div>
            <div class="photo-name">{name or "—"}</div>
            {sub_html}
        </div>
    </div>"""


def compress_image_bytes(raw_bytes: bytes) -> bytes:
    """
    Takes raw image bytes, returns compressed JPEG bytes <300 KB.
    Works entirely on bytes — no file pointer issues possible.
    Phone camera JPEGs are 3-8 MB; OCR.space free tier times out on large files.
    Greyscale + resize + quality reduction brings them to <200 KB reliably.
    """
    try:
        img = Image.open(io.BytesIO(raw_bytes)).convert("L")  # greyscale = 3x smaller

        # Resize: 1200px wide is plenty for OCR accuracy
        max_w = 1200
        if img.width > max_w:
            img = img.resize((max_w, int(img.height * max_w / img.width)), Image.LANCZOS)

        # Enhance contrast/sharpness to help OCR
        img = ImageEnhance.Contrast(img).enhance(1.5)
        img = ImageEnhance.Sharpness(img).enhance(1.4)

        # Try quality levels until under 280 KB
        target = 280 * 1024
        for quality in [75, 60, 45, 30, 20]:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            result_bytes = buf.getvalue()
            if len(result_bytes) <= target or quality == 20:
                return result_bytes

        return buf.getvalue()  # fallback: whatever we got at quality=20
    except Exception as e:
        log_failure("Compress Image", str(e))
        return raw_bytes  # send original if compression fails


def perform_ocr(raw_bytes: bytes, language_code: str, engine_code: int,
                _retry: bool = True) -> dict:
    """
    Takes raw image bytes (not a file handle) — eliminates all seek/pointer bugs.
    Compresses first, sends to OCR.space, retries with Engine 1 on timeout.
    """
    if not OCR_API_KEY:
        err = "Missing OCR_API_KEY"
        log_failure("OCR API", err)
        return {"error": err}
    try:
        # Always compress — the single biggest fix for timeout errors
        compressed_bytes = compress_image_bytes(raw_bytes)
        kb = round(len(compressed_bytes) / 1024, 1)

        response = requests.post(
            OCR_URL,
            data={
                "apikey":            OCR_API_KEY,
                "language":          language_code,
                "OCREngine":         engine_code,
                "isOverlayRequired": False,   # faster — we don't need overlay
                "detectOrientation": True,    # handles rotated phone photos
                "scale":             True,    # OCR.space upscales internally
            },
            files={"file": ("image.jpg", compressed_bytes, "image/jpeg")},
            timeout=90,
        )
        response.raise_for_status()
        result = response.json()

        if result.get("IsErroredOnProcessing"):
            err_msgs = result.get("ErrorMessage", ["Unknown OCR error"])
            err_str  = "; ".join(err_msgs) if isinstance(err_msgs, list) else str(err_msgs)
            if _retry and ("timed out" in err_str.lower() or "timeout" in err_str.lower()):
                log_failure("OCR Retry", f"Engine {engine_code} timed out → retrying Engine 1")
                return perform_ocr(raw_bytes, language_code, 1, _retry=False)
            log_failure("OCR Processing", err_str)
            return {"error": err_str}

        return result

    except requests.Timeout:
        if _retry:
            log_failure("OCR Retry", "Request timed out → retrying with Engine 1")
            return perform_ocr(raw_bytes, language_code, 1, _retry=False)
        msg = "OCR timed out even after retry. Try better lighting or Engine 1."
        log_failure("OCR Timeout", msg)
        return {"error": msg}
    except requests.HTTPError as e:
        msg = f"HTTP error: {e}"
        log_failure("OCR HTTP Error", msg)
        return {"error": msg}
    except Exception as e:
        msg = f"Unexpected error: {e}"
        log_failure("OCR Unknown", msg)
        return {"error": msg}


# ── Document parsing ──────────────────────────────────────────────
def clean_ocr_text(text: str) -> str:
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u200b-\u200f\ufeff]', '', text)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'(?<=\d)[Oo](?=\d)', '0', text)
    text = re.sub(r'(?<=\d)[Il](?=\d)', '1', text)
    return text.strip()

def detect_doc_type(text: str) -> str:
    text = clean_ocr_text(text)
    t = text.lower()

    aadhaar_signals = ["aadhaar","aadhar","aadhar card","uidai","uid","unique identification authority",
                       "enrollment no","enrolment no","date of birth","year of birth","government of india",
                       "भारत सरकार","आधार","मेरा आधार","aadhaa","adhaar","adhar","aadha"]
    pan_signals     = ["permanent account number","income tax department","income tax","आयकर विभाग",
                       "govt. of india","government of india","income"]
    dl_signals      = ["driving licence","driving license","dl no","licence no","license no",
                       "transport department","motor vehicles","रोड ट्रांसपोर्ट","transport authority",
                       "driving","vehicle class","cov","lmv","mcwg","badge no","rto"]
    voter_signals   = ["election commission","voter","electors photo","epic","electoral",
                       "निर्वाचन आयोग","मतदाता","voter id","voter card","part no","serial no",
                       "assembly constituency","parliamentary constituency","elector"]

    pan_pattern     = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text)
    aadhaar_pattern = re.search(r'\b\d{4}[\s\-]\d{4}[\s\-]\d{4}\b|\b\d{12}\b', text)
    masked_pattern  = re.search(r'\bXXXX\s*XXXX\s*\d{4}\b', text, re.IGNORECASE)
    dl_pattern      = re.search(r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?\d{11}\b|\b[A-Z]{2}\d{13}\b', text)
    epic_pattern    = re.search(r'\b[A-Z]{3}\d{7}\b', text)

    if masked_pattern:
        aadhaar_pattern = masked_pattern

    scores = {
        "aadhaar": sum(1 for s in aadhaar_signals if s in t) + (5 if aadhaar_pattern else 0),
        "pan":     sum(1 for s in pan_signals     if s in t) + (5 if pan_pattern     else 0),
        "dl":      sum(1 for s in dl_signals      if s in t) + (5 if dl_pattern      else 0),
        "voter":   sum(1 for s in voter_signals   if s in t) + (5 if epic_pattern    else 0),
    }
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best
    return "unknown"

def extract_aadhaar_fields(text: str) -> dict:
    fields = {}
    text  = clean_ocr_text(text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full  = text

    masked_m = re.search(r'\b(XXXX[\s]*XXXX[\s]*\d{4})\b', full, re.IGNORECASE)
    if masked_m:
        fields["Aadhaar Number"] = re.sub(r'\s+', ' ', masked_m.group(1).upper()).strip()
    else:
        num_patterns = [
            (r'\b(\d{4})\s(\d{4})\s(\d{4})\b', lambda m: f"{m.group(1)} {m.group(2)} {m.group(3)}"),
            (r'\b(\d{4})-(\d{4})-(\d{4})\b',   lambda m: f"{m.group(1)} {m.group(2)} {m.group(3)}"),
            (r'(?<!\d)(\d{12})(?!\d)',           lambda m: f"{m.group(1)[:4]} {m.group(1)[4:8]} {m.group(1)[8:]}"),
        ]
        for pat, fmt in num_patterns:
            m = re.search(pat, full)
            if m:
                fields["Aadhaar Number"] = fmt(m)
                break

    for i, line in enumerate(lines):
        if line.strip().lower() == 'to' and i + 1 < len(lines):
            candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
            words = candidate.split()
            if 1 <= len(words) <= 5 and all(len(w) >= 2 for w in words):
                fields["Name"] = candidate.title()
            break

    if "Name" not in fields:
        m = re.search(r'(?:name|naam|नाम)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,40})', full, re.IGNORECASE)
        if m:
            candidate = re.sub(r'\s+', ' ', m.group(1)).strip().rstrip('.')
            words = candidate.split()
            if len(words) >= 2 or (len(words) == 1 and len(words[0]) >= 5):
                fields["Name"] = candidate.title()

    if "Name" not in fields:
        dob_line_idx, gender_line_idx = None, None
        for i, line in enumerate(lines):
            if re.search(r'\b(dob|date of birth|जन्म|year of birth)\b', line, re.IGNORECASE):
                dob_line_idx = i
            if re.search(r'\b(male|female|transgender|पुरुष|महिला)\b', line, re.IGNORECASE):
                gender_line_idx = i
        search_indices = []
        if dob_line_idx is not None:
            search_indices += [dob_line_idx - 1, dob_line_idx - 2]
        if gender_line_idx is not None:
            search_indices += [gender_line_idx - 1]
        for idx in search_indices:
            if 0 <= idx < len(lines):
                candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[idx]).strip()
                words = candidate.split()
                if 2 <= len(words) <= 5 and all(len(w) >= 2 for w in words):
                    fields["Name"] = candidate.title()
                    break

    if "Name" not in fields:
        skip_words = {'male','female','dob','date','birth','address','government','india',
                      'aadhaar','aadhar','uid','enrollment','year','of','और','भारत'}
        for line in lines[1:12]:
            candidate = re.sub(r'[^A-Za-z\s]', '', line).strip()
            words = [w for w in candidate.split() if len(w) >= 2]
            if 2 <= len(words) <= 5:
                if not {w.lower() for w in words}.intersection(skip_words):
                    if all(w.isalpha() for w in words):
                        fields["Name"] = candidate.title()
                        break

    dob_patterns = [
        r'(?:dob|date\s+of\s+birth|d\.o\.b|जन्म\s*(?:तिथि)?|year\s+of\s+birth)\s*[:\-]?\s*'
        r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b',
        r'\b(\d{1,2}[\s\-](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\-]\d{4})\b',
        r'(?:year\s+of\s+birth|yob)\s*[:\-]?\s*(\d{4})',
    ]
    for pat in dob_patterns:
        m = re.search(pat, full, re.IGNORECASE)
        if m:
            fields["Date of Birth"] = m.group(1).strip()
            break

    gender_map = {'male':'Male','female':'Female','transgender':'Transgender',
                  'पुरुष':'Male (पुरुष)','महिला':'Female (महिला)','mal e':'Male','femal':'Female'}
    for token, label in gender_map.items():
        if re.search(r'\b' + re.escape(token) + r'\b', full, re.IGNORECASE):
            fields["Gender"] = label
            break

    addr_start = re.search(
        r'(?:s[/\\]o|d[/\\]o|w[/\\]o|c[/\\]o|address|पता)\s*[:\-]?\s*(.+)',
        full, re.IGNORECASE | re.DOTALL)
    if addr_start:
        addr_raw = addr_start.group(1)
        addr_raw = re.split(
            r'\b(XXXX|VID\b|\d{4}[\s\-]\d{4}[\s\-]\d{4}|date\s+of\s+birth|dob\b|male\b|female\b|आपका|मेरा)',
            addr_raw, flags=re.IGNORECASE)[0]
        addr_clean = re.sub(r'\s+', ' ', addr_raw).strip().rstrip(',').rstrip('-').strip()
        if len(addr_clean) > 8:
            fields["Address"] = addr_clean[:250]

    for m in re.finditer(r'\b(\d{6})\b', full):
        pin = m.group(1)
        if "Aadhaar Number" in fields and pin in fields["Aadhaar Number"].replace(' ', ''):
            continue
        fields["Pincode"] = pin
        break

    state_pattern = (
        r'\b(andhra\s*pradesh|arunachal\s*pradesh|assam|bihar|chhattisgarh|goa|gujarat|haryana|'
        r'himachal\s*pradesh|jharkhand|karnataka|kerala|madhya\s*pradesh|maharashtra|manipur|'
        r'meghalaya|mizoram|nagaland|odisha|orissa|punjab|rajasthan|sikkim|tamil\s*nadu|telangana|'
        r'tripura|uttar\s*pradesh|uttarakhand|west\s*bengal|delhi|new\s*delhi|jammu|ladakh|'
        r'chandigarh|puducherry|pondicherry)\b')
    sm = re.search(state_pattern, full, re.IGNORECASE)
    if sm:
        fields["State"] = sm.group(1).title()

    vid_m = re.search(
        r'(?:vid|virtual\s*id|virtual\s*identification\s*number)\s*[:\-]?\s*(\d[\d\s]{14,17})',
        full, re.IGNORECASE)
    if vid_m:
        raw_vid = re.sub(r'\s', '', vid_m.group(1))
        if len(raw_vid) == 16:
            fields["VID"] = f"{raw_vid[:4]} {raw_vid[4:8]} {raw_vid[8:12]} {raw_vid[12:]}"

    return fields

def extract_pan_fields(text: str) -> dict:
    fields = {}
    text  = clean_ocr_text(text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full  = text

    m = re.search(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b', full)
    if m:
        fields["PAN Number"] = m.group(1)
    else:
        m = re.search(r'\b([A-Z]{5})\s([0-9]{4}[A-Z])\b', full)
        if m:
            fields["PAN Number"] = m.group(1) + m.group(2)

    for i, line in enumerate(lines):
        if re.search(r'(?:^|[/|])\s*name\s*$', line, re.IGNORECASE):
            if i + 1 < len(lines):
                candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
                if len(candidate.split()) >= 1 and len(candidate) >= 4:
                    fields["Name"] = candidate.title()
            break

    if "Name" not in fields:
        name_label = re.search(r'(?:name|naam|नाम)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,50})',
                               full, re.IGNORECASE)
        if name_label:
            candidate = re.sub(r'\s+', ' ', name_label.group(1)).strip().rstrip('.')
            if len(candidate.split()) >= 1 and len(candidate) >= 4:
                fields["Name"] = candidate.title()

    if "Name" not in fields:
        skip_patterns = [r'income\s+tax',r'govt',r'government',r'permanent\s+account',
                         r'account\s+number',r'india',r'pan\s+card',r'\d',r'विभाग',r'कार्ड',r'संख्या']
        for line in lines:
            clean = re.sub(r'[^A-Za-z\s\.]', '', line).strip()
            words = [w for w in clean.split() if len(w) >= 2]
            if 1 <= len(words) <= 5 and all(w.isalpha() for w in words):
                if not any(re.search(p, line, re.IGNORECASE) for p in skip_patterns) and len(clean) >= 4:
                    fields["Name"] = clean.title()
                    break

    for i, line in enumerate(lines):
        if re.search(r"father'?s?\s*name", line, re.IGNORECASE):
            if i + 1 < len(lines):
                candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
                if len(candidate) >= 4:
                    fields["Father's Name"] = candidate.title()
            break

    if "Father's Name" not in fields:
        father_label = re.search(
            r"(?:father'?s?\s*(?:name)?|father|पिता(?:\s*का\s*नाम)?)\s*[:\-/]\s*([A-Za-z][A-Za-z\s\.]{2,50})",
            full, re.IGNORECASE)
        if father_label:
            candidate = re.sub(r'\s+', ' ', father_label.group(1)).strip().rstrip('.')
            if len(candidate) >= 4:
                fields["Father's Name"] = candidate.title()

    if "Father's Name" not in fields:
        holder_name = fields.get("Name", "")
        skip_patterns = [r'income\s+tax',r'govt',r'government',r'india',r'\d']
        found_holder = False
        for line in lines:
            clean = re.sub(r'[^A-Za-z\s\.]', '', line).strip()
            words = [w for w in clean.split() if len(w) >= 2]
            if clean.title() == holder_name:
                found_holder = True
                continue
            if found_holder and 1 <= len(words) <= 5 and all(w.isalpha() for w in words):
                if not any(re.search(p, line, re.IGNORECASE) for p in skip_patterns) and len(clean) >= 4:
                    fields["Father's Name"] = clean.title()
                    break

    for i, line in enumerate(lines):
        if re.search(r'date\s+of\s+birth|dob|जन्म', line, re.IGNORECASE):
            m = re.search(r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', line)
            if m:
                fields["Date of Birth"] = m.group(1).strip()
                break
            if i + 1 < len(lines):
                m = re.search(r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', lines[i + 1])
                if m:
                    fields["Date of Birth"] = m.group(1).strip()
            break

    if "Date of Birth" not in fields:
        m = re.search(r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b', full)
        if m:
            fields["Date of Birth"] = m.group(1).strip()

    type_m = re.search(r'\b(individual|company|firm|huf|trust|aop|boi|local authority)\b',
                       full, re.IGNORECASE)
    if type_m:
        fields["Account Type"] = type_m.group(1).title()

    if re.search(r'income\s+tax|आयकर', full, re.IGNORECASE):
        fields["Issued By"] = "Income Tax Department, Govt. of India"

    return fields

def extract_dl_fields(text: str) -> dict:
    fields = {}
    text  = clean_ocr_text(text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full  = text

    dl_m = re.search(r'\b([A-Z]{2})[\s\-]?(\d{2})[\s\-]?(\d{4})[\s\-]?(\d{7})\b', full)
    if dl_m:
        fields["DL Number"] = f"{dl_m.group(1)}-{dl_m.group(2)}-{dl_m.group(3)}-{dl_m.group(4)}"
    else:
        dl_m2 = re.search(r'\b([A-Z]{2}\d{13})\b', full)
        if dl_m2:
            fields["DL Number"] = dl_m2.group(1)

    for pat in [r'(?:name|naam|नाम)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,40})',
                r's[/\\]o\s+([A-Za-z][A-Za-z\s\.]{2,40})']:
        m = re.search(pat, full, re.IGNORECASE)
        if m:
            candidate = re.sub(r'[^A-Za-z\s\.]', '', m.group(1)).strip()
            if len(candidate.split()) >= 1 and len(candidate) >= 4:
                fields["Name"] = candidate.title()
                break

    dob_m = re.search(r'(?:dob|date\s*of\s*birth|जन्म)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', full, re.IGNORECASE)
    if dob_m:
        fields["Date of Birth"] = dob_m.group(1)
    else:
        dob_m2 = re.search(r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b', full)
        if dob_m2:
            fields["Date of Birth"] = dob_m2.group(1)

    exp_m = re.search(r'(?:valid\s*till|validity|expiry|exp\s*date|valid\s*upto)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', full, re.IGNORECASE)
    if exp_m:
        fields["Valid Till"] = exp_m.group(1)

    cov_m = re.search(r'(?:cov|class\s*of\s*vehicle|vehicle\s*class|authorisation)\s*[:\-]?\s*([A-Z0-9,/\s]{2,30})', full, re.IGNORECASE)
    if cov_m:
        fields["Vehicle Class"] = cov_m.group(1).strip()[:50]

    bg_m = re.search(r'\b(A|B|AB|O)[\+\-]\b', full)
    if bg_m:
        fields["Blood Group"] = bg_m.group(0)

    addr_m = re.search(r'(?:address|पता)\s*[:\-]?\s*(.+)', full, re.IGNORECASE | re.DOTALL)
    if addr_m:
        addr = addr_m.group(1)
        addr = re.split(r'(?:valid|expiry|blood|cov|vehicle|badge)', addr, flags=re.IGNORECASE)[0]
        addr_clean = re.sub(r'\s+', ' ', addr).strip()[:250]
        if len(addr_clean) > 8:
            fields["Address"] = addr_clean

    rto_m = re.search(r'(?:licensing\s*authority|issued\s*by|rto|issuing\s*authority)\s*[:\-]?\s*([A-Za-z\s,\.]{4,50})', full, re.IGNORECASE)
    if rto_m:
        fields["Issuing Authority"] = rto_m.group(1).strip()

    return fields


def extract_voter_fields(text: str) -> dict:
    fields = {}
    text  = clean_ocr_text(text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full  = text

    epic_m = re.search(r'\b([A-Z]{3}\d{7})\b', full)
    if epic_m:
        fields["EPIC Number"] = epic_m.group(1)

    for pat in [r'(?:elector\s*name|name\s*of\s*elector|नाम|name)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,40})']:
        m = re.search(pat, full, re.IGNORECASE)
        if m:
            candidate = re.sub(r'[^A-Za-z\s\.]', '', m.group(1)).strip()
            if len(candidate) >= 4:
                fields["Name"] = candidate.title()
                break

    rel_m = re.search(r'(?:father|husband|पिता|पति)\s*(?:name|का नाम)?\s*[:\-/]?\s*([A-Za-z][A-Za-z\s\.]{2,40})', full, re.IGNORECASE)
    if rel_m:
        candidate = re.sub(r'[^A-Za-z\s\.]', '', rel_m.group(1)).strip()
        if len(candidate) >= 4:
            fields["Father/Husband Name"] = candidate.title()

    dob_m = re.search(r'(?:date\s*of\s*birth|dob|जन्म\s*तिथि)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', full, re.IGNORECASE)
    if dob_m:
        fields["Date of Birth"] = dob_m.group(1)
    else:
        age_m = re.search(r'\bage\s*[:\-]?\s*(\d{2,3})\b', full, re.IGNORECASE)
        if age_m:
            fields["Age"] = age_m.group(1)

    gender_map = {'male':'Male','female':'Female','पुरुष':'Male','महिला':'Female'}
    for token, label in gender_map.items():
        if re.search(r'\b' + re.escape(token) + r'\b', full, re.IGNORECASE):
            fields["Gender"] = label
            break

    addr_m = re.search(r'(?:address|पता|house|flat)\s*[:\-]?\s*(.+)', full, re.IGNORECASE | re.DOTALL)
    if addr_m:
        addr = addr_m.group(1)
        addr = re.split(r'(?:epic|electoral|election|part\s*no|serial)', addr, flags=re.IGNORECASE)[0]
        addr_clean = re.sub(r'\s+', ' ', addr).strip()[:250]
        if len(addr_clean) > 8:
            fields["Address"] = addr_clean

    const_m = re.search(r'(?:assembly\s*constituency|parliamentary\s*constituency|विधान\s*सभा)\s*[:\-]?\s*([A-Za-z\s]{3,50})', full, re.IGNORECASE)
    if const_m:
        fields["Constituency"] = const_m.group(1).strip()

    part_m = re.search(r'part\s*(?:no\.?|number)\s*[:\-]?\s*(\d+)', full, re.IGNORECASE)
    if part_m:
        fields["Part No"] = part_m.group(1)

    return fields


def render_kv_table(fields: dict):
    if not fields:
        return "<p style='color:#6b7280; font-style:italic;'>No structured fields could be extracted.</p>"
    rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in fields.items())
    return f"""
    <table class="kv-table">
        <thead><tr><th>Field</th><th>Value</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>"""

def confidence_bar(score, label="Confidence"):
    pct = min(max(int(score * 100), 0), 100)
    cls = "conf-high" if pct >= 70 else ("conf-mid" if pct >= 40 else "conf-low")
    return f"""
    <div class="conf-bar-wrap">
        <span style="color:#6b7280; font-size:0.78rem; font-family:'JetBrains Mono',monospace;">{label}</span>
        <div class="conf-bar-bg"><div class="conf-bar-fill {cls}" style="width:{pct}%"></div></div>
        <span style="color:#9ca3af; font-size:0.78rem; font-family:'JetBrains Mono',monospace;">{pct}%</span>
    </div>"""


# ================================================================
# 6. AUTH GATE
# ================================================================
if not st.session_state.user:
    render_auth_ui()
    st.stop()

# ================================================================
# 7. LOGGED-IN USER BAR
# ================================================================
col_user, col_out = st.columns([5, 1])
with col_user:
    st.markdown(
        f"<p style='color:#6b7280; font-size:0.82rem; margin:0;'>"
        f"🔒 Logged in as <b style='color:#a5b4fc'>{st.session_state.user.email}</b></p>",
        unsafe_allow_html=True
    )
with col_out:
    if st.button("Logout", key="btn_logout"):
        auth_logout()
        st.rerun()

# ================================================================
# 8. SAMPLE DATA
# ================================================================
SAMPLE_AADHAAR_TEXT = """भारत सरकार
Government of India
भारतीय विशिष्ट पहचान प्राधिकरण
Unique Identification Authority of India
Enrolment No.: 0000/00381/68118
To
Mohit Somani
S/O SANTOSH KUMAR SOMANI
16-2-139/9/1/303
BHASKARA VIHAR APARTMENT
MALAKPET
AKBERBAGH
Malakpet
Hyderabad Telangana - 500036
9000200510
Date of Birth/DOB: 08/12/1995
Male/ MALE
आपका आधार क्रमांक / Your Aadhaar No.:
XXXX XXXX 4196
VID : 9134 4266 9355 8010
मेरा आधार, मेरी पहचान"""

SAMPLE_PAN_TEXT = """आयकर विभाग    भारत सरकार
INCOME TAX DEPARTMENT    GOVT. OF INDIA
स्थायी लेखा संख्या कार्ड
Permanent Account Number Card
CYMPB5839A
नाम/Name
BORUGULA SURESH
पिता का नाम / Father's Name
BORUGULA MUNASWAMY
जन्म की तारीख / Date of Birth
06/03/1992"""

SAMPLE_AADHAAR_PHOTO_B64 = "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"
SAMPLE_PAN_PHOTO_B64 = "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"

# ================================================================
# 9. MAIN APP HEADER
# ================================================================
st.markdown("""
<div class="ocr-header">
    <h1>📝 OCR Stream</h1>
    <p>Blur-safe · Document-aware · Key-value extraction</p>
</div>
""", unsafe_allow_html=True)

# ================================================================
# 10. MODE TOGGLE
# ================================================================
st.markdown('<div class="section-label">Mode</div>', unsafe_allow_html=True)
col_m1, col_m2 = st.columns(2)
with col_m1:
    if st.button("📄 Normal OCR", use_container_width=True):
        st.session_state.ocr_mode = "Normal"
with col_m2:
    if st.button("🪪 Document Mode", use_container_width=True):
        st.session_state.ocr_mode = "Document"

mode = st.session_state.ocr_mode

if mode == "Document":
    st.markdown("""
    <div class="info-card" style="border-color:#2a3060; margin-top:8px;">
        <div style="display:flex; align-items:center; gap:10px;">
            <span class="badge badge-pan">Document Mode ON</span>
            <span style="color:#9ca3af; font-size:0.85rem;">Aadhaar &amp; PAN key-value extraction enabled</span>
        </div>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="info-card" style="margin-top:8px;">
        <div style="display:flex; align-items:center; gap:10px;">
            <span class="badge badge-normal">Normal Mode</span>
            <span style="color:#9ca3af; font-size:0.85rem;">Plain text extraction for any document</span>
        </div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ================================================================
# 11. LANGUAGE & ENGINE
# ================================================================
col1, col2 = st.columns(2)
languages = {
    "English": "eng", "Spanish": "spa", "French": "fre", "German": "ger",
    "Italian": "ita", "Chinese (Simplified)": "chs", "Chinese (Traditional)": "cht",
}
engine_options = {
    "Engine 1 (Fast)": 1, "Engine 2 (Better)": 2, "Engine 3 (Best - Handwriting)": 3
}
with col1:
    selected_language = st.selectbox("🌍 Language", list(languages.keys()))
    language_code = languages[selected_language]
with col2:
    selected_engine = st.selectbox("⚙ OCR Engine", list(engine_options.keys()))
    engine_code = engine_options[selected_engine]

st.divider()

# ================================================================
# 12. FILE UPLOADER + CAMERA CAPTURE
# ================================================================
MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB

st.markdown('<div class="section-label">Input Source</div>', unsafe_allow_html=True)
input_tab1, input_tab2 = st.tabs(["📂 Upload File", "📷 Camera Capture"])

uploaded_file = None
_fsize        = 0

with input_tab1:
    _uf = st.file_uploader(
        "Upload image or PDF (max 5 MB)",
        type=["png", "jpg", "jpeg", "webp", "pdf"],
        label_visibility="collapsed"
    )
    if _uf is not None:
        _uf.seek(0, 2)
        _sz = _uf.tell()
        _uf.seek(0)
        if _sz > MAX_FILE_BYTES:
            st.error(f"❌ File too large ({round(_sz/1024/1024,2)} MB). Max is **5 MB**.")
        else:
            uploaded_file = _uf
            _fsize        = _sz
            # Clear any stored camera photo so upload takes priority
            st.session_state.camera_bytes = None
            st.session_state.camera_fsize = 0
            st.caption(f"📦 {_uf.name}  ·  {round(_sz/1024,1)} KB")

with input_tab2:
    st.info("📱 Works best on mobile. Point your camera at the document and tap capture.", icon="ℹ️")

    if "camera_open" not in st.session_state:
        st.session_state.camera_open = False

    col_cam1, col_cam2 = st.columns(2)
    with col_cam1:
        if st.button("📷 Open Camera", use_container_width=True, key="btn_open_cam"):
            st.session_state.camera_open = True
    with col_cam2:
        if st.button("✖ Close Camera", use_container_width=True, key="btn_close_cam"):
            st.session_state.camera_open = False
            st.session_state.camera_bytes = None
            st.session_state.camera_fsize = 0

    camera_image = None
    if st.session_state.camera_open:
        camera_image = st.camera_input("Take a photo of your document")

    # ── KEY FIX: persist camera bytes into session_state immediately ──
    # st.camera_input returns None on every rerun EXCEPT the one where
    # the user just snapped the photo. We must save bytes right then.
    if camera_image is not None:
        camera_image.seek(0, 2)
        _csz = camera_image.tell()
        camera_image.seek(0)
        if _csz > MAX_FILE_BYTES:
            st.error(f"❌ Camera capture too large ({round(_csz/1024/1024,2)} MB).")
            st.session_state.camera_bytes = None
            st.session_state.camera_fsize = 0
        else:
            # Save raw bytes — survives all subsequent reruns
            st.session_state.camera_bytes = camera_image.read()
            st.session_state.camera_fsize = _csz
            st.session_state.camera_open  = False  # auto-close camera

    # ── Restore camera file from session_state for upload/extract ──
    if st.session_state.camera_bytes:
        cam_buf = io.BytesIO(st.session_state.camera_bytes)
        cam_buf.name = "camera_capture.jpg"
        cam_buf.type = "image/jpeg"
        cam_buf.seek(0)

        # Only use camera file if no file was uploaded in tab1
        if uploaded_file is None:
            uploaded_file = cam_buf
            _fsize        = st.session_state.camera_fsize

        # Show preview + clear button
        preview_buf = io.BytesIO(st.session_state.camera_bytes)
        st.image(preview_buf, caption="📷 Captured photo (ready to extract)", use_container_width=True)
        if st.button("🗑 Clear Camera Photo", key="btn_clear_cam"):
            st.session_state.camera_bytes = None
            st.session_state.camera_fsize = 0
            st.rerun()
        st.caption(f"📷 camera_capture.jpg  ·  {round(st.session_state.camera_fsize/1024, 1)} KB")

# ================================================================
# 13. SAMPLE BUTTONS (Document Mode only)
# ================================================================
if mode == "Document":
    st.markdown('<div class="section-label">Or try with a real card sample</div>', unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    with sc1:
        if st.button("🪪 Try Sample Aadhaar", use_container_width=True, key="btn_sample_aadhar"):
            st.session_state["sample_text"] = SAMPLE_AADHAAR_TEXT
            st.session_state["sample_type"] = "aadhaar"
            st.session_state["sample_photo_aadhaar"] = SAMPLE_AADHAAR_PHOTO_B64
            st.rerun()
    with sc2:
        if st.button("💳 Try Sample PAN", use_container_width=True, key="btn_sample_pan"):
            st.session_state["sample_text"] = SAMPLE_PAN_TEXT
            st.session_state["sample_type"] = "pan"
            st.session_state["sample_photo_pan"] = SAMPLE_PAN_PHOTO_B64
            st.rerun()

# ================================================================
# 14. RENDER SAMPLE RESULT
# ================================================================
if mode == "Document" and st.session_state.get("sample_text"):
    _stext  = st.session_state["sample_text"]
    _stype  = st.session_state.get("sample_type", "unknown")
    _dlabel = {"aadhaar": "Aadhaar Card", "pan": "PAN Card", "unknown": "Unknown"}[_stype]
    _bcls   = {"aadhaar": "badge-aadhaar", "pan": "badge-pan", "unknown": "badge-unknown"}[_stype]

    st.divider()
    st.markdown(f"""
    <div class="info-card" style="border-color:#1c3a2a;">
        <div style="display:flex; align-items:center; gap:10px;">
            <span class="badge {_bcls}">Sample — {_dlabel}</span>
            <span style="color:#6b7280; font-size:0.8rem; font-family:'JetBrains Mono',monospace;">
                Pre-loaded from real card • Mohit Somani / Borugula Suresh
            </span>
        </div>
    </div>""", unsafe_allow_html=True)

    _fields = extract_aadhaar_fields(_stext) if _stype == "aadhaar" else extract_pan_fields(_stext)
    _holder_name = _fields.get("Name", "")
    _photo_b64   = st.session_state.get("sample_photo_" + _stype)

    st.markdown(photo_html(_photo_b64, _holder_name, _stype), unsafe_allow_html=True)
    if _photo_b64:
        st.download_button("⬇ Download Sample Photo",
            data=base64.b64decode(_photo_b64),
            file_name=f"sample_{_stype}_photo.jpg", mime="image/jpeg", key="sp_photo_dl")

    if _fields:
        st.markdown('<div class="section-label">Extracted Fields</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-card">{render_kv_table(_fields)}</div>', unsafe_allow_html=True)
        _exp  = {"aadhaar": 7, "pan": 4}.get(_stype, 4)
        _conf = min(len(_fields) / _exp, 1.0)
        st.markdown(confidence_bar(_conf, "Extraction Confidence"), unsafe_allow_html=True)

        saved, save_err = save_extraction(_stype, _fields, _stext,
                                          file_name='sample_' + _stype,
                                          file_size_bytes=len(_stext.encode()))
        if saved:
            st.success("✅ Saved to your account.")
        else:
            st.warning(f"⚠️ Could not save: {save_err}")

        _json = json.dumps(_fields, indent=2, ensure_ascii=False)
        _csv  = "\n".join(f'"{k}","{v}"' for k, v in _fields.items())
        _cd1, _cd2 = st.columns(2)
        with _cd1:
            st.download_button("⬇ Download JSON", data=_json,
                file_name=f"sample_{_stype}.json", mime="application/json", key="s_json")
        with _cd2:
            st.download_button("⬇ Download CSV", data=_csv,
                file_name=f"sample_{_stype}.csv", mime="text/csv", key="s_csv")
    else:
        st.warning("⚠ No fields could be extracted from sample text.")

    with st.expander("📄 Raw Sample Text"):
        st.code(_stext, language="text")

    if st.button("✖ Clear Sample", key="clear_sample"):
        st.session_state.pop("sample_text", None)
        st.session_state.pop("sample_type", None)
        st.rerun()

    st.divider()

# ================================================================
# 15. LIVE OCR  — fully bytes-based, no file pointer bugs
# ================================================================
if uploaded_file and st.button("🚀 Extract Text", use_container_width=True):

    # ── Step 1: Read ALL bytes from the file/BytesIO right now ──
    # Do this ONCE, immediately. Everything else works from `raw_bytes`.
    try:
        uploaded_file.seek(0)
        raw_bytes = uploaded_file.read()
    except Exception as e:
        st.error(f"❌ Could not read file: {e}")
        st.stop()

    if not raw_bytes:
        st.error("❌ File is empty. Please retake the photo or re-upload.")
        st.stop()

    file_type = get_file_type(uploaded_file)
    file_name = getattr(uploaded_file, "name", "camera_capture.jpg")

    # ── Step 2: Show preview ──
    if file_type.startswith("image"):
        st.image(io.BytesIO(raw_bytes), use_container_width=True,
                 caption=f"📄 {file_name}  ·  {round(len(raw_bytes)/1024, 1)} KB (original)")

    # ── Step 3: Blur check ──
    if file_type.startswith("image"):
        blur_file = io.BytesIO(raw_bytes)
        blur_score = detect_blur(blur_file)

        if blur_score < 60:
            msg = f"Image too blurry (Sharpness: {round(blur_score, 2)})"
            log_failure("Blur Check", msg)
            st.error(f"⚠ {msg}. Please retake with better lighting.")
            st.stop()
        elif blur_score < 120:
            st.warning(f"Image slightly soft (Sharpness: {round(blur_score, 2)}). Will enhance.")
        else:
            st.success(f"✅ Image sharp (Sharpness: {round(blur_score, 2)}).")

    # ── Step 4: Face photo extraction (Document Mode) ──
    if file_type.startswith("image") and mode == "Document":
        with st.spinner("📸 Detecting photo..."):
            photo_b64 = extract_face_photo(io.BytesIO(raw_bytes))
        if photo_b64:
            st.session_state["doc_photo"] = photo_b64
            st.toast("✅ Photo extracted from document", icon="📸")
        else:
            st.session_state.pop("doc_photo", None)
    elif not file_type.startswith("image"):
        st.session_state.pop("doc_photo", None)

    # ── Step 5: Run OCR — pass raw bytes directly ──
    with st.spinner("🗜️ Compressing & extracting text..."):
        result = perform_ocr(raw_bytes, language_code, engine_code)

    # Clear stored camera photo after extraction
    st.session_state.camera_bytes = None
    st.session_state.camera_fsize = 0

    st.divider()

    if "error" in result:
        st.error(f"❌ {result['error']}")

    elif result.get("ParsedResults"):
        processing_time     = result.get("ProcessingTimeInMilliseconds", 0)
        processing_time_sec = round(float(processing_time) / 1000, 3)
        parsed_results      = result["ParsedResults"]

        page_errors = []
        for i, pr in enumerate(parsed_results):
            ec = pr.get("FileParseExitCode", 1)
            em = pr.get("ErrorMessage", "")
            ed = pr.get("ErrorDetails", "")
            if ec not in (1, 0) or em:
                page_errors.append(f"Page {i+1}: ExitCode={ec} — {em} {ed}".strip())
                log_failure(f"OCR Page {i+1}", f"ExitCode={ec}: {em} {ed}".strip())

        # ── Normal Mode ───────────────────────────────────────────
        if mode == "Normal":
            st.markdown(f"""
            <div class="info-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="badge badge-normal">Normal OCR</span>
                    <span style="color:#6b7280; font-size:0.78rem; font-family:'JetBrains Mono',monospace;">
                        ⏱ {processing_time_sec}s · {len(parsed_results)} page(s)
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)

            searchable_pdf = result.get("SearchablePDFURL")
            if searchable_pdf:
                st.markdown(f"📥 [Download Searchable PDF]({searchable_pdf})")

            if len(parsed_results) > 1:
                tabs = st.tabs([f"Page {i+1}" for i in range(len(parsed_results))])
                for i, tab in enumerate(tabs):
                    with tab:
                        text   = parsed_results[i].get("ParsedText", "").strip()
                        edited = st.text_area("Editable Text", value=text or "No text found.",
                                              height=300, key=f"text_page_{i}")
                        st.download_button("⬇ Download Page", data=edited,
                            file_name=f"ocr_page_{i+1}.txt", mime="text/plain")
            else:
                text   = parsed_results[0].get("ParsedText", "").strip()
                edited = st.text_area("Editable Text", value=text or "No text found.", height=300)
                st.download_button("⬇ Download Text", data=edited,
                    file_name="ocr_text.txt", mime="text/plain")

        # ── Document Mode ─────────────────────────────────────────
        else:
            combined_text = "\n".join(pr.get("ParsedText", "") for pr in parsed_results)
            doc_type  = detect_doc_type(combined_text)
            doc_label = {"aadhaar": "Aadhaar Card", "pan": "PAN Card",
                         "dl": "Driving Licence", "voter": "Voter ID",
                         "unknown": "Unknown Document"}[doc_type]
            badge_cls = {"aadhaar": "badge-aadhaar", "pan": "badge-pan",
                         "dl": "badge-dl", "voter": "badge-voter",
                         "unknown": "badge-unknown"}[doc_type]

            st.markdown(f"""
            <div class="info-card">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span class="badge {badge_cls}">{doc_label}</span>
                        <span style="color:#9ca3af; font-size:0.82rem;">Document Mode</span>
                    </div>
                    <span style="color:#6b7280; font-size:0.78rem; font-family:'JetBrains Mono',monospace;">
                        ⏱ {processing_time_sec}s · {len(parsed_results)} page(s)
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)

            if doc_type == "unknown":
                log_failure("Document Detection",
                            f"Could not identify document type (length={len(combined_text)})")
                st.warning("⚠️ Could not detect document type. Check failure log below.")

            if doc_type == "aadhaar":
                fields = extract_aadhaar_fields(combined_text)
            elif doc_type == "pan":
                fields = extract_pan_fields(combined_text)
            elif doc_type == "dl":
                fields = extract_dl_fields(combined_text)
            elif doc_type == "voter":
                fields = extract_voter_fields(combined_text)
            else:
                fields = {}

            photo_b64   = st.session_state.get("doc_photo")
            holder_name = fields.get("Name", "")
            st.markdown(photo_html(photo_b64, holder_name, doc_type), unsafe_allow_html=True)
            if photo_b64:
                st.download_button("⬇ Download Photo",
                    data=base64.b64decode(photo_b64),
                    file_name=f"{doc_type}_photo_{holder_name.replace(' ', '_') or 'person'}.jpg",
                    mime="image/jpeg", key="photo_dl")

            if fields:
                st.markdown('<div class="section-label">Extracted Fields</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-card">{render_kv_table(fields)}</div>',
                            unsafe_allow_html=True)

                expected = {"aadhaar": 5, "pan": 4, "dl": 5, "voter": 5, "unknown": 1}.get(doc_type, 3)
                conf     = min(len(fields) / expected, 1.0)
                if conf < 0.6:
                    log_failure("Field Extraction",
                        f"Low confidence ({int(conf*100)}%): {len(fields)} of ~{expected} fields found")
                st.markdown(confidence_bar(conf, "Extraction Confidence"), unsafe_allow_html=True)

                saved, save_err = save_extraction(
                    doc_type, fields, combined_text,
                    file_name=file_name,
                    file_size_bytes=len(raw_bytes))
                if saved:
                    st.success("✅ Extraction saved to your account.")
                else:
                    st.warning(f"⚠️ Could not save: {save_err}")

                json_str = json.dumps(fields, indent=2, ensure_ascii=False)
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.download_button("⬇ Download JSON", data=json_str,
                        file_name=f"{doc_type}_fields.json", mime="application/json")
                with col_d2:
                    csv_str = "\n".join(f"{k},{v}" for k, v in fields.items())
                    st.download_button("⬇ Download CSV", data=csv_str,
                        file_name=f"{doc_type}_fields.csv", mime="text/csv")
            else:
                if doc_type != "unknown":
                    log_failure("Field Extraction", f"No fields extracted for {doc_type}.")
                st.warning("No structured fields extracted. Showing raw OCR text.")

            with st.expander("📄 Raw OCR Text"):
                for i, pr in enumerate(parsed_results):
                    raw = pr.get("ParsedText", "").strip()
                    st.text_area(
                        f"Page {i+1}" if len(parsed_results) > 1 else "Raw Text",
                        value=raw or "No text found.", height=200, key=f"doc_raw_{i}")
                    st.download_button(
                        f"⬇ Raw Text (Page {i+1})" if len(parsed_results) > 1 else "⬇ Raw Text",
                        data=raw, file_name=f"ocr_raw_p{i+1}.txt", mime="text/plain",
                        key=f"dl_raw_{i}")

        if page_errors:
            for err in page_errors:
                st.error(f"🔴 {err}")
    else:
        log_failure("OCR Result", "API returned no ParsedResults")
        st.error("❌ No text could be extracted from this file.")

# ================================================================
# 16. SAVED EXTRACTIONS HISTORY
# ================================================================
with st.expander("🗂 My Saved Extractions", expanded=False):
    records = load_extractions()
    if not records:
        st.markdown("<p style='color:#6b7280;'>No saved extractions yet.</p>", unsafe_allow_html=True)
    else:
        st.caption(f"{len(records)} record(s) found")
        for r in records:
            ts     = r.get("created_at", "")[:16].replace("T", " ")
            dtype  = r.get("doc_type", "other")
            dlabel = {"aadhaar": "Aadhaar", "pan": "PAN", "dl": "Driving Licence",
                      "voter": "Voter ID", "other": "Other"}.get(dtype, dtype.title())
            name   = r.get("holder_name") or "—"
            fname  = r.get("file_name") or "sample"
            fsize  = r.get("file_size_kb") or ""
            rid    = r.get("id", "x")

            if dtype == "aadhaar":
                keys = [("Name",           "holder_name"),
                        ("Aadhaar Number", "aadhaar_number"),
                        ("Date of Birth",  "dob"),
                        ("Gender",         "gender"),
                        ("Address",        "address"),
                        ("Pincode",        "pincode"),
                        ("State",          "state"),
                        ("VID",            "vid")]
            elif dtype == "pan":
                keys = [("Name",           "holder_name"),
                        ("PAN Number",     "pan_number"),
                        ("Father's Name", "father_name"),
                        ("Date of Birth",  "dob"),
                        ("Account Type",   "account_type"),
                        ("Issued By",      "issued_by")]
            elif dtype == "dl":
                keys = [("Name",              "holder_name"),
                        ("DL Number",         "dl_number"),
                        ("Date of Birth",     "dob"),
                        ("Valid Till",        "valid_till"),
                        ("Vehicle Class",     "vehicle_class"),
                        ("Blood Group",       "blood_group"),
                        ("Issuing Authority", "issuing_authority")]
            elif dtype == "voter":
                keys = [("Name",                "holder_name"),
                        ("EPIC Number",         "epic_number"),
                        ("Father/Husband Name", "father_husband_name"),
                        ("Date of Birth",       "dob"),
                        ("Gender",              "gender"),
                        ("Constituency",        "constituency"),
                        ("Part No",             "part_no")]
            else:
                keys = [("Raw Text", "raw_text")]

            display = {label: r[col] for label, col in keys if r.get(col)}

            with st.expander(f"📄 {dlabel}  ·  {name}  ·  {ts}"):
                st.caption(f"📁 {fname}{'  ·  ' + str(fsize) + ' KB' if fsize else ''}  ·  {ts}")
                st.markdown(f'<div class="info-card">{render_kv_table(display)}</div>',
                            unsafe_allow_html=True)
                st.download_button("⬇ Download JSON",
                    data=json.dumps(display, indent=2, ensure_ascii=False),
                    file_name=f"{dtype}_{rid[:8]}.json",
                    mime="application/json", key=f"hist_dl_{rid}")

# ================================================================
# 17. FAILURE LOG
# ================================================================
st.divider()
with st.expander(f"🔴 Failure Log ({len(st.session_state.failure_log)} entries)", expanded=False):
    if st.session_state.failure_log:
        col_l, col_r = st.columns([5, 1])
        with col_r:
            if st.button("🗑 Clear Log"):
                st.session_state.failure_log = []
                st.rerun()

        entries_html = ""
        for entry in reversed(st.session_state.failure_log):
            entries_html += f"""
            <div class="fail-entry">
                <span class="fail-ts">[{entry['ts']}]</span>
                <span style="color:#6366f1; flex-shrink:0;">{entry['ctx']}</span>
                <span class="fail-msg">{entry['msg']}</span>
            </div>"""
        st.markdown(f"""
        <div class="fail-log">
            <div class="fail-log-title">⚠ System Failure Log</div>
            {entries_html}
        </div>""", unsafe_allow_html=True)

        log_text = "\n".join(f"[{e['ts']}] [{e['ctx']}] {e['msg']}" for e in st.session_state.failure_log)
        st.download_button("⬇ Download Log", data=log_text,
            file_name="ocr_failure_log.txt", mime="text/plain")
    else:
        st.markdown(
            "<p style='color:#4b5563; font-size:0.85rem; font-family:monospace;'>No failures recorded.</p>",
            unsafe_allow_html=True)
