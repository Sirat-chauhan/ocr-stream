
# 📄 OCR Document Extraction App

A secure document OCR web application built with Streamlit that extracts text from uploaded documents and stores structured results in Supabase with user-level data isolation.

---

## 🚀 Features

* 📤 Upload document images (Aadhaar, PAN, Custom)
* 🔍 Extract text using OCR API
* 🗄 Store structured data in Supabase
* 🖼 Store images in Supabase Storage (private bucket)
* 🔐 Row-Level Security (RLS) enabled
* 👤 User-based data separation
* ☁️ Deployable on Streamlit Cloud

---

## 🛠 Tech Stack

* Python
* Streamlit
* OCR.space API
* Supabase (Database + Storage + Auth)
* PostgreSQL (via Supabase)
* python-dotenv

---

# 🗄 Database Architecture

## ✅ Table: `documents`

Single scalable table for all document types.

```sql
create table documents (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade not null,
  doc_type text not null, -- aadhaar, pan, other
  image_url text not null,
  extracted_data jsonb not null,
  raw_text text,
  created_at timestamptz default now()
);
```

---

## 🔐 Row Level Security (RLS)

Users can only access their own documents.

```sql
alter table documents enable row level security;

create policy "Users can access only their documents"
on documents
for all
using (auth.uid() = user_id);
```

---

# 🖼 Image Storage

* Create a **private bucket** in Supabase Storage
* Upload document images there
* Store only the `image_url` inside the database

⚠️ Do NOT store base64 images inside the database.

---

# 📦 Example Stored Data

## Aadhaar Example (JSONB)

```json
{
  "name": "Rahul Kumar",
  "aadhaar_number": "1234 5678 9012",
  "dob": "01/01/1995"
}
```

## PAN Example (JSONB)

```json
{
  "name": "Rahul Kumar",
  "pan_number": "ABCDE1234F",
  "father_name": "Ramesh Kumar"
}
```

Using `jsonb` makes the system:

* Flexible
* Scalable
* Clean
* Easy to extend for new document types

---

# 🔑 Environment Variables

Create a `.env` file:

```
OCR_API_KEY=your_ocr_api_key
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key
```

⚠️ Never commit `.env` to GitHub
⚠️ Add `.env` to `.gitignore`

---

# ▶️ Run Locally

### 1️⃣ Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run App

```bash
streamlit run app.py
```

App runs at:

```
http://localhost:8501
```

---

# ☁️ Deploy on Streamlit Cloud

1. Push code to GitHub
2. Connect repo to Streamlit Cloud
3. Add secrets in App Settings → Secrets

Example:

```
OCR_API_KEY = "your_key"
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_SERVICE_KEY = "your_key"
```

---

# 🔐 Security Best Practices

* Enable Row Level Security
* Use private storage buckets
* Never expose Service Role Key publicly
* Use Auth for user-based access
* Validate file type and size before upload

---

# 📌 Future Improvements

* Add full Supabase Authentication login
* Add dashboard to view user uploads
* Add document history page
* Add download structured data feature
* Add admin panel
