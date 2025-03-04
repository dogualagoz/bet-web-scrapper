import requests
import json

def get_1xbet_data():
    url = "https://1xlite-931124.top/service-api/LiveFeed/Get1x2_VZip"

    params = {
        "count": 50,  # Maksimum stabil çalışan count
        "lng": "tr",
        "mode": 4,
        "country": 190,
        "noFilterBlockEvent": "true",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://1xlite-931124.top/tr/live",
        "Origin": "https://1xlite-931124.top",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        print("\n✅ API isteği başarılı. Yanıt kodu:", response.status_code)

        data = response.json()
        if not data or 'Value' not in data:
            print("❌ API geçersiz veri döndürdü.")
            return []

    except requests.exceptions.RequestException as e:
        print(f"❌ API isteği başarısız: {e}")
        return []

    matches = []

    for event in data.get("Value", []):
        if event.get("SE") != "Football" and event.get("SN") != "Futbol":
            continue  # Sadece futbol maçlarını al

        takim1 = event.get("O1", "Bilinmeyen Takım")
        takim2 = event.get("O2", "Bilinmeyen Takım")

        if takim1 == "Bilinmeyen Takım" or takim2 == "Bilinmeyen Takım":
            continue  # Takım adı eksikse maçı atla

        oranlar = {}

        # 🛠 **Doğru oranları AE → ME içinden çek**
        for ae in event.get('AE', []):
            for bet in ae.get('ME', []):
                toplam_gol = bet.get("P")  # Bahis türü gol sayısı
                oran_tipi = bet.get("T")  # Üst/Alt tipi
                oran_degeri = bet.get("C")  # Oran değeri

                if toplam_gol is not None and oran_degeri is not None:
                    toplam_gol = str(toplam_gol)

                    if toplam_gol.endswith(".5") and 0.5 <= float(toplam_gol) <= 10.5:
                        if toplam_gol not in oranlar:
                            oranlar[toplam_gol] = {"Üst": None, "Alt": None}

                        if oran_tipi == 9:
                            oranlar[toplam_gol]["Üst"] = oran_degeri
                        elif oran_tipi == 10:
                            oranlar[toplam_gol]["Alt"] = oran_degeri

        # Eğer oranlar tamamen boşsa maçı atla
        if not any(v["Üst"] is not None or v["Alt"] is not None for v in oranlar.values()):
            continue

        oran_listesi = [{"Toplam Oran": k, "Üst": v["Üst"], "Alt": v["Alt"]} for k, v in oranlar.items()]

        match_data = {
            "takim1": takim1,
            "takim2": takim2,
            "oranlar": oran_listesi
        }
        
        matches.append(match_data)

    return matches


# **Test için çalıştır**
if __name__ == "__main__":
    matches = get_1xbet_data()
    
    # JSON formatında yazdır
    print(json.dumps(matches, indent=4, ensure_ascii=False))