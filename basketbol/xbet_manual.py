import requests

def get_basketball_data():
    """Basketbol maçlarını ve toplam sayı oranlarını sözlük formatında çeker."""
    url = "https://1xlite-7209679.top/service-api/LiveFeed/Get1x2_VZip"
    params = {"count": 1000, "lng": "tr", "mode": 4, "country": 190, "noFilterBlockEvent": "true"}

    response = requests.get(url, params=params)
    data = response.json()

    matches = []
    for event in data.get("Value", []):
        if event.get("SE") != "Basketball":
            continue  # Sadece basketbol maçlarını al

        match_info = {
            "lig": event.get("L", "Bilinmeyen Lig"),
            "takim1": event.get("O1", "Bilinmeyen Takım"),
            "takim2": event.get("O2", "Bilinmeyen Takım"),
            "durum": "Bilinmiyor",
            "oranlar": {}
        }

        # Maçın kaçıncı çeyrekte olduğu
        if event.get("SC", {}).get("CP") == 1:
            match_info["durum"] = "1. Çeyrek"
        elif event.get("SC", {}).get("CP") == 2:
            match_info["durum"] = "2. Çeyrek"
        elif event.get("SC", {}).get("CP") == 3:
            match_info["durum"] = "3. Çeyrek"
        elif event.get("SC", {}).get("CP") == 4:
            match_info["durum"] = "4. Çeyrek"
        elif event.get("SC", {}).get("CPS") == "Mola":
            match_info["durum"] = "Devre Arası"

        # **Tüm toplam sayı oranlarını çek ve sözlük yapısına yerleştir**
        for bet_category in event.get("AE", []):
            if bet_category.get("G") == 17:  # G = 17 -> Toplam Sayı Oranları
                for bet in bet_category.get("ME", []):
                    point = bet.get("P")  # Toplam sayı baremi
                    coef = bet.get("C")   # Oran değeri
                    type_id = bet.get("T")

                    if point is not None and coef is not None:
                        point = str(point)
                        if point.endswith(".5"):  # Sadece .5 ile bitenleri al
                            match_info["oranlar"].setdefault(point, {"Üst": None, "Alt": None})
                            if type_id == 9:    # Üst Oranı
                                match_info["oranlar"][point]["Üst"] = coef
                            elif type_id == 10:  # Alt Oranı
                                match_info["oranlar"][point]["Alt"] = coef

        # Eğer en az bir geçerli oran varsa listeye ekle
        if match_info["oranlar"]:
            matches.append(match_info)

    return matches


# 📌 **Basketbol Verilerini Çek**
basketbol_maclari = get_basketball_data()

# 📌 **Veriyi Kullan**
for mac in basketbol_maclari:
    print(f"\n🏆 {mac['lig']}")
    print(f"{mac['takim1']} 🆚 {mac['takim2']}")
    print(f"🕐 Durum: {mac['durum']}")

    # **Tüm toplam sayı oranlarını yazdır**
    for point, odds in sorted(mac["oranlar"].items()):
        ust = f"Üst: {odds['Üst']}" if odds["Üst"] else "Üst: -"
        alt = f"Alt: {odds['Alt']}" if odds["Alt"] else "Alt: -"
        print(f"📊 {point}  | {ust} | {alt} |")

print("\n✅ **Veriler başarıyla çekildi ve sözlük formatında saklandı!**")