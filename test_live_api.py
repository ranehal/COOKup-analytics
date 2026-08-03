import urllib.request
import json

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'okhttp/4.9.2'
}

# 1. Fetch Root Categories
url_cat = "https://api.cookups.app/api/v1/ecosystem/Cookups/subject/Category/index"
payload_root_cats = ["IndexQuery",["And",["EqualToNumeric","IsActive","1"],["EqualToNumeric","IsRoot","1"]],{"Page":{"Size":65535,"Offset":"0"},"OrderBy":"FastestOrSingleSearchScoreIfAvailable"}]

req = urllib.request.Request(url_cat, data=json.dumps(payload_root_cats).encode('utf-8'), headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"Root categories returned: {len(data)} items")
        for item in data[:5]:
            cat_info = item[1]['Data']
            print(f"  - ID: {cat_info['Id'][1]}, Name: {cat_info['Name']['English'][1]}, Slug: {cat_info['UrlSlug'][1][1]}")
            
            # Test fetching subcategories
            cat_id = cat_info['Id'][1]
            sub_payload = ["IndexQuery",["EqualToString","SubCategoryOf", cat_id],{"Page":{"Size":65535,"Offset":"0"},"OrderBy":"FastestOrSingleSearchScoreIfAvailable"}]
            sub_req = urllib.request.Request(url_cat, data=json.dumps(sub_payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(sub_req) as sub_resp:
                sub_data = json.loads(sub_resp.read().decode('utf-8'))
                print(f"    Subcategories count: {len(sub_data)}")
                for sub in sub_data[:3]:
                    sub_info = sub[1]['Data']
                    print(f"      * SubID: {sub_info['Id'][1]}, Name: {sub_info['Name']['English'][1]}")

            # Test fetching dishes for this category
            dish_url = "https://chaldn.com/api/v1/view/DishListView/"
            dish_payload = {
                "SortBy": ["NumericIndexEntry", ["UnionCase_", 7, "NextAvailableDate"], "Ascending"],
                "DishFilters": {"CategoryId": ["CategoryId", cat_id], "DeliveryDate": []},
                "PageNo": "0",
                "PageSize": 15
            }
            dish_req = urllib.request.Request(dish_url, data=json.dumps(dish_payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(dish_req) as dish_resp:
                dishes = json.loads(dish_resp.read().decode('utf-8'))
                print(f"    Dishes returned: {len(dishes)}")
                if len(dishes) > 0:
                    d = dishes[0]
                    print(f"      Dish sample: {d.get('Name', {}).get('English', ['', ''])[1]}, Price: {d.get('Price', ['', ''])[1]}")
except Exception as e:
    print(f"Error: {e}")
