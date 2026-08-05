# 🍳 COOKup Analytics — Home-Cooked Food Price Tracker

> **Artisanal Food Telemetry, Home Cook Analytics & Dish Price History Platform for Cookups Bangladesh.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-0099ff?style=for-the-badge&logo=github)](https://ranehal.github.io/COOKup-analytics/)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite3](https://img.shields.io/badge/Database-SQLite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## 📌 Executive Summary

**COOKup Analytics** is an interactive telemetry and price analytics platform built for [Cookups](https://cookups.com.bd), Bangladesh's premier marketplace for home-cooked meals and artisanal dishes.

The system ingests dish catalogs, tracks pricing fluctuations across home cooks, calculates price drop trends, and provides interactive modal analytics. Built on a hybrid architecture, COOKup Analytics operates seamlessly via a local Python REST API server or statically through pre-baked JSON datasets deployed to GitHub Pages.

---

## 🚀 Key Features

- **👨‍🍳 Cook & Dish Telemetry**: Track active home cooks, dish availability, category distribution, and average dish pricing metrics.
- **📉 Dynamic Price Drop Tracker**: Dedicated filter highlighting active price reductions across home-cooked meals.
- **📊 Interactive Chart.js Modals**: Detailed price history charts displaying price trends over time per dish.
- **⚡ Hybrid Architecture**: Runs as a dynamic HTTP REST API service ([`server.py`](file:///C:/PROJECTS/COOKup/server.py)) or as a static site backed by exported JSON datasets ([`export_static_data.py`](file:///C:/PROJECTS/COOKup/export_static_data.py)).
- **💾 Relational SQLite Database**: Structured storage (`cookups.db`) maintaining dishes, categories, cooks, and daily price logs.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Data_Collection ["⚡ Ingestion Pipeline"]
        Scraper[scraper.py] -->|Crawl Cookups API| CookupsAPI[Cookups Platform]
        CookupsAPI -->|Parse Dishes & Cooks| DB[(SQLite: cookups.db)]
    end

    subgraph Data_Export ["💾 Static Dataset Generation"]
        DB -->|export_static_data.py| StaticFiles[data/*.json]
        StaticFiles --> Stats[stats.json]
        StaticFiles --> Dishes[dishes.json]
        StaticFiles --> History[history.json]
    end

    subgraph Deployment_Modes ["🌐 Execution Modes"]
        DB -->|server.py REST API| LocalUI[Local Web App :8080]
        StaticFiles -->|GitHub Actions| GHPages[GitHub Pages Deployment]
    end
```

---

## 📁 Repository Structure

```
COOKup/
├── scraper.py              # API crawler and SQLite database populator
├── server.py               # Python HTTP server & REST API handler (:8080)
├── export_static_data.py   # Exporter script generating static JSON datasets
├── cookups.db              # SQLite database (dishes, cooks, categories, price history)
├── app.js                  # Frontend interactive SPA (dual REST API / static fallback)
├── index.html              # Responsive dashboard markup
├── style.css               # Modern dashboard layout styling
├── data/                   # Pre-baked static JSON files for GitHub Pages
│   ├── stats.json          # Overall platform statistics summary
│   ├── categories.json     # Category breakdown map
│   ├── dishes.json         # Dish records lookup
│   └── history.json        # Historical price change logs
└── .github/workflows/
    └── deploy.yml          # GitHub Pages automated deployment workflow
```

---

## 🛠️ Usage & Local Setup

### 1. Local Server Mode (Dynamic REST API)
To launch the backend API server and web interface:
```bash
python server.py
```
Open `http://localhost:8080` in your web browser.

### 2. Updating Static Data for GitHub Pages
To crawl fresh data and update SQLite database:
```bash
python scraper.py
```
To export updated database records into static JSON datasets:
```bash
python export_static_data.py
```

---

## 📜 License

Distributed under the MIT License. Data rights belong to Cookups. Built for analytical and personal tracking purposes.
