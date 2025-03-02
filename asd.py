import requests
import json

def inspect_1xbet_api():
    url = "https://1xlite-819117.top/service-api/LiveFeed/Get1x2_VZip"
    params = {
        "count": 5,  # İlk 5 veriyi çekelim
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

    # API yanıtını JSON dosyasına kaydet
    with open("xbet_api_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("\n✅ API Yanıtı `xbet_api_response.json` olarak kaydedildi! Aç ve incele.")

inspect_1xbet_api()