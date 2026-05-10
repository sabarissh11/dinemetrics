# 🛒 E-Commerce Intelligence Hub

An end-to-end AI-powered analytics platform: **Power BI-style dashboard · Full EDA · Advanced Analytics · Claude AI Analyst**

---

## ⚡ Quick Start (Local)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Anthropic API key
cp .env.example .env
# Edit .env → ANTHROPIC_API_KEY=sk-ant-your-key-here

# 3. Run
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🌐 Deployment Options

### Option 1 — Streamlit Community Cloud (Free, Recommended)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Connect your GitHub repo, set main file: `app.py`
4. Under **Advanced settings → Secrets**, add:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
5. Click **Deploy** — live in ~2 minutes

### Option 2 — Docker

```bash
# Build
docker build -t ecom-hub .

# Run (with API key)
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=sk-ant-... ecom-hub

# Or with .env file
docker run -p 8501:8501 --env-file .env ecom-hub
```

Open http://localhost:8501

### Option 3 — Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    restart: unless-stopped
```

```bash
docker-compose up -d
```

### Option 4 — Railway / Render

Both support Docker deployments. Set `ANTHROPIC_API_KEY` as an environment variable in the platform dashboard, then connect your GitHub repo.

---

## 🔑 API Key Setup

The app uses **Anthropic Claude** for the AI Analyst tab.

| Method | How |
|--------|-----|
| `.env` file | `ANTHROPIC_API_KEY=sk-ant-...` |
| Streamlit Cloud | Secrets → `ANTHROPIC_API_KEY = "sk-ant-..."` |
| Docker | `-e ANTHROPIC_API_KEY=sk-ant-...` |
| Sidebar | Paste directly in the app UI |

Get your key at [console.anthropic.com](https://console.anthropic.com).

---

## 📊 Features

| Tab | What you get |
|-----|-------------|
| **Dashboard** | 8 KPI cards, revenue trend, category/region/channel charts, weekly heatmap, top products |
| **Full EDA** | Dataset overview, stats, univariate/bivariate analysis, correlation heatmap, outlier detection, time series |
| **Advanced Analytics** | Category×Region matrix, RFM segmentation, QoQ growth, discount impact, profitability bubble chart |
| **AI Analyst** | Chat with Claude about your data — context-aware, conversation history, quick-question buttons |

---

## 📁 Files

```
ecommerce-hub/
├── app.py                  # Main Streamlit app (all 4 tabs)
├── generate_dataset.py     # Regenerate the sample CSV
├── ecommerce_data.csv      # 5,000-row sample dataset
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker deployment
├── .env.example            # API key template
├── .streamlit/
│   └── config.toml         # Streamlit theme config
└── README.md
```

---

## 🛠️ Tech Stack

Streamlit · Plotly · Pandas · NumPy · SciPy · Anthropic Claude (`claude-sonnet-4-20250514`)
