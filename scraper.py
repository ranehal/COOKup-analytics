import json
import urllib.request
import sqlite3
import datetime
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding='utf-8')

DB_NAME = "cookups.db"
BASE_URL = "https://api.cookups.app/api/v1"

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'okhttp/4.9.2'
}

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT,
            parent_ids TEXT,
            image_url TEXT,
            sort_order INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    
    # Cooks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cooks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            image_url TEXT
        )
    ''')

    # Dishes / Items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dishes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            bengali_name TEXT,
            slug TEXT,
            category_id TEXT,
            cook_id TEXT,
            cook_name TEXT,
            cook_image_url TEXT,
            serving_size INTEGER,
            serving_type TEXT,
            rating REAL,
            rating_count INTEGER,
            current_price REAL NOT NULL,
            previous_price REAL,
            image_url TEXT,
            all_images TEXT,
            updated_at TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (cook_id) REFERENCES cooks (id)
        )
    ''')

    # Price History table (CamelCamelCamel / SteamDB style tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dish_id TEXT NOT NULL,
            price REAL NOT NULL,
            timestamp TEXT NOT NULL,
            date_str TEXT NOT NULL,
            FOREIGN KEY (dish_id) REFERENCES dishes (id)
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dishes_category ON dishes(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_dish ON price_history(dish_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(date_str)')
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_price_history_dish_date ON price_history(dish_id, date_str)')

    conn.commit()
    conn.close()

def parse_image_url(img_data):
    if not img_data:
        return ""
    # Format can be tuple [ "Legacy", "https://..." ] or [ "Blob", { "Id_": "..." } ]
    if isinstance(img_data, list):
        for item in img_data:
            if isinstance(item, list) and len(item) == 2:
                kind, val = item
                if kind == "Legacy" and isinstance(val, str):
                    return val
                elif kind == "Blob" and isinstance(val, dict):
                    blob_id = val.get("Id_")
                    owner = val.get("Owner_", {})
                    life_cycle = owner.get("LifeCycleName")
                    subject_id = owner.get("SubjectIdStr")
                    if blob_id and life_cycle and subject_id:
                        src_url = f"https://api.cookups.app/api/v1/ecosystem/Cookups/subject/{life_cycle}/blob/{subject_id}/{blob_id}"
                        return f"https://chaldn.com/_mpimage?src={urllib.parse.quote(src_url, safe='')}&w=400&q=low"
            elif isinstance(item, str) and item.startswith("http"):
                return item
    elif isinstance(img_data, dict):
        blob_id = img_data.get("Id_")
        owner = img_data.get("Owner_", {})
        life_cycle = owner.get("LifeCycleName")
        subject_id = owner.get("SubjectIdStr")
        if blob_id and life_cycle and subject_id:
            src_url = f"https://api.cookups.app/api/v1/ecosystem/Cookups/subject/{life_cycle}/blob/{subject_id}/{blob_id}"
            return f"https://chaldn.com/_mpimage?src={urllib.parse.quote(src_url, safe='')}&w=400&q=low"
    return ""

def parse_all_images(images_data):
    if not images_data:
        return []
    urls = []
    if isinstance(images_data, list):
        for img in images_data:
            url = parse_image_url([img]) if not isinstance(img, list) else parse_image_url(img)
            if url and url not in urls:
                urls.append(url)
    return urls

def fetch_categories():
    req = urllib.request.Request(f"{BASE_URL}/categories", headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
            return raw.get("data", raw) if isinstance(raw, dict) else raw
    except Exception as _cke:
        print(f"  [!] Live categories fetch failed ({_cke}). Falling back to database...", flush=True)
        try:
            conn = get_db_connection()
            rows = conn.cursor().execute("SELECT id, name, slug, parent_ids, image_url, sort_order FROM categories").fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception as _dbe:
            print(f"  [!] DB fallback failed ({_dbe})", flush=True)
            return []


def fetch_dishes_for_category(cat_id, now_str, today_str):
    url = f"{BASE_URL}/view/DishListView/"
    page = 0
    pageSize = 30
    total_dishes = 0
    conn = get_db_connection()
    cursor = conn.cursor()

    while True:
        payload = {
            "SortBy": ["NumericIndexEntry", ["UnionCase_", 7, "NextAvailableDate"], "Ascending"],
            "DishFilters": {"CategoryId": ["CategoryId", cat_id], "DeliveryDate": []},
            "PageNo": str(page),
            "PageSize": pageSize
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                items = json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            print(f"  Error fetching page {page} for cat {cat_id}: {e}")
            break

        if not items or len(items) == 0:
            break

        for item in items:
            dish_id = item.get("Id", [None, None])[1]
            if not dish_id:
                continue

            name = item.get("Name", {}).get("English", [None, ""])[1] or "Unknown Dish"
            bengali_name = item.get("Name", {}).get("Bengali", "") or ""
            slug = item.get("UrlSlug", [None, [None, ""]])[1][1] if item.get("UrlSlug") else ""
            
            # Price
            price_raw = item.get("Price", [None, "0"])[1]
            try:
                price = float(price_raw)
            except:
                price = 0.0

            # Rating
            rating_obj = item.get("Rating") or {}
            rating = None
            rating_count = 0
            if isinstance(rating_obj, dict):
                r_val = rating_obj.get("Rating")
                if isinstance(r_val, list) and len(r_val) == 2:
                    try: rating = float(r_val[1])
                    except: pass
                c_val = rating_obj.get("TotalCount")
                if isinstance(c_val, list) and len(c_val) == 2:
                    try: rating_count = int(c_val[1])
                    except: pass

            # Serving
            serving = item.get("Serving") or {}
            serving_size = 1
            serving_type = "Persons"
            if isinstance(serving, dict):
                sz = serving.get("Size")
                if isinstance(sz, list) and len(sz) == 2:
                    try: serving_size = int(sz[1])
                    except: pass
                serving_type = serving.get("Type", "Persons")

            # Cook
            cook_id = item.get("CookId", [None, [None, None]])[1][1] if item.get("CookId") else ""
            cook_name = item.get("CookName", "") or "Home Cook"
            cook_image = parse_image_url(item.get("CookImage"))

            if cook_id:
                cursor.execute('''
                    INSERT INTO cooks (id, name, description, image_url)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET name=excluded.name, image_url=excluded.image_url
                ''', (cook_id, cook_name, "", cook_image))

            # Image
            img_url = parse_image_url(item.get("Image"))
            all_imgs = json.dumps(parse_all_images(item.get("Image")))

            # Check existing price to detect price changes
            cursor.execute("SELECT current_price FROM dishes WHERE id = ?", (dish_id,))
            row = cursor.fetchone()
            prev_price = None
            if row:
                prev_price = row["current_price"]

            # Save Dish
            cursor.execute('''
                INSERT INTO dishes (
                    id, name, bengali_name, slug, category_id, cook_id, cook_name, cook_image_url,
                    serving_size, serving_type, rating, rating_count, current_price, previous_price,
                    image_url, all_images, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    bengali_name=excluded.bengali_name,
                    slug=excluded.slug,
                    category_id=excluded.category_id,
                    cook_id=excluded.cook_id,
                    cook_name=excluded.cook_name,
                    cook_image_url=excluded.cook_image_url,
                    serving_size=excluded.serving_size,
                    serving_type=excluded.serving_type,
                    rating=excluded.rating,
                    rating_count=excluded.rating_count,
                    previous_price=CASE WHEN excluded.current_price != dishes.current_price THEN dishes.current_price ELSE dishes.previous_price END,
                    current_price=excluded.current_price,
                    image_url=excluded.image_url,
                    all_images=excluded.all_images,
                    updated_at=excluded.updated_at
            ''', (dish_id, name, bengali_name, slug, cat_id, cook_id, cook_name, cook_image,
                  serving_size, serving_type, rating, rating_count, price, prev_price,
                  img_url, all_imgs, now_str))

            # Price History Entry (1 entry per dish per date - keep the latest price of the day)
            cursor.execute('''
                INSERT INTO price_history (dish_id, price, timestamp, date_str)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(dish_id, date_str) DO UPDATE SET
                    price = excluded.price,
                    timestamp = excluded.timestamp
            ''', (dish_id, price, now_str, today_str))

            total_dishes += 1

        if len(items) < pageSize:
            break
        page += 1
        time.sleep(0.05) # gentle speed

    conn.commit()
    conn.close()
    return total_dishes

def run_full_scrape():
    start_time = time.time()
    print("=== STARTING COOKUPS DEEP SCRAPE ===")
    init_db()
    
    categories = fetch_categories()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    total_dishes_scraped = 0
    cats_with_dishes = 0

    MAX_WORKERS = 5

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_dishes_for_category, cat["id"], now_str, today_str): (idx, cat)
            for idx, cat in enumerate(categories)
        }
        for future in futures:
            idx, cat = futures[future]
            cid = cat["id"]
            cname = cat["name"]
            try:
                dishes_count = future.result()
            except Exception as e:
                print(f"  WARNING: category {cname} ({cid}) failed: {e}")
                continue
            if dishes_count > 0:
                cats_with_dishes += 1
                total_dishes_scraped += dishes_count
                print(f"[{idx+1}/{len(categories)}] {cname}: {dishes_count} items")

    elapsed = round(time.time() - start_time, 2)
    print(f"=== DEEP SCRAPE COMPLETE in {elapsed}s ===")
    print(f"Total Categories: {len(categories)} ({cats_with_dishes} active with items)")
    print(f"Total Dish Records Processed: {total_dishes_scraped}")

    # Auto-export static data for GitHub Pages hosting
    try:
        from export_static_data import export_data
        print("\nExporting static data for GitHub Pages...")
        export_data()
    except Exception as e:
        print(f"  [WARN] Failed to auto-export static data: {e}")

if __name__ == "__main__":
    run_full_scrape()
