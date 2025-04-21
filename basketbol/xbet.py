import requests
import unidecode
import re

def normalize_team_name(name):
    return re.sub(r"[^a-z0-9]", "", unidecode.unidecode(name or "").lower())

def get_basketball_data():
    url = "https://1xlite-118920.top/service-api/LiveFeed/Get1x2_VZip"
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
        print(f"⚠️ API hatası: {e}")
        return []

    matches = []
    for event in data.get("Value", []):
        if event.get("SE") != "Basketball":
            continue

        t1 = normalize_team_name(event.get("O1", ""))
        t2 = normalize_team_name(event.get("O2", ""))
        oranlar = {}

        for ae in event.get("AE", []):
            if ae.get("G") != 17:
                continue

            for me in ae.get("ME", []):
                toplam = str(me.get("P", "")).strip()
                if not toplam.endswith(".5"):
                    continue

                oran_tipi = me.get("T")
                oran_degeri = me.get("C")
                if oran_degeri is None or me.get("CE", 0) != 0:
                    continue

                oranlar.setdefault(toplam, {"Üst": None, "Alt": None})
                if oran_tipi == 9:
                    oranlar[toplam]["Üst"] = oran_degeri
                elif oran_tipi == 10:
                    oranlar[toplam]["Alt"] = oran_degeri

        oranlar = {k: v for k, v in oranlar.items() if v["Üst"] and v["Alt"]}

        if oranlar:
            matches.append({
                "takim1": t1,
                "takim2": t2,
                "oranlar": oranlar
            })

    return matches