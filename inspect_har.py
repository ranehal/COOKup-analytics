import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('cookup dc.services.visualstudio.com_2026_08_02_04_19_27.har', 'r', encoding='utf-8') as f:
    har = json.load(f)

entries = har.get('log', {}).get('entries', [])

api_entries = []
for entry in entries:
    req = entry.get('request', {})
    res = entry.get('response', {})
    url = req.get('url', '')
    if ('cookup' in url.lower() or 'chaldn' in url.lower()) and '_mpimage' not in url:
        method = req.get('method')
        status = res.get('status')
        headers = {h['name']: h['value'] for h in req.get('headers', [])}
        post_data = req.get('postData', {}).get('text', '')
        res_text = res.get('content', {}).get('text', '')
        api_entries.append({
            'url': url,
            'method': method,
            'status': status,
            'headers': headers,
            'post_data': post_data,
            'res_text': res_text
        })

print(f"Total API requests (excluding images): {len(api_entries)}")
for idx, item in enumerate(api_entries):
    u = item['url']
    m = item['method']
    s = item['status']
    print(f"\n==========================================")
    print(f"[{idx+1}] {m} ({s}) {u}")
    print(f"--- Request Headers ---")
    for k, v in item['headers'].items():
        if k.lower() in ['authorization', 'cookie', 'x-chaldal-client', 'user-agent', 'content-type', 'accept', 'x-device-id', 'x-app-version']:
            print(f"  {k}: {v}")
    if item['post_data']:
        print(f"--- Post Data ---")
        print(item['post_data'][:500])
    if item['res_text']:
        print(f"--- Response Sample ---")
        print(item['res_text'][:400])
