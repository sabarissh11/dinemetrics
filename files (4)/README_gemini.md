# 🛒 E-Commerce Intelligence Hub (Gemini Edition)

An end-to-end AI-powered analytics platform: **Power BI-style dashboard · Full EDA · Advanced Analytics · Gemini AI Analyst**

---

## 📁 Files in This Package

```
├── app_gemini.py             ← Main Streamlit app (Gemini-powered)
├── requirements_gemini.txt   ← Python dependencies
├── Dockerfile_gemini         ← Docker deployment file
├── env_gemini.example        ← API key template → rename to .env
├── secrets_gemini.toml.example ← Streamlit Cloud secrets template
├── generate_dataset.py       ← Regenerate sample CSV (optional)
└── config.toml               ← Streamlit dark theme
```

---

## 🔑 Step 1 — Get Your FREE Gemini API Key

1. Go to **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (starts with `AIza...`)

> Gemini 1.5 Flash is **free** with generous limits (15 RPM, 1M tokens/day on the free tier).

---

## ⚡ Quick Start — Run Locally

```bash
# 1. Install dependencies
pip install -r requirements_gemini.txt

# 2. Set your API key
cp env_gemini.example .env
# Edit .env → GEMINI_API_KEY=AIza...your-key-here

# 3. Run the app
streamlit run app_gemini.py
```

Open http://localhost:8501 in your browser.

Alternatively, paste your API key directly in the **sidebar** of the running app.

---

## 🌐 Deployment Options

### Option 1 — Streamlit Community Cloud (Free · Recommended)

1. Push your files to a **GitHub repo**
2. Go to https://share.streamlit.io → **New app**
3. Select your repo, set main file: `app_gemini.py`
4. Under **Advanced settings → Secrets**, paste:
   ```toml
   GEMINI_API_KEY = "AIza...your-key-here"
   ```
5. Click **Deploy** — live in ~2 minutes at a public URL

> This is the easiest zero-cost option. Streamlit Community Cloud is free.

---

### Option 2 — Docker (Local or Any Server)

```bash
# Build the image
docker build -f Dockerfile_gemini -t ecom-hub-gemini .

# Run with API key as env var
docker run -p 8501:8501 -e GEMINI_API_KEY=AIza...your-key ecom-hub-gemini

# OR use a .env file
docker run -p 8501:8501 --env-file .env ecom-hub-gemini
```

Open http://localhost:8501

---

### Option 3 — Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile_gemini
    ports:
      - "8501:8501"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    restart: unless-stopped
```

```bash
# Start
GEMINI_API_KEY=AIza...your-key docker-compose up -d

# Or add it to your shell's .env and just run:
docker-compose up -d
```

---

### Option 4 — Railway (Free tier available)

1. Go to https://railway.app and sign in
2. Click **"New Project" → "Deploy from GitHub repo"**
3. Select your repo
4. Under **Variables**, add:
   - `GEMINI_API_KEY` = `AIza...your-key`
   - `PORT` = `8501`
5. Add a **Start Command** in Settings:
   ```
   streamlit run app_gemini.py --server.port=8501 --server.address=0.0.0.0
   ```
6. Deploy — Railway auto-detects Python and installs `requirements_gemini.txt`

---

### Option 5 — Render (Free tier available)

1. Go to https://render.com → **New Web Service**
2. Connect your GitHub repo
3. Set:
   - **Build Command**: `pip install -r requirements_gemini.txt`
   - **Start Command**: `streamlit run app_gemini.py --server.port=10000 --server.address=0.0.0.0`
4. Under **Environment Variables**, add `GEMINI_API_KEY`
5. Deploy

> Render's free tier spins down after inactivity; paid tier keeps it always-on.

---

## 📊 Features

| Tab | What you get |
|-----|-------------|
| **Dashboard** | 8 KPI cards, revenue trend, category/region/channel charts, weekly heatmap, top products |
| **Full EDA** | Dataset overview, stats, univariate/bivariate analysis, correlation heatmap, outlier detection, time series |
| **Advanced Analytics** | Category×Region matrix, RFM segmentation, QoQ growth, discount impact, profitability bubble chart |
| **AI Analyst** | Chat with Gemini about your data — conversation history, quick-question buttons |

---

## 🛠️ Tech Stack

Streamlit · Plotly · Pandas · NumPy · SciPy · **Google Gemini 1.5 Flash** (`google-generativeai`)

---

## 💡 Tips

- The sidebar **API key input** lets you switch keys without restarting the app.
- Upload your own **CSV or Excel** file in the sidebar; the schema is auto-detected.
- Use **Filters** in the sidebar to slice by year, category, region, or channel before asking AI questions.
- The AI Analyst tab maintains full **conversation history** — ask follow-up questions naturally.
