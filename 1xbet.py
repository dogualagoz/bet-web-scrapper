import requests
import json

# API URL'si
url = "https://1xlite-819117.top/service-api/LineFeed/GetExpressDayExtendedZip?partner=7&lng=tr&page=0"

# HTTP başlıkları
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15",
    "Referer": "https://1xlite-819117.top/tr/live/football",
    "x-requested-with": "XMLHttpRequest",
    "x-svc-source": "__BETTING_APP__"
}

# Çerezler (Kimlik doğrulama için)
cookies = {
    "SESSION": "bd00f4a2ca5193abe3442792bf1d4e7c",
    "lng": "tr"
}

# API isteği gönderme
response = requests.get(url, headers=headers, cookies=cookies)

# Yanıtı kontrol et
if response.status_code == 200:
    print("✅ API Başarıyla Çekildi!\n")
    
    # Yanıtı JSON formatına çevir
    try:
        data = response.json()
        
        # JSON verisini ekrana yazdır
        print("📌 API Yanıtı:")
        print(json.dumps(data, indent=4, ensure_ascii=False))  # JSON verisini düzgün şekilde yazdır
        
    except json.JSONDecodeError:
        print("❌ JSON çözümlenirken hata oluştu.")
else:
    print(f"❌ API Hatası: {response.status_code}")