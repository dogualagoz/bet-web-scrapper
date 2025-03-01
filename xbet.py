import requests

def get_1xbet_data():
    url = "https://1xlite-819117.top/service-api/LiveFeed/Get1x2_VZip"
    params = {
        "count": 10,
        "lng": "tr",
        "mode": 4,
        "country": 190,
        "top": "true",
        "partner": 7,
        "virtualSports": "true",
        "noFilterBlockEvent": "true"
    }

    response = requests.get(url, params=params)
    data = response.json()

    matches = []
    for event in data.get('Value', []):
        match_data = {
            "takim1": event.get("O1", "Bilinmeyen Takım"),
            "takim2": event.get("O2", "Bilinmeyen Takım"),
            "lig": event.get("L", "Bilinmeyen Lig"),
            "toplam": None,
            "ust": None,
            "alt": None
        }

        for bet in event.get('E', []):
            if bet["T"] == 9:
                match_data["toplam"] = bet["C"]
            elif bet["T"] == 10:
                match_data["ust"] = bet["C"]
            elif bet["T"] == 11:
                match_data["alt"] = bet["C"]

        matches.append(match_data)

    print("\n✅ 1XBET Verileri Çekildi!\n")
    for m in matches:
        print(m)

    return matches

# **Test için çalıştır**
if __name__ == "__main__":
    get_1xbet_data()