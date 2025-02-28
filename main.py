import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1) Chrome ayarları (Bot olarak algılanmayı azaltır)
options = uc.ChromeOptions()
options.headless = False  # Görünür mod (Cloudflare gizli modları tespit edebiliyor)
options.add_argument("--disable-blink-features=AutomationControlled")

# 2) Chrome'u başlat
driver = uc.Chrome(options=options)

# 3) Siteye git
url = "https://onwin1764.com/sportsbook/live"
driver.get(url)

# 4) Cloudflare CAPTCHA’yı manuel geçmen için bekle
print("Lütfen Cloudflare CAPTCHA varsa geçin. 20 saniye bekleniyor...")
time.sleep(20)

# 5) WebDriverWait ayarla
wait = WebDriverWait(driver, 20)

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

        # 🌟 Maç başlıklarını (cell--bkl140) al
        try:
            headers = match.find_elements(By.XPATH, ".//div[contains(@class, 'cell--bkl140')]")
            match_data["Başlıklar"] = [header.text.strip() for header in headers if header.text.strip()]
        except:
            match_data["Başlıklar"] = []

        # 🌟 Maç oranlarını (cell--KxlIy) al
        try:
            odds = match.find_elements(By.XPATH, ".//div[contains(@class, 'cell--KxlIy')]")
            match_data["Oranlar"] = [odd.text.strip() for odd in odds if odd.text.strip()]
        except:
            match_data["Oranlar"] = []

        # 🌟 Tüm veriyi listeye ekle
        matches_data.append(match_data)

except Exception as e:
    print("❌ Hata oluştu:", str(e))

# 6) Tarayıcıyı kapat
time.sleep(5)
driver.quit()

# 📌 Tüm veriyi ekrana yazdıralım
print("\n📌 Tüm Maç Verileri Çekildi!\n")

for index, match in enumerate(matches_data):
    print(f"📌 Maç {index + 1}:")
    print("  🏆 Başlıklar:", ", ".join(match["Başlıklar"]))
    print("  ⚽ Oranlar:", ", ".join(match["Oranlar"]))
    print("-" * 50)  # Ayrım çizgisi