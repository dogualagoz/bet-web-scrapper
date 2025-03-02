import requests

def get_1xbet_data():
    url = "https://1xlite-819117.top/service-api/LiveFeed/Get1x2_VZip"
    params = {
        "count": 1000,
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

        total_value = None  # Toplam değeri belirlemek için
        
        for bet in event.get('E', []):
            if bet["T"] == 9:  # Üst oran
                match_data["ust"] = bet["C"]
                total_value = bet.get("P", total_value)  # P değeri toplam olabilir
            elif bet["T"] == 10:  # Alt oran
                match_data["alt"] = bet["C"]
                if bet.get("P", None) == total_value:  # Aynı P varsa, bu toplamdır
                    match_data["toplam"] = total_value

        # Eğer toplam belirlenemediyse, en sık tekrar eden P değeri al
        if match_data["toplam"] is None and total_value is not None:
            match_data["toplam"] = total_value

        matches.append(match_data)

    return matches

# **Test için çalıştır**
if __name__ == "__main__":
    get_1xbet_data()