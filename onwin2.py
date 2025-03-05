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
    driver = uc.Chrome(options=options, version_main=133)
    return driver

# **Sayfa Açma ve CAPTCHA Bekleme**
def open_page(driver, url, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            driver.get(url)
            print("\n✅ Sayfa açıldı:", url)
            time.sleep(4)  # Sayfanın tamamen yüklenmesi için bekleme
            return True
        except Exception as e:
            print(f"❌ Sayfa yüklenemedi! {retries + 1}. deneme... Hata: {e}")
            retries += 1
            time.sleep(1)
    return False

# **Futbol maçlarının linklerini çekme fonksiyonu**
def get_match_links(driver):
    url = "https://onwin1765.com/sportsbook/live"

    if not open_page(driver, url):
        print("🚨 Siteye erişilemedi, program duruyor!")
        return []

    wait = WebDriverWait(driver, 30)
    match_links = []

    try:
        # **Sidebar'ı bul**
        sidebar = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "side--PJTtW")))
        print("✅ Sidebar bulundu.")

        print("✅ Futbol kategorisi bulundu ve açıldı.")
        time.sleep(2)

        # **Liglerin yüklenmesini bekle**
        ligler = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//*[@id='sportsbook-center-scroll']/div/div/div[1]/div/div[2]/div[2]/div[contains(@class, 'menu-category--DcdaK')]")
        ))
        print(f"✅ {len(ligler)} lig bulundu.")

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
        print("🚨 Sayfa açılmadı, maç atlanıyor!")
        return None

    wait = WebDriverWait(driver, 10)  # Daha uzun süre bekleme eklendi

    try:
        # **Takım isimlerini bul**
        team_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "team--uwjbd")))
        if len(team_elements) < 2:
            print("⚠️ Takım isimleri bulunamadı, maç atlanıyor.")
            return None

        takim1 = team_elements[0].text.strip()
        takim2 = team_elements[1].text.strip()

        print(f"\n⚽ Maç: {takim1} - {takim2}")

        # **Doğru Market bölgesini bul**
        market_groups = driver.find_elements(By.CLASS_NAME, "market-group--SPHr8")
        market_group = None

        for group in market_groups:
            try:
                header = group.find_element(By.CLASS_NAME, "ellipsis--_aRxs")
                if header.text.strip() == "Toplam Gol Üst/Alt":
                    market_group = group
                    break
            except:
                continue

        if not market_group:
            print("❌ Doğru Market bölgesi bulunamadı, maç atlanıyor...")
            return None

        print("\n✅ Doğru Market bölgesi bulundu.")

        # **Oranları çek**
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

                if not total_value.endswith(".5"):  # Sadece buçuklu oranları al
                    continue  

                retry_count = 0
                while retry_count < 3:
                    try:
                        top_value = top_odds_element.find_element(By.CLASS_NAME, "odds--YbHFY").text.strip().split("\n")[-1]
                        bottom_value = bottom_odds_element.find_element(By.CLASS_NAME, "odds--YbHFY").text.strip().split("\n")[-1]
                        break
                    except:
                        retry_count += 1
                        time.sleep(0.3)

                match_odds.append({
                    "Toplam Oran": total_value,
                    "Üst": top_value,
                    "Alt": bottom_value
                })

            except Exception as e:
                print(f"⚠️ Veri çekme hatası: {e}")
                continue

        return {
            "takim1": takim1,
            "takim2": takim2,
            "oranlar": match_odds
        }

    except Exception as e:
        print(f"⚠️ Genel hata oluştu: {e}")
        return None

# **Ana Çalıştırma Kodu**
if __name__ == "__main__":
    driver = start_driver()
    
    match_links = get_match_links(driver)

    if not match_links:
        print("\n❌ Hiç maç bulunamadı, program sonlandırılıyor!")
        driver.quit()
        exit()

    matches_data = []  # Bellekte maç verilerini saklamak için liste

    for index, match_url in enumerate(match_links, start=1):
        print(f"\n🎯 [{index}/{len(match_links)}] Maç için oranlar çekiliyor: {match_url}")
        match_data = get_match_odds(driver, match_url)

        if match_data:
            matches_data.append(match_data)

    driver.quit()

    # Bellekte tutulan verileri kontrol et
    print("\n📊 **Tüm Maç Verileri:**")
    for match in matches_data:
        print(match)
