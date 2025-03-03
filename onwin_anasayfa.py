import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# **Tarayıcıyı başlatma fonksiyonu**
def start_driver():
    print("\n🔄 Selenium Başlatılıyor...")
    options = uc.ChromeOptions()
    options.headless = False  # Tarayıcıyı görünür başlat
    options.add_argument("--disable-blink-features=AutomationControlled")  # Bot algılanmasını önleme
    driver = uc.Chrome(options=options)
    return driver

# **Futbol maçlarının linklerini çekme fonksiyonu**
def get_match_links():
    driver = start_driver()
    url = "https://onwin1764.com/sportsbook/live"

    if not open_page(driver, url):
        print("🚨 Siteye erişilemedi, program duruyor!")
        driver.quit()
        return []

    print("\n🛑 Cloudflare CAPTCHA geçin. 10 saniye bekleniyor...")
    time.sleep(10)  # CAPTCHA için bekleme

    wait = WebDriverWait(driver, 30)

    try:
        # **Sidebar'ı bul**
        sidebar = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "side--PJTtW")))
        print("✅ Sidebar bulundu.")

        # **Futbol kategorisini bul ve tıkla**
        futbol_kategorisi = sidebar.find_element(By.XPATH, "//*[@id='sportsbook-center-scroll']/div/div/div[1]/div/div[2]/div[2]")
        futbol_kategorisi.click()
        print("✅ Futbol kategorisi bulundu ve açıldı.")
        time.sleep(3)  # Açılması için bekleme

        # **Tüm ligleri bul**
        ligler = sidebar.find_elements(By.XPATH, "//*[@id='sportsbook-center-scroll']/div/div/div[1]/div/div[2]/div[2]/div[contains(@class, 'menu-category--DcdaK')]")
        print(f"✅ {len(ligler)} lig bulundu.")

        match_links = []

        # **Her lig içindeki maçları bul**
        for lig in ligler:
            maclar = lig.find_elements(By.XPATH, ".//a[contains(@class, 'sb__reset_link')]")
            for mac in maclar:
                link = mac.get_attribute("href")
                if link:
                    match_links.append(link)

        print(f"\n📌 **Toplam {len(match_links)} maç linki bulundu.**")
        for link in match_links:
            print(f"🌍 Maç Linki: {link}")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

    driver.quit()
    return match_links

# **Sayfa açma fonksiyonu**
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

# **Fonksiyonu çalıştır**
if __name__ == "__main__":
    get_match_links()