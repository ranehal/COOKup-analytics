# COOKup Analytics

An interactive analytics dashboard and tracking platform for Cookups dishes, cooks, category distributions, and price history.

🌐 **Live GitHub Pages Demo**: [https://ranehal.github.io/COOKup-analytics/](https://ranehal.github.io/COOKup-analytics/)

## 🚀 Features

- **Dashboard Statistics**: Real-time overview of total dishes, categories, active cooks, price drops, average prices, and historical records.
- **Price Drop Tracker**: Dedicated view highlighting dishes with active price reductions.
- **Dish Explorer & Search**: Search, filter by category, and sort dishes dynamically.
- **Category Analytics**: Browse categories with dish counts and hierarchy.
- **CamelCamelCamel & SteamDB Price History**: Interactive price history chart modals per dish.
- **Hybrid Hosting Architecture**: Works dynamically with local Python backend (`server.py`) OR fully statically on GitHub Pages.

## 📁 Project Structure (Root Level)

- [`index.html`](file:///C:/PROJECTS/COOKup/index.html) - Main dashboard HTML interface
- [`style.css`](file:///C:/PROJECTS/COOKup/style.css) - Modern responsive dashboard styling
- [`app.js`](file:///C:/PROJECTS/COOKup/app.js) - Interactive logic with live API + static fallback
- [`server.py`](file:///C:/PROJECTS/COOKup/server.py) - Python HTTP server & REST API handler (`:8080`)
- [`scraper.py`](file:///C:/PROJECTS/COOKup/scraper.py) - Cookups API scraper and database populator
- [`export_static_data.py`](file:///C:/PROJECTS/COOKup/export_static_data.py) - Exporter to generate static JSON datasets for GitHub Pages
- [`data/`](file:///C:/PROJECTS/COOKup/data) - Pre-baked static JSON files (`stats.json`, `categories.json`, `dishes.json`, `history.json`)
- [`cookups.db`](file:///C:/PROJECTS/COOKup/cookups.db) - SQLite database storing dishes, cooks, categories, and price history
- [`.github/workflows/deploy.yml`](file:///C:/PROJECTS/COOKup/.github/workflows/deploy.yml) - Automatic GitHub Pages deployment workflow

## 🛠️ Usage

### Local Server Mode

Start the backend server and static host:

```bash
python server.py
```

Open `http://localhost:8080` in your web browser.

### Refreshing Static Data for GitHub Pages

To export updated database records to static JSON files for GitHub Pages hosting:

```bash
python export_static_data.py
```

### GitHub Pages Setup

1. Go to repository settings on GitHub: **Settings > Pages**.
2. Under **Build and deployment > Source**, select **GitHub Actions** (or `main` branch).
3. Any push to `main` will automatically build and publish the site.
