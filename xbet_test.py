import requests
import unidecode
import re
import json

def normalize(name):
    name = unidecode.unidecode(name).lower()
    return re.sub(r"[\s\-\(\)]", "", name)

def dump_full_data_for_match(match_keyword):
    url = "https://1xlite-7196329.top/service-api/LiveFeed/Get1x2_VZip"
    params = {
        "count": 1000,
        "lng": "tr",
        "mode": 4,
        "country": 190,
        "noFilterBlockEvent": "true"
    }

    response = requests.get(url, params=params)
    data = response.json()

    matches = data.get("Value", [])
    normalized_keyword = normalize(match_keyword)
    found = False

    for event in matches:
        team1 = event.get("O1", "")
        team2 = event.get("O2", "")
        match_name = f"{team1} vs {team2}"

        if normalized_keyword in normalize(team1 + team2):
            print(f"\n✅ Maç bulundu: {match_name}")
            print("=" * 80)

            # Tüm event objesini detaylı olarak yazdır
            print(json.dumps(event, indent=4, ensure_ascii=False))

            # İstersen dosyaya da kaydedelim
            with open("xbet_match_dump.json", "w", encoding="utf-8") as f:
                json.dump(event, f, indent=4, ensure_ascii=False)
                print("\n📁 Dump JSON dosyasına yazıldı: xbet_match_dump.json")

            found = True
            break

    if not found:
        print(f"❌ '{match_keyword}' ile eşleşen maç bulunamadı.")

# 🔍 Aramak istediğin maçın adını yaz
dump_full_data_for_match("scfreiburg unionberlin")