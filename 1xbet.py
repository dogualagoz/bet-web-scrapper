import requests

# API Endpoint ve Parametreler
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

# API İsteği Gönder
response = requests.get(url, params=params)
data = response.json()

# Maçları işleyelim
for event in data.get('Value', []):
    takim1 = event.get("O1", "Bilinmeyen Takım")
    takim2 = event.get("O2", "Bilinmeyen Takım")
    lig = event.get("L", "Bilinmeyen Lig")

    toplam, ust, alt = None, None, None

    # Bahis oranlarını kontrol et
    for bet in event.get('E', []):
        if bet["T"] == 9:
            toplam = bet["C"]
        elif bet["T"] == 10:
            ust = bet["C"]
        elif bet["T"] == 11:
            alt = bet["C"]

    # Çıktıyı yazdır
    print(f"\n🏆 {lig}")
    print(f"⚽ {takim1} vs {takim2}")
    print(f"📌 Toplam: {toplam} | Üst: {ust} | Alt: {alt}")
    print("-" * 50)