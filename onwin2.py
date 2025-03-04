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

# **Belirli bir element içinde scroll yapma fonksiyonu**
def scroll_in_element(driver, element, max_attempts=5):
    last_height = driver.execute_script("return arguments[0].scrollHeight;", element)
    for _ in range(max_attempts):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", element)
        time.sleep(1)
        new_height = driver.execute_script("return arguments[0].scrollHeight;", element)
        if new_height == last_height:
            break
        last_height = new_height

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

        # **Tüm ligleri aç (eğer kapalıysa)**
        for lig in ligler:
            try:
                lig.click()
                time.sleep(0.5)
            except:
                continue

        # **Markets bölgesini bul ve içinde scroll yap**
        try:
            container = driver.find_element(By.CLASS_NAME, "markets-main-container--Ui7dX")
            print("🔄 Markets alanında scroll yapılıyor...")
            scroll_in_element(driver, container, 5)
        except Exception as e:
            print(f"⚠️ Sayfa kaydırma hatası: {e}")
            driver.execute_script("window.scrollBy(0, 500);")  # Yedek olarak sayfanın aşağı kaydırılması

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
        return []

    wait = WebDriverWait(driver, 10)  # Daha uzun süre bekleme eklendi

    retries = 0
    market_group = None

    # **Market bölgesinde scroll yapma**
    try:
        container = driver.find_element(By.CLASS_NAME, "markets-main-container--Ui7dX")
        print("🔄 Market bölgesinde scroll yapılıyor...")
        scroll_in_element(driver, container, 5)
    except Exception as e:
        print(f"⚠️ Sayfa kaydırma hatası: {e}")
        driver.execute_script("window.scrollBy(0, 500);")

    # **Market bölgesini bulmaya çalış**
    while retries < 5:
        try:
            market_group = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='sportsbook-center-scroll']/div/div/div[2]/div/div[5]/div[2]/div[2]/div[6]")
            ))
            driver.execute_script("arguments[0].scrollIntoView();", market_group)  
            time.sleep(1)
            print("\n✅ Doğru Market bölgesi bulundu.")
            break
        except:
            print(f"\n⚠️ Doğru Market bölgesi bulunamadı! {retries + 1}. deneme...")
            retries += 1
            driver.execute_script("window.scrollBy(0, 500);")  # Yedek olarak sayfanın aşağı kaydırılması

    if market_group is None:
        print("❌ Market bölgesi bulunamadı, maç atlanıyor...")
        return []

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

            if not total_value.endswith(".5"):
                continue  

            retry_count = 0
            while retry_count < 5:
                try:
                    top_value = top_odds_element.find_element(By.CLASS_NAME, "odds--YbHFY").text.strip().split("\n")[-1]
                    bottom_value = bottom_odds_element.find_element(By.CLASS_NAME, "odds--YbHFY").text.strip().split("\n")[-1]
                    if "+" in top_value or "+" in bottom_value or "-" in top_value or "-" in bottom_value:
                        retry_count += 1
                        time.sleep(0.5)
                        continue
                    break
                except:
                    retry_count += 1
                    time.sleep(0.5)

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
    
    match_links = get_match_links(driver)

    if not match_links:
        print("\n❌ Hiç maç bulunamadı, program sonlandırılıyor!")
        driver.quit()
        exit()

    for index, match_url in enumerate(match_links, start=1):
        print(f"\n🎯 [{index}/{len(match_links)}] Maç için oranlar çekiliyor: {match_url}")
        odds_data = get_match_odds(driver, match_url)

        if not odds_data:
            print("⚠️ Oran bulunamadı, maç atlanıyor.")
            continue

        print("\n✅ Çekilen Oranlar:")
        for data in odds_data:
            print(data)

    driver.quit()