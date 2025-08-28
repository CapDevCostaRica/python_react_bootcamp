import requests
import json

LIST_ENDPOINT = "http://127.0.0.1:4000/list"
GET_ENDPOINT = "http://127.0.0.1:4000/get"
HEADERS = {"Content-Type": "application/json"}

def fetch_monsters():
    """ Get monsters list"""
    payload = {"resource": "monsters"}
    try:
        response = requests.post(LIST_ENDPOINT, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Could not get monsters list: {e}")
        return None

def test_monsters(monsters_data, output_file="monsters_results.json"):
    """ Get monster details """
    results = {}
    for monster in monsters_data.get("results", []):
        payload = {"monster_index": monster["index"]}
        status_key = None
        try:
            response = requests.post(GET_ENDPOINT, json=payload, headers=HEADERS, timeout=10)
            status_key = str(response.status_code)
            if response.status_code != 200:
                print(f"❌ {monster['name']} ({monster['index']}) → {response.status_code}")
            else:
               print(f"✅ {monster['name']} ({monster['index']}) → 200 OK")

        except requests.exceptions.RequestException as e:
            status_key = "Error"
            print(f"⚠️  {monster['name']} ({monster['index']}) → Error: {e}")

        # Group by http response code
        if status_key not in results:
            results[status_key] = []
        results[status_key].append({
            "index": monster["index"],
            "name": monster["name"]
        })

    # Save results to a file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    total = sum(len(v) for v in results.values())
    oks = len(results.get("200", []))
    failed = total - oks
    print(f"\n📂 Results saved on {output_file} / {oks} Ok / ({failed} errors)")

if __name__ == "__main__":
    monsters_data = fetch_monsters()    
    if monsters_data:
        test_monsters(monsters_data)
