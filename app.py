
# import streamlit as st
# import requests
# import cv2
# import numpy as np
# import os
# import re
# import json
# import base64
# from datetime import datetime
# from PIL import Image, ImageEnhance
# import io
# from supabase import create_client, Client
# try:
#     from pdf2image import convert_from_bytes
#     PDF2IMAGE_AVAILABLE = True
# except ImportError:
#     PDF2IMAGE_AVAILABLE = False

# # ================================================================
# # 1. PAGE CONFIG
# # ================================================================
# st.set_page_config(page_title="OCR Stream", page_icon="📝", layout="wide")

# # ================================================================
# # 2. CUSTOM CSS — Light Theme matching preview
# # ================================================================
# st.markdown("""
# <style>
#     @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

#     html, body, [class*="css"] {
#         font-family: 'DM Sans', sans-serif !important;
#         color: #1a1a2e;
#     }
#     .stApp {
#         background: #f5f6fa !important;
#         color: #1a1a2e;
#     }
#     h1,h2,h3 { font-family:'DM Sans',sans-serif !important; font-weight:700; color:#1a1a2e; }

#     .ocr-header {
#         background: #ffffff;
#         border: 1px solid #e8eaf0;
#         border-radius: 16px;
#         padding: 22px 28px;
#         margin-bottom: 18px;
#         box-shadow: 0 2px 12px rgba(0,0,0,0.06);
#         display: flex;
#         align-items: center;
#         gap: 16px;
#     }
#     .ocr-header h1 { font-size:1.5rem; margin:0; color:#1a1a2e; letter-spacing:-0.3px; }
#     .ocr-header p  { margin:4px 0 0; color:#374151; font-size:0.82rem; font-family:'DM Mono',monospace; line-height:1.5; }

#     .panel-card {
#         background: #ffffff;
#         border: 1px solid #e8eaf0;
#         border-radius: 14px;
#         padding: 18px;
#         box-shadow: 0 1px 6px rgba(0,0,0,0.04);
#         height: 100%;
#     }
#     .info-card {
#         background: #ffffff;
#         border: 1px solid #e8eaf0;
#         border-radius: 12px;
#         padding: 16px 18px;
#         margin-bottom: 12px;
#         box-shadow: 0 1px 4px rgba(0,0,0,0.04);
#     }
#     .info-card.accent { border-left: 3px solid #6366f1; }
#     .info-card.green  { border-left: 3px solid #10b981; }
#     .info-card.blue   { border-left: 3px solid #3b82f6; }

#     .section-label {
#         font-size: 0.68rem;
#         font-weight: 700;
#         letter-spacing: 1.5px;
#         text-transform: uppercase;
#         color: #4b5563;
#         margin: 14px 0 6px;
#     }

#     .badge {
#         display: inline-block;
#         padding: 3px 10px;
#         border-radius: 20px;
#         font-size: 0.7rem;
#         font-weight: 700;
#         letter-spacing: 0.5px;
#         text-transform: uppercase;
#     }
#     .badge-aadhaar { background:#ecfdf5; color:#059669; border:1px solid #a7f3d0; }
#     .badge-pan     { background:#eff6ff; color:#4f46e5; border:1px solid #bfdbfe; }
#     .badge-unknown { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
#     .badge-normal  { background:#eff6ff; color:#3b82f6; border:1px solid #bfdbfe; }
#     .badge-dl      { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
#     .badge-voter   { background:#faf5ff; color:#7c3aed; border:1px solid #ddd6fe; }

#     .kv-table { width:100%; border-collapse:collapse; font-family:'DM Mono',monospace; font-size:0.8rem; }
#     .kv-table th {
#         text-align:left; padding:8px 12px;
#         background:#f5f6fa; color:#6366f1;
#         font-weight:600; font-size:0.7rem; letter-spacing:1px; text-transform:uppercase;
#         border-bottom:1px solid #e8eaf0;
#     }
#     .kv-table td { padding:8px 12px; border-bottom:1px solid #f0f1f5; color:#374151; vertical-align:top; }
#     .kv-table td:first-child { color:#6b7280; width:38%; font-weight:500; }
#     .kv-table tr:hover td { background:#fafbff; }

#     .photo-card {
#         background:#f9fafb; border:1px solid #e8eaf0; border-radius:10px;
#         padding:12px; display:flex; align-items:center; gap:12px; margin-bottom:12px;
#     }
#     .photo-frame {
#         width:48px; height:58px; border-radius:8px; border:1.5px solid #e8eaf0;
#         background:#e8eaf0; display:flex; align-items:center; justify-content:center;
#         font-size:1.3rem; flex-shrink:0; overflow:hidden;
#     }
#     .photo-frame img { width:100%; height:100%; object-fit:cover; }
#     .photo-placeholder {
#         width:48px; height:58px; border-radius:8px; border:2px dashed #d1d5db;
#         background:#f9fafb; display:flex; flex-direction:column; align-items:center;
#         justify-content:center; font-size:0.6rem; color:#9ca3af;
#         font-family:'DM Mono',monospace; text-align:center; flex-shrink:0;
#     }
#     .photo-meta { flex:1; }
#     .photo-label { font-size:0.62rem; font-weight:700; letter-spacing:1px; text-transform:uppercase; color:#9ca3af; margin-bottom:3px; }
#     .photo-name  { font-size:0.95rem; font-weight:700; color:#1a1a2e; margin-bottom:2px; }
#     .photo-sub   { font-size:0.72rem; color:#4b5563; font-family:'DM Mono',monospace; line-height:1.5; }

#     .conf-wrap { display:flex; align-items:center; gap:10px; margin:10px 0; }
#     .conf-label { font-size:0.72rem; font-family:'DM Mono',monospace; color:#4b5563; min-width:72px; }
#     .conf-bg { flex:1; background:#e8eaf0; border-radius:4px; height:6px; overflow:hidden; }
#     .conf-fill { height:100%; border-radius:4px; }
#     .conf-high { background:#10b981; }
#     .conf-mid  { background:#f59e0b; }
#     .conf-low  { background:#ef4444; }
#     .conf-pct  { font-size:0.72rem; font-family:'DM Mono',monospace; color:#374151; min-width:32px; text-align:right; }

#     .empty-state {
#         display:flex; flex-direction:column; align-items:center; justify-content:center;
#         text-align:center; padding:48px 20px; color:#9ca3af;
#     }
#     .empty-icon { font-size:2.5rem; opacity:0.35; margin-bottom:12px; }
#     .empty-title { font-weight:600; font-size:0.9rem; margin-bottom:4px; }
#     .empty-sub { font-size:0.76rem; font-family:'DM Mono',monospace; }

#     .fail-log { background:#fff9f9; border:1px solid #fecaca; border-radius:12px; padding:16px; margin-top:12px; }
#     .fail-log-title { color:#dc2626; font-weight:700; font-size:0.78rem; letter-spacing:1px; text-transform:uppercase; margin-bottom:10px; }
#     .fail-entry { font-family:'DM Mono',monospace; font-size:0.76rem; color:#6b7280; padding:5px 0; border-bottom:1px solid #fee2e2; display:flex; gap:10px; flex-wrap:wrap; }
#     .fail-entry:last-child { border-bottom:none; }
#     .fail-ts  { color:#9ca3af; flex-shrink:0; }
#     .fail-msg { color:#dc2626; }

#     .stButton > button {
#         background: linear-gradient(135deg,#4f46e5,#6366f1) !important;
#         color: white !important; border: none !important;
#         border-radius: 10px !important; padding: 10px 20px !important;
#         font-family: 'DM Sans',sans-serif !important; font-weight: 600 !important;
#         box-shadow: 0 2px 8px rgba(99,102,241,0.3) !important;
#         transition: all 0.2s !important;
#     }
#     .stButton > button:hover {
#         opacity: 0.9 !important;
#         box-shadow: 0 4px 14px rgba(99,102,241,0.4) !important;
#         transform: translateY(-1px) !important;
#     }

#     .sec-btn > button {
#         background: #ffffff !important; color: #4f46e5 !important;
#         border: 1.5px solid #c7d2fe !important;
#         box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
#     }
#     .sec-btn > button:hover { background: #eef2ff !important; }

#     .stDownloadButton > button {
#         background: #ffffff !important; color: #4f46e5 !important;
#         border: 1px solid #c7d2fe !important; border-radius: 8px !important;
#         font-family: 'DM Sans',sans-serif !important; font-weight: 600 !important;
#         box-shadow: none !important;
#     }
#     .stDownloadButton > button:hover { background: #eef2ff !important; border-color: #a5b4fc !important; }

#     .stSelectbox > div > div {
#         background: #ffffff !important; border: 1px solid #e8eaf0 !important;
#         border-radius: 8px !important; color: #374151 !important;
#         font-family: 'DM Sans',sans-serif !important;
#     }
#     [data-testid="stTextInputRootElement"] input {
#         background: #eef2f7 !important;
#         color: #0f172a !important;
#         border: 1px solid #bcc7d8 !important;
#         border-radius: 10px !important;
#     }
#     [data-testid="stTextInputRootElement"] input::placeholder {
#         color: #64748b !important;
#         opacity: 1 !important;
#     }
#     [data-testid="stTextInputRootElement"] input:focus {
#         border-color: #6366f1 !important;
#         box-shadow: 0 0 0 1px #6366f1 inset !important;
#     }
#     [data-testid="stWidgetLabel"] p {
#         color: #111827 !important;
#         font-weight: 600 !important;
#     }
#     .stTextArea textarea {
#         background: #eef2f7 !important; color: #111827 !important;
#         border: 1px solid #bcc7d8 !important; border-radius: 8px !important;
#         font-family: 'DM Mono',monospace !important; font-size: 0.8rem !important;
#     }

#     [data-testid="stFileUploader"] {
#         background: #fafbff !important; border: 2px dashed #c7d2fe !important;
#         border-radius: 10px !important;
#     }
#     [data-testid="stFileUploader"]:hover { border-color: #6366f1 !important; }

#     .stTabs [data-baseweb="tab-list"] {
#         background: #e9edf4 !important; border-radius: 10px !important;
#         padding: 4px !important; gap: 4px !important; border: 1px solid #cdd6e3 !important;
#     }
#     .stTabs [data-baseweb="tab"] {
#         background: transparent !important; color: #374151 !important;
#         border-radius: 7px !important; font-family: 'DM Sans',sans-serif !important;
#         font-weight: 600 !important; padding: 7px 14px !important; border: none !important;
#     }
#     .stTabs [aria-selected="true"] {
#         background: #ffffff !important; color: #111827 !important;
#         font-weight: 700 !important; box-shadow: 0 1px 4px rgba(0,0,0,0.12) !important;
#     }

#     [data-testid="stExpander"] {
#         background: #ffffff !important; border: 1px solid #e8eaf0 !important;
#         border-radius: 10px !important; box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
#         margin-bottom: 8px !important;
#     }
#     [data-testid="stExpander"] summary {
#         color: #374151 !important; font-weight: 600 !important;
#         font-family: 'DM Sans',sans-serif !important; padding: 12px 16px !important;
#     }

#     [data-testid="stAlert"]   { border-radius: 10px !important; font-family:'DM Sans',sans-serif !important; }
#     [data-testid="stInfo"]    { background:#eff6ff !important; border-color:#bfdbfe !important; color:#1e40af !important; }
#     [data-testid="stWarning"] { background:#fffbeb !important; border-color:#fcd34d !important; }
#     [data-testid="stSuccess"] { background:#ecfdf5 !important; border-color:#a7f3d0 !important; }

#     [data-testid="stCameraInput"] {
#         border:2px dashed #c7d2fe !important;
#         border-radius:12px !important;
#         background:#fafbff !important;
#     }

#     hr { border-color:#e8eaf0 !important; margin:16px 0 !important; }
#     [data-testid="stCaptionContainer"] p { color:#4b5563 !important; font-family:'DM Mono',monospace !important; font-size:0.76rem !important; }
#     .stSpinner > div { border-top-color:#6366f1 !important; }

#     .vdivider {
#         width: 1px; background: #e8eaf0; margin: 0 4px; border-radius: 2px;
#         min-height: 400px;
#     }

#     @media (max-width:768px) {
#         .photo-card { flex-direction:column; align-items:center; text-align:center; }
#         .kv-table td, .kv-table th { padding:6px 8px; font-size:0.74rem; }
#     }
# </style>
# """, unsafe_allow_html=True)

# # ================================================================
# # 3. CONFIG & SUPABASE INIT
# # ================================================================
# OCR_API_KEY = os.getenv("OCR_API_KEY", "")
# OCR_URL = "https://api.ocr.space/parse/image"

# def _get_secret(key: str, default: str = "") -> str:
#     val = os.getenv(key)
#     if val:
#         return val
#     try:
#         return st.secrets.get(key, default)
#     except Exception:
#         return default

# SUPABASE_URL = _get_secret("SUPABASE_URL")
# SUPABASE_KEY = _get_secret("SUPABASE_ANON_KEY")

# @st.cache_resource
# def get_supabase() -> Client:
#     return create_client(SUPABASE_URL, SUPABASE_KEY)

# supabase = get_supabase()

# # ================================================================
# # 4. SESSION STATE INIT
# # ================================================================
# for key, default in [
#     ("user", None), ("access_token", None), ("failure_log", []),
#     ("ocr_mode", "Normal"), ("camera_bytes", None), ("camera_fsize", 0),
#     ("camera_open", False),
#     ("camera_widget_nonce", 0),
#     ("last_result", None),
#     ("last_login", None),
#     ("user_created_at", None),
# ]:
#     if key not in st.session_state:
#         st.session_state[key] = default

# # ================================================================
# # 5. HELPER FUNCTIONS
# # ================================================================

# def log_failure(context: str, message: str):
#     ts = datetime.now().strftime("%H:%M:%S")
#     st.session_state.failure_log.append({"ts": ts, "ctx": context, "msg": message})


# # ── Auth ─────────────────────────────────────────────────────────
# def auth_login(email, password):
#     try:
#         res = supabase.auth.sign_in_with_password({"email": email, "password": password})
#         st.session_state.user = res.user
#         st.session_state.access_token = res.session.access_token
#         supabase.postgrest.auth(res.session.access_token)

#         try:
#             supabase.rpc("upsert_user_login", {
#                 "p_user_id": res.user.id,
#                 "p_email": res.user.email
#             }).execute()
#             user_row = (supabase.table("users")
#                         .select("last_login, created_at")
#                         .eq("id", res.user.id)
#                         .single().execute())
#             st.session_state.last_login = user_row.data.get("last_login") if user_row.data else None
#             st.session_state.user_created_at = user_row.data.get("created_at") if user_row.data else None
#         except Exception:
#             st.session_state.last_login = None
#             st.session_state.user_created_at = None

#         return True, None
#     except Exception as e:
#         return False, str(e)

# def auth_signup(email, password):
#     try:
#         supabase.auth.sign_up({"email": email, "password": password,
#             "options": {"email_redirect_to": "https://ocr-stream-nhjd5pbhtxcm99hfgncbre.streamlit.app"}})
#         return True, None
#     except Exception as e:
#         return False, str(e)

# def auth_logout():
#     supabase.auth.sign_out()
#     st.session_state.user = None
#     st.session_state.access_token = None


# # ── Supabase save/load ────────────────────────────────────────────

# # Columns that are guaranteed to exist in the original schema
# _CORE_COLUMNS = {
#     "user_id", "doc_type", "file_name", "file_size_kb",
#     "holder_name", "dob", "gender",
#     "aadhaar_number", "address", "pincode", "state", "vid",
#     "pan_number", "father_name", "account_type", "issued_by",
#     "dl_number", "valid_till", "vehicle_class", "blood_group", "issuing_authority",
#     "epic_number", "father_husband_name", "constituency", "part_no",
#     "raw_text",
# }

# # Extended columns added in the improved schema — may not exist yet
# _EXTENDED_COLUMNS = {
#     "enrolment_no", "date_of_issue", "son_daughter_wife_of",
#     "serial_no", "polling_station", "mobile",
# }

# def _build_row(fields, doc_type, file_name, size_kb, raw_text, include_extended=True):
#     """Build the insert row dict, optionally excluding extended columns."""
#     row = {
#         "user_id":             st.session_state.user.id,
#         "doc_type":            doc_type if doc_type in ("aadhaar","pan","dl","voter") else "other",
#         "file_name":           file_name,
#         "file_size_kb":        size_kb,
#         # ── Common ──
#         "holder_name":         fields.get("Name", ""),
#         "dob":                 fields.get("Date of Birth", ""),
#         "gender":              fields.get("Gender", ""),
#         # ── Aadhaar ──
#         "aadhaar_number":      fields.get("Aadhaar Number", ""),
#         "address":             fields.get("Address", ""),
#         "pincode":             fields.get("Pincode", ""),
#         "state":               fields.get("State", ""),
#         "vid":                 fields.get("VID", ""),
#         # ── PAN ──
#         "pan_number":          fields.get("PAN Number", ""),
#         "father_name":         fields.get("Father's Name", ""),
#         "account_type":        fields.get("Account Type", ""),
#         "issued_by":           fields.get("Issued By", ""),
#         # ── DL ──
#         "dl_number":           fields.get("DL Number", ""),
#         "valid_till":          fields.get("Valid Till", ""),
#         "vehicle_class":       fields.get("Vehicle Class", ""),
#         "blood_group":         fields.get("Blood Group", ""),
#         "issuing_authority":   fields.get("Issuing Authority", ""),
#         # ── Voter ──
#         "epic_number":         fields.get("EPIC Number", ""),
#         "father_husband_name": fields.get("Father's Name", "") or fields.get("Father/Husband Name", ""),
#         "constituency":        fields.get("Constituency", ""),
#         "part_no":             fields.get("Part No", ""),
#         # ── Raw ──
#         "raw_text":            raw_text[:4000],
#     }
#     if include_extended:
#         row.update({
#             "enrolment_no":         fields.get("Enrolment No", ""),
#             "date_of_issue":        fields.get("Date of Issue", ""),
#             "son_daughter_wife_of": fields.get("Son/Daughter/Wife of", ""),
#             "serial_no":            fields.get("Serial No", ""),
#             "polling_station":      fields.get("Polling Station", ""),
#             "mobile":               fields.get("Mobile", ""),
#         })
#     # Strip empty strings to keep DB clean (insert NULL instead)
#     return {k: v for k, v in row.items() if v != ""}

# def _get_doc_unique_key(doc_type, fields):
#     """
#     Return (column_name, value) for the natural unique identifier of each doc type.
#     This is the field we use to detect duplicates before inserting.
#     """
#     mapping = {
#         "aadhaar": ("aadhaar_number", fields.get("Aadhaar Number", "").replace(" ", "")),
#         "pan":     ("pan_number",     fields.get("PAN Number", "")),
#         "dl":      ("dl_number",      fields.get("DL Number", "").replace(" ", "").replace("-", "")),
#         "voter":   ("epic_number",    fields.get("EPIC Number", "")),
#     }
#     return mapping.get(doc_type, (None, None))


# def check_duplicate(doc_type, fields):
#     """
#     Returns True if this exact document number already exists for this user.
#     Falls back to False (allow insert) if the check itself fails.
#     """
#     col, val = _get_doc_unique_key(doc_type, fields)
#     if not col or not val:
#         return False   # No unique key available — can't check, allow insert
#     try:
#         # Normalise stored value too: strip spaces/dashes for comparison
#         existing = (
#             supabase.table("extractions")
#             .select("id")
#             .eq("user_id", st.session_state.user.id)
#             .eq("doc_type", doc_type)
#             .execute()
#         )
#         if not existing.data:
#             return False
#         # Compare normalised values
#         norm_val = val.replace(" ", "").replace("-", "").upper()
#         for row in existing.data:
#             stored = str(row.get(col) or "").replace(" ", "").replace("-", "").upper()
#             if stored and stored == norm_val:
#                 return True
#         return False
#     except Exception:
#         return False   # If check fails, let insert proceed (DB constraint is backup)


# def save_extraction(doc_type, fields, raw_text="", file_name="", file_size_bytes=0):
#     if not st.session_state.user:
#         return False, "Not logged in"

#     supabase.postgrest.auth(st.session_state.access_token)
#     size_kb = round(file_size_bytes / 1024, 1) if file_size_bytes else 0

#     # ── Step 1: Pre-check for duplicate by document number ──
#     if check_duplicate(doc_type, fields):
#         return False, "duplicate"

#     # ── Step 2: Attempt insert with all columns (including extended) ──
#     try:
#         row = _build_row(fields, doc_type, file_name, size_kb, raw_text, include_extended=True)
#         supabase.table("extractions").insert(row).execute()
#         return True, None
#     except Exception as e:
#         err = str(e)
#         # DB-level duplicate (safety net in case pre-check missed it)
#         if "duplicate" in err.lower() or "unique" in err.lower() or "23505" in err:
#             return False, "duplicate"
#         # Missing column error → fall back to core-only insert
#         is_column_error = (
#             "PGRST204" in err
#             or "column" in err.lower()
#             or "schema cache" in err.lower()
#         )
#         if not is_column_error:
#             return False, err

#     # ── Step 3: Fallback — core columns only (extended cols not in DB yet) ──
#     try:
#         row = _build_row(fields, doc_type, file_name, size_kb, raw_text, include_extended=False)
#         supabase.table("extractions").insert(row).execute()
#         return True, "partial"   # Saved, but missing new columns
#     except Exception as e2:
#         err2 = str(e2)
#         if "duplicate" in err2.lower() or "unique" in err2.lower() or "23505" in err2:
#             return False, "duplicate"
#         return False, err2

# def load_extractions():
#     if not st.session_state.user:
#         return []
#     try:
#         supabase.postgrest.auth(st.session_state.access_token)
#         res = (supabase.table("extractions").select("*")
#                .eq("user_id", st.session_state.user.id)
#                .order("created_at", desc=True).execute())
#         return res.data or []
#     except Exception as e:
#         log_failure("Supabase Fetch", str(e))
#         return []


# # ── Image helpers ─────────────────────────────────────────────────
# def get_file_type(f) -> str:
#     try:
#         t = getattr(f, "type", None)
#         if t and isinstance(t, str) and t.strip():
#             return t.strip()
#         name = getattr(f, "name", "") or ""
#         if name.lower().endswith(".pdf"):
#             return "application/pdf"
#         return "image/jpeg"
#     except Exception:
#         return "image/jpeg"

# def detect_blur(file) -> float:
#     try:
#         file.seek(0)
#         image = Image.open(file).convert("L")
#         score = cv2.Laplacian(np.array(image), cv2.CV_64F).var()
#         file.seek(0)
#         return score
#     except Exception as e:
#         log_failure("Blur Detection", str(e))
#         return 999

# def compress_image_bytes(raw_bytes: bytes) -> bytes:
#     try:
#         img = Image.open(io.BytesIO(raw_bytes)).convert("L")
#         if img.width > 1200:
#             img = img.resize((1200, int(img.height * 1200 / img.width)), Image.LANCZOS)
#         img = ImageEnhance.Contrast(img).enhance(1.5)
#         img = ImageEnhance.Sharpness(img).enhance(1.4)
#         for quality in [75, 60, 45, 30, 20]:
#             buf = io.BytesIO()
#             img.save(buf, format="JPEG", quality=quality, optimize=True)
#             if len(buf.getvalue()) <= 280*1024 or quality == 20:
#                 return buf.getvalue()
#         return buf.getvalue()
#     except Exception as e:
#         log_failure("Compress Image", str(e))
#         return raw_bytes

# def extract_face_photo(file):
#     try:
#         file.seek(0)
#         img_pil = Image.open(file).convert("RGB")
#         img_np  = np.array(img_pil)
#         img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
#         h, w    = img_bgr.shape[:2]
#         gray    = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

#         cascade_paths = [
#             cv2.data.haarcascades + "haarcascade_frontalface_default.xml",
#             "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml",
#         ]
#         face_cascade = None
#         for cp in cascade_paths:
#             if os.path.exists(cp):
#                 face_cascade = cv2.CascadeClassifier(cp)
#                 break

#         face_rect = None
#         if face_cascade and not face_cascade.empty():
#             faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30,30))
#             if len(faces) > 0:
#                 best, best_score = None, -1
#                 for (fx, fy, fw, fh) in faces:
#                     score = (1 if fx > w*0.4 else 0) + (fw*fh)/(w*h)
#                     if score > best_score:
#                         best_score, best = score, (fx, fy, fw, fh)
#                 face_rect = best

#         if face_rect:
#             fx, fy, fw, fh = face_rect
#             px, py = int(fw*0.2), int(fh*0.2)
#             face_crop = img_pil.crop((max(0,fx-px), max(0,fy-py), min(w,fx+fw+px), min(h,fy+fh+py)))
#         else:
#             face_crop = img_pil.crop((int(w*0.6), int(h*0.1), int(w*0.85), int(h*0.7)))
#             log_failure("Face Detection", "No face found — using ROI fallback")

#         face_crop = face_crop.resize((100, 120), Image.LANCZOS)
#         buf = io.BytesIO()
#         face_crop.save(buf, format="JPEG", quality=85)
#         buf.seek(0)
#         return base64.b64encode(buf.read()).decode("utf-8")
#     except Exception as e:
#         log_failure("Face Extraction", str(e))
#         return None


# # ── OCR ───────────────────────────────────────────────────────────
# def perform_ocr(raw_bytes, language_code, engine_code, is_pdf=False, _retry=True):
#     if not OCR_API_KEY:
#         return {"error": "Missing OCR_API_KEY"}
#     try:
#         if is_pdf:
#             safe_engine = 2 if engine_code == 3 else engine_code
#             send_bytes, filename, mimetype = raw_bytes, "document.pdf", "application/pdf"
#         else:
#             safe_engine = engine_code
#             send_bytes, filename, mimetype = compress_image_bytes(raw_bytes), "image.jpg", "image/jpeg"

#         response = requests.post(OCR_URL, data={
#             "apikey": OCR_API_KEY, "language": language_code,
#             "OCREngine": safe_engine, "isOverlayRequired": False,
#             "detectOrientation": True, "scale": True,
#         }, files={"file": (filename, send_bytes, mimetype)}, timeout=90)
#         response.raise_for_status()
#         result = response.json()

#         if result.get("IsErroredOnProcessing"):
#             err_msgs = result.get("ErrorMessage", ["Unknown OCR error"])
#             err_str = "; ".join(err_msgs) if isinstance(err_msgs, list) else str(err_msgs)
#             if _retry and "timed out" in err_str.lower():
#                 return perform_ocr(raw_bytes, language_code, 1, is_pdf, _retry=False)
#             log_failure("OCR Processing", err_str)
#             return {"error": err_str}
#         return result

#     except requests.Timeout:
#         if _retry:
#             return perform_ocr(raw_bytes, language_code, 1, is_pdf, _retry=False)
#         msg = "OCR timed out. Try Engine 1 or a smaller file."
#         log_failure("OCR Timeout", msg)
#         return {"error": msg}
#     except Exception as e:
#         log_failure("OCR Error", str(e))
#         return {"error": str(e)}


# # ================================================================
# # DOCUMENT PARSING — IMPROVED BASED ON SAMPLE CARDS
# # ================================================================

# def clean_ocr_text(text):
#     """Normalize OCR output: fix common substitutions, whitespace."""
#     text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u200b-\u200f\ufeff]', '', text)
#     text = text.replace('\r\n', '\n').replace('\r', '\n')
#     text = re.sub(r'[ \t]+', ' ', text)
#     # Fix common OCR digit confusions in numbers
#     text = re.sub(r'(?<=\d)[Oo](?=\d)', '0', text)
#     text = re.sub(r'(?<=\d)[Il](?=\d)', '1', text)
#     return text.strip()


# def detect_doc_type(text):
#     """Detect Indian ID document type with weighted scoring."""
#     t = clean_ocr_text(text).lower()

#     aadhaar_signals = [
#         "aadhaar", "aadhar", "uidai", "uid", "unique identification authority",
#         "enrollment no", "enrolment no", "भारत सरकार", "आधार", "मेरा आधार",
#         "government of india", "xxxx xxxx", "virtual id", "vid :"
#     ]
#     pan_signals = [
#         "permanent account number", "income tax department", "income tax",
#         "आयकर विभाग", "govt. of india", "pan", "स्थायी लेखा"
#     ]
#     dl_signals = [
#         "driving licence", "driving license", "dl no", "licence no",
#         "transport department", "vehicle class", "cov", "lmv", "mcwg", "rto",
#         "union of india", "date of issue", "valid till", "son/daughter/wife"
#     ]
#     voter_signals = [
#         "election commission", "voter", "electors photo", "epic",
#         "electoral", "निर्वाचन आयोग", "मतदाता", "part no",
#         "assembly constituency", "elector photo identity card", "kkd", "kk"
#     ]

#     pan_pat     = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text)
#     aadhaar_pat = re.search(r'\b\d{4}[\s\-]\d{4}[\s\-]\d{4}\b|\b\d{12}\b|XXXX\s*XXXX\s*\d{4}', text, re.IGNORECASE)
#     dl_pat      = re.search(r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?\d{4,11}\b', text)
#     epic_pat    = re.search(r'\b[A-Z]{3}\d{7}\b', text)

#     scores = {
#         "aadhaar": sum(2 for s in aadhaar_signals if s in t) + (6 if aadhaar_pat else 0),
#         "pan":     sum(2 for s in pan_signals     if s in t) + (6 if pan_pat     else 0),
#         "dl":      sum(2 for s in dl_signals      if s in t) + (6 if dl_pat      else 0),
#         "voter":   sum(2 for s in voter_signals   if s in t) + (6 if epic_pat    else 0),
#     }
#     best = max(scores, key=scores.get)
#     return best if scores[best] > 0 else "unknown"


# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# # AADHAAR EXTRACTION
# # Fields: Aadhaar Number, VID, Enrolment No, Name, DOB, Gender,
# #         Address, Pincode, State, Mobile (if present)
# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# def extract_aadhaar_fields(text):
#     fields = {}
#     text = clean_ocr_text(text)
#     lines = [l.strip() for l in text.splitlines() if l.strip()]
#     full  = text

#     # ── Aadhaar Number (masked or plain) ──
#     masked_m = re.search(r'\b(XXXX[\s]*XXXX[\s]*\d{4})\b', full, re.IGNORECASE)
#     if masked_m:
#         fields["Aadhaar Number"] = re.sub(r'\s+', ' ', masked_m.group(1).upper()).strip()
#     else:
#         for pat, fmt in [
#             (r'\b(\d{4})\s(\d{4})\s(\d{4})\b',
#              lambda m: f"{m.group(1)} {m.group(2)} {m.group(3)}"),
#             (r'\b(\d{4})-(\d{4})-(\d{4})\b',
#              lambda m: f"{m.group(1)} {m.group(2)} {m.group(3)}"),
#             (r'(?<!\d)(\d{12})(?!\d)',
#              lambda m: f"{m.group(1)[:4]} {m.group(1)[4:8]} {m.group(1)[8:]}"),
#         ]:
#             m = re.search(pat, full)
#             if m:
#                 fields["Aadhaar Number"] = fmt(m)
#                 break

#     # ── VID ──
#     vid_m = re.search(
#         r'(?:vid|virtual\s*id|virtual\s*identification)\s*[:\-]?\s*(\d[\d\s]{14,18})',
#         full, re.IGNORECASE)
#     if not vid_m:
#         # Pattern: "VID : 9134 4266 9355 8010"
#         vid_m = re.search(r'VID\s*[:\-]\s*([\d\s]{16,20})', full, re.IGNORECASE)
#     if vid_m:
#         raw_vid = re.sub(r'\s', '', vid_m.group(1))
#         if len(raw_vid) == 16:
#             fields["VID"] = f"{raw_vid[:4]} {raw_vid[4:8]} {raw_vid[8:12]} {raw_vid[12:]}"
#         else:
#             fields["VID"] = raw_vid

#     # ── Enrolment No ──
#     enrol_m = re.search(
#         r'(?:enrolment|enrollment)\s*(?:no\.?|number)?\s*[:\-]?\s*([\d/\s]{14,25})',
#         full, re.IGNORECASE)
#     if enrol_m:
#         fields["Enrolment No"] = enrol_m.group(1).strip()

#     # ── Name ──
#     # Strategy 1: Line after "To" (postal format on Aadhaar letter)
#     for i, line in enumerate(lines):
#         if line.strip().lower() == 'to' and i + 1 < len(lines):
#             candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
#             words = candidate.split()
#             if 1 <= len(words) <= 5 and all(len(w) >= 2 for w in words):
#                 fields["Name"] = candidate.title()
#             break

#     # Strategy 2: explicit "Name:" label
#     if "Name" not in fields:
#         m = re.search(
#             r'(?:^|\n)\s*(?:name|naam|नाम)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,40})',
#             full, re.IGNORECASE | re.MULTILINE)
#         if m:
#             candidate = re.sub(r'\s+', ' ', m.group(1)).strip().rstrip('.')
#             if len(candidate.split()) >= 1 and len(candidate) >= 4:
#                 fields["Name"] = candidate.title()

#     # Strategy 3: scan lines for likely name (2-5 capitalised words)
#     if "Name" not in fields:
#         skip_words = {
#             'male', 'female', 'dob', 'date', 'birth', 'address', 'government',
#             'india', 'aadhaar', 'aadhar', 'uid', 'enrollment', 'year', 'of',
#             'और', 'भारत', 'unique', 'identification', 'authority', 'enrolment'
#         }
#         for line in lines[1:15]:
#             candidate = re.sub(r'[^A-Za-z\s]', '', line).strip()
#             words = [w for w in candidate.split() if len(w) >= 2]
#             if 2 <= len(words) <= 5 and not {w.lower() for w in words}.intersection(skip_words):
#                 if all(w.isalpha() for w in words):
#                     fields["Name"] = candidate.title()
#                     break

#     # ── Date of Birth ──
#     for pat in [
#         r'(?:dob|date\s*of\s*birth|d\.o\.b|जन्म\s*तिथि)\s*[:\-/]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
#         r'DOB\s*[:/]?\s*(\d{2}/\d{2}/\d{4})',
#         r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b',
#     ]:
#         m = re.search(pat, full, re.IGNORECASE)
#         if m:
#             fields["Date of Birth"] = m.group(1).strip()
#             break

#     # ── Gender ──
#     for token, label in [
#         ('female', 'Female'), ('male', 'Male'), ('transgender', 'Transgender'),
#         ('महिला', 'Female'), ('पुरुष', 'Male'),
#     ]:
#         if re.search(r'\b' + re.escape(token) + r'\b', full, re.IGNORECASE):
#             fields["Gender"] = label
#             break

#     # ── Address — look for S/O, D/O, C/O, W/O or "Address" keyword ──
#     addr_m = re.search(
#         r'(?:s[/\\]o|d[/\\]o|w[/\\]o|c[/\\]o|address|पता)\s*[:\-]?\s*(.+)',
#         full, re.IGNORECASE | re.DOTALL)
#     if addr_m:
#         addr_raw = addr_m.group(1)
#         # Stop at common terminators
#         addr_raw = re.split(
#             r'\b(XXXX|VID\b|\d{4}[\s\-]\d{4}[\s\-]\d{4}|dob\b|male\b|female\b|'
#             r'मेरा\s*आधार|government|aadhaar\s*no)',
#             addr_raw, flags=re.IGNORECASE)[0]
#         addr_clean = re.sub(r'\s+', ' ', addr_raw).strip().rstrip(',').strip()
#         if len(addr_clean) > 8:
#             fields["Address"] = addr_clean[:300]

#     # ── Pincode ──
#     used_digits = fields.get("Aadhaar Number", "").replace(" ", "")
#     for m in re.finditer(r'\b(\d{6})\b', full):
#         pin = m.group(1)
#         if pin in used_digits:
#             continue
#         fields["Pincode"] = pin
#         break

#     # ── State ──
#     state_pat = (
#         r'\b(andhra\s*pradesh|arunachal\s*pradesh|assam|bihar|chhattisgarh|goa|gujarat|'
#         r'haryana|himachal\s*pradesh|jharkhand|karnataka|kerala|madhya\s*pradesh|'
#         r'maharashtra|manipur|meghalaya|mizoram|nagaland|odisha|punjab|rajasthan|'
#         r'sikkim|tamil\s*nadu|telangana|tripura|uttar\s*pradesh|uttarakhand|'
#         r'west\s*bengal|delhi|jammu|ladakh|chandigarh|puducherry)\b'
#     )
#     sm = re.search(state_pat, full, re.IGNORECASE)
#     if sm:
#         fields["State"] = sm.group(1).title()

#     # ── Mobile (10-digit, not the Aadhaar digits) ──
#     aadhaar_digits = fields.get("Aadhaar Number", "").replace(" ", "")
#     for m in re.finditer(r'(?<!\d)([6-9]\d{9})(?!\d)', full):
#         mob = m.group(1)
#         if mob not in aadhaar_digits:
#             fields["Mobile"] = mob
#             break

#     return fields


# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# # PAN CARD EXTRACTION
# # Fields: PAN Number, Name, Father's Name, Date of Birth,
# #         Account Type, Issued By
# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# def extract_pan_fields(text):
#     fields = {}
#     text = clean_ocr_text(text)
#     lines = [l.strip() for l in text.splitlines() if l.strip()]
#     full  = text

#     # ── PAN Number: AAAAA9999A pattern ──
#     m = re.search(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b', full)
#     if m:
#         fields["PAN Number"] = m.group(1)

#     # ── Name: appears after "Name" label line ──
#     # PAN cards print "Name" on one line then the value on the next
#     name_found = False
#     for i, line in enumerate(lines):
#         # Exact label match (e.g. "Name" or "नाम / Name")
#         if re.search(r'(?:^|/)\s*name\s*$', line, re.IGNORECASE) or \
#            re.fullmatch(r'(?:naam|नाम\s*/\s*name)', line.strip(), re.IGNORECASE):
#             if i + 1 < len(lines):
#                 candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
#                 if len(candidate) >= 3:
#                     fields["Name"] = candidate.title()
#                     name_found = True
#             break

#     # Fallback: inline "Name: VALUE"
#     if not name_found:
#         m2 = re.search(r'(?:name|naam)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,50})', full, re.IGNORECASE)
#         if m2:
#             candidate = re.sub(r'\s+', ' ', m2.group(1)).strip().rstrip('.')
#             if len(candidate) >= 3:
#                 fields["Name"] = candidate.title()
#                 name_found = True

#     # Fallback: look for ALL-CAPS name block (PAN often has name in caps)
#     if not name_found:
#         for line in lines:
#             # Pure uppercase line, 2–5 words, all alpha
#             words = line.split()
#             if (2 <= len(words) <= 5
#                     and all(w.isupper() and w.isalpha() and len(w) >= 2 for w in words)
#                     and not any(skip in line.lower() for skip in
#                                 ['income', 'tax', 'govt', 'government', 'permanent',
#                                  'account', 'india', 'department'])):
#                 fields["Name"] = line.title()
#                 name_found = True
#                 break

#     # ── Father's Name: line after "Father's Name" label ──
#     fname_found = False
#     for i, line in enumerate(lines):
#         if re.search(r"father'?s?\s*name", line, re.IGNORECASE) or \
#            re.search(r'पिता\s*का\s*नाम', line):
#             # Check same line first (inline)
#             same_line = re.sub(r"(?:father'?s?\s*name|पिता\s*का\s*नाम)\s*[:\-/]?\s*", '', line, flags=re.IGNORECASE).strip()
#             if len(same_line) >= 3 and re.search(r'[A-Za-z]', same_line):
#                 candidate = re.sub(r'[^A-Za-z\s\.]', '', same_line).strip()
#                 if len(candidate) >= 3:
#                     fields["Father's Name"] = candidate.title()
#                     fname_found = True
#                     break
#             # Next line
#             if not fname_found and i + 1 < len(lines):
#                 candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
#                 if len(candidate) >= 3:
#                     fields["Father's Name"] = candidate.title()
#                     fname_found = True
#             break

#     if not fname_found:
#         m3 = re.search(
#             r"(?:father'?s?\s*(?:name)?|पिता)\s*[:\-/]\s*([A-Za-z][A-Za-z\s\.]{2,50})",
#             full, re.IGNORECASE)
#         if m3:
#             candidate = re.sub(r'\s+', ' ', m3.group(1)).strip().rstrip('.')
#             if len(candidate) >= 3:
#                 fields["Father's Name"] = candidate.title()

#     # ── Date of Birth ──
#     # Strategy 1: line after DOB label
#     for i, line in enumerate(lines):
#         if re.search(r'date\s*of\s*birth|dob|जन्म\s*की\s*तारीख', line, re.IGNORECASE):
#             # Same line
#             m4 = re.search(r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', line)
#             if m4:
#                 fields["Date of Birth"] = m4.group(1).strip()
#                 break
#             # Next line
#             if i + 1 < len(lines):
#                 m4 = re.search(r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', lines[i + 1])
#                 if m4:
#                     fields["Date of Birth"] = m4.group(1).strip()
#             break

#     if "Date of Birth" not in fields:
#         m5 = re.search(r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b', full)
#         if m5:
#             fields["Date of Birth"] = m5.group(1).strip()

#     # ── Account Type ──
#     type_m = re.search(
#         r'\b(individual|company|firm|huf|trust|aop|boi|llp|partnership)\b',
#         full, re.IGNORECASE)
#     if type_m:
#         fields["Account Type"] = type_m.group(1).title()

#     # ── Issued By ──
#     if re.search(r'income\s*tax|आयकर', full, re.IGNORECASE):
#         fields["Issued By"] = "Income Tax Department, Govt. of India"

#     return fields


# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# # DRIVING LICENCE EXTRACTION
# # Fields: DL Number, Date of Issue, Valid Till, Date of Birth,
# #         Blood Group, Name, Son/Daughter/Wife of, Address,
# #         Vehicle Class, Issuing Authority, State
# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# def extract_dl_fields(text):
#     fields = {}
#     text = clean_ocr_text(text)
#     lines = [l.strip() for l in text.splitlines() if l.strip()]
#     full  = text

#     # ── DL Number — many formats: TN07X19990000286, MH-12-2020-1234567 ──
#     dl_patterns = [
#         # State code (2) + 2-digit RTO + year + serial
#         r'\b([A-Z]{2})[\s\-]?(\d{2})[\s\-]?(\d{4})[\s\-]?(\d{7})\b',
#         # Compact 15-digit: TN07X19990000286
#         r'\b([A-Z]{2}\d{2}[A-Z]?\d{10,11})\b',
#         # Generic 2-letter + 13 digits
#         r'\b([A-Z]{2}\d{13})\b',
#     ]
#     for pat in dl_patterns:
#         dl_m = re.search(pat, full)
#         if dl_m:
#             if dl_m.lastindex == 4:
#                 fields["DL Number"] = (
#                     f"{dl_m.group(1)}-{dl_m.group(2)}-{dl_m.group(3)}-{dl_m.group(4)}"
#                 )
#             else:
#                 fields["DL Number"] = dl_m.group(1)
#             break

#     # ── Dates: Issue, Valid Till, DOB (may appear in compact layout) ──
#     # Look for all DD-MM-YYYY dates and assign by context
#     all_dates = re.findall(
#         r'(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{4})', full)
#     # Try contextual patterns first
#     issue_m = re.search(
#         r'(?:date\s*of\s*issue|d\.?\s*o\.?\s*i\.?|issued\s*on)\s*[:\-]?\s*(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{4})',
#         full, re.IGNORECASE)
#     if issue_m:
#         fields["Date of Issue"] = issue_m.group(1)

#     valid_m = re.search(
#         r'(?:valid\s*till|validity|expiry|expires?\s*on|valid\s*upto)\s*[:\-]?\s*(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{4})',
#         full, re.IGNORECASE)
#     if valid_m:
#         fields["Valid Till"] = valid_m.group(1)

#     dob_m = re.search(
#         r'(?:date\s*of\s*birth|d\.?\s*o\.?\s*b\.?|dob)\s*[:\-]?\s*(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{4})',
#         full, re.IGNORECASE)
#     if dob_m:
#         fields["Date of Birth"] = dob_m.group(1)

#     # Fallback: assign by order if context not found (Issue, Valid, DOB = first 3 dates)
#     if all_dates and len(all_dates) >= 2:
#         if "Date of Issue" not in fields and "Valid Till" not in fields:
#             # TN DL layout: Date of Issue | Valid Till appear together
#             block_m = re.search(
#                 r'(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{4})\s+(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{4})',
#                 full)
#             if block_m:
#                 fields["Date of Issue"] = block_m.group(1)
#                 fields["Valid Till"]    = block_m.group(2)
#         if "Date of Birth" not in fields and len(all_dates) >= 3:
#             # 3rd date is usually DOB (after issue + valid)
#             used = {fields.get("Date of Issue",""), fields.get("Valid Till","")}
#             for d in all_dates:
#                 if d not in used:
#                     fields["Date of Birth"] = d
#                     break

#     # ── Blood Group ──
#     bg_m = re.search(r'\b(A|B|AB|O)[\+\-]\b', full)
#     if bg_m:
#         fields["Blood Group"] = bg_m.group(0)
#     else:
#         bg_m2 = re.search(r'blood\s*group\s*[:\-]?\s*([ABO]{1,2}[\+\-]?)', full, re.IGNORECASE)
#         if bg_m2:
#             fields["Blood Group"] = bg_m2.group(1).upper()

#     # ── Name ──
#     name_found = False
#     for i, line in enumerate(lines):
#         if re.search(r'(?:^|\s)(?:name|naam)\s*$', line, re.IGNORECASE):
#             if i + 1 < len(lines):
#                 candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
#                 if len(candidate) >= 3:
#                     fields["Name"] = candidate.title()
#                     name_found = True
#             break
#     if not name_found:
#         m = re.search(
#             r'(?:name|naam)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,45})',
#             full, re.IGNORECASE)
#         if m:
#             candidate = re.sub(r'[^A-Za-z\s\.]', '', m.group(1)).strip()
#             if len(candidate) >= 3:
#                 fields["Name"] = candidate.title()
#                 name_found = True

#     # Scan for name-like ALL CAPS lines (DL often prints name in caps)
#     if not name_found:
#         for line in lines:
#             words = line.strip().split()
#             if (1 <= len(words) <= 4
#                     and all(w.isupper() and w.isalpha() and len(w) >= 2 for w in words)
#                     and not any(skip in line.upper() for skip in [
#                         'DRIVING', 'LICENCE', 'LICENSE', 'UNION', 'INDIA',
#                         'TRANSPORT', 'AUTHORITY', 'VEHICLE', 'CLASS', 'BLOOD',
#                         'VALID', 'ISSUE', 'BIRTH', 'GROUP', 'LMV', 'MCWG', 'COV'])):
#                 fields["Name"] = line.title()
#                 break

#     # ── Son/Daughter/Wife of ──
#     sdw_m = re.search(
#         r'(?:son|daughter|wife)\s*/?\s*(?:daughter\s*/\s*)?(?:son\s*/\s*)?(?:wife\s*of|of)\s*[:\-]?\s*([A-Za-z][A-Za-z\s\.]{2,50})',
#         full, re.IGNORECASE)
#     if sdw_m:
#         candidate = re.sub(r'[^A-Za-z\s\.]', '', sdw_m.group(1)).strip()
#         if len(candidate) >= 3:
#             fields["Son/Daughter/Wife of"] = candidate.title()

#     # ── Vehicle Class / COV ──
#     cov_m = re.search(
#         r'(?:cov|class\s*of\s*vehicle|vehicle\s*class|authorised\s*to\s*drive)\s*[:\-]?\s*([A-Z0-9,/\s\-]{2,40})',
#         full, re.IGNORECASE)
#     if cov_m:
#         vc = cov_m.group(1).strip().rstrip(',').strip()[:60]
#         if vc:
#             fields["Vehicle Class"] = vc

#     # ── Issuing Authority / RTO ──
#     rto_m = re.search(
#         r'(?:licensing\s*authority|issued\s*by|issuing\s*authority|licencing\s*authority|rto)\s*[:\-]?\s*([A-Za-z\s,\.]{4,60})',
#         full, re.IGNORECASE)
#     if rto_m:
#         fields["Issuing Authority"] = rto_m.group(1).strip()

#     # ── Address ──
#     addr_m = re.search(
#         r'(?:address|addr|पता)\s*[:\-]?\s*(.+?)(?:\n\n|\bDL\b|\bLicen|\bValid|\bCOV\b|$)',
#         full, re.IGNORECASE | re.DOTALL)
#     if addr_m:
#         addr_raw = addr_m.group(1)
#         addr_clean = re.sub(r'\s+', ' ', addr_raw).strip().rstrip(',')[:250]
#         if len(addr_clean) > 6:
#             fields["Address"] = addr_clean

#     # ── State (from DL number prefix) ──
#     if "DL Number" in fields:
#         state_code_map = {
#             "AN": "Andaman & Nicobar", "AP": "Andhra Pradesh", "AR": "Arunachal Pradesh",
#             "AS": "Assam", "BR": "Bihar", "CH": "Chandigarh", "CG": "Chhattisgarh",
#             "DN": "Dadra & Nagar Haveli", "DD": "Daman & Diu", "DL": "Delhi",
#             "GA": "Goa", "GJ": "Gujarat", "HR": "Haryana", "HP": "Himachal Pradesh",
#             "JK": "Jammu & Kashmir", "JH": "Jharkhand", "KA": "Karnataka",
#             "KL": "Kerala", "LD": "Lakshadweep", "MP": "Madhya Pradesh",
#             "MH": "Maharashtra", "MN": "Manipur", "ML": "Meghalaya", "MZ": "Mizoram",
#             "NL": "Nagaland", "OD": "Odisha", "OR": "Odisha", "PY": "Puducherry",
#             "PB": "Punjab", "RJ": "Rajasthan", "SK": "Sikkim", "TN": "Tamil Nadu",
#             "TG": "Telangana", "TR": "Tripura", "UP": "Uttar Pradesh",
#             "UK": "Uttarakhand", "WB": "West Bengal",
#         }
#         dl_prefix = fields["DL Number"][:2].upper()
#         if dl_prefix in state_code_map:
#             fields["State"] = state_code_map[dl_prefix]

#     return fields


# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# # VOTER ID EXTRACTION
# # Fields: EPIC Number, Name, Father's Name / Father/Husband Name,
# #         Date of Birth / Age, Gender, Constituency, Part No,
# #         Serial No, Polling Station, State
# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# def extract_voter_fields(text):
#     fields = {}
#     text = clean_ocr_text(text)
#     lines = [l.strip() for l in text.splitlines() if l.strip()]
#     full  = text

#     # ── EPIC Number: 3 letters + 7 digits, e.g. KKD1933993 ──
#     epic_m = re.search(r'\b([A-Z]{2,3}\d{7})\b', full)
#     if epic_m:
#         fields["EPIC Number"] = epic_m.group(1)

#     # ── Name ──
#     name_found = False
#     # Inline label
#     for pat in [
#         r'(?:elector\s*name|name\s*of\s*elector|name|नाम)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,50})',
#         r'Name\s*:\s*([A-Za-z][A-Za-z\s\.]{2,50})',
#     ]:
#         m = re.search(pat, full, re.IGNORECASE)
#         if m:
#             candidate = re.sub(r'[^A-Za-z\s\.]', '', m.group(1)).strip()
#             if len(candidate) >= 4:
#                 fields["Name"] = candidate.title()
#                 name_found = True
#                 break

#     # Line after label "Name:" across two lines
#     if not name_found:
#         for i, line in enumerate(lines):
#             if re.fullmatch(r'(?:name|naam)', line.strip(), re.IGNORECASE):
#                 if i + 1 < len(lines):
#                     candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
#                     if len(candidate) >= 4:
#                         fields["Name"] = candidate.title()
#                         name_found = True
#                 break

#     # ── Father's / Husband's Name ──
#     rel_patterns = [
#         r"(?:father'?s?\s*name|father\s*name|पिता\s*का\s*नाम)\s*[:\-]?\s*([A-Za-z][A-Za-z\s\.]{2,50})",
#         r"(?:husband'?s?\s*name|पति\s*का\s*नाम)\s*[:\-]?\s*([A-Za-z][A-Za-z\s\.]{2,50})",
#         r"Father'?s?\s*Name\s*:\s*([A-Za-z][A-Za-z\s\.]{2,50})",
#     ]
#     for pat in rel_patterns:
#         rel_m = re.search(pat, full, re.IGNORECASE)
#         if rel_m:
#             candidate = re.sub(r'[^A-Za-z\s\.]', '', rel_m.group(1)).strip()
#             if len(candidate) >= 4:
#                 fields["Father's Name"] = candidate.title()
#                 break

#     # Also try two-line format
#     if "Father's Name" not in fields:
#         for i, line in enumerate(lines):
#             if re.search(r"father'?s?\s*name|पिता", line, re.IGNORECASE):
#                 same = re.sub(r"father'?s?\s*name\s*[:\-]?", '', line, flags=re.IGNORECASE).strip()
#                 same = re.sub(r'[^A-Za-z\s\.]', '', same).strip()
#                 if len(same) >= 4:
#                     fields["Father's Name"] = same.title()
#                     break
#                 if i + 1 < len(lines):
#                     nxt = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
#                     if len(nxt) >= 4:
#                         fields["Father's Name"] = nxt.title()
#                 break

#     # ── Date of Birth / Age ──
#     dob_m = re.search(
#         r'(?:date\s*of\s*birth|dob|जन्म\s*तिथि|जन्म\s*दिनांक)\s*[:\-/]?\s*(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})',
#         full, re.IGNORECASE)
#     if dob_m:
#         fields["Date of Birth"] = dob_m.group(1)
#     else:
#         # DOB without label (common in Voter IDs like "11-08-1990")
#         date_m = re.search(r'\b(\d{2}[\-/\.]\d{2}[\-/\.]\d{4})\b', full)
#         if date_m:
#             fields["Date of Birth"] = date_m.group(1)

#     if "Date of Birth" not in fields:
#         age_m = re.search(r'(?:age|आयु)\s*[:\-/]?\s*(\d{2,3})', full, re.IGNORECASE)
#         if age_m:
#             fields["Age"] = age_m.group(1)

#     # ── Gender ──
#     for token, label in [
#         ('female', 'Female'), ('male', 'Male'),
#         ('पुरुष', 'Male'), ('महिला', 'Female'),
#     ]:
#         if re.search(r'\b' + re.escape(token) + r'\b', full, re.IGNORECASE):
#             fields["Gender"] = label
#             break

#     # ── Constituency ──
#     const_m = re.search(
#         r'(?:assembly\s*constituency|parliamentary\s*constituency|विधान\s*सभा)\s*[:\-]?\s*([A-Za-z\s\(\)\d]{3,60})',
#         full, re.IGNORECASE)
#     if const_m:
#         fields["Constituency"] = const_m.group(1).strip().rstrip('.')

#     # ── Part No ──
#     part_m = re.search(r'part\s*(?:no\.?|number|संख्या)?\s*[:\-]?\s*(\d+)', full, re.IGNORECASE)
#     if part_m:
#         fields["Part No"] = part_m.group(1)

#     # ── Serial No ──
#     serial_m = re.search(r'(?:serial|sl\.?|क्रमांक)\s*(?:no\.?|number)?\s*[:\-]?\s*(\d+)', full, re.IGNORECASE)
#     if serial_m:
#         fields["Serial No"] = serial_m.group(1)

#     # ── Polling Station ──
#     poll_m = re.search(
#         r'polling\s*station\s*[:\-]?\s*([A-Za-z0-9\s,\.]{4,80})',
#         full, re.IGNORECASE)
#     if poll_m:
#         fields["Polling Station"] = poll_m.group(1).strip()

#     # ── State (from EPIC prefix heuristic) ──
#     state_pat = (
#         r'\b(andhra\s*pradesh|arunachal\s*pradesh|assam|bihar|chhattisgarh|goa|gujarat|'
#         r'haryana|himachal\s*pradesh|jharkhand|karnataka|kerala|madhya\s*pradesh|'
#         r'maharashtra|manipur|meghalaya|mizoram|nagaland|odisha|punjab|rajasthan|'
#         r'sikkim|tamil\s*nadu|telangana|tripura|uttar\s*pradesh|uttarakhand|'
#         r'west\s*bengal|delhi|jammu|ladakh|chandigarh|puducherry)\b'
#     )
#     sm = re.search(state_pat, full, re.IGNORECASE)
#     if sm:
#         fields["State"] = sm.group(1).title()

#     return fields


# # ── Render helpers ────────────────────────────────────────────────
# def render_kv_table(fields):
#     if not fields:
#         return "<p style='color:#9ca3af;font-style:italic;font-size:0.82rem;'>No fields extracted.</p>"
#     rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in fields.items())
#     return f"""<table class="kv-table">
#         <thead><tr><th>Field</th><th>Value</th></tr></thead>
#         <tbody>{rows}</tbody></table>"""

# def render_confidence_bar(score):
#     pct = min(max(int(score * 100), 0), 100)
#     cls = "conf-high" if pct >= 70 else ("conf-mid" if pct >= 40 else "conf-low")
#     return f"""<div class="conf-wrap">
#         <span class="conf-label">Confidence</span>
#         <div class="conf-bg"><div class="conf-fill {cls}" style="width:{pct}%"></div></div>
#         <span class="conf-pct">{pct}%</span></div>"""

# def photo_html(b64, name="", doc_type=""):
#     if b64:
#         photo_div = f'<div class="photo-frame"><img src="data:image/jpeg;base64,{b64}"/></div>'
#     else:
#         photo_div = '<div class="photo-placeholder">👤<br/>No photo</div>'
#     sub_map = {
#         "aadhaar": "Aadhaar Card Holder · भारत सरकार",
#         "pan":     "PAN Card Holder · Income Tax Dept.",
#         "dl":      "Driving Licence Holder · Transport Dept.",
#         "voter":   "Voter ID Holder · Election Commission",
#     }
#     sub = sub_map.get(doc_type, "")
#     return f"""<div class="photo-card">
#         {photo_div}
#         <div class="photo-meta">
#             <div class="photo-label">ID Card Holder</div>
#             <div class="photo-name">{name or "—"}</div>
#             <div class="photo-sub">{sub}</div>
#         </div></div>"""


# # ── Auth UI ───────────────────────────────────────────────────────
# def render_auth_ui():
#     _, col, _ = st.columns([1, 1.2, 1])
#     with col:
#         st.markdown("""
#         <div style="text-align:center;margin-bottom:28px;margin-top:40px;">
#             <div style="width:52px;height:52px;background:linear-gradient(135deg,#4f46e5,#818cf8);
#                 border-radius:14px;display:inline-flex;align-items:center;justify-content:center;
#                 font-size:1.5rem;margin-bottom:14px;box-shadow:0 4px 16px rgba(99,102,241,0.35);">📝</div>
#             <h1 style="font-size:1.9rem;font-weight:800;color:#1a1a2e;margin:0 0 6px;">OCR Stream</h1>
#             <p style="color:#374151;font-size:0.85rem;margin:0;font-family:'DM Mono',monospace;">
#                 Sign in to extract &amp; store document data</p>
#         </div>
#         """, unsafe_allow_html=True)

#         tab_login, tab_signup = st.tabs(["🔐 Login", "✍ Sign Up"])
#         with tab_login:
#             email = st.text_input("Email", key="login_email", placeholder="you@example.com")
#             password = st.text_input("Password", type="password", key="login_pw", placeholder="••••••••")
#             if st.button("Login", use_container_width=True, key="btn_login"):
#                 ok, err = auth_login(email, password)
#                 if ok:
#                     st.success("Logged in!")
#                     st.rerun()
#                 else:
#                     st.error(f"Login failed: {err}")

#         with tab_signup:
#             email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
#             password = st.text_input("Password (min 6 chars)", type="password", key="signup_pw", placeholder="••••••••")
#             if st.button("Create Account", use_container_width=True, key="btn_signup"):
#                 ok, err = auth_signup(email, password)
#                 if ok:
#                     st.success("Account created! Check your email to confirm, then log in.")
#                 else:
#                     st.error(f"Sign up failed: {err}")


# # ================================================================
# # 6. AUTH GATE
# # ================================================================
# if not st.session_state.user:
#     render_auth_ui()
#     st.stop()

# # ================================================================
# # 7. USER BAR
# # ================================================================
# col_user, col_out = st.columns([6, 1])
# with col_user:
#     login_info = ""
#     if st.session_state.last_login:
#         try:
#             from datetime import timezone
#             import dateutil.parser
#             lt = dateutil.parser.parse(st.session_state.last_login)
#             login_info = f" · Last login: {lt.strftime('%d %b %Y, %I:%M %p')}"
#         except Exception:
#             login_info = ""
#     st.markdown(
#         f"<p style='color:#4b5563;font-size:0.82rem;margin:4px 0;'>"
#         f"🔒 <b style='color:#4f46e5'>{st.session_state.user.email}</b>"
#         f"<span style='color:#9ca3af;font-size:0.76rem;'>{login_info}</span></p>",
#         unsafe_allow_html=True)
# with col_out:
#     if st.button("Logout", key="btn_logout"):
#         auth_logout()
#         st.rerun()

# # ================================================================
# # 8. HEADER
# # ================================================================
# st.markdown("""
# <div class="ocr-header">
#     <div style="width:44px;height:44px;background:linear-gradient(135deg,#4f46e5,#818cf8);
#         border-radius:12px;display:flex;align-items:center;justify-content:center;
#         font-size:1.3rem;box-shadow:0 2px 10px rgba(99,102,241,0.3);flex-shrink:0;">📝</div>
#     <div>
#         <h1>OCR Stream</h1>
#         <p>Extract text from images &amp; PDFs · Blur detection · Document-aware key-value extraction for Indian ID documents (Aadhaar, PAN, DL, Voter ID)</p>
#     </div>
# </div>
# """, unsafe_allow_html=True)

# # ================================================================
# # 9. MODE + SETTINGS
# # ================================================================
# st.markdown('<div class="section-label">Select Mode</div>', unsafe_allow_html=True)
# with st.container(border=True):
#     mode = st.session_state.ocr_mode
#     mode_label = "Text Extraction" if mode == "Normal" else "Document OCR"
#     st.markdown(
#         f"<p style='margin:0 0 10px;color:#334155;font-size:0.82rem;font-weight:600;'>Selected Mode: {mode_label}</p>",
#         unsafe_allow_html=True
#     )
#     col_m1, col_m2 = st.columns(2)
#     with col_m1:
#         if mode == "Normal":
#             st.markdown(
#                 """<div style="background:#0f172a;color:#ffffff;border-radius:10px;padding:10px 12px;
#                 text-align:center;font-weight:700;border:1px solid #020617;">📄 Text Extraction</div>""",
#                 unsafe_allow_html=True,
#             )
#         else:
#             if st.button("📄 Text Extraction", use_container_width=True, key="btn_mode_text"):
#                 st.session_state.ocr_mode = "Normal"
#                 st.session_state.last_result = None
#                 st.rerun()
#     with col_m2:
#         if mode == "Document":
#             st.markdown(
#                 """<div style="background:#0f172a;color:#ffffff;border-radius:10px;padding:10px 12px;
#                 text-align:center;font-weight:700;border:1px solid #020617;">🪪 Document OCR</div>""",
#                 unsafe_allow_html=True,
#             )
#         else:
#             if st.button("🪪 Document OCR", use_container_width=True, key="btn_mode_doc"):
#                 st.session_state.ocr_mode = "Document"
#                 st.session_state.last_result = None
#                 st.rerun()

# mode = st.session_state.ocr_mode
# if mode == "Document":
#     st.markdown("""<div class="info-card accent">
#         <div style="display:flex;align-items:center;gap:10px;">
#             <span class="badge badge-pan">Document OCR</span>
#             <span style="color:#6b7280;font-size:0.82rem;">Aadhaar, PAN, DL &amp; Voter ID key-value extraction with face detection</span>
#         </div></div>""", unsafe_allow_html=True)
# else:
#     st.markdown("""<div class="info-card blue">
#         <div style="display:flex;align-items:center;gap:10px;">
#             <span class="badge badge-normal">Text Extraction</span>
#             <span style="color:#6b7280;font-size:0.82rem;">Plain text extraction for any document or image</span>
#         </div></div>""", unsafe_allow_html=True)

# st.divider()

# st.markdown('<div class="section-label">🌍 Language &nbsp;&nbsp; ⚙ OCR Engine</div>', unsafe_allow_html=True)
# col_l, col_e = st.columns(2)
# languages = {"English":"eng","Spanish":"spa","French":"fre","German":"ger",
#              "Italian":"ita","Chinese (Simplified)":"chs","Chinese (Traditional)":"cht"}
# engine_options = {"Engine 1 (Fast)":1,"Engine 2 (Better)":2,"Engine 3 (Best - Handwriting)":3}
# with col_l:
#     selected_language = st.selectbox("Language", list(languages.keys()), label_visibility="collapsed")
#     language_code = languages[selected_language]
# with col_e:
#     selected_engine = st.selectbox("OCR Engine", list(engine_options.keys()), label_visibility="collapsed")
#     engine_code = engine_options[selected_engine]

# st.divider()

# # ================================================================
# # 10. SPLIT SCREEN — Left: Input  |  Right: Result
# # ================================================================
# MAX_FILE_BYTES = 5 * 1024 * 1024

# col_left, col_right = st.columns([1, 1.4], gap="large")

# # ── LEFT: Input ──────────────────────────────────────────────────
# with col_left:
#     st.markdown('<div class="section-label" style="margin-top:0;">Input Source</div>', unsafe_allow_html=True)

#     input_tab1, input_tab2 = st.tabs(["📂 Upload File", "📷 Camera"])

#     uploaded_file = None
#     _fsize = 0

#     with input_tab1:
#         _uf = st.file_uploader(
#             "Upload image or PDF (max 5 MB)",
#             type=["png","jpg","jpeg","webp","pdf"],
#             label_visibility="collapsed"
#         )
#         if _uf is not None:
#             _uf.seek(0, 2); _sz = _uf.tell(); _uf.seek(0)
#             if _sz > MAX_FILE_BYTES:
#                 st.error(f"❌ File too large ({round(_sz/1024/1024,2)} MB). Max 5 MB.")
#             else:
#                 uploaded_file = _uf
#                 _fsize = _sz
#                 st.session_state.camera_bytes = None
#                 file_type_check = get_file_type(_uf)
#                 if file_type_check.startswith("image"):
#                     _uf.seek(0)
#                     st.image(_uf, use_container_width=True, caption=f"📄 {_uf.name} · {round(_sz/1024,1)} KB")
#                     _uf.seek(0)
#                 else:
#                     st.caption(f"📄 {_uf.name} · {round(_sz/1024,1)} KB")

#     with input_tab2:
#         st.info("📱 Works best on mobile. Point camera at document and capture.", icon="ℹ️")
#         b1, b2 = st.columns(2)
#         with b1:
#             if st.button("📸 Open Camera", use_container_width=True, key="btn_open_camera"):
#                 st.session_state.camera_open = True
#                 st.rerun()
#         with b2:
#             if st.button("✖ Close Camera", use_container_width=True, key="btn_close_camera"):
#                 st.session_state.camera_open = False
#                 st.rerun()

#         camera_image = None
#         if st.session_state.camera_open:
#             st.markdown(
#                 "<p style='margin:8px 0 6px;color:#0f172a;font-weight:700;'>Take Photo</p>",
#                 unsafe_allow_html=True
#             )
#             cam_key = f"camera_input_{st.session_state.camera_widget_nonce}"
#             camera_image = st.camera_input("Take Photo", key=cam_key, label_visibility="visible")
#         else:
#             st.caption("Click `Open Camera` to show the take photo option.")

#         if camera_image is not None:
#             camera_image.seek(0, 2); _csz = camera_image.tell(); camera_image.seek(0)
#             if _csz > MAX_FILE_BYTES:
#                 st.error("❌ Capture too large.")
#             else:
#                 st.session_state.camera_bytes = camera_image.read()
#                 st.session_state.camera_fsize = _csz
#                 st.session_state.camera_open = False

#         if st.session_state.camera_bytes:
#             cam_buf = io.BytesIO(st.session_state.camera_bytes)
#             cam_buf.name = "camera_capture.jpg"
#             cam_buf.type = "image/jpeg"
#             cam_buf.seek(0)
#             if uploaded_file is None:
#                 uploaded_file = cam_buf
#                 _fsize = st.session_state.camera_fsize
#             preview_buf = io.BytesIO(st.session_state.camera_bytes)
#             st.image(preview_buf, use_container_width=True, caption=f"📷 {round(st.session_state.camera_fsize/1024,1)} KB")
#             if st.button("🗑 Clear Photo", key="btn_clear_cam"):
#                 st.session_state.camera_bytes = None
#                 st.session_state.camera_fsize = 0
#                 st.session_state.camera_widget_nonce += 1
#                 st.session_state.camera_open = False
#                 st.rerun()

#     st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
#     extract_clicked = st.button("🚀 Extract Text", use_container_width=True, key="btn_extract")

#     if extract_clicked and uploaded_file:
#         try:
#             uploaded_file.seek(0)
#             raw_bytes = uploaded_file.read()
#         except Exception as e:
#             st.error(f"❌ Could not read file: {e}")
#             raw_bytes = None

#         if raw_bytes:
#             file_type = get_file_type(uploaded_file)
#             file_name = getattr(uploaded_file, "name", "camera_capture.jpg")
#             is_pdf = file_type == "application/pdf" or file_name.lower().endswith(".pdf")

#             if is_pdf and engine_code == 3:
#                 st.warning("⚠️ Engine 3 doesn't support PDFs — using Engine 2.")

#             blur_ok = True
#             if file_type.startswith("image"):
#                 blur_score = detect_blur(io.BytesIO(raw_bytes))
#                 if blur_score < 60:
#                     st.error(f"⚠ Too blurry (score: {round(blur_score,1)}). Retake with better lighting.")
#                     blur_ok = False
#                 elif blur_score < 120:
#                     st.warning(f"Slightly soft (score: {round(blur_score,1)}). Will enhance.")

#             if blur_ok:
#                 photo_b64 = None
#                 if file_type.startswith("image") and mode == "Document":
#                     with st.spinner("📸 Detecting photo..."):
#                         photo_b64 = extract_face_photo(io.BytesIO(raw_bytes))

#                 with st.spinner("🔍 Extracting text..."):
#                     result = perform_ocr(raw_bytes, language_code, engine_code, is_pdf=is_pdf)

#                 st.session_state.camera_bytes = None

#                 if "error" in result:
#                     st.error(f"❌ {result['error']}")
#                 elif result.get("ParsedResults"):
#                     parsed_results = result["ParsedResults"]
#                     processing_time = round(float(result.get("ProcessingTimeInMilliseconds", 0)) / 1000, 3)
#                     combined_text = "\n".join(pr.get("ParsedText", "") for pr in parsed_results)

#                     if mode == "Document":
#                         doc_type = detect_doc_type(combined_text)
#                         if doc_type == "aadhaar":
#                             fields = extract_aadhaar_fields(combined_text)
#                         elif doc_type == "pan":
#                             fields = extract_pan_fields(combined_text)
#                         elif doc_type == "dl":
#                             fields = extract_dl_fields(combined_text)
#                         elif doc_type == "voter":
#                             fields = extract_voter_fields(combined_text)
#                         else:
#                             fields = {}
#                     else:
#                         doc_type = "normal"
#                         fields = {}

#                     st.session_state.last_result = {
#                         "mode":             mode,
#                         "doc_type":         doc_type,
#                         "fields":           fields,
#                         "raw_text":         combined_text,
#                         "photo_b64":        photo_b64,
#                         "processing_time":  processing_time,
#                         "file_name":        file_name,
#                         "file_size_bytes":  len(raw_bytes),
#                         "parsed_results":   parsed_results,
#                     }

#                     if mode == "Document" and fields:
#                         saved, save_err = save_extraction(
#                             doc_type, fields, combined_text, file_name, len(raw_bytes))
#                         st.session_state.last_result["saved"]    = saved
#                         st.session_state.last_result["save_err"] = save_err

#                     st.rerun()
#                 else:
#                     st.error("❌ No text could be extracted.")

#     elif extract_clicked and not uploaded_file:
#         st.warning("⚠️ Please upload a file or take a photo first.")


# # ── RIGHT: Results ───────────────────────────────────────────────
# with col_right:
#     st.markdown('<div class="section-label" style="margin-top:0;">Extracted Result</div>', unsafe_allow_html=True)

#     res = st.session_state.last_result

#     if res is None:
#         st.markdown("""
#         <div class="empty-state">
#             <div class="empty-icon">📄</div>
#             <div class="empty-title">No extraction yet</div>
#             <div class="empty-sub">Upload a file and click Extract Text</div>
#         </div>""", unsafe_allow_html=True)

#     else:
#         if res["mode"] == "Document":
#             doc_type  = res["doc_type"]
#             fields    = res["fields"]
#             photo_b64 = res.get("photo_b64")

#             doc_label = {
#                 "aadhaar": "Aadhaar Card",
#                 "pan":     "PAN Card",
#                 "dl":      "Driving Licence",
#                 "voter":   "Voter ID",
#                 "unknown": "Unknown Document",
#             }.get(doc_type, "Document")
#             badge_cls = {
#                 "aadhaar": "badge-aadhaar",
#                 "pan":     "badge-pan",
#                 "dl":      "badge-dl",
#                 "voter":   "badge-voter",
#                 "unknown": "badge-unknown",
#             }.get(doc_type, "badge-unknown")

#             st.markdown(f"""
#             <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:12px;">
#                 <div style="display:flex;align-items:center;gap:8px;">
#                     <span class="badge {badge_cls}">{doc_label}</span>
#                     <span style="color:#9ca3af;font-size:0.78rem;">Document OCR</span>
#                 </div>
#                 <span style="color:#9ca3af;font-size:0.72rem;font-family:'DM Mono',monospace;">
#                     ⏱ {res['processing_time']}s
#                 </span>
#             </div>""", unsafe_allow_html=True)

#             if doc_type == "unknown":
#                 st.warning("⚠️ Could not detect document type.")

#             holder_name = fields.get("Name", "")
#             st.markdown(photo_html(photo_b64, holder_name, doc_type), unsafe_allow_html=True)
#             if photo_b64:
#                 st.download_button("⬇ Download Photo",
#                     data=base64.b64decode(photo_b64),
#                     file_name=f"{doc_type}_photo.jpg", mime="image/jpeg", key="dl_photo")

#             if fields:
#                 st.markdown('<div class="section-label">Extracted Fields</div>', unsafe_allow_html=True)
#                 st.markdown(f'<div class="info-card">{render_kv_table(fields)}</div>', unsafe_allow_html=True)

#                 # Confidence based on expected field count
#                 expected = {
#                     "aadhaar": 8,   # Number, VID, Enrolment, Name, DOB, Gender, Address, Pincode
#                     "pan":     5,   # PAN No, Name, Father, DOB, Issued By
#                     "dl":      8,   # DL No, Issue, Valid, DOB, Blood, Name, SDW, State
#                     "voter":   7,   # EPIC, Name, Father, DOB, Gender, Constituency, Part No
#                 }.get(doc_type, 4)
#                 conf = min(len(fields) / expected, 1.0)
#                 st.markdown(render_confidence_bar(conf), unsafe_allow_html=True)

#                 saved    = res.get("saved")
#                 save_err = res.get("save_err")
#                 if saved and save_err == "partial":
#                     st.success("✅ Saved to your account (core fields only — run the SQL below to enable all fields).")
#                     with st.expander("📋 Add missing columns to Supabase", expanded=False):
#                         st.code("""
# -- Run this in your Supabase SQL Editor to add the new columns:
# ALTER TABLE extractions
#   ADD COLUMN IF NOT EXISTS enrolment_no       TEXT,
#   ADD COLUMN IF NOT EXISTS date_of_issue      TEXT,
#   ADD COLUMN IF NOT EXISTS son_daughter_wife_of TEXT,
#   ADD COLUMN IF NOT EXISTS serial_no          TEXT,
#   ADD COLUMN IF NOT EXISTS polling_station    TEXT,
#   ADD COLUMN IF NOT EXISTS mobile             TEXT;
# """, language="sql")
#                 elif saved:
#                     st.success("✅ Saved to your account.")
#                 elif save_err == "duplicate":
#                     st.info("ℹ️ Already saved — no duplicate created.")
#                 elif save_err:
#                     st.warning(f"⚠️ Could not save: {save_err}")

#                 json_str = json.dumps(fields, indent=2, ensure_ascii=False)
#                 csv_str  = "\n".join(f"{k},{v}" for k, v in fields.items())
#                 dl1, dl2 = st.columns(2)
#                 with dl1:
#                     st.download_button("⬇ Download JSON", data=json_str,
#                         file_name=f"{doc_type}_fields.json", mime="application/json", key="dl_json")
#                 with dl2:
#                     st.download_button("⬇ Download CSV", data=csv_str,
#                         file_name=f"{doc_type}_fields.csv", mime="text/csv", key="dl_csv")
#             else:
#                 st.warning("No structured fields extracted.")

#             with st.expander("📄 Raw OCR Text"):
#                 for i, pr in enumerate(res["parsed_results"]):
#                     raw = pr.get("ParsedText", "").strip()
#                     st.text_area(f"Page {i+1}" if len(res["parsed_results"]) > 1 else "Raw Text",
#                                  value=raw or "No text found.", height=160, key=f"raw_{i}")
#                     st.download_button(f"⬇ Raw Text", data=raw,
#                         file_name=f"raw_p{i+1}.txt", mime="text/plain", key=f"dl_raw_{i}")

#         else:
#             parsed_results = res["parsed_results"]
#             st.markdown(f"""
#             <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
#                 <span class="badge badge-normal">Text Extraction</span>
#                 <span style="color:#9ca3af;font-size:0.72rem;font-family:'DM Mono',monospace;">
#                     ⏱ {res['processing_time']}s · {len(parsed_results)} page(s)</span>
#             </div>""", unsafe_allow_html=True)

#             if len(parsed_results) > 1:
#                 tabs = st.tabs([f"Page {i+1}" for i in range(len(parsed_results))])
#                 for i, tab in enumerate(tabs):
#                     with tab:
#                         text = parsed_results[i].get("ParsedText", "").strip()
#                         edited = st.text_area("Text", value=text or "No text found.",
#                                               height=300, key=f"norm_text_{i}")
#                         st.download_button("⬇ Download", data=edited,
#                             file_name=f"page_{i+1}.txt", mime="text/plain", key=f"dl_norm_{i}")
#             else:
#                 text = parsed_results[0].get("ParsedText", "").strip()
#                 edited = st.text_area("Extracted Text", value=text or "No text found.", height=300)
#                 st.download_button("⬇ Download Text", data=edited,
#                     file_name="ocr_text.txt", mime="text/plain", key="dl_norm")

#         if st.button("✖ Clear Result", key="btn_clear_result"):
#             st.session_state.last_result = None
#             st.rerun()

# # ================================================================
# # 11. SAVED EXTRACTIONS
# # ================================================================
# st.divider()
# with st.expander("🗂 My Saved Extractions", expanded=False):
#     records = load_extractions()
#     if not records:
#         st.markdown("<p style='color:#9ca3af;font-size:0.85rem;'>No saved extractions yet.</p>", unsafe_allow_html=True)
#     else:
#         st.caption(f"{len(records)} record(s) found")
#         for r in records:
#             ts     = r.get("created_at", "")[:16].replace("T", " ")
#             dtype  = r.get("doc_type", "other")
#             dlabel = {"aadhaar":"Aadhaar","pan":"PAN","dl":"Driving Licence",
#                       "voter":"Voter ID","other":"Other"}.get(dtype, dtype.title())
#             name   = r.get("holder_name") or "—"
#             rid    = r.get("id", "x")

#             if dtype == "aadhaar":
#                 keys = [
#                     ("Name",           "holder_name"),
#                     ("Aadhaar Number", "aadhaar_number"),
#                     ("Date of Birth",  "dob"),
#                     ("Gender",         "gender"),
#                     ("Address",        "address"),
#                     ("Pincode",        "pincode"),
#                     ("State",          "state"),
#                     ("VID",            "vid"),
#                     ("Enrolment No",   "enrolment_no"),
#                     ("Mobile",         "mobile"),
#                 ]
#             elif dtype == "pan":
#                 keys = [
#                     ("Name",           "holder_name"),
#                     ("PAN Number",     "pan_number"),
#                     ("Father's Name",  "father_name"),
#                     ("Date of Birth",  "dob"),
#                     ("Account Type",   "account_type"),
#                     ("Issued By",      "issued_by"),
#                 ]
#             elif dtype == "dl":
#                 keys = [
#                     ("Name",               "holder_name"),
#                     ("DL Number",          "dl_number"),
#                     ("Date of Issue",      "date_of_issue"),
#                     ("Valid Till",         "valid_till"),
#                     ("Date of Birth",      "dob"),
#                     ("Blood Group",        "blood_group"),
#                     ("Vehicle Class",      "vehicle_class"),
#                     ("Son/Daughter/Wife of","son_daughter_wife_of"),
#                     ("Issuing Authority",  "issuing_authority"),
#                     ("State",              "state"),
#                 ]
#             elif dtype == "voter":
#                 keys = [
#                     ("Name",                "holder_name"),
#                     ("EPIC Number",         "epic_number"),
#                     ("Father's Name",       "father_husband_name"),
#                     ("Date of Birth",       "dob"),
#                     ("Gender",              "gender"),
#                     ("Constituency",        "constituency"),
#                     ("Part No",             "part_no"),
#                     ("Serial No",           "serial_no"),
#                     ("Polling Station",     "polling_station"),
#                     ("State",               "state"),
#                 ]
#             else:
#                 keys = [("Raw Text", "raw_text")]

#             display = {label: r[col] for label, col in keys if r.get(col)}

#             with st.expander(f"📄 {dlabel}  ·  {name}  ·  {ts}"):
#                 st.markdown(f'<div class="info-card">{render_kv_table(display)}</div>', unsafe_allow_html=True)
#                 st.download_button("⬇ Download JSON",
#                     data=json.dumps(display, indent=2, ensure_ascii=False),
#                     file_name=f"{dtype}_{rid[:8]}.json", mime="application/json",
#                     key=f"hist_dl_{rid}")

# # ================================================================
# # 12. FAILURE LOG
# # ================================================================
# with st.expander(f"🔴 Failure Log ({len(st.session_state.failure_log)} entries)", expanded=False):
#     if st.session_state.failure_log:
#         col_l, col_r = st.columns([5, 1])
#         with col_r:
#             if st.button("🗑 Clear", key="clear_log"):
#                 st.session_state.failure_log = []
#                 st.rerun()
#         entries_html = "".join(f"""
#         <div class="fail-entry">
#             <span class="fail-ts">[{e['ts']}]</span>
#             <span style="color:#6366f1;font-family:'DM Mono',monospace;">{e['ctx']}</span>
#             <span class="fail-msg">{e['msg']}</span>
#         </div>""" for e in reversed(st.session_state.failure_log))
#         st.markdown(f'<div class="fail-log"><div class="fail-log-title">⚠ System Failure Log</div>{entries_html}</div>',
#                     unsafe_allow_html=True)
#         log_text = "\n".join(f"[{e['ts']}] [{e['ctx']}] {e['msg']}" for e in st.session_state.failure_log)
#         st.download_button("⬇ Download Log", data=log_text,
#             file_name="failure_log.txt", mime="text/plain", key="dl_log")
#     else:
#         st.markdown("<p style='color:#9ca3af;font-size:0.82rem;font-family:monospace;'>No failures recorded.</p>",
#                     unsafe_allow_html=True)

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
st.set_page_config(page_title="OCR Stream", page_icon="📝", layout="wide", initial_sidebar_state="expanded")

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

    .section-label {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #4b5563;
        margin: 14px 0 6px;
    }

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

    .conf-wrap { display:flex; align-items:center; gap:10px; margin:10px 0; }
    .conf-label { font-size:0.72rem; font-family:'DM Mono',monospace; color:#4b5563; min-width:72px; }
    .conf-bg { flex:1; background:#e8eaf0; border-radius:4px; height:6px; overflow:hidden; }
    .conf-fill { height:100%; border-radius:4px; }
    .conf-high { background:#10b981; }
    .conf-mid  { background:#f59e0b; }
    .conf-low  { background:#ef4444; }
    .conf-pct  { font-size:0.72rem; font-family:'DM Mono',monospace; color:#374151; min-width:32px; text-align:right; }

    .empty-state {
        display:flex; flex-direction:column; align-items:center; justify-content:center;
        text-align:center; padding:48px 20px; color:#9ca3af;
    }
    .empty-icon { font-size:2.5rem; opacity:0.35; margin-bottom:12px; }
    .empty-title { font-weight:600; font-size:0.9rem; margin-bottom:4px; }
    .empty-sub { font-size:0.76rem; font-family:'DM Mono',monospace; }

    .fail-log { background:#fff9f9; border:1px solid #fecaca; border-radius:12px; padding:16px; margin-top:12px; }
    .fail-log-title { color:#dc2626; font-weight:700; font-size:0.78rem; letter-spacing:1px; text-transform:uppercase; margin-bottom:10px; }
    .fail-entry { font-family:'DM Mono',monospace; font-size:0.76rem; color:#6b7280; padding:5px 0; border-bottom:1px solid #fee2e2; display:flex; gap:10px; flex-wrap:wrap; }
    .fail-entry:last-child { border-bottom:none; }
    .fail-ts  { color:#9ca3af; flex-shrink:0; }
    .fail-msg { color:#dc2626; }

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

    [data-testid="stCameraInput"] {
        border:2px dashed #c7d2fe !important;
        border-radius:12px !important;
        background:#fafbff !important;
    }

    hr { border-color:#e8eaf0 !important; margin:16px 0 !important; }
    [data-testid="stCaptionContainer"] p { color:#4b5563 !important; font-family:'DM Mono',monospace !important; font-size:0.76rem !important; }
    .stSpinner > div { border-top-color:#6366f1 !important; }

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

        try:
            supabase.rpc("upsert_user_login", {
                "p_user_id": res.user.id,
                "p_email": res.user.email
            }).execute()
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

# Columns that are guaranteed to exist in the original schema
_CORE_COLUMNS = {
    "user_id", "doc_type", "file_name", "file_size_kb",
    "holder_name", "dob", "gender",
    "aadhaar_number", "address", "pincode", "state", "vid",
    "pan_number", "father_name", "account_type", "issued_by",
    "dl_number", "valid_till", "vehicle_class", "blood_group", "issuing_authority",
    "epic_number", "father_husband_name", "constituency", "part_no",
    "raw_text",
}

# Extended columns added in the improved schema — may not exist yet
_EXTENDED_COLUMNS = {
    "enrolment_no", "date_of_issue", "son_daughter_wife_of",
    "serial_no", "polling_station", "mobile",
}

def _build_row(fields, doc_type, file_name, size_kb, raw_text, include_extended=True):
    """Build the insert row dict, optionally excluding extended columns."""
    row = {
        "user_id":             st.session_state.user.id,
        "doc_type":            doc_type if doc_type in ("aadhaar","pan","dl","voter") else "other",
        "file_name":           file_name,
        "file_size_kb":        size_kb,
        # ── Common ──
        "holder_name":         fields.get("Name", ""),
        "dob":                 fields.get("Date of Birth", ""),
        "gender":              fields.get("Gender", ""),
        # ── Aadhaar ──
        "aadhaar_number":      fields.get("Aadhaar Number", ""),
        "address":             fields.get("Address", ""),
        "pincode":             fields.get("Pincode", ""),
        "state":               fields.get("State", ""),
        "vid":                 fields.get("VID", ""),
        # ── PAN ──
        "pan_number":          fields.get("PAN Number", ""),
        "father_name":         fields.get("Father's Name", ""),
        "account_type":        fields.get("Account Type", ""),
        "issued_by":           fields.get("Issued By", ""),
        # ── DL ──
        "dl_number":           fields.get("DL Number", ""),
        "valid_till":          fields.get("Valid Till", ""),
        "vehicle_class":       fields.get("Vehicle Class", ""),
        "blood_group":         fields.get("Blood Group", ""),
        "issuing_authority":   fields.get("Issuing Authority", ""),
        # ── Voter ──
        "epic_number":         fields.get("EPIC Number", ""),
        "father_husband_name": fields.get("Father's Name", "") or fields.get("Father/Husband Name", ""),
        "constituency":        fields.get("Constituency", ""),
        "part_no":             fields.get("Part No", ""),
        # ── Raw ──
        "raw_text":            raw_text[:4000],
    }
    if include_extended:
        row.update({
            "enrolment_no":         fields.get("Enrolment No", ""),
            "date_of_issue":        fields.get("Date of Issue", ""),
            "son_daughter_wife_of": fields.get("Son/Daughter/Wife of", ""),
            "serial_no":            fields.get("Serial No", ""),
            "polling_station":      fields.get("Polling Station", ""),
            "mobile":               fields.get("Mobile", ""),
        })
    # Strip empty strings to keep DB clean (insert NULL instead)
    return {k: v for k, v in row.items() if v != ""}

def _get_doc_unique_key(doc_type, fields):
    """
    Return (column_name, value) for the natural unique identifier of each doc type.
    This is the field we use to detect duplicates before inserting.
    """
    mapping = {
        "aadhaar": ("aadhaar_number", fields.get("Aadhaar Number", "").replace(" ", "")),
        "pan":     ("pan_number",     fields.get("PAN Number", "")),
        "dl":      ("dl_number",      fields.get("DL Number", "").replace(" ", "").replace("-", "")),
        "voter":   ("epic_number",    fields.get("EPIC Number", "")),
    }
    return mapping.get(doc_type, (None, None))


def check_duplicate(doc_type, fields):
    """
    Returns True if this exact document number already exists for this user.
    Falls back to False (allow insert) if the check itself fails.
    """
    col, val = _get_doc_unique_key(doc_type, fields)
    if not col or not val:
        return False   # No unique key available — can't check, allow insert
    try:
        # Normalise stored value too: strip spaces/dashes for comparison
        existing = (
            supabase.table("extractions")
            .select("id")
            .eq("user_id", st.session_state.user.id)
            .eq("doc_type", doc_type)
            .execute()
        )
        if not existing.data:
            return False
        # Compare normalised values
        norm_val = val.replace(" ", "").replace("-", "").upper()
        for row in existing.data:
            stored = str(row.get(col) or "").replace(" ", "").replace("-", "").upper()
            if stored and stored == norm_val:
                return True
        return False
    except Exception:
        return False   # If check fails, let insert proceed (DB constraint is backup)


def save_extraction(doc_type, fields, raw_text="", file_name="", file_size_bytes=0):
    if not st.session_state.user:
        return False, "Not logged in"

    supabase.postgrest.auth(st.session_state.access_token)
    size_kb = round(file_size_bytes / 1024, 1) if file_size_bytes else 0

    # ── Step 1: Pre-check for duplicate by document number ──
    if check_duplicate(doc_type, fields):
        return False, "duplicate"

    # ── Step 2: Attempt insert with all columns (including extended) ──
    try:
        row = _build_row(fields, doc_type, file_name, size_kb, raw_text, include_extended=True)
        supabase.table("extractions").insert(row).execute()
        return True, None
    except Exception as e:
        err = str(e)
        # DB-level duplicate (safety net in case pre-check missed it)
        if "duplicate" in err.lower() or "unique" in err.lower() or "23505" in err:
            return False, "duplicate"
        # Missing column error → fall back to core-only insert
        is_column_error = (
            "PGRST204" in err
            or "column" in err.lower()
            or "schema cache" in err.lower()
        )
        if not is_column_error:
            return False, err

    # ── Step 3: Fallback — core columns only (extended cols not in DB yet) ──
    try:
        row = _build_row(fields, doc_type, file_name, size_kb, raw_text, include_extended=False)
        supabase.table("extractions").insert(row).execute()
        return True, "partial"   # Saved, but missing new columns
    except Exception as e2:
        err2 = str(e2)
        if "duplicate" in err2.lower() or "unique" in err2.lower() or "23505" in err2:
            return False, "duplicate"
        return False, err2

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


# ================================================================
# DOCUMENT PARSING — IMPROVED BASED ON SAMPLE CARDS
# ================================================================

def clean_ocr_text(text):
    """Normalize OCR output: fix common substitutions, whitespace."""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u200b-\u200f\ufeff]', '', text)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'[ \t]+', ' ', text)
    # Fix common OCR digit confusions in numbers
    text = re.sub(r'(?<=\d)[Oo](?=\d)', '0', text)
    text = re.sub(r'(?<=\d)[Il](?=\d)', '1', text)
    return text.strip()


def detect_doc_type(text):
    """Detect Indian ID document type with weighted scoring."""
    t = clean_ocr_text(text).lower()

    aadhaar_signals = [
        "aadhaar", "aadhar", "uidai", "uid", "unique identification authority",
        "enrollment no", "enrolment no", "भारत सरकार", "आधार", "मेरा आधार",
        "government of india", "xxxx xxxx", "virtual id", "vid :"
    ]
    pan_signals = [
        "permanent account number", "income tax department", "income tax",
        "आयकर विभाग", "govt. of india", "pan", "स्थायी लेखा"
    ]
    dl_signals = [
        "driving licence", "driving license", "dl no", "licence no",
        "transport department", "vehicle class", "cov", "lmv", "mcwg", "rto",
        "union of india", "date of issue", "valid till", "son/daughter/wife"
    ]
    voter_signals = [
        "election commission", "voter", "electors photo", "epic",
        "electoral", "निर्वाचन आयोग", "मतदाता", "part no",
        "assembly constituency", "elector photo identity card", "kkd", "kk"
    ]

    pan_pat     = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text)
    aadhaar_pat = re.search(r'\b\d{4}[\s\-]\d{4}[\s\-]\d{4}\b|\b\d{12}\b|XXXX\s*XXXX\s*\d{4}', text, re.IGNORECASE)
    dl_pat      = re.search(r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?\d{4,11}\b', text)
    epic_pat    = re.search(r'\b[A-Z]{3}\d{7}\b', text)

    scores = {
        "aadhaar": sum(2 for s in aadhaar_signals if s in t) + (6 if aadhaar_pat else 0),
        "pan":     sum(2 for s in pan_signals     if s in t) + (6 if pan_pat     else 0),
        "dl":      sum(2 for s in dl_signals      if s in t) + (6 if dl_pat      else 0),
        "voter":   sum(2 for s in voter_signals   if s in t) + (6 if epic_pat    else 0),
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AADHAAR EXTRACTION
# Fields: Aadhaar Number, VID, Enrolment No, Name, DOB, Gender,
#         Address, Pincode, State, Mobile (if present)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def extract_aadhaar_fields(text):
    fields = {}
    text = clean_ocr_text(text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full  = text

    # ── Aadhaar Number (masked or plain) ──
    masked_m = re.search(r'\b(XXXX[\s]*XXXX[\s]*\d{4})\b', full, re.IGNORECASE)
    if masked_m:
        fields["Aadhaar Number"] = re.sub(r'\s+', ' ', masked_m.group(1).upper()).strip()
    else:
        for pat, fmt in [
            (r'\b(\d{4})\s(\d{4})\s(\d{4})\b',
             lambda m: f"{m.group(1)} {m.group(2)} {m.group(3)}"),
            (r'\b(\d{4})-(\d{4})-(\d{4})\b',
             lambda m: f"{m.group(1)} {m.group(2)} {m.group(3)}"),
            (r'(?<!\d)(\d{12})(?!\d)',
             lambda m: f"{m.group(1)[:4]} {m.group(1)[4:8]} {m.group(1)[8:]}"),
        ]:
            m = re.search(pat, full)
            if m:
                fields["Aadhaar Number"] = fmt(m)
                break

    # ── VID ──
    vid_m = re.search(
        r'(?:vid|virtual\s*id|virtual\s*identification)\s*[:\-]?\s*(\d[\d\s]{14,18})',
        full, re.IGNORECASE)
    if not vid_m:
        # Pattern: "VID : 9134 4266 9355 8010"
        vid_m = re.search(r'VID\s*[:\-]\s*([\d\s]{16,20})', full, re.IGNORECASE)
    if vid_m:
        raw_vid = re.sub(r'\s', '', vid_m.group(1))
        if len(raw_vid) == 16:
            fields["VID"] = f"{raw_vid[:4]} {raw_vid[4:8]} {raw_vid[8:12]} {raw_vid[12:]}"
        else:
            fields["VID"] = raw_vid

    # ── Enrolment No ──
    enrol_m = re.search(
        r'(?:enrolment|enrollment)\s*(?:no\.?|number)?\s*[:\-]?\s*([\d/\s]{14,25})',
        full, re.IGNORECASE)
    if enrol_m:
        fields["Enrolment No"] = enrol_m.group(1).strip()

    # ── Name ──
    # Strategy 1: Line after "To" (postal format on Aadhaar letter)
    for i, line in enumerate(lines):
        if line.strip().lower() == 'to' and i + 1 < len(lines):
            candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
            words = candidate.split()
            if 1 <= len(words) <= 5 and all(len(w) >= 2 for w in words):
                fields["Name"] = candidate.title()
            break

    # Strategy 2: explicit "Name:" label
    if "Name" not in fields:
        m = re.search(
            r'(?:^|\n)\s*(?:name|naam|नाम)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,40})',
            full, re.IGNORECASE | re.MULTILINE)
        if m:
            candidate = re.sub(r'\s+', ' ', m.group(1)).strip().rstrip('.')
            if len(candidate.split()) >= 1 and len(candidate) >= 4:
                fields["Name"] = candidate.title()

    # Strategy 3: scan lines for likely name (2-5 capitalised words)
    if "Name" not in fields:
        skip_words = {
            'male', 'female', 'dob', 'date', 'birth', 'address', 'government',
            'india', 'aadhaar', 'aadhar', 'uid', 'enrollment', 'year', 'of',
            'और', 'भारत', 'unique', 'identification', 'authority', 'enrolment'
        }
        for line in lines[1:15]:
            candidate = re.sub(r'[^A-Za-z\s]', '', line).strip()
            words = [w for w in candidate.split() if len(w) >= 2]
            if 2 <= len(words) <= 5 and not {w.lower() for w in words}.intersection(skip_words):
                if all(w.isalpha() for w in words):
                    fields["Name"] = candidate.title()
                    break

    # ── Date of Birth ──
    for pat in [
        r'(?:dob|date\s*of\s*birth|d\.o\.b|जन्म\s*तिथि)\s*[:\-/]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        r'DOB\s*[:/]?\s*(\d{2}/\d{2}/\d{4})',
        r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b',
    ]:
        m = re.search(pat, full, re.IGNORECASE)
        if m:
            fields["Date of Birth"] = m.group(1).strip()
            break

    # ── Gender ──
    for token, label in [
        ('female', 'Female'), ('male', 'Male'), ('transgender', 'Transgender'),
        ('महिला', 'Female'), ('पुरुष', 'Male'),
    ]:
        if re.search(r'\b' + re.escape(token) + r'\b', full, re.IGNORECASE):
            fields["Gender"] = label
            break

    # ── Address — look for S/O, D/O, C/O, W/O or "Address" keyword ──
    addr_m = re.search(
        r'(?:s[/\\]o|d[/\\]o|w[/\\]o|c[/\\]o|address|पता)\s*[:\-]?\s*(.+)',
        full, re.IGNORECASE | re.DOTALL)
    if addr_m:
        addr_raw = addr_m.group(1)
        # Stop at common terminators
        addr_raw = re.split(
            r'\b(XXXX|VID\b|\d{4}[\s\-]\d{4}[\s\-]\d{4}|dob\b|male\b|female\b|'
            r'मेरा\s*आधार|government|aadhaar\s*no)',
            addr_raw, flags=re.IGNORECASE)[0]
        addr_clean = re.sub(r'\s+', ' ', addr_raw).strip().rstrip(',').strip()
        if len(addr_clean) > 8:
            fields["Address"] = addr_clean[:300]

    # ── Pincode ──
    used_digits = fields.get("Aadhaar Number", "").replace(" ", "")
    for m in re.finditer(r'\b(\d{6})\b', full):
        pin = m.group(1)
        if pin in used_digits:
            continue
        fields["Pincode"] = pin
        break

    # ── State ──
    state_pat = (
        r'\b(andhra\s*pradesh|arunachal\s*pradesh|assam|bihar|chhattisgarh|goa|gujarat|'
        r'haryana|himachal\s*pradesh|jharkhand|karnataka|kerala|madhya\s*pradesh|'
        r'maharashtra|manipur|meghalaya|mizoram|nagaland|odisha|punjab|rajasthan|'
        r'sikkim|tamil\s*nadu|telangana|tripura|uttar\s*pradesh|uttarakhand|'
        r'west\s*bengal|delhi|jammu|ladakh|chandigarh|puducherry)\b'
    )
    sm = re.search(state_pat, full, re.IGNORECASE)
    if sm:
        fields["State"] = sm.group(1).title()

    # ── Mobile (10-digit, not the Aadhaar digits) ──
    aadhaar_digits = fields.get("Aadhaar Number", "").replace(" ", "")
    for m in re.finditer(r'(?<!\d)([6-9]\d{9})(?!\d)', full):
        mob = m.group(1)
        if mob not in aadhaar_digits:
            fields["Mobile"] = mob
            break

    return fields


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAN CARD EXTRACTION
# Fields: PAN Number, Name, Father's Name, Date of Birth,
#         Account Type, Issued By
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def extract_pan_fields(text):
    fields = {}
    text = clean_ocr_text(text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full  = text

    # ── PAN Number: AAAAA9999A pattern ──
    m = re.search(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b', full)
    if m:
        fields["PAN Number"] = m.group(1)

    # ── Name: appears after "Name" label line ──
    # PAN cards print "Name" on one line then the value on the next
    name_found = False
    for i, line in enumerate(lines):
        # Exact label match (e.g. "Name" or "नाम / Name")
        if re.search(r'(?:^|/)\s*name\s*$', line, re.IGNORECASE) or \
           re.fullmatch(r'(?:naam|नाम\s*/\s*name)', line.strip(), re.IGNORECASE):
            if i + 1 < len(lines):
                candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
                if len(candidate) >= 3:
                    fields["Name"] = candidate.title()
                    name_found = True
            break

    # Fallback: inline "Name: VALUE"
    if not name_found:
        m2 = re.search(r'(?:name|naam)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,50})', full, re.IGNORECASE)
        if m2:
            candidate = re.sub(r'\s+', ' ', m2.group(1)).strip().rstrip('.')
            if len(candidate) >= 3:
                fields["Name"] = candidate.title()
                name_found = True

    # Fallback: look for ALL-CAPS name block (PAN often has name in caps)
    if not name_found:
        for line in lines:
            # Pure uppercase line, 2–5 words, all alpha
            words = line.split()
            if (2 <= len(words) <= 5
                    and all(w.isupper() and w.isalpha() and len(w) >= 2 for w in words)
                    and not any(skip in line.lower() for skip in
                                ['income', 'tax', 'govt', 'government', 'permanent',
                                 'account', 'india', 'department'])):
                fields["Name"] = line.title()
                name_found = True
                break

    # ── Father's Name: line after "Father's Name" label ──
    fname_found = False
    for i, line in enumerate(lines):
        if re.search(r"father'?s?\s*name", line, re.IGNORECASE) or \
           re.search(r'पिता\s*का\s*नाम', line):
            # Check same line first (inline)
            same_line = re.sub(r"(?:father'?s?\s*name|पिता\s*का\s*नाम)\s*[:\-/]?\s*", '', line, flags=re.IGNORECASE).strip()
            if len(same_line) >= 3 and re.search(r'[A-Za-z]', same_line):
                candidate = re.sub(r'[^A-Za-z\s\.]', '', same_line).strip()
                if len(candidate) >= 3:
                    fields["Father's Name"] = candidate.title()
                    fname_found = True
                    break
            # Next line
            if not fname_found and i + 1 < len(lines):
                candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
                if len(candidate) >= 3:
                    fields["Father's Name"] = candidate.title()
                    fname_found = True
            break

    if not fname_found:
        m3 = re.search(
            r"(?:father'?s?\s*(?:name)?|पिता)\s*[:\-/]\s*([A-Za-z][A-Za-z\s\.]{2,50})",
            full, re.IGNORECASE)
        if m3:
            candidate = re.sub(r'\s+', ' ', m3.group(1)).strip().rstrip('.')
            if len(candidate) >= 3:
                fields["Father's Name"] = candidate.title()

    # ── Date of Birth ──
    # Strategy 1: line after DOB label
    for i, line in enumerate(lines):
        if re.search(r'date\s*of\s*birth|dob|जन्म\s*की\s*तारीख', line, re.IGNORECASE):
            # Same line
            m4 = re.search(r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', line)
            if m4:
                fields["Date of Birth"] = m4.group(1).strip()
                break
            # Next line
            if i + 1 < len(lines):
                m4 = re.search(r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', lines[i + 1])
                if m4:
                    fields["Date of Birth"] = m4.group(1).strip()
            break

    if "Date of Birth" not in fields:
        m5 = re.search(r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b', full)
        if m5:
            fields["Date of Birth"] = m5.group(1).strip()

    # ── Account Type ──
    type_m = re.search(
        r'\b(individual|company|firm|huf|trust|aop|boi|llp|partnership)\b',
        full, re.IGNORECASE)
    if type_m:
        fields["Account Type"] = type_m.group(1).title()

    # ── Issued By ──
    if re.search(r'income\s*tax|आयकर', full, re.IGNORECASE):
        fields["Issued By"] = "Income Tax Department, Govt. of India"

    return fields


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DRIVING LICENCE EXTRACTION
# Fields: DL Number, Date of Issue, Valid Till, Date of Birth,
#         Blood Group, Name, Son/Daughter/Wife of, Address,
#         Vehicle Class, Issuing Authority, State
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def extract_dl_fields(text):
    fields = {}
    text = clean_ocr_text(text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full  = text

    # ── DL Number — many formats: TN07X19990000286, MH-12-2020-1234567 ──
    dl_patterns = [
        # State code (2) + 2-digit RTO + year + serial
        r'\b([A-Z]{2})[\s\-]?(\d{2})[\s\-]?(\d{4})[\s\-]?(\d{7})\b',
        # Compact 15-digit: TN07X19990000286
        r'\b([A-Z]{2}\d{2}[A-Z]?\d{10,11})\b',
        # Generic 2-letter + 13 digits
        r'\b([A-Z]{2}\d{13})\b',
    ]
    for pat in dl_patterns:
        dl_m = re.search(pat, full)
        if dl_m:
            if dl_m.lastindex == 4:
                fields["DL Number"] = (
                    f"{dl_m.group(1)}-{dl_m.group(2)}-{dl_m.group(3)}-{dl_m.group(4)}"
                )
            else:
                fields["DL Number"] = dl_m.group(1)
            break

    # ── Dates: Issue, Valid Till, DOB (may appear in compact layout) ──
    # Look for all DD-MM-YYYY dates and assign by context
    all_dates = re.findall(
        r'(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{4})', full)
    # Try contextual patterns first
    issue_m = re.search(
        r'(?:date\s*of\s*issue|d\.?\s*o\.?\s*i\.?|issued\s*on)\s*[:\-]?\s*(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{4})',
        full, re.IGNORECASE)
    if issue_m:
        fields["Date of Issue"] = issue_m.group(1)

    valid_m = re.search(
        r'(?:valid\s*till|validity|expiry|expires?\s*on|valid\s*upto)\s*[:\-]?\s*(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{4})',
        full, re.IGNORECASE)
    if valid_m:
        fields["Valid Till"] = valid_m.group(1)

    dob_m = re.search(
        r'(?:date\s*of\s*birth|d\.?\s*o\.?\s*b\.?|dob)\s*[:\-]?\s*(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{4})',
        full, re.IGNORECASE)
    if dob_m:
        fields["Date of Birth"] = dob_m.group(1)

    # Fallback: assign by order if context not found (Issue, Valid, DOB = first 3 dates)
    if all_dates and len(all_dates) >= 2:
        if "Date of Issue" not in fields and "Valid Till" not in fields:
            # TN DL layout: Date of Issue | Valid Till appear together
            block_m = re.search(
                r'(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{4})\s+(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{4})',
                full)
            if block_m:
                fields["Date of Issue"] = block_m.group(1)
                fields["Valid Till"]    = block_m.group(2)
        if "Date of Birth" not in fields and len(all_dates) >= 3:
            # 3rd date is usually DOB (after issue + valid)
            used = {fields.get("Date of Issue",""), fields.get("Valid Till","")}
            for d in all_dates:
                if d not in used:
                    fields["Date of Birth"] = d
                    break

    # ── Blood Group ──
    bg_m = re.search(r'\b(A|B|AB|O)[\+\-]\b', full)
    if bg_m:
        fields["Blood Group"] = bg_m.group(0)
    else:
        bg_m2 = re.search(r'blood\s*group\s*[:\-]?\s*([ABO]{1,2}[\+\-]?)', full, re.IGNORECASE)
        if bg_m2:
            fields["Blood Group"] = bg_m2.group(1).upper()

    # ── Name ──
    name_found = False
    for i, line in enumerate(lines):
        if re.search(r'(?:^|\s)(?:name|naam)\s*$', line, re.IGNORECASE):
            if i + 1 < len(lines):
                candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
                if len(candidate) >= 3:
                    fields["Name"] = candidate.title()
                    name_found = True
            break
    if not name_found:
        m = re.search(
            r'(?:name|naam)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,45})',
            full, re.IGNORECASE)
        if m:
            candidate = re.sub(r'[^A-Za-z\s\.]', '', m.group(1)).strip()
            if len(candidate) >= 3:
                fields["Name"] = candidate.title()
                name_found = True

    # Scan for name-like ALL CAPS lines (DL often prints name in caps)
    if not name_found:
        for line in lines:
            words = line.strip().split()
            if (1 <= len(words) <= 4
                    and all(w.isupper() and w.isalpha() and len(w) >= 2 for w in words)
                    and not any(skip in line.upper() for skip in [
                        'DRIVING', 'LICENCE', 'LICENSE', 'UNION', 'INDIA',
                        'TRANSPORT', 'AUTHORITY', 'VEHICLE', 'CLASS', 'BLOOD',
                        'VALID', 'ISSUE', 'BIRTH', 'GROUP', 'LMV', 'MCWG', 'COV'])):
                fields["Name"] = line.title()
                break

    # ── Son/Daughter/Wife of ──
    sdw_m = re.search(
        r'(?:son|daughter|wife)\s*/?\s*(?:daughter\s*/\s*)?(?:son\s*/\s*)?(?:wife\s*of|of)\s*[:\-]?\s*([A-Za-z][A-Za-z\s\.]{2,50})',
        full, re.IGNORECASE)
    if sdw_m:
        candidate = re.sub(r'[^A-Za-z\s\.]', '', sdw_m.group(1)).strip()
        if len(candidate) >= 3:
            fields["Son/Daughter/Wife of"] = candidate.title()

    # ── Vehicle Class / COV ──
    cov_m = re.search(
        r'(?:cov|class\s*of\s*vehicle|vehicle\s*class|authorised\s*to\s*drive)\s*[:\-]?\s*([A-Z0-9,/\s\-]{2,40})',
        full, re.IGNORECASE)
    if cov_m:
        vc = cov_m.group(1).strip().rstrip(',').strip()[:60]
        if vc:
            fields["Vehicle Class"] = vc

    # ── Issuing Authority / RTO ──
    rto_m = re.search(
        r'(?:licensing\s*authority|issued\s*by|issuing\s*authority|licencing\s*authority|rto)\s*[:\-]?\s*([A-Za-z\s,\.]{4,60})',
        full, re.IGNORECASE)
    if rto_m:
        fields["Issuing Authority"] = rto_m.group(1).strip()

    # ── Address ──
    addr_m = re.search(
        r'(?:address|addr|पता)\s*[:\-]?\s*(.+?)(?:\n\n|\bDL\b|\bLicen|\bValid|\bCOV\b|$)',
        full, re.IGNORECASE | re.DOTALL)
    if addr_m:
        addr_raw = addr_m.group(1)
        addr_clean = re.sub(r'\s+', ' ', addr_raw).strip().rstrip(',')[:250]
        if len(addr_clean) > 6:
            fields["Address"] = addr_clean

    # ── State (from DL number prefix) ──
    if "DL Number" in fields:
        state_code_map = {
            "AN": "Andaman & Nicobar", "AP": "Andhra Pradesh", "AR": "Arunachal Pradesh",
            "AS": "Assam", "BR": "Bihar", "CH": "Chandigarh", "CG": "Chhattisgarh",
            "DN": "Dadra & Nagar Haveli", "DD": "Daman & Diu", "DL": "Delhi",
            "GA": "Goa", "GJ": "Gujarat", "HR": "Haryana", "HP": "Himachal Pradesh",
            "JK": "Jammu & Kashmir", "JH": "Jharkhand", "KA": "Karnataka",
            "KL": "Kerala", "LD": "Lakshadweep", "MP": "Madhya Pradesh",
            "MH": "Maharashtra", "MN": "Manipur", "ML": "Meghalaya", "MZ": "Mizoram",
            "NL": "Nagaland", "OD": "Odisha", "OR": "Odisha", "PY": "Puducherry",
            "PB": "Punjab", "RJ": "Rajasthan", "SK": "Sikkim", "TN": "Tamil Nadu",
            "TG": "Telangana", "TR": "Tripura", "UP": "Uttar Pradesh",
            "UK": "Uttarakhand", "WB": "West Bengal",
        }
        dl_prefix = fields["DL Number"][:2].upper()
        if dl_prefix in state_code_map:
            fields["State"] = state_code_map[dl_prefix]

    return fields


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VOTER ID EXTRACTION
# Fields: EPIC Number, Name, Father's Name / Father/Husband Name,
#         Date of Birth / Age, Gender, Constituency, Part No,
#         Serial No, Polling Station, State
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def extract_voter_fields(text):
    fields = {}
    text = clean_ocr_text(text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full  = text

    # ── EPIC Number: 3 letters + 7 digits, e.g. KKD1933993 ──
    epic_m = re.search(r'\b([A-Z]{2,3}\d{7})\b', full)
    if epic_m:
        fields["EPIC Number"] = epic_m.group(1)

    # ── Name ──
    name_found = False
    # Inline label
    for pat in [
        r'(?:elector\s*name|name\s*of\s*elector|name|नाम)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,50})',
        r'Name\s*:\s*([A-Za-z][A-Za-z\s\.]{2,50})',
    ]:
        m = re.search(pat, full, re.IGNORECASE)
        if m:
            candidate = re.sub(r'[^A-Za-z\s\.]', '', m.group(1)).strip()
            if len(candidate) >= 4:
                fields["Name"] = candidate.title()
                name_found = True
                break

    # Line after label "Name:" across two lines
    if not name_found:
        for i, line in enumerate(lines):
            if re.fullmatch(r'(?:name|naam)', line.strip(), re.IGNORECASE):
                if i + 1 < len(lines):
                    candidate = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
                    if len(candidate) >= 4:
                        fields["Name"] = candidate.title()
                        name_found = True
                break

    # ── Father's / Husband's Name ──
    rel_patterns = [
        r"(?:father'?s?\s*name|father\s*name|पिता\s*का\s*नाम)\s*[:\-]?\s*([A-Za-z][A-Za-z\s\.]{2,50})",
        r"(?:husband'?s?\s*name|पति\s*का\s*नाम)\s*[:\-]?\s*([A-Za-z][A-Za-z\s\.]{2,50})",
        r"Father'?s?\s*Name\s*:\s*([A-Za-z][A-Za-z\s\.]{2,50})",
    ]
    for pat in rel_patterns:
        rel_m = re.search(pat, full, re.IGNORECASE)
        if rel_m:
            candidate = re.sub(r'[^A-Za-z\s\.]', '', rel_m.group(1)).strip()
            if len(candidate) >= 4:
                fields["Father's Name"] = candidate.title()
                break

    # Also try two-line format
    if "Father's Name" not in fields:
        for i, line in enumerate(lines):
            if re.search(r"father'?s?\s*name|पिता", line, re.IGNORECASE):
                same = re.sub(r"father'?s?\s*name\s*[:\-]?", '', line, flags=re.IGNORECASE).strip()
                same = re.sub(r'[^A-Za-z\s\.]', '', same).strip()
                if len(same) >= 4:
                    fields["Father's Name"] = same.title()
                    break
                if i + 1 < len(lines):
                    nxt = re.sub(r'[^A-Za-z\s\.]', '', lines[i + 1]).strip()
                    if len(nxt) >= 4:
                        fields["Father's Name"] = nxt.title()
                break

    # ── Date of Birth / Age ──
    dob_m = re.search(
        r'(?:date\s*of\s*birth|dob|जन्म\s*तिथि|जन्म\s*दिनांक)\s*[:\-/]?\s*(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})',
        full, re.IGNORECASE)
    if dob_m:
        fields["Date of Birth"] = dob_m.group(1)
    else:
        # DOB without label (common in Voter IDs like "11-08-1990")
        date_m = re.search(r'\b(\d{2}[\-/\.]\d{2}[\-/\.]\d{4})\b', full)
        if date_m:
            fields["Date of Birth"] = date_m.group(1)

    if "Date of Birth" not in fields:
        age_m = re.search(r'(?:age|आयु)\s*[:\-/]?\s*(\d{2,3})', full, re.IGNORECASE)
        if age_m:
            fields["Age"] = age_m.group(1)

    # ── Gender ──
    for token, label in [
        ('female', 'Female'), ('male', 'Male'),
        ('पुरुष', 'Male'), ('महिला', 'Female'),
    ]:
        if re.search(r'\b' + re.escape(token) + r'\b', full, re.IGNORECASE):
            fields["Gender"] = label
            break

    # ── Constituency ──
    const_m = re.search(
        r'(?:assembly\s*constituency|parliamentary\s*constituency|विधान\s*सभा)\s*[:\-]?\s*([A-Za-z\s\(\)\d]{3,60})',
        full, re.IGNORECASE)
    if const_m:
        fields["Constituency"] = const_m.group(1).strip().rstrip('.')

    # ── Part No ──
    part_m = re.search(r'part\s*(?:no\.?|number|संख्या)?\s*[:\-]?\s*(\d+)', full, re.IGNORECASE)
    if part_m:
        fields["Part No"] = part_m.group(1)

    # ── Serial No ──
    serial_m = re.search(r'(?:serial|sl\.?|क्रमांक)\s*(?:no\.?|number)?\s*[:\-]?\s*(\d+)', full, re.IGNORECASE)
    if serial_m:
        fields["Serial No"] = serial_m.group(1)

    # ── Polling Station ──
    poll_m = re.search(
        r'polling\s*station\s*[:\-]?\s*([A-Za-z0-9\s,\.]{4,80})',
        full, re.IGNORECASE)
    if poll_m:
        fields["Polling Station"] = poll_m.group(1).strip()

    # ── State (from EPIC prefix heuristic) ──
    state_pat = (
        r'\b(andhra\s*pradesh|arunachal\s*pradesh|assam|bihar|chhattisgarh|goa|gujarat|'
        r'haryana|himachal\s*pradesh|jharkhand|karnataka|kerala|madhya\s*pradesh|'
        r'maharashtra|manipur|meghalaya|mizoram|nagaland|odisha|punjab|rajasthan|'
        r'sikkim|tamil\s*nadu|telangana|tripura|uttar\s*pradesh|uttarakhand|'
        r'west\s*bengal|delhi|jammu|ladakh|chandigarh|puducherry)\b'
    )
    sm = re.search(state_pat, full, re.IGNORECASE)
    if sm:
        fields["State"] = sm.group(1).title()

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
# 7. USER BAR — email, last login, + sidebar open button
# ================================================================
login_info = ""
if st.session_state.last_login:
    try:
        import dateutil.parser
        lt = dateutil.parser.parse(st.session_state.last_login)
        login_info = lt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        login_info = ""

st.markdown(
    f"""<div style="display:flex;align-items:center;
        background:#ffffff;border:1px solid #e8eaf0;border-radius:10px;
        padding:8px 16px;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
        <b style="color:#4f46e5;font-size:0.85rem;">{st.session_state.user.email}</b>
    </div>""",
    unsafe_allow_html=True)

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
# 9. MODE + SETTINGS
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

    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
    extract_clicked = st.button("🚀 Extract Text", use_container_width=True, key="btn_extract")

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

            blur_ok = True
            if file_type.startswith("image"):
                blur_score = detect_blur(io.BytesIO(raw_bytes))
                if blur_score < 60:
                    st.error(f"⚠ Too blurry (score: {round(blur_score,1)}). Retake with better lighting.")
                    blur_ok = False
                elif blur_score < 120:
                    st.warning(f"Slightly soft (score: {round(blur_score,1)}). Will enhance.")

            if blur_ok:
                photo_b64 = None
                if file_type.startswith("image") and mode == "Document":
                    with st.spinner("📸 Detecting photo..."):
                        photo_b64 = extract_face_photo(io.BytesIO(raw_bytes))

                with st.spinner("🔍 Extracting text..."):
                    result = perform_ocr(raw_bytes, language_code, engine_code, is_pdf=is_pdf)

                st.session_state.camera_bytes = None

                if "error" in result:
                    st.error(f"❌ {result['error']}")
                elif result.get("ParsedResults"):
                    parsed_results = result["ParsedResults"]
                    processing_time = round(float(result.get("ProcessingTimeInMilliseconds", 0)) / 1000, 3)
                    combined_text = "\n".join(pr.get("ParsedText", "") for pr in parsed_results)

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

                    st.session_state.last_result = {
                        "mode":             mode,
                        "doc_type":         doc_type,
                        "fields":           fields,
                        "raw_text":         combined_text,
                        "photo_b64":        photo_b64,
                        "processing_time":  processing_time,
                        "file_name":        file_name,
                        "file_size_bytes":  len(raw_bytes),
                        "parsed_results":   parsed_results,
                    }

                    if mode == "Document" and fields:
                        saved, save_err = save_extraction(
                            doc_type, fields, combined_text, file_name, len(raw_bytes))
                        st.session_state.last_result["saved"]    = saved
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
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📄</div>
            <div class="empty-title">No extraction yet</div>
            <div class="empty-sub">Upload a file and click Extract Text</div>
        </div>""", unsafe_allow_html=True)

    else:
        if res["mode"] == "Document":
            doc_type  = res["doc_type"]
            fields    = res["fields"]
            photo_b64 = res.get("photo_b64")

            doc_label = {
                "aadhaar": "Aadhaar Card",
                "pan":     "PAN Card",
                "dl":      "Driving Licence",
                "voter":   "Voter ID",
                "unknown": "Unknown Document",
            }.get(doc_type, "Document")
            badge_cls = {
                "aadhaar": "badge-aadhaar",
                "pan":     "badge-pan",
                "dl":      "badge-dl",
                "voter":   "badge-voter",
                "unknown": "badge-unknown",
            }.get(doc_type, "badge-unknown")

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

            holder_name = fields.get("Name", "")
            st.markdown(photo_html(photo_b64, holder_name, doc_type), unsafe_allow_html=True)
            if photo_b64:
                st.download_button("⬇ Download Photo",
                    data=base64.b64decode(photo_b64),
                    file_name=f"{doc_type}_photo.jpg", mime="image/jpeg", key="dl_photo")

            if fields:
                st.markdown('<div class="section-label">Extracted Fields</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-card">{render_kv_table(fields)}</div>', unsafe_allow_html=True)

                # Confidence based on expected field count
                expected = {
                    "aadhaar": 8,   # Number, VID, Enrolment, Name, DOB, Gender, Address, Pincode
                    "pan":     5,   # PAN No, Name, Father, DOB, Issued By
                    "dl":      8,   # DL No, Issue, Valid, DOB, Blood, Name, SDW, State
                    "voter":   7,   # EPIC, Name, Father, DOB, Gender, Constituency, Part No
                }.get(doc_type, 4)
                conf = min(len(fields) / expected, 1.0)
                st.markdown(render_confidence_bar(conf), unsafe_allow_html=True)

                saved    = res.get("saved")
                save_err = res.get("save_err")
                if saved and save_err == "partial":
                    st.success("✅ Saved to your account (core fields only — run the SQL below to enable all fields).")
                    with st.expander("📋 Add missing columns to Supabase", expanded=False):
                        st.code("""
-- Run this in your Supabase SQL Editor to add the new columns:
ALTER TABLE extractions
  ADD COLUMN IF NOT EXISTS enrolment_no       TEXT,
  ADD COLUMN IF NOT EXISTS date_of_issue      TEXT,
  ADD COLUMN IF NOT EXISTS son_daughter_wife_of TEXT,
  ADD COLUMN IF NOT EXISTS serial_no          TEXT,
  ADD COLUMN IF NOT EXISTS polling_station    TEXT,
  ADD COLUMN IF NOT EXISTS mobile             TEXT;
""", language="sql")
                elif saved:
                    st.success("✅ Saved to your account.")
                elif save_err == "duplicate":
                    st.info("ℹ️ Already saved — no duplicate created.")
                elif save_err:
                    st.warning(f"⚠️ Could not save: {save_err}")

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

            with st.expander("📄 Raw OCR Text"):
                for i, pr in enumerate(res["parsed_results"]):
                    raw = pr.get("ParsedText", "").strip()
                    st.text_area(f"Page {i+1}" if len(res["parsed_results"]) > 1 else "Raw Text",
                                 value=raw or "No text found.", height=160, key=f"raw_{i}")
                    st.download_button(f"⬇ Raw Text", data=raw,
                        file_name=f"raw_p{i+1}.txt", mime="text/plain", key=f"dl_raw_{i}")

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
                        text = parsed_results[i].get("ParsedText", "").strip()
                        edited = st.text_area("Text", value=text or "No text found.",
                                              height=300, key=f"norm_text_{i}")
                        st.download_button("⬇ Download", data=edited,
                            file_name=f"page_{i+1}.txt", mime="text/plain", key=f"dl_norm_{i}")
            else:
                text = parsed_results[0].get("ParsedText", "").strip()
                edited = st.text_area("Extracted Text", value=text or "No text found.", height=300)
                st.download_button("⬇ Download Text", data=edited,
                    file_name="ocr_text.txt", mime="text/plain", key="dl_norm")

        if st.button("✖ Clear Result", key="btn_clear_result"):
            st.session_state.last_result = None
            st.rerun()



# ================================================================
# 11. SIDEBAR — Saved Extractions + Failure Log
# ================================================================

# ── Sidebar CSS (native collapse behavior) ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

/* ═══ 1. SIDEBAR PANEL ═══ */
[data-testid="stSidebar"][aria-expanded="true"] {
    background: #ffffff !important;
    border-right: 1px solid #e8eaf0 !important;
    width: 280px !important;
    min-width: 280px !important;
    max-width: 280px !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.06) !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 0 !important;
    width: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
    padding-left: 16px !important;
    padding-right: 16px !important;
}

/* ═══ 2. SIDEBAR INNER ELEMENTS ═══ */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: #f9fafb !important;
    border: 1px solid #e8eaf0 !important;
    border-radius: 10px !important;
    margin-bottom: 6px !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    font-size: 0.77rem !important;
    color: #374151 !important;
    padding: 8px 12px !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
    background: #f0f4ff !important;
    border-radius: 8px !important;
}

/* ═══ 3. SIDEBAR SECTION HEADERS ═══ */
.sb-header {
    font-size: 0.62rem;
    font-weight: 800;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: #6366f1;
    margin: 14px 0 8px;
    padding-bottom: 5px;
    border-bottom: 2px solid #e8eaf0;
}

/* ═══ 4. DOC TYPE BADGES ═══ */
.sb-record-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-right: 4px;
}
.sb-badge-aadhaar { background:#ecfdf5; color:#059669; border:1px solid #a7f3d0; }
.sb-badge-pan     { background:#eff6ff; color:#4f46e5; border:1px solid #c7d2fe; }
.sb-badge-dl      { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
.sb-badge-voter   { background:#faf5ff; color:#7c3aed; border:1px solid #ddd6fe; }
.sb-badge-other   { background:#f3f4f6; color:#6b7280; border:1px solid #e5e7eb; }

/* ═══ 5. KV TABLE IN SIDEBAR ═══ */
.sb-kv { font-family:'DM Mono',monospace; font-size:0.7rem; }
.sb-kv-row {
    display: flex;
    gap: 6px;
    padding: 3px 0;
    border-bottom: 1px solid #f0f1f5;
}
.sb-kv-row:last-child { border-bottom: none; }
.sb-key {
    color: #9ca3af;
    min-width: 82px;
    flex-shrink: 0;
    font-weight: 600;
}
.sb-val { color: #1a1a2e; word-break: break-all; }
.sb-ts {
    font-size: 0.6rem;
    color: #9ca3af;
    font-family: 'DM Mono', monospace;
    margin-bottom: 5px;
    display: block;
}

/* ═══ 6. FAILURE LOG ═══ */
.fail-entry-sb {
    font-family: 'DM Mono', monospace;
    font-size: 0.67rem;
    padding: 5px 0;
    border-bottom: 1px solid #fee2e2;
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.fail-entry-sb:last-child { border-bottom: none; }
.fail-ts-sb  { color: #9ca3af; }
.fail-ctx-sb { color: #6366f1; font-weight: 700; }
.fail-msg-sb { color: #dc2626; }

/* ═══ 7. SIDEBAR BUTTONS ═══ */
/* All sidebar buttons — reset to secondary style */
[data-testid="stSidebar"] .stButton > button {
    background: #f8faff !important;
    color: #4f46e5 !important;
    border: 1px solid #c7d2fe !important;
    box-shadow: none !important;
    font-size: 0.78rem !important;
    padding: 5px 10px !important;
    border-radius: 8px !important;
    transform: none !important;
    transition: background 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #eef2ff !important;
    transform: none !important;
    box-shadow: none !important;
}
/* Logout button — red style */
[data-testid="stSidebar"] [data-testid="sb_logout"] > button,
.logout-btn > button {
    background: #fff1f2 !important;
    color: #dc2626 !important;
    border: 1px solid #fecaca !important;
}
[data-testid="stSidebar"] .logout-btn > button:hover {
    background: #fee2e2 !important;
}

/* ═══ 8. SEARCH INPUT IN SIDEBAR ═══ */
[data-testid="stSidebar"] [data-testid="stTextInputRootElement"] input {
    font-size: 0.78rem !important;
    padding: 6px 10px !important;
    border-radius: 8px !important;
    background: #f5f6fa !important;
    border: 1px solid #e8eaf0 !important;
}
[data-testid="stSidebar"] [data-testid="stTextInputRootElement"] input:focus {
    border-color: #6366f1 !important;
    background: #ffffff !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.12) !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:

    # ── Top: logo + close button ──
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;
        padding:14px 0 8px;border-bottom:1px solid #e8eaf0;margin-bottom:4px;">
        <div style="display:flex;align-items:center;gap:9px;">
            <div style="width:28px;height:28px;
                background:linear-gradient(135deg,#4f46e5,#818cf8);
                border-radius:7px;display:flex;align-items:center;
                justify-content:center;font-size:0.85rem;">📝</div>
            <div>
                <div style="font-weight:800;font-size:0.88rem;
                    color:#1a1a2e;line-height:1.1;">OCR Stream</div>
                <div style="font-size:0.58rem;color:#9ca3af;
                    font-family:'DM Mono',monospace;letter-spacing:0.5px;">
                    Document Extractor</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("⏻  Logout", key="sb_logout", use_container_width=True):
        auth_logout()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════
    # SAVED EXTRACTIONS
    # ════════════════════════════════════════
    st.markdown('<div class="sb-header">🗂 Saved Extractions</div>', unsafe_allow_html=True)

    sb_r1, sb_r2 = st.columns([4, 1])
    with sb_r2:
        if st.button("↺", key="sb_refresh", help="Refresh"):
            st.rerun()

    records = load_extractions()

    if not records:
        st.markdown("""
        <div style="text-align:center;padding:24px 8px 16px;color:#9ca3af;">
            <div style="font-size:1.6rem;opacity:0.3;margin-bottom:6px;">🗃️</div>
            <div style="font-size:0.76rem;font-weight:600;">No extractions yet</div>
            <div style="font-size:0.63rem;font-family:'DM Mono',monospace;margin-top:3px;">
                Extract a document to see it here
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        # Summary badges
        type_counts = {}
        for r in records:
            t = r.get("doc_type", "other")
            type_counts[t] = type_counts.get(t, 0) + 1

        label_map = {
            "aadhaar": "Aadhaar", "pan": "PAN",
            "dl": "DL", "voter": "Voter", "other": "Other"
        }
        badges_html = " ".join(
            f'<span class="sb-record-badge sb-badge-{t}">{label_map.get(t,t)} {c}</span>'
            for t, c in type_counts.items()
        )
        st.markdown(
            f'<div style="margin-bottom:8px;line-height:2.4;">{badges_html}'
            f'<span style="font-size:0.62rem;color:#9ca3af;margin-left:4px;">'
            f'({len(records)} total)</span></div>',
            unsafe_allow_html=True)

        # Search
        search_q = st.text_input(
            "search", placeholder="🔍  Search by name, number…",
            key="sb_search", label_visibility="collapsed")

        for r in records:
            ts     = r.get("created_at", "")[:16].replace("T", " ")
            dtype  = r.get("doc_type", "other")
            dlabel = label_map.get(dtype, dtype.title())
            name   = r.get("holder_name") or "—"
            rid    = r.get("id", "x")

            if dtype == "aadhaar":
                keys = [
                    ("Name",        "holder_name"),
                    ("Aadhaar No",  "aadhaar_number"),
                    ("DOB",         "dob"),
                    ("Gender",      "gender"),
                    ("Address",     "address"),
                    ("Pincode",     "pincode"),
                    ("State",       "state"),
                    ("VID",         "vid"),
                    ("Enrolment",   "enrolment_no"),
                    ("Mobile",      "mobile"),
                ]
            elif dtype == "pan":
                keys = [
                    ("Name",        "holder_name"),
                    ("PAN No",      "pan_number"),
                    ("Father",      "father_name"),
                    ("DOB",         "dob"),
                    ("Acct Type",   "account_type"),
                    ("Issued By",   "issued_by"),
                ]
            elif dtype == "dl":
                keys = [
                    ("Name",        "holder_name"),
                    ("DL No",       "dl_number"),
                    ("Issued",      "date_of_issue"),
                    ("Valid Till",  "valid_till"),
                    ("DOB",         "dob"),
                    ("Blood",       "blood_group"),
                    ("Vehicle",     "vehicle_class"),
                    ("S/D/W of",    "son_daughter_wife_of"),
                    ("Authority",   "issuing_authority"),
                    ("State",       "state"),
                ]
            elif dtype == "voter":
                keys = [
                    ("Name",        "holder_name"),
                    ("EPIC No",     "epic_number"),
                    ("Father/Husb", "father_husband_name"),
                    ("DOB",         "dob"),
                    ("Gender",      "gender"),
                    ("Constitency", "constituency"),
                    ("Part No",     "part_no"),
                    ("Serial No",   "serial_no"),
                    ("State",       "state"),
                ]
            else:
                keys = [("Raw Text", "raw_text")]

            display = {label: r[col] for label, col in keys if r.get(col)}

            if search_q:
                searchable = " ".join(str(v) for v in display.values()).lower()
                if search_q.lower() not in searchable:
                    continue

            doc_num = (
                r.get("aadhaar_number") or r.get("pan_number") or
                r.get("dl_number") or r.get("epic_number") or ""
            )
            short_num = (doc_num[:10] + "…") if len(doc_num) > 10 else doc_num

            with st.expander(f"{dlabel} · {name}", expanded=False):
                st.markdown(
                    f'<span class="sb-ts">{ts}'
                    f'{(" · " + short_num) if short_num else ""}</span>',
                    unsafe_allow_html=True)
                rows_html = "".join(
                    f'<div class="sb-kv-row">'
                    f'<span class="sb-key">{k}</span>'
                    f'<span class="sb-val">{v}</span></div>'
                    for k, v in display.items()
                )
                st.markdown(f'<div class="sb-kv">{rows_html}</div>', unsafe_allow_html=True)
                st.download_button(
                    "⬇ JSON",
                    data=json.dumps(display, indent=2, ensure_ascii=False),
                    file_name=f"{dtype}_{rid[:8]}.json",
                    mime="application/json",
                    key=f"sb_dl_{rid}",
                    use_container_width=True,
                )

    # ════════════════════════════════════════
    # FAILURE LOG
    # ════════════════════════════════════════
    st.markdown('<div class="sb-header">🔴 Failure Log</div>', unsafe_allow_html=True)

    fail_count = len(st.session_state.failure_log)

    if fail_count == 0:
        st.markdown(
            "<p style='color:#9ca3af;font-size:0.73rem;font-family:monospace;"
            "text-align:center;padding:6px 0 0;margin:0;'>No failures ✓</p>",
            unsafe_allow_html=True)
    else:
        fl_c1, fl_c2 = st.columns([3, 1])
        with fl_c1:
            st.markdown(
                f"<p style='color:#dc2626;font-size:0.73rem;font-weight:700;"
                f"margin:4px 0;'>{fail_count} error(s)</p>",
                unsafe_allow_html=True)
        with fl_c2:
            if st.button("🗑", key="sb_clear_log", help="Clear log"):
                st.session_state.failure_log = []
                st.rerun()

        entries_html = "".join(
            f'<div class="fail-entry-sb">'
            f'<span class="fail-ts-sb">[{e["ts"]}] '
            f'<span class="fail-ctx-sb">{e["ctx"]}</span></span>'
            f'<span class="fail-msg-sb">{e["msg"]}</span>'
            f'</div>'
            for e in reversed(st.session_state.failure_log)
        )
        st.markdown(
            f'<div style="background:#fff9f9;border:1px solid #fecaca;'
            f'border-radius:8px;padding:10px 12px;'
            f'max-height:220px;overflow-y:auto;margin-top:6px;">'
            f'{entries_html}</div>',
            unsafe_allow_html=True)

        log_text = "\n".join(
            f"[{e['ts']}] [{e['ctx']}] {e['msg']}"
            for e in st.session_state.failure_log)
        st.download_button(
            "⬇ Download Log", data=log_text,
            file_name="failure_log.txt", mime="text/plain",
            key="sb_dl_log", use_container_width=True)

# Keep Streamlit's default collapsed control visible.
