import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'okhttp/4.9.2'
}

def test_req(name, url, payload):
    print(f"\n--- Testing {name} ---")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload)}")
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"STATUS: {resp.status}")
            print(f"COUNT: {len(data)}")
            if len(data) > 0:
                print("SAMPLE ITEM 0:", json.dumps(data[0], indent=2)[:300])
    except Exception as e:
        print(f"ERROR: {e}")

# 1. DishListView with category
test_req("DishListView with Category", "https://api.cookups.app/api/v1/view/DishListView/", {
    "SortBy": ["NumericIndexEntry", ["UnionCase_", 7, "NextAvailableDate"], "Ascending"],
    "DishFilters": {"CategoryId": ["CategoryId", "0ee1627c-cd8c-4740-8aa8-c9c6522be760"], "DeliveryDate": []},
    "PageNo": "0",
    "PageSize": 15
})

# 2. DishListView with null/empty CategoryId
test_req("DishListView with empty CategoryId", "https://api.cookups.app/api/v1/view/DishListView/", {
    "SortBy": ["NumericIndexEntry", ["UnionCase_", 7, "NextAvailableDate"], "Ascending"],
    "DishFilters": {"DeliveryDate": []},
    "PageNo": "0",
    "PageSize": 15
})

# 3. DishIndex with IsActive query
test_req("Dish Index IsActive", "https://api.cookups.app/api/v1/ecosystem/Cookups/subject/Dish/index?projection=PublicDish", [
    "IndexQuery",
    ["EqualToNumeric", "IsActive", "1"],
    {"Page": {"Size": 10, "Offset": "0"}, "OrderBy": "FastestOrSingleSearchScoreIfAvailable"}
])

# 4. DishIndex with Cook search
test_req("Dish Index Cook", "https://api.cookups.app/api/v1/ecosystem/Cookups/subject/Dish/index?projection=PublicDish", [
    "IndexQuery",
    ["EqualToString", "Cook", "CookId (UserId 51fbff1d-2fd0-df28-1a12-31dff45247dd)"],
    {"Page": {"Size": 10, "Offset": "0"}, "OrderBy": ["NumericIndexEntry", "UserRating", "Descending"]}
])

# 5. DishInfoView
test_req("DishInfoView", "https://api.cookups.app/api/v1/view/DishInfoView/", [
    "DishId", "a63328d2-a166-4fc7-8ced-eaf0aea69fd7"
])
