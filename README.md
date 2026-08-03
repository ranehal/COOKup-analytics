# COOKup Analytics

An interactive analytics dashboard and tracking platform for Cookups dishes, cooks, category distributions, and price history.

## 🚀 Features

- **Dashboard Statistics**: Real-time overview of total dishes, categories, active cooks, price drops, average prices, and historical records.
- **Price Drop Tracker**: Dedicated view highlighting dishes with active price reductions.
- **Dish Explorer & Search**: Search, filter by category, and sort dishes dynamically.
- **Category Analytics**: Browse categories with dish counts and hierarchy.
- **Cook Directory**: Explore active cooks, rating distribution, and dish offerings.
- **Automated Web Scraper**: Python scraper to fetch and sync public Cookups dish catalog into a local SQLite database (`cookups.db`).
- **REST API Backend**: Lightweight Python HTTP server serving JSON endpoints and static dashboard assets.

## 📁 Project Structure (Root Level)

- [`index.html`](file:///C:/PROJECTS/COOKup/index.html) - Main dashboard HTML interface
- [`style.css`](file:///C:/PROJECTS/COOKup/style.css) - Modern responsive dashboard styling
- [`app.js`](file:///C:/PROJECTS/COOKup/app.js) - Frontend interactive logic & API integration
- [`server.py`](file:///C:/PROJECTS/COOKup/server.py) - Python HTTP server & REST API handler (`:8080`)
- [`scraper.py`](file:///C:/PROJECTS/COOKup/scraper.py) - Cookups API scraper and database populator
- [`seed_history.py`](file:///C:/PROJECTS/COOKup/seed_history.py) - Database seeding helper for price history
- [`explore_dish_api.py`](file:///C:/PROJECTS/COOKup/explore_dish_api.py) - Cookups API endpoint exploration utility
- [`inspect_har.py`](file:///C:/PROJECTS/COOKup/inspect_har.py) - HAR file parsing utility
- [`test_live_api.py`](file:///C:/PROJECTS/COOKup/test_live_api.py) - Live API testing script
- [`cookups.db`](file:///C:/PROJECTS/COOKup/cookups.db) - SQLite database storing dishes, cooks, categories, and price history

## 🛠️ Usage

### Running the Server

Start the backend server and static host:

```bash
python server.py
```

Then open `http://localhost:8080` in your web browser.

### Running the Scraper

To trigger a manual database refresh/scrape:

```bash
python scraper.py
```

Or trigger a background scrape directly from the web UI dashboard.

## 📡 API Endpoints

- `GET /api/stats` - Summary statistics
- `GET /api/categories` - Categories list with dish counts
- `GET /api/dishes` - Dish listing with filters (category, search, sorting)
- `GET /api/cooks` - Cook statistics and ratings
- `GET /api/pricedrops` - Dishes with reduced prices
- `POST /api/scrape` - Trigger background scrape task
