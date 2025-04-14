import requests
import re
import unidecode

def normalize_team_name(name):
    name = unidecode.unidecode(name).lower()
    return re.sub(r"\s|-|\(.*?\)", "", name)

def is_valid_goal_value(value):
    try:
        val = float(value)
        return str(val).endswith(".5")
    except:
        return False

def get_1xbet_data():
    url = "https://1xlite-4937855.top/service-api/LiveFeed/Get1x2_VZip"
    params = {
        "count": 1000,
        "lng": "tr",
        "mode": 4,
        "country": 190,
        "noFilterBlockEvent": "true"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
    except Exception as e:
        print(f"⚠️ API isteği başarısız: {e}")
        return []

    matches = []
    for event in data.get("Value", []):
        takim1 = normalize_team_name(event.get("O1", ""))
        takim2 = normalize_team_name(event.get("O2", ""))

        oranlar = {}

        for ae in event.get('AE', []):
            if ae.get("G") != 17:
                continue

            for bet in ae.get('ME', []):
                toplam_gol = bet.get("P")
                oran_tipi = bet.get("T")
                oran_degeri = bet.get("C")
                ce = bet.get("CE", 0)

                if toplam_gol is None or oran_degeri is None:
                    continue

                if ce != 0:
                    continue  # Sadece ana market

                if not isinstance(toplam_gol, (int, float, str)):
                    continue

                toplam_gol = str(toplam_gol).strip()
                if not is_valid_goal_value(toplam_gol):
                    continue

                oranlar.setdefault(toplam_gol, {"Üst": None, "Alt": None})

                if oran_tipi == 9:
                    oranlar[toplam_gol]["Üst"] = oran_degeri
                elif oran_tipi == 10:
                    oranlar[toplam_gol]["Alt"] = oran_degeri

        # Sadece tam çift olanlar kalsın
        oranlar = {
            k: v for k, v in oranlar.items()
            if v["Üst"] is not None and v["Alt"] is not None
        }

        if oranlar:
            matches.append({
                "takim1": takim1,
                "takim2": takim2,
                "oranlar": oranlar
            })

    return matches