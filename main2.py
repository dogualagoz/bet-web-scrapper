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
print("\n🛑 Lütfen Cloudflare CAPTCHA varsa geçin. 60 saniye bekleniyor...")
time.sleep(60)

# 7) WebDriverWait ayarla (120 saniye bekleyelim)
wait = WebDriverWait(driver, 120)

# 📌 Tüm veriyi saklayacağımız liste
matches_data = []

try:
    # 🌟 Tüm maçları (row-renderer--xfjWW) al
    matches = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, "//div[contains(@class, 'row-renderer--xfjWW') and @role='gridcell']")
    ))

    print(f"\n📌 Toplam {len(matches)} maç bulundu.\n")

    for index, match in enumerate(matches):
        match_data = {}  # Tek bir maçın verilerini saklayacağımız dict

        # 🌟 **Doğrudan `scroll_container` içindeki div[7]'yi al**
        try:
            headers = match.find_elements(By.XPATH, ".//*[@id='scroll_container']/div/div[1]/div/div/div[2]/div[7]")
            match_data["Başlıklar"] = [header.get_attribute("innerText").strip() for header in headers if header.get_attribute("innerText").strip()]
        except:
            match_data["Başlıklar"] = ["YOK"]  # Eğer başlık bulunamazsa "YOK" yazsın

        # 🌟 Maç oranlarını (cell--KxlIy) al
        try:
            odds = match.find_elements(By.XPATH, ".//div[contains(@class, 'cell--KxlIy')]")
            match_data["Oranlar"] = [odd.text.strip() for odd in odds if odd.text.strip()]
        except:
            match_data["Oranlar"] = ["YOK"]

        # 🌟 Tüm veriyi listeye ekle
        matches_data.append(match_data)

except Exception as e:
    print("❌ Hata oluştu:", str(e))

# 8) Tarayıcıyı kapat
time.sleep(5)
driver.quit()

# 📌 Tüm veriyi ekrana yazdıralım
print("\n📌 Tüm Maç Verileri Çekildi!\n")

for index, match in enumerate(matches_data):
    print(f"📌 Maç {index + 1}:")
    print("  🏆 Başlıklar:", ", ".join(match["Başlıklar"]))
    print("  ⚽ Oranlar:", ", ".join(match["Oranlar"]))
    print("-" * 50)  # Ayrım çizgisi 