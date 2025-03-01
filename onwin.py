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
print("\n🛑 Cloudflare CAPTCHA geçin. 10 saniye bekleniyor...")
time.sleep(10)

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
                teams = team_elements[0].text.strip().split("\n")  # TAKIM ADLARINI BÖLÜYORUZ
                takim1 = teams[0] if len(teams) > 0 else "Bilinmeyen"
                takim2 = teams[1] if len(teams) > 1 else "Bilinmeyen"
            else:
                takim1, takim2 = "Bilinmeyen", "Bilinmeyen"
        except:
            takim1, takim2 = "Bilinmeyen", "Bilinmeyen"

        match_data["takim1"] = takim1
        match_data["takim2"] = takim2

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
        match_data["toplam"] = all_odds[-3]
        match_data["ust"] = all_odds[-2]
        match_data["alt"] = all_odds[-1]

        # **Maçı listeye ekle**
        matches_data.append(match_data)

except Exception as e:
    print("❌ Hata oluştu:", str(e))

# 8) Tarayıcıyı kapat
time.sleep(5)
driver.quit()

# 📌 **Tüm maçları ekrana yazdıralım**
print("\n✅ ONWIN Verileri Çekildi!\n")

for index, match in enumerate(matches_data):
    print(match)

# 📌 **Onwin Verilerini `main.py`ye Gönderme**
def get_onwin_data():
    return matches_data