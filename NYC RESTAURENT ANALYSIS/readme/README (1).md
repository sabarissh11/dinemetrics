# 🍽️ NYC Restaurant Intelligence

> **End-to-end analysis pipeline** — Google Places crawl → Python EDA → Power BI dashboard  
> Data sourced via Apify's Google Places crawler · 1,243 restaurants · 5 NYC boroughs

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Dataset Description](#3-dataset-description)
4. [Feature Engineering](#4-feature-engineering)
5. [Exploratory Data Analysis](#5-exploratory-data-analysis)
6. [Installation & Setup](#6-installation--setup)
7. [Usage](#7-usage)
8. [Power BI Dashboard](#8-power-bi-dashboard)
9. [Key Findings](#9-key-findings)
10. [Roadmap](#10-roadmap)
11. [Contributing](#11-contributing)
12. [License](#12-license)

---

## 1. Project Overview

This project crawls NYC restaurant listings from **Google Places** using the [Apify Google Places Scraper](https://apify.com/compass/crawler-google-places), performs a structured **Exploratory Data Analysis (EDA)** in Python, and visualises insights via an interactive **Power BI dashboard**.

### Goals

| Goal | Detail |
|---|---|
| Cuisine landscape | Which food categories dominate each borough? |
| Rating distribution | How are scores distributed across NYC? |
| Hidden gems | High-rated restaurants with low review counts (undiscovered) |
| Overrated detection | High-traffic restaurants with below-average scores |
| Composite scoring | Weighted rank combining rating × log(reviews) |
| Borough comparison | Side-by-side borough performance |

---

## 2. Repository Structure

```
nyc-restaurant-intelligence/
│
├── data/
│   ├── raw/                          # Raw Apify export (gitignored)
│   │   └── dataset_crawler-google-places_*.csv
│   ├── processed/                    # Cleaned output (gitignored)
│   │   └── nyc_restaurants_clean.csv
│   └── samples/                      # Tiny fixture for tests
│       └── sample_10.csv
│
├── notebooks/
│   └── NYC_RESTAURANT_ANALYSIS_GENIO_AI.ipynb   # Main EDA notebook
│
├── powerbi/
│   └── NYC_Restaurant_Dashboard.pbix            # Power BI file (gitignored by default)
│
├── reports/
│   └── figures/                      # Exported charts (gitignored)
│
├── assets/
│   └── images/                       # README / docs images (tracked)
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 3. Dataset Description

### Source
- **Crawler**: [Apify — Google Places Scraper](https://apify.com/compass/crawler-google-places)
- **Date scraped**: 2026-05-06
- **Geography**: New York City (Bronx, Brooklyn, Manhattan, Queens, Staten Island)
- **Records**: ~1,243 restaurants after cleaning

### Raw Schema

| Column | Type | Description |
|---|---|---|
| `title` | string | Restaurant name |
| `totalScore` | float | Google star rating (1.0 – 5.0) |
| `reviewsCount` | int | Total Google review count |
| `street` | string | Street address |
| `city` | string | Borough / city |
| `state` | string | State (New York) |
| `countryCode` | string | ISO country code (US) |
| `website` | string | Restaurant website URL |
| `phone` | string | Contact phone number |
| `categories/0`…`categories/10` | string | All Google category tags |
| `categoryName` | string | Primary category (e.g., "Italian restaurant") |
| `url` | string | Google Maps URL |

### Cleaned / Engineered Schema (added columns)

| Column | Type | Description |
|---|---|---|
| `log_reviews` | float | `log1p(reviewsCount)` — reduces skew |
| `composite` | float | `totalScore × log_reviews` — weighted quality rank |
| `tier` | category | Review-count bucket: Micro / Small / Popular / Viral |
| `score_band` | category | Rating bucket: <3.0 / 3.0–3.5 / 3.5–4.0 / 4.0–4.5 / 4.5–5.0 |

---

## 4. Feature Engineering

All transformations live in **`notebooks/NYC_RESTAURANT_ANALYSIS_GENIO_AI.ipynb`**.

### Composite Score
```python
df["log_reviews"] = np.log1p(df["reviewsCount"])
df["composite"]   = (df["totalScore"] * df["log_reviews"]).round(3)
```
Addresses the problem where a 5.0-star restaurant with 2 reviews ranks above a 4.7-star with 5,000 reviews.

### Review Tier
```python
df["tier"] = pd.cut(
    df["reviewsCount"],
    bins=[0, 100, 500, 2000, 1e9],
    labels=["Micro", "Small", "Popular", "Viral"]
)
```

| Tier | Review Range | Count |
|---|---|---|
| Micro | 0 – 100 | 194 |
| Small | 101 – 500 | 520 |
| Popular | 501 – 2,000 | 423 |
| Viral | 2,001+ | 106 |

### Score Band
```python
df["score_band"] = pd.cut(
    df["totalScore"],
    bins=[0, 3.0, 3.5, 4.0, 4.5, 5.01],
    labels=["<3.0", "3.0–3.5", "3.5–4.0", "4.0–4.5", "4.5–5.0"]
)
```

---

## 5. Exploratory Data Analysis

The notebook covers:

- **Null audit** — rows dropped for missing `totalScore`, `reviewsCount`, `city`, `categoryName`
- **Summary statistics** — total restaurants, total reviews, unique cuisines, borough count
- **Top 15 cuisines** by count, avg score, avg reviews
- **Borough breakdown** — count, avg score, total reviews per borough
- **Correlation matrix** — `totalScore` vs `reviewsCount`, `log_reviews`, `composite`
- **Hidden gems** — `totalScore ≥ 4.8` AND `reviewsCount < 300`
- **Overrated** — `reviewsCount > 1,000` AND `totalScore < 4.0`

---

## 6. Installation & Setup

### Prerequisites

- Python 3.9+
- pip or conda
- Jupyter Lab / Notebook
- Power BI Desktop (Windows) — for the dashboard

### Clone & Install

```bash
git clone https://github.com/<your-username>/nyc-restaurant-intelligence.git
cd nyc-restaurant-intelligence

# Create virtual environment
python -m venv .venv
source .venv/bin/activate       # macOS / Linux
.venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt
```

### requirements.txt

```
pandas>=2.0
numpy>=1.24
seaborn>=0.13
matplotlib>=3.7
jupyter>=1.0
openpyxl>=3.1        # Power BI Excel export compatibility
```

---

## 7. Usage

### Step 1 — Place the raw CSV

Put your Apify export in `data/raw/`:

```
data/raw/dataset_crawler-google-places_<timestamp>.csv
```

Update the path in the first notebook cell:

```python
df_raw = pd.read_csv('data/raw/dataset_crawler-google-places_<timestamp>.csv')
```

### Step 2 — Run the notebook

```bash
jupyter lab notebooks/NYC_RESTAURANT_ANALYSIS_GENIO_AI.ipynb
```

Run all cells. The cleaned CSV is exported to `data/processed/nyc_restaurants_clean.csv`.

### Step 3 — Open the Power BI dashboard

1. Open `powerbi/NYC_Restaurant_Dashboard.pbix` in Power BI Desktop.
2. Go to **Home → Transform Data → Data Source Settings**.
3. Update the path to `data/processed/nyc_restaurants_clean.csv`.
4. Click **Refresh**.

---

## 8. Power BI Dashboard

### Recommended Dashboard Design

Below is the suggested **3-page Power BI report** structure for this dataset.

---

#### Page 1 — 🗺️ City Overview

| Visual | Type | Fields |
|---|---|---|
| KPI cards | Card | Total restaurants · Avg rating · Total reviews · Unique cuisines |
| Restaurants by borough | Bar chart | `city` (axis) · Count (value) |
| Rating distribution | Histogram / Column | `score_band` |
| Review tier breakdown | Donut chart | `tier` |
| Avg composite score by borough | Clustered bar | `city` · avg(`composite`) |

**Slicers**: `city`, `score_band`, `tier`

---

#### Page 2 — 🍜 Cuisine Deep Dive

| Visual | Type | Fields |
|---|---|---|
| Top 20 cuisines by count | Horizontal bar | `categoryName` · Count |
| Cuisine vs avg rating | Scatter plot | `categoryName` · avg(`totalScore`) · sum(`reviewsCount`) |
| Cuisine heat map by borough | Matrix | `city` (rows) · `categoryName` (cols) · Count (values) |
| Top 10 by composite score | Table | `title`, `categoryName`, `city`, `composite`, `totalScore`, `reviewsCount` |

**Slicers**: `categoryName`, `city`, `tier`

---

#### Page 3 — 💎 Hidden Gems & Overrated

| Visual | Type | Fields |
|---|---|---|
| Hidden gems table | Table (conditional fmt) | `title`, `city`, `categoryName`, `totalScore`, `reviewsCount` filtered to score ≥ 4.8 & reviews < 300 |
| Overrated table | Table (conditional fmt) | `title`, `city`, `totalScore`, `reviewsCount` filtered to reviews > 1,000 & score < 4.0 |
| Rating vs log(reviews) scatter | Scatter | `log_reviews` (x) · `totalScore` (y) · `tier` (legend) · `title` (tooltip) |
| Borough filter for gems | Slicer | `city` |

---

### DAX Measures to Add

```dax
-- Composite Score (average)
Avg Composite = AVERAGE(nyc_restaurants_clean[composite])

-- Total Reviews
Total Reviews = SUM(nyc_restaurants_clean[reviewsCount])

-- Hidden Gems Count
Hidden Gems =
CALCULATE(
    COUNTROWS(nyc_restaurants_clean),
    nyc_restaurants_clean[totalScore] >= 4.8,
    nyc_restaurants_clean[reviewsCount] < 300
)

-- Overrated Count
Overrated =
CALCULATE(
    COUNTROWS(nyc_restaurants_clean),
    nyc_restaurants_clean[reviewsCount] > 1000,
    nyc_restaurants_clean[totalScore] < 4.0
)

-- % with Rating ≥ 4.5
Pct High Rated =
DIVIDE(
    CALCULATE(COUNTROWS(nyc_restaurants_clean), nyc_restaurants_clean[totalScore] >= 4.5),
    COUNTROWS(nyc_restaurants_clean)
)
```

---

### Recommended Theme

Use Power BI's **"City Park"** or **"Executive"** built-in theme, or apply a custom JSON theme with NYC-inspired colours:

```json
{
  "name": "NYC Restaurant",
  "dataColors": ["#E63946","#457B9D","#1D3557","#F4A261","#2A9D8F","#E9C46A","#264653"],
  "background": "#FFFFFF",
  "foreground": "#1D3557",
  "tableAccent": "#E63946"
}
```

---

## 9. Key Findings

> *(Placeholder — fill in after running the notebook on your dataset)*

- 🏆 **Top borough by avg rating**: TBD
- 🍕 **Most common cuisine**: Restaurant (generic) → 144, followed by Mexican (103) and Italian (100)
- 💎 **Hidden gems discovered**: TBD restaurants with score ≥ 4.8 and < 300 reviews
- ⚠️ **Overrated count**: TBD high-traffic restaurants scoring below 4.0
- 📊 **Score concentration**: 53% of all restaurants fall in the 4.0–4.5 band

---

## 10. Roadmap

- [ ] Add latitude/longitude geocoding for a map visual in Power BI
- [ ] Sentiment analysis on scraped reviews (Phase 2)
- [ ] Automate Apify crawl via GitHub Actions on a weekly schedule
- [ ] Publish Power BI report to Power BI Service (web embed)
- [ ] Add competitor city comparison (LA, Chicago, Miami)

---

## 11. Contributing

Pull requests are welcome. For major changes, please open an issue first.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/add-geocoding`)
3. Commit your changes (`git commit -m 'feat: add lat/lon geocoding step'`)
4. Push to the branch (`git push origin feature/add-geocoding`)
5. Open a Pull Request

---

## 12. License

This project is licensed under the **MIT License**.  
Data sourced from Google Places via Apify — subject to [Google's Terms of Service](https://developers.google.com/maps/terms-20180207).

---

*Built with ❤️ · Genio AI · 2026*
