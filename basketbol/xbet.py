import requests
import unidecode  
import re  

def normalize_team_name(name):
    if not name:
        return ""
    name = unidecode.unidecode(name).lower()
    name = re.sub(r'[^a-z0-9]', '', name)
    return name.strip()

def get_basketball_data():
    url = "https://1xlite-4937855.top/service-api/LiveFeed/Get1x2_VZip"
    params = {"count": 1000, "lng": "tr", "mode": 4, "country": 190, "noFilterBlockEvent": "true"}

    try:
        response = requests.get(url, params=params)
        data = response.json()
    except Exception as e:
        print(f"⚠️ API isteği başarısız: {e}")
        return []

    matches = []
    for event in data.get("Value", []):
        if event.get("SE") != "Basketball":
            continue

        takim1 = normalize_team_name(event.get("O1", ""))
        takim2 = normalize_team_name(event.get("O2", ""))

        # Durum bilgisi
        durum = "Bilinmiyor"
        sc_data = event.get("SC", {})
        if sc_data.get("CPS") == "Mola":
            durum = "Devre Arası"
        elif "CP" in sc_data and isinstance(sc_data["CP"], int):
            durum_map = {
                1: "1. Çeyrek",
                2: "2. Çeyrek",
                3: "3. Çeyrek",
                4: "4. Çeyrek"
            }
            durum = durum_map.get(sc_data["CP"], "Bilinmiyor")

        oranlar = {}

        for ae in event.get('AE', []):
            if ae.get("G") != 17:
                continue

            for bet in ae.get('ME', []):
                toplam = bet.get("P")
                oran_tipi = bet.get("T")
                oran_degeri = bet.get("C")
                ce = bet.get("CE", 0)

                if toplam is None or oran_degeri is None or ce != 0:
                    continue

                if not isinstance(toplam, (int, float, str)):
                    continue

                toplam = str(toplam).strip()
                if not toplam.endswith(".5"):
                    continue

                oranlar.setdefault(toplam, {"Üst": None, "Alt": None})

                if oran_tipi == 9:
                    oranlar[toplam]["Üst"] = oran_degeri
                elif oran_tipi == 10:
                    oranlar[toplam]["Alt"] = oran_degeri

        oranlar = {k: v for k, v in oranlar.items() if v["Üst"] and v["Alt"]}

        if oranlar:
            matches.append({
                "takim1": takim1,
                "takim2": takim2,
                "durum": durum,
                "oranlar": oranlar
            })

    return matches