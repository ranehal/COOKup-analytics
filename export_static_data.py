import json
import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_NAME = 'cookups.db'
OUTPUT_DIR = 'data'

def export_data():
    if not os.path.exists(DB_NAME):
        print(f"Database {DB_NAME} not found.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Stats
    cursor.execute("SELECT COUNT(*) as cnt FROM dishes")
    total_dishes = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM categories")
    total_categories = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM cooks")
    total_cooks = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM dishes WHERE previous_price IS NOT NULL AND current_price < previous_price")
    price_drops = cursor.fetchone()["cnt"]

    cursor.execute("SELECT AVG(current_price) as avg_p FROM dishes")
    avg_price = round(cursor.fetchone()["avg_p"] or 0, 2)

    cursor.execute("SELECT COUNT(*) as cnt FROM price_history")
    total_history_records = cursor.fetchone()["cnt"]

    stats_data = {
        "total_dishes": total_dishes,
        "total_categories": total_categories,
        "total_cooks": total_cooks,
        "price_drops": price_drops,
        "avg_price": avg_price,
        "total_history_records": total_history_records
    }
    with open(os.path.join(OUTPUT_DIR, 'stats.json'), 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)

    # 2. Categories
    cursor.execute("SELECT c.*, (SELECT COUNT(*) FROM dishes d WHERE d.category_id = c.id) as dish_count FROM categories c ORDER BY c.name ASC")
    cat_rows = cursor.fetchall()
    categories_data = []
    for r in cat_rows:
        d = dict(r)
        d['parent_ids'] = json.loads(d['parent_ids']) if d['parent_ids'] else []
        categories_data.append(d)

    with open(os.path.join(OUTPUT_DIR, 'categories.json'), 'w', encoding='utf-8') as f:
        json.dump(categories_data, f, ensure_ascii=False, indent=2)

    # 3. Dishes
    cursor.execute("""
        SELECT d.*, c.name as category_name 
        FROM dishes d 
        LEFT JOIN categories c ON d.category_id = c.id 
        ORDER BY d.name ASC
    """)
    dish_rows = cursor.fetchall()
    dishes_data = []
    for r in dish_rows:
        d = dict(r)
        d['all_images'] = json.loads(d['all_images']) if d.get('all_images') else []
        dishes_data.append(d)

    with open(os.path.join(OUTPUT_DIR, 'dishes.json'), 'w', encoding='utf-8') as f:
        json.dump(dishes_data, f, ensure_ascii=False, indent=2)

    # 4. History map per dish
    cursor.execute("SELECT dish_id, price, timestamp, date_str FROM price_history ORDER BY date_str ASC, timestamp ASC")
    hist_rows = cursor.fetchall()
    history_map = {}
    for r in hist_rows:
        did = r["dish_id"]
        if did not in history_map:
            history_map[did] = []
        history_map[did].append({
            "price": r["price"],
            "timestamp": r["timestamp"],
            "date_str": r["date_str"]
        })

    with open(os.path.join(OUTPUT_DIR, 'history.json'), 'w', encoding='utf-8') as f:
        json.dump(history_map, f, ensure_ascii=False)

    conn.close()
    print(f"Exported static data to '{OUTPUT_DIR}/': stats.json, categories.json, dishes.json ({len(dishes_data)} dishes), history.json ({len(history_map)} dishes with history).")

if __name__ == '__main__':
    export_data()
