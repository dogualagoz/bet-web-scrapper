import requests
import re
import unidecode  

def normalize_team_name(name):
    name = unidecode.unidecode(name).lower()
    return re.sub(r"\s|-|\(.*?\)", "", name)  

def get_1xbet_data():
    url = "https://1xlite-238339.top/service-api/LiveFeed/Get1x2_VZip"
    params = {"count": 1000, "lng": "tr", "mode": 4, "country": 190, "noFilterBlockEvent": "true"}

    response = requests.get(url, params=params)
    data = response.json()

    matches = []
    for event in data.get("Value", []):
        takim1 = normalize_team_name(event.get("O1", ""))
        takim2 = normalize_team_name(event.get("O2", ""))

        oranlar = {}
        for ae in event.get('AE', []):
            for bet in ae.get('ME', []):
                toplam_gol = bet.get("P")
                oran_tipi = bet.get("T")
                oran_degeri = bet.get("C")

                if toplam_gol is not None and oran_degeri is not None:
                    toplam_gol = str(toplam_gol)
                    if toplam_gol.endswith(".5"):
                        oranlar.setdefault(toplam_gol, {"Üst": None, "Alt": None})
                        if oran_tipi == 9:
                            oranlar[toplam_gol]["Üst"] = oran_degeri
                        elif oran_tipi == 10:
                            oranlar[toplam_gol]["Alt"] = oran_degeri

        if any(v["Üst"] and v["Alt"] for v in oranlar.values()):
            matches.append({"takim1": takim1, "takim2": takim2, "oranlar": oranlar})

    print(f"📌 **1xBet'ten {len(matches)} maç çekildi.**")
    return matches