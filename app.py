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
try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

# ================================================================
# 1. PAGE CONFIG
# ================================================================
st.set_page_config(page_title="OCR Stream", page_icon="📝", layout="wide")

# ================================================================
# 2. CUSTOM CSS — Light Theme matching preview
# ================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
        color: #1a1a2e;
    }
    .stApp {
        background: #f5f6fa !important;
        color: #1a1a2e;
    }
    h1,h2,h3 { font-family:'DM Sans',sans-serif !important; font-weight:700; color:#1a1a2e; }

    /* ── Header card ── */
    .ocr-header {
        background: #ffffff;
        border: 1px solid #e8eaf0;
        border-radius: 16px;
        padding: 22px 28px;
        margin-bottom: 18px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .ocr-header h1 { font-size:1.5rem; margin:0; color:#1a1a2e; letter-spacing:-0.3px; }
    .ocr-header p  { margin:4px 0 0; color:#374151; font-size:0.82rem; font-family:'DM Mono',monospace; line-height:1.5; }

    /* ── Panel cards ── */
    .panel-card {
        background: #ffffff;
        border: 1px solid #e8eaf0;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
        height: 100%;
    }
    .info-card {
        background: #ffffff;
        border: 1px solid #e8eaf0;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .info-card.accent { border-left: 3px solid #6366f1; }
    .info-card.green  { border-left: 3px solid #10b981; }
    .info-card.blue   { border-left: 3px solid #3b82f6; }

    /* ── Section label ── */
    .section-label {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #4b5563;
        margin: 14px 0 6px;
    }

    /* ── Badges ── */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .badge-aadhaar { background:#ecfdf5; color:#059669; border:1px solid #a7f3d0; }
    .badge-pan     { background:#eff6ff; color:#4f46e5; border:1px solid #bfdbfe; }
    .badge-unknown { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
    .badge-normal  { background:#eff6ff; color:#3b82f6; border:1px solid #bfdbfe; }
    .badge-dl      { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
    .badge-voter   { background:#faf5ff; color:#7c3aed; border:1px solid #ddd6fe; }

    /* ── KV Table ── */
    .kv-table { width:100%; border-collapse:collapse; font-family:'DM Mono',monospace; font-size:0.8rem; }
    .kv-table th {
        text-align:left; padding:8px 12px;
        background:#f5f6fa; color:#6366f1;
        font-weight:600; font-size:0.7rem; letter-spacing:1px; text-transform:uppercase;
        border-bottom:1px solid #e8eaf0;
    }
    .kv-table td { padding:8px 12px; border-bottom:1px solid #f0f1f5; color:#374151; vertical-align:top; }
    .kv-table td:first-child { color:#6b7280; width:38%; font-weight:500; }
    .kv-table tr:hover td { background:#fafbff; }

    /* ── Photo card ── */
    .photo-card {
        background:#f9fafb; border:1px solid #e8eaf0; border-radius:10px;
        padding:12px; display:flex; align-items:center; gap:12px; margin-bottom:12px;
    }
    .photo-frame {
        width:48px; height:58px; border-radius:8px; border:1.5px solid #e8eaf0;
        background:#e8eaf0; display:flex; align-items:center; justify-content:center;
        font-size:1.3rem; flex-shrink:0; overflow:hidden;
    }
    .photo-frame img { width:100%; height:100%; object-fit:cover; }
    .photo-placeholder {
        width:48px; height:58px; border-radius:8px; border:2px dashed #d1d5db;
        background:#f9fafb; display:flex; flex-direction:column; align-items:center;
        justify-content:center; font-size:0.6rem; color:#9ca3af;
        font-family:'DM Mono',monospace; text-align:center; flex-shrink:0;
    }
    .photo-meta { flex:1; }
    .photo-label { font-size:0.62rem; font-weight:700; letter-spacing:1px; text-transform:uppercase; color:#9ca3af; margin-bottom:3px; }
    .photo-name  { font-size:0.95rem; font-weight:700; color:#1a1a2e; margin-bottom:2px; }
    .photo-sub   { font-size:0.72rem; color:#4b5563; font-family:'DM Mono',monospace; line-height:1.5; }

    /* ── Confidence bar ── */
    .conf-wrap { display:flex; align-items:center; gap:10px; margin:10px 0; }
    .conf-label { font-size:0.72rem; font-family:'DM Mono',monospace; color:#4b5563; min-width:72px; }
    .conf-bg { flex:1; background:#e8eaf0; border-radius:4px; height:6px; overflow:hidden; }
    .conf-fill { height:100%; border-radius:4px; }
    .conf-high { background:#10b981; }
    .conf-mid  { background:#f59e0b; }
    .conf-low  { background:#ef4444; }
    .conf-pct  { font-size:0.72rem; font-family:'DM Mono',monospace; color:#374151; min-width:32px; text-align:right; }

    /* ── Empty state ── */
    .empty-state {
        display:flex; flex-direction:column; align-items:center; justify-content:center;
        text-align:center; padding:48px 20px; color:#9ca3af;
    }
    .empty-icon { font-size:2.5rem; opacity:0.35; margin-bottom:12px; }
    .empty-title { font-weight:600; font-size:0.9rem; margin-bottom:4px; }
    .empty-sub { font-size:0.76rem; font-family:'DM Mono',monospace; }

    /* ── Failure log ── */
    .fail-log { background:#fff9f9; border:1px solid #fecaca; border-radius:12px; padding:16px; margin-top:12px; }
    .fail-log-title { color:#dc2626; font-weight:700; font-size:0.78rem; letter-spacing:1px; text-transform:uppercase; margin-bottom:10px; }
    .fail-entry { font-family:'DM Mono',monospace; font-size:0.76rem; color:#6b7280; padding:5px 0; border-bottom:1px solid #fee2e2; display:flex; gap:10px; flex-wrap:wrap; }
    .fail-entry:last-child { border-bottom:none; }
    .fail-ts  { color:#9ca3af; flex-shrink:0; }
    .fail-msg { color:#dc2626; }

    /* ── Streamlit overrides ── */
    .stButton > button {
        background: linear-gradient(135deg,#4f46e5,#6366f1) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; padding: 10px 20px !important;
        font-family: 'DM Sans',sans-serif !important; font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(99,102,241,0.3) !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
        box-shadow: 0 4px 14px rgba(99,102,241,0.4) !important;
        transform: translateY(-1px) !important;
    }

    /* Secondary button style via wrapper */
    .sec-btn > button {
        background: #ffffff !important; color: #4f46e5 !important;
        border: 1.5px solid #c7d2fe !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
    }
    .sec-btn > button:hover { background: #eef2ff !important; }

    .stDownloadButton > button {
        background: #ffffff !important; color: #4f46e5 !important;
        border: 1px solid #c7d2fe !important; border-radius: 8px !important;
        font-family: 'DM Sans',sans-serif !important; font-weight: 600 !important;
        box-shadow: none !important;
    }
    .stDownloadButton > button:hover { background: #eef2ff !important; border-color: #a5b4fc !important; }

    .stSelectbox > div > div {
        background: #ffffff !important; border: 1px solid #e8eaf0 !important;
        border-radius: 8px !important; color: #374151 !important;
        font-family: 'DM Sans',sans-serif !important;
    }
    [data-testid="stTextInputRootElement"] input {
        background: #eef2f7 !important;
        color: #0f172a !important;
        border: 1px solid #bcc7d8 !important;
        border-radius: 10px !important;
    }
    [data-testid="stTextInputRootElement"] input::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }
    [data-testid="stTextInputRootElement"] input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 inset !important;
    }
    [data-testid="stWidgetLabel"] p {
        color: #111827 !important;
        font-weight: 600 !important;
    }
    .stTextArea textarea {
        background: #eef2f7 !important; color: #111827 !important;
        border: 1px solid #bcc7d8 !important; border-radius: 8px !important;
        font-family: 'DM Mono',monospace !important; font-size: 0.8rem !important;
    }

    [data-testid="stFileUploader"] {
        background: #fafbff !important; border: 2px dashed #c7d2fe !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploader"]:hover { border-color: #6366f1 !important; }

    .stTabs [data-baseweb="tab-list"] {
        background: #e9edf4 !important; border-radius: 10px !important;
        padding: 4px !important; gap: 4px !important; border: 1px solid #cdd6e3 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important; color: #374151 !important;
        border-radius: 7px !important; font-family: 'DM Sans',sans-serif !important;
        font-weight: 600 !important; padding: 7px 14px !important; border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important; color: #111827 !important;
        font-weight: 700 !important; box-shadow: 0 1px 4px rgba(0,0,0,0.12) !important;
    }

    [data-testid="stExpander"] {
        background: #ffffff !important; border: 1px solid #e8eaf0 !important;
        border-radius: 10px !important; box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stExpander"] summary {
        color: #374151 !important; font-weight: 600 !important;
        font-family: 'DM Sans',sans-serif !important; padding: 12px 16px !important;
    }

    [data-testid="stAlert"]   { border-radius: 10px !important; font-family:'DM Sans',sans-serif !important; }
    [data-testid="stInfo"]    { background:#eff6ff !important; border-color:#bfdbfe !important; color:#1e40af !important; }
    [data-testid="stWarning"] { background:#fffbeb !important; border-color:#fcd34d !important; }
    [data-testid="stSuccess"] { background:#ecfdf5 !important; border-color:#a7f3d0 !important; }

    [data-testid="stCameraInput"] { border:2px dashed #c7d2fe !important; border-radius:12px !important; background:#fafbff !important; }

    hr { border-color:#e8eaf0 !important; margin:16px 0 !important; }
    [data-testid="stCaptionContainer"] p { color:#4b5563 !important; font-family:'DM Mono',monospace !important; font-size:0.76rem !important; }
    .stSpinner > div { border-top-color:#6366f1 !important; }

    /* Vertical divider between split panels */
    .vdivider {
        width: 1px; background: #e8eaf0; margin: 0 4px; border-radius: 2px;
        min-height: 400px;
    }

    @media (max-width:768px) {
        .photo-card { flex-direction:column; align-items:center; text-align:center; }
        .kv-table td, .kv-table th { padding:6px 8px; font-size:0.74rem; }
    }
</style>
""", unsafe_allow_html=True)

# ================================================================
# 3. CONFIG & SUPABASE INIT
# ================================================================
OCR_API_KEY = os.getenv("OCR_API_KEY", "")
OCR_URL = "https://api.ocr.space/parse/image"

def _get_secret(key: str, default: str = "") -> str:
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
for key, default in [
    ("user", None), ("access_token", None), ("failure_log", []),
    ("ocr_mode", "Normal"), ("camera_bytes", None), ("camera_fsize", 0),
    ("camera_open", False),
    ("camera_widget_nonce", 0),
    ("last_result", None),
    ("last_login", None),        
    ("user_created_at", None),   
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ================================================================
# 5. HELPER FUNCTIONS
# ================================================================

def log_failure(context: str, message: str):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.failure_log.append({"ts": ts, "ctx": context, "msg": message})


# ── Auth ─────────────────────────────────────────────────────────
def auth_login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = res.user
        st.session_state.access_token = res.session.access_token
        supabase.postgrest.auth(res.session.access_token)

        # ── Update last_login in public.users (upsert, no duplicates) ──
        try:
            supabase.rpc("upsert_user_login", {
                "p_user_id": res.user.id,
                "p_email": res.user.email
            }).execute()
            # Fetch last_login to show in UI
            user_row = (supabase.table("users")
                        .select("last_login, created_at")
                        .eq("id", res.user.id)
                        .single().execute())
            st.session_state.last_login = user_row.data.get("last_login") if user_row.data else None
            st.session_state.user_created_at = user_row.data.get("created_at") if user_row.data else None
        except Exception:
            st.session_state.last_login = None
            st.session_state.user_created_at = None

        return True, None
    except Exception as e:
        return False, str(e)

def auth_signup(email, password):
    try:
        supabase.auth.sign_up({"email": email, "password": password,
            "options": {"email_redirect_to": "https://ocr-stream-nhjd5pbhtxcm99hfgncbre.streamlit.app"}})
        return True, None
    except Exception as e:
        return False, str(e)

def auth_logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.access_token = None


# ── Supabase save/load ────────────────────────────────────────────
def save_extraction(doc_type, fields, raw_text="", file_name="", file_size_bytes=0):
    if not st.session_state.user:
        return False, "Not logged in"
    try:
        supabase.postgrest.auth(st.session_state.access_token)
        size_kb = round(file_size_bytes / 1024, 1) if file_size_bytes else 0
        row = {
            "user_id":           st.session_state.user.id,
            "doc_type":          doc_type if doc_type in ("aadhaar","pan","dl","voter") else "other",
            "file_name":         file_name, "file_size_kb": size_kb,
            "holder_name":       fields.get("Name",""),
            "dob":               fields.get("Date of Birth",""),
            "aadhaar_number":    fields.get("Aadhaar Number",""),
            "gender":            fields.get("Gender",""),
            "address":           fields.get("Address",""),
            "pincode":           fields.get("Pincode",""),
            "state":             fields.get("State",""),
            "vid":               fields.get("VID",""),
            "pan_number":        fields.get("PAN Number",""),
            "father_name":       fields.get("Father's Name",""),
            "account_type":      fields.get("Account Type",""),
            "issued_by":         fields.get("Issued By",""),
            "dl_number":         fields.get("DL Number",""),
            "valid_till":        fields.get("Valid Till",""),
            "vehicle_class":     fields.get("Vehicle Class",""),
            "blood_group":       fields.get("Blood Group",""),
            "issuing_authority": fields.get("Issuing Authority",""),
            "epic_number":           fields.get("EPIC Number",""),
            "father_husband_name":   fields.get("Father/Husband Name",""),
            "constituency":          fields.get("Constituency",""),
            "part_no":               fields.get("Part No",""),
            "raw_text":              raw_text[:4000],
        }
        supabase.table("extractions").insert(row).execute()
        return True, None
    except Exception as e:
        err = str(e)
        if "duplicate" in err.lower() or "unique" in err.lower() or "23505" in err:
            return False, "duplicate"
        return False, err

def load_extractions():
    if not st.session_state.user:
        return []
    try:
        supabase.postgrest.auth(st.session_state.access_token)
        res = (supabase.table("extractions").select("*")
               .eq("user_id", st.session_state.user.id)
               .order("created_at", desc=True).execute())
        return res.data or []
    except Exception as e:
        log_failure("Supabase Fetch", str(e))
        return []


# ── Image helpers ─────────────────────────────────────────────────
def get_file_type(f) -> str:
    try:
        t = getattr(f, "type", None)
        if t and isinstance(t, str) and t.strip():
            return t.strip()
        name = getattr(f, "name", "") or ""
        if name.lower().endswith(".pdf"):
            return "application/pdf"
        return "image/jpeg"
    except Exception:
        return "image/jpeg"

def detect_blur(file) -> float:
    try:
        file.seek(0)
        image = Image.open(file).convert("L")
        score = cv2.Laplacian(np.array(image), cv2.CV_64F).var()
        file.seek(0)
        return score
    except Exception as e:
        log_failure("Blur Detection", str(e))
        return 999

def compress_image_bytes(raw_bytes: bytes) -> bytes:
    try:
        img = Image.open(io.BytesIO(raw_bytes)).convert("L")
        if img.width > 1200:
            img = img.resize((1200, int(img.height * 1200 / img.width)), Image.LANCZOS)
        img = ImageEnhance.Contrast(img).enhance(1.5)
        img = ImageEnhance.Sharpness(img).enhance(1.4)
        for quality in [75, 60, 45, 30, 20]:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            if len(buf.getvalue()) <= 280*1024 or quality == 20:
                return buf.getvalue()
        return buf.getvalue()
    except Exception as e:
        log_failure("Compress Image", str(e))
        return raw_bytes

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
        ]
        face_cascade = None
        for cp in cascade_paths:
            if os.path.exists(cp):
                face_cascade = cv2.CascadeClassifier(cp)
                break

        face_rect = None
        if face_cascade and not face_cascade.empty():
            faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30,30))
            if len(faces) > 0:
                best, best_score = None, -1
                for (fx, fy, fw, fh) in faces:
                    score = (1 if fx > w*0.4 else 0) + (fw*fh)/(w*h)
                    if score > best_score:
                        best_score, best = score, (fx, fy, fw, fh)
                face_rect = best

        if face_rect:
            fx, fy, fw, fh = face_rect
            px, py = int(fw*0.2), int(fh*0.2)
            face_crop = img_pil.crop((max(0,fx-px), max(0,fy-py), min(w,fx+fw+px), min(h,fy+fh+py)))
        else:
            face_crop = img_pil.crop((int(w*0.6), int(h*0.1), int(w*0.85), int(h*0.7)))
            log_failure("Face Detection", "No face found — using ROI fallback")

        face_crop = face_crop.resize((100, 120), Image.LANCZOS)
        buf = io.BytesIO()
        face_crop.save(buf, format="JPEG", quality=85)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception as e:
        log_failure("Face Extraction", str(e))
        return None


# ── OCR ───────────────────────────────────────────────────────────
def perform_ocr(raw_bytes, language_code, engine_code, is_pdf=False, _retry=True):
    if not OCR_API_KEY:
        return {"error": "Missing OCR_API_KEY"}
    try:
        if is_pdf:
            safe_engine = 2 if engine_code == 3 else engine_code
            send_bytes, filename, mimetype = raw_bytes, "document.pdf", "application/pdf"
        else:
            safe_engine = engine_code
            send_bytes, filename, mimetype = compress_image_bytes(raw_bytes), "image.jpg", "image/jpeg"

        response = requests.post(OCR_URL, data={
            "apikey": OCR_API_KEY, "language": language_code,
            "OCREngine": safe_engine, "isOverlayRequired": False,
            "detectOrientation": True, "scale": True,
        }, files={"file": (filename, send_bytes, mimetype)}, timeout=90)
        response.raise_for_status()
        result = response.json()

        if result.get("IsErroredOnProcessing"):
            err_msgs = result.get("ErrorMessage", ["Unknown OCR error"])
            err_str = "; ".join(err_msgs) if isinstance(err_msgs, list) else str(err_msgs)
            if _retry and "timed out" in err_str.lower():
                return perform_ocr(raw_bytes, language_code, 1, is_pdf, _retry=False)
            log_failure("OCR Processing", err_str)
            return {"error": err_str}
        return result

    except requests.Timeout:
        if _retry:
            return perform_ocr(raw_bytes, language_code, 1, is_pdf, _retry=False)
        msg = "OCR timed out. Try Engine 1 or a smaller file."
        log_failure("OCR Timeout", msg)
        return {"error": msg}
    except Exception as e:
        log_failure("OCR Error", str(e))
        return {"error": str(e)}


# ── Document parsing ──────────────────────────────────────────────
def clean_ocr_text(text):
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u200b-\u200f\ufeff]', '', text)
    text = text.replace('\r\n','\n').replace('\r','\n')
    text = re.sub(r'[ \t]+',' ', text)
    text = re.sub(r'(?<=\d)[Oo](?=\d)','0', text)
    text = re.sub(r'(?<=\d)[Il](?=\d)','1', text)
    return text.strip()

def detect_doc_type(text):
    t = clean_ocr_text(text).lower()
    aadhaar_signals = ["aadhaar","aadhar","uidai","uid","unique identification","enrollment no",
                       "enrolment no","भारत सरकार","आधार","मेरा आधार","government of india"]
    pan_signals     = ["permanent account number","income tax department","income tax","आयकर विभाग","govt. of india"]
    dl_signals      = ["driving licence","driving license","dl no","licence no","transport department",
                       "vehicle class","cov","lmv","mcwg","rto"]
    voter_signals   = ["election commission","voter","electors photo","epic","electoral",
                       "निर्वाचन आयोग","मतदाता","part no","assembly constituency"]

    pan_pat     = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text)
    aadhaar_pat = re.search(r'\b\d{4}[\s\-]\d{4}[\s\-]\d{4}\b|\b\d{12}\b|XXXX\s*XXXX\s*\d{4}', text, re.IGNORECASE)
    dl_pat      = re.search(r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?\d{11}\b|\b[A-Z]{2}\d{13}\b', text)
    epic_pat    = re.search(r'\b[A-Z]{3}\d{7}\b', text)

    scores = {
        "aadhaar": sum(1 for s in aadhaar_signals if s in t) + (5 if aadhaar_pat else 0),
        "pan":     sum(1 for s in pan_signals     if s in t) + (5 if pan_pat     else 0),
        "dl":      sum(1 for s in dl_signals      if s in t) + (5 if dl_pat      else 0),
        "voter":   sum(1 for s in voter_signals   if s in t) + (5 if epic_pat    else 0),
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"

def extract_aadhaar_fields(text):
    fields = {}
    text = clean_ocr_text(text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full = text

    masked_m = re.search(r'\b(XXXX[\s]*XXXX[\s]*\d{4})\b', full, re.IGNORECASE)
    if masked_m:
        fields["Aadhaar Number"] = re.sub(r'\s+',' ', masked_m.group(1).upper()).strip()
    else:
        for pat, fmt in [
            (r'\b(\d{4})\s(\d{4})\s(\d{4})\b', lambda m: f"{m.group(1)} {m.group(2)} {m.group(3)}"),
            (r'\b(\d{4})-(\d{4})-(\d{4})\b',   lambda m: f"{m.group(1)} {m.group(2)} {m.group(3)}"),
            (r'(?<!\d)(\d{12})(?!\d)',           lambda m: f"{m.group(1)[:4]} {m.group(1)[4:8]} {m.group(1)[8:]}"),
        ]:
            m = re.search(pat, full)
            if m:
                fields["Aadhaar Number"] = fmt(m)
                break

    for i, line in enumerate(lines):
        if line.strip().lower() == 'to' and i+1 < len(lines):
            candidate = re.sub(r'[^A-Za-z\s\.]','', lines[i+1]).strip()
            words = candidate.split()
            if 1 <= len(words) <= 5 and all(len(w) >= 2 for w in words):
                fields["Name"] = candidate.title()
            break

    if "Name" not in fields:
        m = re.search(r'(?:name|naam|नाम)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,40})', full, re.IGNORECASE)
        if m:
            candidate = re.sub(r'\s+',' ', m.group(1)).strip().rstrip('.')
            words = candidate.split()
            if len(words) >= 2 or (len(words)==1 and len(words[0])>=5):
                fields["Name"] = candidate.title()

    if "Name" not in fields:
        skip = {'male','female','dob','date','birth','address','government','india',
                'aadhaar','aadhar','uid','enrollment','year','of','और','भारत'}
        for line in lines[1:12]:
            candidate = re.sub(r'[^A-Za-z\s]','', line).strip()
            words = [w for w in candidate.split() if len(w)>=2]
            if 2 <= len(words) <= 5 and not {w.lower() for w in words}.intersection(skip):
                if all(w.isalpha() for w in words):
                    fields["Name"] = candidate.title()
                    break

    for pat in [
        r'(?:dob|date\s+of\s+birth|d\.o\.b|जन्म)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b',
    ]:
        m = re.search(pat, full, re.IGNORECASE)
        if m:
            fields["Date of Birth"] = m.group(1).strip()
            break

    for token, label in [('male','Male'),('female','Female'),('transgender','Transgender'),
                          ('पुरुष','Male (पुरुष)'),('महिला','Female (महिला)')]:
        if re.search(r'\b'+re.escape(token)+r'\b', full, re.IGNORECASE):
            fields["Gender"] = label
            break

    addr_start = re.search(r'(?:s[/\\]o|d[/\\]o|w[/\\]o|c[/\\]o|address|पता)\s*[:\-]?\s*(.+)',
                           full, re.IGNORECASE | re.DOTALL)
    if addr_start:
        addr_raw = addr_start.group(1)
        addr_raw = re.split(r'\b(XXXX|VID\b|\d{4}[\s\-]\d{4}[\s\-]\d{4}|dob\b|male\b|female\b)',
                            addr_raw, flags=re.IGNORECASE)[0]
        addr_clean = re.sub(r'\s+',' ', addr_raw).strip().rstrip(',').strip()
        if len(addr_clean) > 8:
            fields["Address"] = addr_clean[:250]

    for m in re.finditer(r'\b(\d{6})\b', full):
        pin = m.group(1)
        if "Aadhaar Number" in fields and pin in fields["Aadhaar Number"].replace(' ',''):
            continue
        fields["Pincode"] = pin
        break

    state_pat = (r'\b(andhra\s*pradesh|arunachal\s*pradesh|assam|bihar|chhattisgarh|goa|gujarat|haryana|'
                 r'himachal\s*pradesh|jharkhand|karnataka|kerala|madhya\s*pradesh|maharashtra|manipur|'
                 r'meghalaya|mizoram|nagaland|odisha|punjab|rajasthan|sikkim|tamil\s*nadu|telangana|'
                 r'tripura|uttar\s*pradesh|uttarakhand|west\s*bengal|delhi|jammu|ladakh|chandigarh|puducherry)\b')
    sm = re.search(state_pat, full, re.IGNORECASE)
    if sm:
        fields["State"] = sm.group(1).title()

    vid_m = re.search(r'(?:vid|virtual\s*id)\s*[:\-]?\s*(\d[\d\s]{14,17})', full, re.IGNORECASE)
    if vid_m:
        raw_vid = re.sub(r'\s','', vid_m.group(1))
        if len(raw_vid) == 16:
            fields["VID"] = f"{raw_vid[:4]} {raw_vid[4:8]} {raw_vid[8:12]} {raw_vid[12:]}"

    return fields

def extract_pan_fields(text):
    fields = {}
    text = clean_ocr_text(text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full = text

    m = re.search(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b', full)
    if m:
        fields["PAN Number"] = m.group(1)

    for i, line in enumerate(lines):
        if re.search(r'(?:^|[/|])\s*name\s*$', line, re.IGNORECASE):
            if i+1 < len(lines):
                candidate = re.sub(r'[^A-Za-z\s\.]','', lines[i+1]).strip()
                if len(candidate) >= 4:
                    fields["Name"] = candidate.title()
            break

    if "Name" not in fields:
        skip = [r'income\s+tax',r'govt',r'government',r'permanent\s+account',r'india',r'\d',r'विभाग']
        for line in lines:
            clean = re.sub(r'[^A-Za-z\s\.]','', line).strip()
            words = [w for w in clean.split() if len(w)>=2]
            if 1 <= len(words) <= 5 and all(w.isalpha() for w in words):
                if not any(re.search(p, line, re.IGNORECASE) for p in skip) and len(clean)>=4:
                    fields["Name"] = clean.title()
                    break

    for i, line in enumerate(lines):
        if re.search(r"father'?s?\s*name", line, re.IGNORECASE):
            if i+1 < len(lines):
                candidate = re.sub(r'[^A-Za-z\s\.]','', lines[i+1]).strip()
                if len(candidate) >= 4:
                    fields["Father's Name"] = candidate.title()
            break

    if "Father's Name" not in fields:
        m2 = re.search(r"(?:father'?s?\s*(?:name)?|पिता)\s*[:\-/]\s*([A-Za-z][A-Za-z\s\.]{2,50})",
                       full, re.IGNORECASE)
        if m2:
            candidate = re.sub(r'\s+',' ', m2.group(1)).strip().rstrip('.')
            if len(candidate) >= 4:
                fields["Father's Name"] = candidate.title()

    for i, line in enumerate(lines):
        if re.search(r'date\s+of\s+birth|dob|जन्म', line, re.IGNORECASE):
            m3 = re.search(r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', line)
            if m3:
                fields["Date of Birth"] = m3.group(1).strip()
                break
            if i+1 < len(lines):
                m3 = re.search(r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', lines[i+1])
                if m3:
                    fields["Date of Birth"] = m3.group(1).strip()
            break

    if "Date of Birth" not in fields:
        m4 = re.search(r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b', full)
        if m4:
            fields["Date of Birth"] = m4.group(1).strip()

    type_m = re.search(r'\b(individual|company|firm|huf|trust|aop|boi)\b', full, re.IGNORECASE)
    if type_m:
        fields["Account Type"] = type_m.group(1).title()

    if re.search(r'income\s+tax|आयकर', full, re.IGNORECASE):
        fields["Issued By"] = "Income Tax Department, Govt. of India"

    return fields

def extract_dl_fields(text):
    fields = {}
    text = clean_ocr_text(text)
    full = text

    dl_m = re.search(r'\b([A-Z]{2})[\s\-]?(\d{2})[\s\-]?(\d{4})[\s\-]?(\d{7})\b', full)
    if dl_m:
        fields["DL Number"] = f"{dl_m.group(1)}-{dl_m.group(2)}-{dl_m.group(3)}-{dl_m.group(4)}"
    else:
        dl_m2 = re.search(r'\b([A-Z]{2}\d{13})\b', full)
        if dl_m2:
            fields["DL Number"] = dl_m2.group(1)

    for pat in [r'(?:name|naam|नाम)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,40})']:
        m = re.search(pat, full, re.IGNORECASE)
        if m:
            candidate = re.sub(r'[^A-Za-z\s\.]','', m.group(1)).strip()
            if len(candidate) >= 4:
                fields["Name"] = candidate.title()
                break

    dob_m = re.search(r'(?:dob|date\s*of\s*birth)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', full, re.IGNORECASE)
    if dob_m:
        fields["Date of Birth"] = dob_m.group(1)
    else:
        dob_m2 = re.search(r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b', full)
        if dob_m2:
            fields["Date of Birth"] = dob_m2.group(1)

    exp_m = re.search(r'(?:valid\s*till|validity|expiry)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', full, re.IGNORECASE)
    if exp_m:
        fields["Valid Till"] = exp_m.group(1)

    cov_m = re.search(r'(?:cov|class\s*of\s*vehicle|vehicle\s*class)\s*[:\-]?\s*([A-Z0-9,/\s]{2,30})', full, re.IGNORECASE)
    if cov_m:
        fields["Vehicle Class"] = cov_m.group(1).strip()[:50]

    bg_m = re.search(r'\b(A|B|AB|O)[\+\-]\b', full)
    if bg_m:
        fields["Blood Group"] = bg_m.group(0)

    rto_m = re.search(r'(?:licensing\s*authority|issued\s*by|issuing\s*authority)\s*[:\-]?\s*([A-Za-z\s,\.]{4,50})', full, re.IGNORECASE)
    if rto_m:
        fields["Issuing Authority"] = rto_m.group(1).strip()

    return fields

def extract_voter_fields(text):
    fields = {}
    text = clean_ocr_text(text)
    full = text

    epic_m = re.search(r'\b([A-Z]{3}\d{7})\b', full)
    if epic_m:
        fields["EPIC Number"] = epic_m.group(1)

    m = re.search(r'(?:elector\s*name|name\s*of\s*elector|name)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,40})', full, re.IGNORECASE)
    if m:
        candidate = re.sub(r'[^A-Za-z\s\.]','', m.group(1)).strip()
        if len(candidate) >= 4:
            fields["Name"] = candidate.title()

    rel_m = re.search(r'(?:father|husband|पिता|पति)\s*(?:name)?\s*[:\-/]?\s*([A-Za-z][A-Za-z\s\.]{2,40})', full, re.IGNORECASE)
    if rel_m:
        candidate = re.sub(r'[^A-Za-z\s\.]','', rel_m.group(1)).strip()
        if len(candidate) >= 4:
            fields["Father/Husband Name"] = candidate.title()

    dob_m = re.search(r'(?:date\s*of\s*birth|dob)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', full, re.IGNORECASE)
    if dob_m:
        fields["Date of Birth"] = dob_m.group(1)
    else:
        age_m = re.search(r'\bage\s*[:\-]?\s*(\d{2,3})\b', full, re.IGNORECASE)
        if age_m:
            fields["Age"] = age_m.group(1)

    for token, label in [('male','Male'),('female','Female'),('पुरुष','Male'),('महिला','Female')]:
        if re.search(r'\b'+re.escape(token)+r'\b', full, re.IGNORECASE):
            fields["Gender"] = label
            break

    const_m = re.search(r'(?:assembly\s*constituency|parliamentary\s*constituency)\s*[:\-]?\s*([A-Za-z\s]{3,50})', full, re.IGNORECASE)
    if const_m:
        fields["Constituency"] = const_m.group(1).strip()

    part_m = re.search(r'part\s*(?:no\.?|number)\s*[:\-]?\s*(\d+)', full, re.IGNORECASE)
    if part_m:
        fields["Part No"] = part_m.group(1)

    return fields


# ── Render helpers ────────────────────────────────────────────────
def render_kv_table(fields):
    if not fields:
        return "<p style='color:#9ca3af;font-style:italic;font-size:0.82rem;'>No fields extracted.</p>"
    rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in fields.items())
    return f"""<table class="kv-table">
        <thead><tr><th>Field</th><th>Value</th></tr></thead>
        <tbody>{rows}</tbody></table>"""

def render_confidence_bar(score):
    pct = min(max(int(score * 100), 0), 100)
    cls = "conf-high" if pct >= 70 else ("conf-mid" if pct >= 40 else "conf-low")
    return f"""<div class="conf-wrap">
        <span class="conf-label">Confidence</span>
        <div class="conf-bg"><div class="conf-fill {cls}" style="width:{pct}%"></div></div>
        <span class="conf-pct">{pct}%</span></div>"""

def photo_html(b64, name="", doc_type=""):
    if b64:
        photo_div = f'<div class="photo-frame"><img src="data:image/jpeg;base64,{b64}"/></div>'
    else:
        photo_div = '<div class="photo-placeholder">👤<br/>No photo</div>'
    sub_map = {
        "aadhaar": "Aadhaar Card Holder · भारत सरकार",
        "pan":     "PAN Card Holder · Income Tax Dept.",
        "dl":      "Driving Licence Holder · Transport Dept.",
        "voter":   "Voter ID Holder · Election Commission",
    }
    sub = sub_map.get(doc_type, "")
    return f"""<div class="photo-card">
        {photo_div}
        <div class="photo-meta">
            <div class="photo-label">ID Card Holder</div>
            <div class="photo-name">{name or "—"}</div>
            <div class="photo-sub">{sub}</div>
        </div></div>"""


# ── Auth UI ───────────────────────────────────────────────────────
def render_auth_ui():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;margin-bottom:28px;margin-top:40px;">
            <div style="width:52px;height:52px;background:linear-gradient(135deg,#4f46e5,#818cf8);
                border-radius:14px;display:inline-flex;align-items:center;justify-content:center;
                font-size:1.5rem;margin-bottom:14px;box-shadow:0 4px 16px rgba(99,102,241,0.35);">📝</div>
            <h1 style="font-size:1.9rem;font-weight:800;color:#1a1a2e;margin:0 0 6px;">OCR Stream</h1>
            <p style="color:#374151;font-size:0.85rem;margin:0;font-family:'DM Mono',monospace;">
                Sign in to extract &amp; store document data</p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔐 Login", "✍ Sign Up"])
        with tab_login:
            email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pw", placeholder="••••••••")
            if st.button("Login", use_container_width=True, key="btn_login"):
                ok, err = auth_login(email, password)
                if ok:
                    st.success("Logged in!")
                    st.rerun()
                else:
                    st.error(f"Login failed: {err}")

        with tab_signup:
            email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
            password = st.text_input("Password (min 6 chars)", type="password", key="signup_pw", placeholder="••••••••")
            if st.button("Create Account", use_container_width=True, key="btn_signup"):
                ok, err = auth_signup(email, password)
                if ok:
                    st.success("Account created! Check your email to confirm, then log in.")
                else:
                    st.error(f"Sign up failed: {err}")


# ================================================================
# 6. AUTH GATE
# ================================================================
if not st.session_state.user:
    render_auth_ui()
    st.stop()

# ================================================================
# 7. USER BAR
# ================================================================
col_user, col_out = st.columns([6, 1])
with col_user:
    login_info = ""
    if st.session_state.last_login:
        try:
            from datetime import timezone
            import dateutil.parser
            lt = dateutil.parser.parse(st.session_state.last_login)
            login_info = f" · Last login: {lt.strftime('%d %b %Y, %I:%M %p')}"
        except Exception:
            login_info = ""
    st.markdown(
        f"<p style='color:#4b5563;font-size:0.82rem;margin:4px 0;'>"
        f"🔒 <b style='color:#4f46e5'>{st.session_state.user.email}</b>"
        f"<span style='color:#9ca3af;font-size:0.76rem;'>{login_info}</span></p>",
        unsafe_allow_html=True)
with col_out:
    if st.button("Logout", key="btn_logout"):
        auth_logout()
        st.rerun()

# ================================================================
# 8. HEADER
# ================================================================
st.markdown("""
<div class="ocr-header">
    <div style="width:44px;height:44px;background:linear-gradient(135deg,#4f46e5,#818cf8);
        border-radius:12px;display:flex;align-items:center;justify-content:center;
        font-size:1.3rem;box-shadow:0 2px 10px rgba(99,102,241,0.3);flex-shrink:0;">📝</div>
    <div>
        <h1>OCR Stream</h1>
        <p>Extract text from images &amp; PDFs · Blur detection · Document-aware key-value extraction for Indian ID documents (Aadhaar, PAN, DL, Voter ID)</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ================================================================
# 9. MODE + SETTINGS (above the split)
# ================================================================
st.markdown('<div class="section-label">Select Mode</div>', unsafe_allow_html=True)
with st.container(border=True):
    mode = st.session_state.ocr_mode
    mode_label = "Text Extraction" if mode == "Normal" else "Document OCR"
    st.markdown(
        f"<p style='margin:0 0 10px;color:#334155;font-size:0.82rem;font-weight:600;'>Selected Mode: {mode_label}</p>",
        unsafe_allow_html=True
    )
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        if mode == "Normal":
            st.markdown(
                """<div style="background:#0f172a;color:#ffffff;border-radius:10px;padding:10px 12px;
                text-align:center;font-weight:700;border:1px solid #020617;">📄 Text Extraction</div>""",
                unsafe_allow_html=True,
            )
        else:
            if st.button("📄 Text Extraction", use_container_width=True, key="btn_mode_text"):
                st.session_state.ocr_mode = "Normal"
                st.session_state.last_result = None
                st.rerun()
    with col_m2:
        if mode == "Document":
            st.markdown(
                """<div style="background:#0f172a;color:#ffffff;border-radius:10px;padding:10px 12px;
                text-align:center;font-weight:700;border:1px solid #020617;">🪪 Document OCR</div>""",
                unsafe_allow_html=True,
            )
        else:
            if st.button("🪪 Document OCR", use_container_width=True, key="btn_mode_doc"):
                st.session_state.ocr_mode = "Document"
                st.session_state.last_result = None
                st.rerun()

mode = st.session_state.ocr_mode
if mode == "Document":
    st.markdown("""<div class="info-card accent">
        <div style="display:flex;align-items:center;gap:10px;">
            <span class="badge badge-pan">Document OCR</span>
            <span style="color:#6b7280;font-size:0.82rem;">Aadhaar, PAN, DL &amp; Voter ID key-value extraction with face detection</span>
        </div></div>""", unsafe_allow_html=True)
else:
    st.markdown("""<div class="info-card blue">
        <div style="display:flex;align-items:center;gap:10px;">
            <span class="badge badge-normal">Text Extraction</span>
            <span style="color:#6b7280;font-size:0.82rem;">Plain text extraction for any document or image</span>
        </div></div>""", unsafe_allow_html=True)

st.divider()

# Language & Engine
st.markdown('<div class="section-label">🌍 Language &nbsp;&nbsp; ⚙ OCR Engine</div>', unsafe_allow_html=True)
col_l, col_e = st.columns(2)
languages = {"English":"eng","Spanish":"spa","French":"fre","German":"ger",
             "Italian":"ita","Chinese (Simplified)":"chs","Chinese (Traditional)":"cht"}
engine_options = {"Engine 1 (Fast)":1,"Engine 2 (Better)":2,"Engine 3 (Best - Handwriting)":3}
with col_l:
    selected_language = st.selectbox("Language", list(languages.keys()), label_visibility="collapsed")
    language_code = languages[selected_language]
with col_e:
    selected_engine = st.selectbox("OCR Engine", list(engine_options.keys()), label_visibility="collapsed")
    engine_code = engine_options[selected_engine]

st.divider()

# ================================================================
# 10. SPLIT SCREEN — Left: Input  |  Right: Result
# ================================================================
MAX_FILE_BYTES = 5 * 1024 * 1024

col_left, col_right = st.columns([1, 1.4], gap="large")

# ── LEFT: Input ──────────────────────────────────────────────────
with col_left:
    st.markdown('<div class="section-label" style="margin-top:0;">Input Source</div>', unsafe_allow_html=True)

    input_tab1, input_tab2 = st.tabs(["📂 Upload File", "📷 Camera"])

    uploaded_file = None
    _fsize = 0

    with input_tab1:
        _uf = st.file_uploader(
            "Upload image or PDF (max 5 MB)",
            type=["png","jpg","jpeg","webp","pdf"],
            label_visibility="collapsed"
        )
        if _uf is not None:
            _uf.seek(0, 2); _sz = _uf.tell(); _uf.seek(0)
            if _sz > MAX_FILE_BYTES:
                st.error(f"❌ File too large ({round(_sz/1024/1024,2)} MB). Max 5 MB.")
            else:
                uploaded_file = _uf
                _fsize = _sz
                st.session_state.camera_bytes = None
                # Small preview
                file_type_check = get_file_type(_uf)
                if file_type_check.startswith("image"):
                    _uf.seek(0)
                    st.image(_uf, use_container_width=True, caption=f"📄 {_uf.name} · {round(_sz/1024,1)} KB")
                    _uf.seek(0)
                else:
                    st.caption(f"📄 {_uf.name} · {round(_sz/1024,1)} KB")

    with input_tab2:
        st.info("📱 Works best on mobile. Point camera at document and capture.", icon="ℹ️")
        b1, b2 = st.columns(2)
        with b1:
            if st.button("📸 Open Camera", use_container_width=True, key="btn_open_camera"):
                st.session_state.camera_open = True
                st.rerun()
        with b2:
            if st.button("✖ Close Camera", use_container_width=True, key="btn_close_camera"):
                st.session_state.camera_open = False
                st.rerun()

        camera_image = None
        if st.session_state.camera_open:
            st.markdown(
                "<p style='margin:8px 0 6px;color:#0f172a;font-weight:700;'>Take Photo</p>",
                unsafe_allow_html=True
            )
            st.caption("Tap the capture button shown under the camera preview.")
            cam_key = f"camera_input_{st.session_state.camera_widget_nonce}"
            camera_image = st.camera_input("Take Photo", key=cam_key, label_visibility="visible")
        else:
            st.caption("Click `Open Camera` to show the take photo option.")

        if camera_image is not None:
            camera_image.seek(0, 2); _csz = camera_image.tell(); camera_image.seek(0)
            if _csz > MAX_FILE_BYTES:
                st.error("❌ Capture too large.")
            else:
                st.session_state.camera_bytes = camera_image.read()
                st.session_state.camera_fsize = _csz
                st.session_state.camera_open = False

        if st.session_state.camera_bytes:
            cam_buf = io.BytesIO(st.session_state.camera_bytes)
            cam_buf.name = "camera_capture.jpg"
            cam_buf.type = "image/jpeg"
            cam_buf.seek(0)
            if uploaded_file is None:
                uploaded_file = cam_buf
                _fsize = st.session_state.camera_fsize
            preview_buf = io.BytesIO(st.session_state.camera_bytes)
            st.image(preview_buf, use_container_width=True, caption=f"📷 {round(st.session_state.camera_fsize/1024,1)} KB")
            if st.button("🗑 Clear Photo", key="btn_clear_cam"):
                st.session_state.camera_bytes = None
                st.session_state.camera_fsize = 0
                st.session_state.camera_widget_nonce += 1
                st.session_state.camera_open = False
                st.rerun()

    # Extract button
    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
    extract_clicked = st.button("🚀 Extract Text", use_container_width=True, key="btn_extract")

    # ── Run OCR on click ──
    if extract_clicked and uploaded_file:
        try:
            uploaded_file.seek(0)
            raw_bytes = uploaded_file.read()
        except Exception as e:
            st.error(f"❌ Could not read file: {e}")
            raw_bytes = None

        if raw_bytes:
            file_type = get_file_type(uploaded_file)
            file_name = getattr(uploaded_file, "name", "camera_capture.jpg")
            is_pdf = file_type == "application/pdf" or file_name.lower().endswith(".pdf")

            if is_pdf and engine_code == 3:
                st.warning("⚠️ Engine 3 doesn't support PDFs — using Engine 2.")

            # Blur check
            blur_ok = True
            if file_type.startswith("image"):
                blur_score = detect_blur(io.BytesIO(raw_bytes))
                if blur_score < 60:
                    st.error(f"⚠ Too blurry (score: {round(blur_score,1)}). Retake with better lighting.")
                    blur_ok = False
                elif blur_score < 120:
                    st.warning(f"Slightly soft (score: {round(blur_score,1)}). Will enhance.")

            if blur_ok:
                # Face extraction (Document mode only)
                photo_b64 = None
                if file_type.startswith("image") and mode == "Document":
                    with st.spinner("📸 Detecting photo..."):
                        photo_b64 = extract_face_photo(io.BytesIO(raw_bytes))

                # Run OCR
                with st.spinner("🔍 Extracting text..."):
                    result = perform_ocr(raw_bytes, language_code, engine_code, is_pdf=is_pdf)

                st.session_state.camera_bytes = None

                if "error" in result:
                    st.error(f"❌ {result['error']}")
                elif result.get("ParsedResults"):
                    parsed_results = result["ParsedResults"]
                    processing_time = round(float(result.get("ProcessingTimeInMilliseconds",0))/1000, 3)
                    combined_text = "\n".join(pr.get("ParsedText","") for pr in parsed_results)

                    if mode == "Document":
                        doc_type = detect_doc_type(combined_text)
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
                    else:
                        doc_type = "normal"
                        fields = {}

                    # Save result to session state for right panel
                    st.session_state.last_result = {
                        "mode": mode,
                        "doc_type": doc_type,
                        "fields": fields,
                        "raw_text": combined_text,
                        "photo_b64": photo_b64,
                        "processing_time": processing_time,
                        "file_name": file_name,
                        "file_size_bytes": len(raw_bytes),
                        "parsed_results": parsed_results,
                    }

                    # Auto-save to Supabase
                    if mode == "Document" and fields:
                        saved, save_err = save_extraction(
                            doc_type, fields, combined_text, file_name, len(raw_bytes))
                        st.session_state.last_result["saved"] = saved
                        st.session_state.last_result["save_err"] = save_err

                    st.rerun()
                else:
                    st.error("❌ No text could be extracted.")

    elif extract_clicked and not uploaded_file:
        st.warning("⚠️ Please upload a file or take a photo first.")


# ── RIGHT: Results ───────────────────────────────────────────────
with col_right:
    st.markdown('<div class="section-label" style="margin-top:0;">Extracted Result</div>', unsafe_allow_html=True)

    res = st.session_state.last_result

    if res is None:
        # Empty state
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📄</div>
            <div class="empty-title">No extraction yet</div>
            <div class="empty-sub">Upload a file and click Extract Text</div>
        </div>""", unsafe_allow_html=True)

    else:
        # ── DOCUMENT MODE result ──
        if res["mode"] == "Document":
            doc_type  = res["doc_type"]
            fields    = res["fields"]
            photo_b64 = res.get("photo_b64")

            doc_label = {"aadhaar":"Aadhaar Card","pan":"PAN Card","dl":"Driving Licence",
                         "voter":"Voter ID","unknown":"Unknown Document"}.get(doc_type, "Document")
            badge_cls = {"aadhaar":"badge-aadhaar","pan":"badge-pan","dl":"badge-dl",
                         "voter":"badge-voter","unknown":"badge-unknown"}.get(doc_type,"badge-unknown")

            # Doc type banner
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:12px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span class="badge {badge_cls}">{doc_label}</span>
                    <span style="color:#9ca3af;font-size:0.78rem;">Document OCR</span>
                </div>
                <span style="color:#9ca3af;font-size:0.72rem;font-family:'DM Mono',monospace;">
                    ⏱ {res['processing_time']}s
                </span>
            </div>""", unsafe_allow_html=True)

            if doc_type == "unknown":
                st.warning("⚠️ Could not detect document type.")

            # Photo card
            holder_name = fields.get("Name", "")
            st.markdown(photo_html(photo_b64, holder_name, doc_type), unsafe_allow_html=True)
            if photo_b64:
                st.download_button("⬇ Download Photo",
                    data=base64.b64decode(photo_b64),
                    file_name=f"{doc_type}_photo.jpg", mime="image/jpeg", key="dl_photo")

            # Fields table
            if fields:
                st.markdown('<div class="section-label">Extracted Fields</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-card">{render_kv_table(fields)}</div>', unsafe_allow_html=True)

                # Confidence
                expected = {"aadhaar":5,"pan":4,"dl":5,"voter":5}.get(doc_type, 3)
                conf = min(len(fields)/expected, 1.0)
                st.markdown(render_confidence_bar(conf), unsafe_allow_html=True)

                # Save status
                saved    = res.get("saved")
                save_err = res.get("save_err")
                if saved:
                    st.success("✅ Saved to your account.")
                elif save_err == "duplicate":
                    st.info("ℹ️ Already saved — no duplicate created.")
                elif save_err:
                    st.warning(f"⚠️ Could not save: {save_err}")

                # Downloads
                json_str = json.dumps(fields, indent=2, ensure_ascii=False)
                csv_str  = "\n".join(f"{k},{v}" for k, v in fields.items())
                dl1, dl2 = st.columns(2)
                with dl1:
                    st.download_button("⬇ Download JSON", data=json_str,
                        file_name=f"{doc_type}_fields.json", mime="application/json", key="dl_json")
                with dl2:
                    st.download_button("⬇ Download CSV", data=csv_str,
                        file_name=f"{doc_type}_fields.csv", mime="text/csv", key="dl_csv")
            else:
                st.warning("No structured fields extracted.")

            # Raw text
            with st.expander("📄 Raw OCR Text"):
                for i, pr in enumerate(res["parsed_results"]):
                    raw = pr.get("ParsedText","").strip()
                    st.text_area(f"Page {i+1}" if len(res["parsed_results"])>1 else "Raw Text",
                                 value=raw or "No text found.", height=160, key=f"raw_{i}")
                    st.download_button(f"⬇ Raw Text", data=raw,
                        file_name=f"raw_p{i+1}.txt", mime="text/plain", key=f"dl_raw_{i}")

        # ── NORMAL MODE result ──
        else:
            parsed_results = res["parsed_results"]
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <span class="badge badge-normal">Text Extraction</span>
                <span style="color:#9ca3af;font-size:0.72rem;font-family:'DM Mono',monospace;">
                    ⏱ {res['processing_time']}s · {len(parsed_results)} page(s)</span>
            </div>""", unsafe_allow_html=True)

            if len(parsed_results) > 1:
                tabs = st.tabs([f"Page {i+1}" for i in range(len(parsed_results))])
                for i, tab in enumerate(tabs):
                    with tab:
                        text = parsed_results[i].get("ParsedText","").strip()
                        edited = st.text_area("Text", value=text or "No text found.",
                                              height=300, key=f"norm_text_{i}")
                        st.download_button("⬇ Download", data=edited,
                            file_name=f"page_{i+1}.txt", mime="text/plain", key=f"dl_norm_{i}")
            else:
                text = parsed_results[0].get("ParsedText","").strip()
                edited = st.text_area("Extracted Text", value=text or "No text found.", height=300)
                st.download_button("⬇ Download Text", data=edited,
                    file_name="ocr_text.txt", mime="text/plain", key="dl_norm")

        # Clear result button
        if st.button("✖ Clear Result", key="btn_clear_result"):
            st.session_state.last_result = None
            st.rerun()

# ================================================================
# 11. SAVED EXTRACTIONS (below split)
# ================================================================
st.divider()
with st.expander("🗂 My Saved Extractions", expanded=False):
    records = load_extractions()
    if not records:
        st.markdown("<p style='color:#9ca3af;font-size:0.85rem;'>No saved extractions yet.</p>", unsafe_allow_html=True)
    else:
        st.caption(f"{len(records)} record(s) found")
        for r in records:
            ts     = r.get("created_at","")[:16].replace("T"," ")
            dtype  = r.get("doc_type","other")
            dlabel = {"aadhaar":"Aadhaar","pan":"PAN","dl":"Driving Licence",
                      "voter":"Voter ID","other":"Other"}.get(dtype, dtype.title())
            name   = r.get("holder_name") or "—"
            rid    = r.get("id","x")

            if dtype == "aadhaar":
                keys = [("Name","holder_name"),("Aadhaar Number","aadhaar_number"),
                        ("Date of Birth","dob"),("Gender","gender"),("Address","address"),
                        ("Pincode","pincode"),("State","state"),("VID","vid")]
            elif dtype == "pan":
                keys = [("Name","holder_name"),("PAN Number","pan_number"),
                        ("Father's Name","father_name"),("Date of Birth","dob"),
                        ("Account Type","account_type"),("Issued By","issued_by")]
            elif dtype == "dl":
                keys = [("Name","holder_name"),("DL Number","dl_number"),
                        ("Date of Birth","dob"),("Valid Till","valid_till"),
                        ("Vehicle Class","vehicle_class"),("Blood Group","blood_group"),
                        ("Issuing Authority","issuing_authority")]
            elif dtype == "voter":
                keys = [("Name","holder_name"),("EPIC Number","epic_number"),
                        ("Father/Husband Name","father_husband_name"),("Date of Birth","dob"),
                        ("Gender","gender"),("Constituency","constituency"),("Part No","part_no")]
            else:
                keys = [("Raw Text","raw_text")]

            display = {label: r[col] for label, col in keys if r.get(col)}

            with st.expander(f"📄 {dlabel}  ·  {name}  ·  {ts}"):
                st.markdown(f'<div class="info-card">{render_kv_table(display)}</div>', unsafe_allow_html=True)
                st.download_button("⬇ Download JSON",
                    data=json.dumps(display, indent=2, ensure_ascii=False),
                    file_name=f"{dtype}_{rid[:8]}.json", mime="application/json",
                    key=f"hist_dl_{rid}")

# ================================================================
# 12. FAILURE LOG
# ================================================================
with st.expander(f"🔴 Failure Log ({len(st.session_state.failure_log)} entries)", expanded=False):
    if st.session_state.failure_log:
        col_l, col_r = st.columns([5, 1])
        with col_r:
            if st.button("🗑 Clear", key="clear_log"):
                st.session_state.failure_log = []
                st.rerun()
        entries_html = "".join(f"""
        <div class="fail-entry">
            <span class="fail-ts">[{e['ts']}]</span>
            <span style="color:#6366f1;font-family:'DM Mono',monospace;">{e['ctx']}</span>
            <span class="fail-msg">{e['msg']}</span>
        </div>""" for e in reversed(st.session_state.failure_log))
        st.markdown(f'<div class="fail-log"><div class="fail-log-title">⚠ System Failure Log</div>{entries_html}</div>',
                    unsafe_allow_html=True)
        log_text = "\n".join(f"[{e['ts']}] [{e['ctx']}] {e['msg']}" for e in st.session_state.failure_log)
        st.download_button("⬇ Download Log", data=log_text,
            file_name="failure_log.txt", mime="text/plain", key="dl_log")
    else:
        st.markdown("<p style='color:#9ca3af;font-size:0.82rem;font-family:monospace;'>No failures recorded.</p>",
                    unsafe_allow_html=True)
