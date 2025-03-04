import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# **Chrome ayarları (Bot olarak algılanmayı azaltır)**
options = uc.ChromeOptions()
options.headless = False  # Görünür mod
options.add_argument("--disable-blink-features=AutomationControlled")

# **WebDriver başlatma fonksiyonu**
def start_driver():
    print("\n🔄 Selenium Başlatılıyor...")
    driver = uc.Chrome(options=options)
    return driver

# **Sayfayı açma fonksiyonu**
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
            time.sleep(5)
    return False

# **Ana fonksiyon: Onwin verilerini çekme**
def get_onwin_data():
    global driver

    # **WebDriver başlat (Eğer daha önce başlatılmadıysa)**
    if 'driver' not in globals():
        driver = start_driver()

    url = "https://onwin1765.com/sportsbook/live"
    if not open_page(driver, url):
        print("🚨 Siteye erişilemedi, program duruyor!")
        driver.quit()
        return []

    # **Cloudflare CAPTCHA geçmek için bekleme süresi**
    print("\n🛑 Cloudflare CAPTCHA geçin. 10 saniye bekleniyor...")
    time.sleep(10)

    # **WebDriverWait ayarla**
    wait = WebDriverWait(driver, 30)
    matches_data = []

    try:
        # **Tüm maçları al**
        matches = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//div[contains(@class, 'event-row--KpnRq')]")
        ))

        print(f"\n📌 Toplam {len(matches)} maç bulundu.\n")

        for match in matches:
            match_data = {}

            # **Takım isimlerini al**
            try:
                team_elements = match.find_elements(By.XPATH, ".//div[contains(@class, 'teams--voqkz')]")
                if team_elements:
                    teams = team_elements[0].text.strip().split("\n")
                    takim1 = teams[0] if len(teams) > 0 else "Bilinmeyen"
                    takim2 = teams[1] if len(teams) > 1 else "Bilinmeyen"
                else:
                    takim1, takim2 = "Bilinmeyen", "Bilinmeyen"
            except:
                takim1, takim2 = "Bilinmeyen", "Bilinmeyen"

            match_data["takim1"] = takim1
            match_data["takim2"] = takim2

            # **Oranları al**
            all_odds = []
            odds_elements = match.find_elements(By.XPATH, ".//div[contains(@class, 'cell--KxlIy')]")
            for odd in odds_elements:
                if "locked--CPs7M" in odd.get_attribute("class"):
                    all_odds.append("Boş")
                else:
                    all_odds.append(odd.text.strip())

            # **Eksik oranları tamamla**
            while len(all_odds) < 11:
                all_odds.append("Boş")

            match_data["Oranlar"] = all_odds
            match_data["toplam"] = all_odds[-3]
            match_data["ust"] = all_odds[-2]
            match_data["alt"] = all_odds[-1]

            matches_data.append(match_data)

    except Exception as e:
        print("❌ Hata oluştu:", str(e))

    return matches_data

