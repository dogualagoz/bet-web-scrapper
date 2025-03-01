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
print("\n🛑 Lütfen Cloudflare CAPTCHA varsa geçin. Sayfanın tam yüklenmesini bekliyoruz...")
time.sleep(10)  # Sayfa yüklenme süresi azaltıldı

# 7) WebDriverWait ayarla (Maksimum 30 saniye bekleme süresi)
wait = WebDriverWait(driver, 30)

# 📌 Tüm maçların verilerini saklayacağımız liste
matches_data = []

try:
    # 🌟 Tüm maçları (event-row--KpnRq) al
    matches = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, "//div[contains(@class, 'event-row--KpnRq')]")
    ))

    print(f"\n📌 Toplam {len(matches)} maç bulundu.\n")

    for match in matches:
        match_data = {}  # **Tek maç için veri saklama**
        
        # 🌟 Takım isimlerini al (`teams--voqkz`)
        try:
            team_elements = match.find_elements(By.XPATH, ".//div[contains(@class, 'teams--voqkz')]")
            if team_elements:
                teams = " - ".join([team.text.strip() for team in team_elements])
            else:
                teams = "Bilinmeyen Takımlar"
        except:
            teams = "Bilinmeyen Takımlar"

        match_data["Takımlar"] = teams

        # 🌟 Oranları al (`cell--KxlIy`)
        all_odds = []
        odds_elements = match.find_elements(By.XPATH, ".//div[contains(@class, 'cell--KxlIy')]")
        for odd in odds_elements:
            if "locked--CPs7M" in odd.get_attribute("class"):
                all_odds.append("Boş")
            else:
                all_odds.append(odd.text.strip())

        # **Eğer oran sayısı 11 değilse, eksik olanları boş yap**
        while len(all_odds) < 11:
            all_odds.append("Boş")

        match_data["Oranlar"] = all_odds

        # **Son 3 oranı `toplam`, `üst`, `alt` olarak eşle**
        match_data["Son Üçlü"] = {
            "toplam": all_odds[-3],
            "ust": all_odds[-2],
            "alt": all_odds[-1]
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
    print(f"📌 {match['Takımlar']}:")
    print("  ⚽ Oranlar:", ", ".join(match["Oranlar"]))
    print(f"  🏆 Toplam: {match['Son Üçlü']['toplam']}, Üst: {match['Son Üçlü']['ust']}, Alt: {match['Son Üçlü']['alt']}")
    print("-" * 50)