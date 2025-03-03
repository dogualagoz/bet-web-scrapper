import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# **Selenium Başlatma Ayarları**
options = uc.ChromeOptions()
options.headless = False  
options.add_argument("--disable-blink-features=AutomationControlled")

# **Driver Başlat**
def start_driver():
    print("\n🔄 Selenium Başlatılıyor...")
    driver = uc.Chrome(options=options)
    return driver

# **Sayfa Açma ve CAPTCHA Bekleme**
def open_page(driver, url, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            driver.get(url)
            print("\n✅ Sayfa açıldı:", url)
            print("\n🛑 Cloudflare CAPTCHA geçin. 10 saniye bekleniyor...")
            time.sleep(10)
            return True
        except Exception as e:
            print(f"❌ Sayfa yüklenemedi! {retries + 1}. deneme... Hata: {e}")
            retries += 1
            time.sleep(5)
    return False

# **Futbol maçlarının linklerini çekme fonksiyonu**
def get_match_links(driver):
    url = "https://onwin1764.com/sportsbook/live"

    if not open_page(driver, url):
        print("🚨 Siteye erişilemedi, program duruyor!")
        return []

    wait = WebDriverWait(driver, 30)
    match_links = []

    try:
        # **Sidebar'ı bul**
        sidebar = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "side--PJTtW")))
        print("✅ Sidebar bulundu.")

        # **Futbol kategorisini bul ve tıkla**
        futbol_kategorisi = sidebar.find_element(By.XPATH, "//*[@id='sportsbook-center-scroll']/div/div/div[1]/div/div[2]/div[2]")
        futbol_kategorisi.click()
        print("✅ Futbol kategorisi bulundu ve açıldı.")
        time.sleep(5)  

        # **Liglerin yüklenmesini bekle**
        ligler = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='sportsbook-center-scroll']/div/div/div[1]/div/div[2]/div[2]/div[contains(@class, 'menu-category--DcdaK')]")))
        print(f"✅ {len(ligler)} lig bulundu.")

        # **Tüm ligleri aç (eğer kapalıysa)**
        for lig in ligler:
            try:
                lig.click()
                time.sleep(1)  
            except:
                continue

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

    return match_links  

# **Oranları Çekme Fonksiyonu**
def get_match_odds(driver, url):
    if not open_page(driver, url):
        print("🚨 Siteye erişilemedi, program duruyor!")
        return []

    wait = WebDriverWait(driver, 10)

    # **Market bölgesini doğru almak için XPATH**
    try:
        market_group = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id='sportsbook-center-scroll']/div/div/div[2]/div/div[5]/div[2]/div[2]/div[6]")
        ))
        print("\n✅ Doğru Market bölgesi bulundu.")
        time.sleep(2)  
    except:
        print("\n⚠️ Doğru Market bölgesi bulunamadı!")
        return []

    # **Tüm `outcomes--HBEPX` bloklarını al**
    outcomes = market_group.find_elements(By.CLASS_NAME, "outcomes--HBEPX")
    match_odds = []

    for outcome in outcomes:
        try:
            outcome_wrappers = outcome.find_elements(By.CLASS_NAME, "outcome-wrapper--lXXkI")

            if len(outcome_wrappers) < 2:
                continue  

            top_odds_element = outcome_wrappers[0]
            bottom_odds_element = outcome_wrappers[1]

            try:
                total_value = outcome.find_element(By.CLASS_NAME, "parameter--JXoWS").text.strip()
            except:
                total_value = "Bilinmiyor"

            try:
                top_value = top_odds_element.find_element(By.CLASS_NAME, "odds--YbHFY").text.strip().split("\n")[-1]  
            except:
                top_value = "Bilinmiyor"

            try:
                bottom_value = bottom_odds_element.find_element(By.CLASS_NAME, "odds--YbHFY").text.strip().split("\n")[-1]  
            except:
                bottom_value = "Bilinmiyor"

            match_odds.append({
                "Toplam Oran": total_value,
                "Üst": top_value,
                "Alt": bottom_value
            })

        except Exception as e:
            print(f"⚠️ Veri çekme hatası: {e}")
            continue

    return match_odds

# **Ana Çalıştırma Kodu**
if __name__ == "__main__":
    driver = start_driver()
    
    # **Ana sayfadan maç linklerini çek**
    match_links = get_match_links(driver)

    if not match_links:
        print("\n❌ Hiç maç bulunamadı, program sonlandırılıyor!")
        driver.quit()
        exit()

    # **Her maça gidip oranları çek**
    for index, match_url in enumerate(match_links, start=1):
        print(f"\n🎯 [{index}/{len(match_links)}] Maç için oranlar çekiliyor: {match_url}")
        odds_data = get_match_odds(driver, match_url)

        print("\n✅ Çekilen Oranlar:")
        for data in odds_data:
            print(data)

    driver.quit()