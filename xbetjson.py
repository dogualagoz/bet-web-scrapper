import requests
import json

def save_api_json():
    url = "https://1xlite-931124.top/service-api/LiveFeed/Get1x2_VZip"
    params = {
        "count": 40,  
        "lng": "tr",
        "mode": 4,
        "country": 190,
        "top": "true",
        "partner": 7,
        "virtualSports": "true",
        "noFilterBlockEvent": "true"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        with open("1xbet_api_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print("✅ API yanıtı kaydedildi: 1xbet_api_response.json")

    except requests.exceptions.RequestException as e:
        print(f"API isteği başarısız: {e}")

# Çalıştır
save_api_json()