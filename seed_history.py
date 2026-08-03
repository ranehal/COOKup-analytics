import sqlite3
import random
import datetime

DB_NAME = "cookups.db"

def seed_price_history():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, current_price FROM dishes")
    dishes = cursor.fetchall()

    if not dishes:
        print("No dishes found in DB yet.")
        conn.close()
        return

    print(f"Seeding 30-day price history for {len(dishes)} dishes...")

    today = datetime.datetime.now()
    history_entries = []

    for dish in dishes:
        dish_id = dish["id"]
        base_price = dish["current_price"]
        
        # Determine price fluctuation profile (some stable, some with price drop, some with promo)
        profile = random.choice(["stable", "discount_now", "fluctuating", "recent_drop"])

        for i in range(30, -1, -1):
            date_dt = today - datetime.timedelta(days=i)
            date_str = date_dt.strftime("%Y-%m-%d")
            timestamp = date_dt.isoformat()

            if profile == "stable":
                price = base_price
            elif profile == "discount_now":
                if i <= 5:
                    price = round(base_price * 0.85, 0)
                else:
                    price = round(base_price * 1.1, 0)
            elif profile == "recent_drop":
                if i <= 3:
                    price = base_price
                else:
                    price = round(base_price * 1.2, 0)
            else: # fluctuating
                variation = random.choice([0, 0, 0, 0.05, -0.05, 0.1, -0.1])
                price = round(base_price * (1 + variation), 0)

            # Ensure positive price
            price = max(50.0, price)

            # Insert snapshot
            cursor.execute('''
                INSERT OR IGNORE INTO price_history (dish_id, price, timestamp, date_str)
                VALUES (?, ?, ?, ?)
            ''', (dish_id, price, timestamp, date_str))

        # Update previous_price and current_price based on profile
        if profile in ["discount_now", "recent_drop"]:
            cursor.execute('''
                UPDATE dishes 
                SET previous_price = ?, current_price = ?
                WHERE id = ?
            ''', (round(base_price * 1.2, 0), base_price, dish_id))

    conn.commit()
    conn.close()
    print("Price history seeding complete!")

if __name__ == "__main__":
    seed_price_history()
