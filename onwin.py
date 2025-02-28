import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1) Chrome ayarları (Bot olarak algılanmayı azaltır)
options = uc.ChromeOptions()
options.headless = False  # Görünür mod (Cloudflare gizli modları tespit edebiliyor)
options.add_argument("--disable-blink-features=AutomationControlled")

# 2) Tarayıcıyı başlatma fonksiyonu
def start_driver():
    print("\n🔄 Selenium Başlatılıyor...")
    driver = uc.Chrome(options=options)
    return driver

# 3) Sayfayı açma fonksiyonu
def open_page(driver, url, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            driver.get(url)
            print("\n✅ Sayfa açıldı:", url)
            return True
        except Exception as e:
            print(f"❌ Sayfa yüklenemedi! {retries + 1}. deneme... Hata: {e}")
            retries += 1
            time.sleep(5)  # Biraz bekleyip tekrar dene
    return False

# 4) WebDriver başlat
driver = start_driver()

# 5) Siteye git
url = "https://onwin1764.com/sportsbook/live"
if not open_page(driver, url):
    print("🚨 3 deneme sonunda siteye erişilemedi, program duruyor!")
    driver.quit()
    exit()

# 6) Cloudflare CAPTCHA’yı manuel geçmen için bekle
print("\n🛑 Lütfen Cloudflare CAPTCHA varsa geçin. 30 saniye bekleniyor...")
time.sleep(30)

# 7) WebDriverWait ayarla (Maksimum 60 saniye bekleme süresi)
wait = WebDriverWait(driver, 60)

# 📌 Tüm maçların verilerini saklayacağımız liste
matches_data = []

try:
    # 🌟 Tüm ligleri (row-renderer--xfjWW) al
    leagues = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, "//div[contains(@class, 'row-renderer--xfjWW') and @role='gridcell']")
    ))

    print(f"\n📌 Toplam {len(leagues)} lig bulundu.\n")

    for league in leagues:
        all_odds = []  # **Bu lig içindeki tüm oranları geçici olarak saklayacağız.**

        # 🌟 Oranları al (`cell--KxlIy`)
        odds_elements = league.find_elements(By.XPATH, ".//div[contains(@class, 'cell--KxlIy')]")
        for odd in odds_elements:
            # Eğer oran kitli ise "Boş" yazacağız.
            if "locked--CPs7M" in odd.get_attribute("class"):
                all_odds.append("Boş")
            else:
                all_odds.append(odd.text.strip())

        # **Maçları oranlara göre ayıracağız.**
        num_matches = len(all_odds) // 11  # Her maçın tam 11 oranı olmalı
        match_list = [all_odds[i:i + 11] for i in range(0, len(all_odds), 11)]

        for idx, match_odds in enumerate(match_list):
            if len(match_odds) == 11:
                match_data = {}  # **Tek maç için veri saklama**

                # **Oranları sakla**
                match_data["Oranlar"] = match_odds

                # **Son 3 oranı `toplam`, `üst`, `alt` olarak eşle**
                match_data["Son Üçlü"] = {
                    "toplam": match_odds[-3],
                    "ust": match_odds[-2],
                    "alt": match_odds[-1]
                }

                # **Maçı listeye ekle**
                matches_data.append(match_data)

except Exception as e:
    print("❌ Hata oluştu:", str(e))

# 8) Tarayıcıyı kapat
time.sleep(5)
driver.quit()

# 📌 **Tüm maçları ekrana yazdıralım**
print("\n📌 Tüm Maç Verileri Çekildi!\n")

for index, match in enumerate(matches_data):
    print(f"📌 Maç {index + 1}:")
    print("  ⚽ Oranlar:", ", ".join(match["Oranlar"]))
    print(f"  🏆 Toplam: {match['Son Üçlü']['toplam']}, Üst: {match['Son Üçlü']['ust']}, Alt: {match['Son Üçlü']['alt']}")
    print("-" * 50)  # Ayrım çizgisi