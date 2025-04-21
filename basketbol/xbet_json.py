import requests
import json

# API URL'si
api_url = "https://1xlite-7209679.top/service-api/LiveFeed/Get1x2_VZip"

# API'nin boş veri dönmesini engellemek için bazı parametreler ekliyoruz.
params = {"count": 1000, "lng": "tr", "mode": 4, "country": 190, "noFilterBlockEvent": "true"}

asd = 123
try:
    # API'ye GET isteği gönder
    response = requests.get(api_url, params=params)
    response.raise_for_status()  # Eğer hata dönerse, yakala

    # JSON verisini al
    data = response.json()

    # JSON verisini bir dosyaya kaydet
    with open("xbet_data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print("✅ API'den gelen veriler başarıyla 'xbet_data.json' dosyasına kaydedildi!")

except requests.exceptions.RequestException as e:
    print(f"❌ API isteğinde bir hata oluştu: {e}")
except json.JSONDecodeError:
    print("❌ API'den geçersiz JSON verisi alındı.")