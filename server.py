import http.server
import socketserver
import json
import sqlite3
import urllib.parse
import os
import sys
import threading
import datetime
from scraper import run_full_scrape, DB_NAME, get_db_connection

sys.stdout.reconfigure(encoding='utf-8')

PORT = 8080

class CookupsRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)

        if path.startswith('/api/'):
            self.handle_api(path, query_params)
        else:
            # Serve static files from current directory
            super().do_GET()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == '/api/scrape':
            # Run scraper in background thread
            t = threading.Thread(target=run_full_scrape)
            t.daemon = True
            t.start()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "started", "message": "Scraper execution launched in background."}).encode('utf-8'))
        else:
            self.send_error(404, "Endpoint not found")

    def handle_api(self, path, params):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            if path == '/api/stats':
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

                res_data = {
                    "total_dishes": total_dishes,
                    "total_categories": total_categories,
                    "total_cooks": total_cooks,
                    "price_drops": price_drops,
                    "avg_price": avg_price,
                    "total_history_records": total_history_records
                }

            elif path == '/api/categories':
                cursor.execute("SELECT c.*, (SELECT COUNT(*) FROM dishes d WHERE d.category_id = c.id) as dish_count FROM categories c ORDER BY c.name ASC")
                rows = cursor.fetchall()
                res_data = []
                for r in rows:
                    d = dict(r)
                    d['parent_ids'] = json.loads(d['parent_ids']) if d['parent_ids'] else []
                    res_data.append(d)

            elif path == '/api/dishes':
                cat_id = params.get('category_id', [None])[0]
                search = params.get('search', [None])[0]
                sort = params.get('sort', ['name_asc'])[0]
                min_price = params.get('min_price', [None])[0]
                max_price = params.get('max_price', [None])[0]
                min_rating = params.get('min_rating', [None])[0]
                price_drops_only = params.get('price_drops', ['false'])[0] == 'true'
                page = int(params.get('page', ['1'])[0])
                limit = int(params.get('limit', ['24'])[0])
                offset = (page - 1) * limit

                query = "SELECT d.*, c.name as category_name FROM dishes d LEFT JOIN categories c ON d.category_id = c.id WHERE 1=1"
                sql_params = []

                if cat_id:
                    # Include subcategories if any
                    cursor.execute("SELECT id FROM categories WHERE parent_ids LIKE ?", (f'%"{cat_id}"%',))
                    sub_ids = [r['id'] for r in cursor.fetchall()]
                    sub_ids.append(cat_id)
                    placeholders = ','.join(['?'] * len(sub_ids))
                    query += f" AND d.category_id IN ({placeholders})"
                    sql_params.extend(sub_ids)

                if search:
                    query += " AND (d.name LIKE ? OR d.bengali_name LIKE ? OR d.cook_name LIKE ?)"
                    sql_params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

                if min_price:
                    query += " AND d.current_price >= ?"
                    sql_params.append(float(min_price))

                if max_price:
                    query += " AND d.current_price <= ?"
                    sql_params.append(float(max_price))

                if min_rating:
                    query += " AND d.rating >= ?"
                    sql_params.append(float(min_rating))

                if price_drops_only:
                    query += " AND d.previous_price IS NOT NULL AND d.current_price < d.previous_price"

                # Count total matching
                count_sql = f"SELECT COUNT(*) as cnt FROM ({query})"
                cursor.execute(count_sql, sql_params)
                total_count = cursor.fetchone()["cnt"]

                # Order By
                if sort == 'price_asc':
                    query += " ORDER BY d.current_price ASC"
                elif sort == 'price_desc':
                    query += " ORDER BY d.current_price DESC"
                elif sort == 'rating_desc':
                    query += " ORDER BY d.rating DESC"
                elif sort == 'discount_desc':
                    query += " ORDER BY (CASE WHEN d.previous_price > 0 THEN (d.previous_price - d.current_price) / d.previous_price ELSE 0 END) DESC"
                else:
                    query += " ORDER BY d.name ASC"

                query += " LIMIT ? OFFSET ?"
                sql_params.extend([limit, offset])

                cursor.execute(query, sql_params)
                dishes = [dict(r) for r in cursor.fetchall()]

                res_data = {
                    "items": dishes,
                    "total": total_count,
                    "page": page,
                    "limit": limit,
                    "total_pages": (total_count + limit - 1) // limit if limit > 0 else 1
                }

            elif path.startswith('/api/dish/'):
                dish_id = path.split('/api/dish/')[1]
                cursor.execute("SELECT d.*, c.name as category_name FROM dishes d LEFT JOIN categories c ON d.category_id = c.id WHERE d.id = ?", (dish_id,))
                dish_row = cursor.fetchone()
                if not dish_row:
                    self.send_error(404, "Dish not found")
                    conn.close()
                    return

                dish = dict(dish_row)
                dish['all_images'] = json.loads(dish['all_images']) if dish['all_images'] else []

                # Price history entries
                cursor.execute("SELECT price, timestamp, date_str FROM price_history WHERE dish_id = ? ORDER BY date_str ASC, timestamp ASC", (dish_id,))
                ph_rows = [dict(r) for r in cursor.fetchall()]

                # Calculate CamelCamelCamel style price stats
                prices = [r['price'] for r in ph_rows] if ph_rows else [dish['current_price']]
                lowest_price = min(prices)
                highest_price = max(prices)
                avg_price = round(sum(prices) / len(prices), 2)
                is_lowest_ever = dish['current_price'] <= lowest_price

                res_data = {
                    "dish": dish,
                    "price_history": ph_rows,
                    "stats": {
                        "lowest_price": lowest_price,
                        "highest_price": highest_price,
                        "avg_price": avg_price,
                        "is_lowest_ever": is_lowest_ever,
                        "history_count": len(ph_rows)
                    }
                }
            else:
                self.send_error(404, "Endpoint not found")
                conn.close()
                return

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res_data).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        finally:
            conn.close()

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer(("", PORT), CookupsRequestHandler) as httpd:
        print(f"Serving Cookups Analytics & Price Tracker Dashboard at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()
