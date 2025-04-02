import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# **Selenium Ayarları**
options = uc.ChromeOptions()
options.headless = False  
options.add_argument("--disable-blink-features=AutomationControlled")

# **Driver Başlat**
def start_driver():
    print("\n🔄 Selenium Başlatılıyor...")
    try:
        driver = uc.Chrome(options=options, version_main=133)
        print("✅ ChromeDriver başarıyla başlatıldı.")

        # **Captcha için bekle (Sadece İlk Açılışta)**
        driver.get("https://onwin1768.com/sportsbook/live")
        print("⚠️ Captcha'yı geçmek için 10 saniye bekleniyor...")
        time.sleep(15)  
        print("✅ Captcha süresi sona erdi, devam ediliyor...")

        return driver
    except Exception as e:
        print(f"❌ Selenium başlatma hatası: {e}")
        return None

# **Basketbol Maç Linklerini Çek**
def get_match_links(driver):
    wait = WebDriverWait(driver, 5)
    match_links = []
    start_time = time.time()

    try:
        # **Basketbol bölümünü buluyoruz**
        ligler = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//*[@id='sportsbook-center-scroll']/div/div/div[1]/div/div[2]/div[3]")
        ))

        for lig in ligler:
            maclar = lig.find_elements(By.XPATH, ".//a[contains(@class, 'sb__reset_link')]")
            for mac in maclar:
                link = mac.get_attribute("href")
                if link:
                    match_links.append(link)

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

    elapsed_time = time.time() - start_time
    print(f"📌 **Toplam {len(match_links)} basketbol maçı bulundu ({elapsed_time:.2f} saniye)**")

    return match_links  

# **Sayfanın Yüklendiğini Kontrol Et**
def wait_for_page_load(driver, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "basketball-live-widget--KtoTV"))
        )
        return True
    except:
        return False

# **Basketbol Takım İsimlerini Çek**
def get_team_names(driver):
    try:
        # **Maç gösterilen widget'e gir**
        widget = driver.find_element(By.CLASS_NAME, "basketball-live-widget--KtoTV")

        # **basketball table'ı bul**
        table = widget.find_element(By.CLASS_NAME, "basketball-table--RtybO")

        # **tbody içindeki takım satırlarını çek**
        rows = table.find_elements(By.CLASS_NAME, "basket-row--M1fgV")
        if len(rows) < 2:
            print("⚠️ Takım bilgileri eksik, atlanıyor...")
            return None, None

        # **Her iki tr içinde basket-name--dy3fi olan td etiketlerini bul**
        takim1 = rows[0].find_element(By.CLASS_NAME, "basket-name--dy3fi").text.strip()
        takim2 = rows[1].find_element(By.CLASS_NAME, "basket-name--dy3fi").text.strip()

        return takim1, takim2

    except Exception as e:
        print(f"❌ Takım isimleri çekilemedi: {e}")
        return None, None

# **Oran Verisini Temizleme**
def clean_odds_text(element):
    text = element.text.strip()
    parts = text.split("\n")
    
    # **Eğer oran yoksa, None döndür**
    if len(parts) < 2:
        return None  
    return parts[-1]  # **Sadece sayıyı al**

# **Basketbol Maç Oranlarını Çek**
def get_match_odds(driver, url):
    try:
        print(f"🔍 Maç işleniyor: {url}")
        driver.get(url)  
        if not wait_for_page_load(driver, timeout=5):
            print(f"⚠️ Sayfa yüklenmedi, atlanıyor: {url}")
            return None

        # **Takım isimlerini çek**
        takim1, takim2 = get_team_names(driver)
        if not takim1 or not takim2:
            return None

        # **"Toplam Sayı Üst/Alt" marketini bul**
        market_groups = driver.find_elements(By.CLASS_NAME, "market-group--SPHr8")
        market_group = None

        for group in market_groups:
            try:
                header = group.find_element(By.CLASS_NAME, "ellipsis--_aRxs")
                if header.text.strip() == "Toplam Sayı Üst/ Alt":
                    market_group = group
                    break
            except:
                continue

        if not market_group:
            return None

        match_odds = {}
        outcomes = market_group.find_elements(By.CLASS_NAME, "outcomes--HBEPX")

        for outcome in outcomes:
            try:
                total_value = outcome.find_element(By.CLASS_NAME, "parameter--JXoWS").text.strip()
                if not total_value.endswith(".5"):  
                    continue  

                odds_elements = outcome.find_elements(By.CLASS_NAME, "odds--YbHFY")
                if len(odds_elements) < 2:
                    continue

                top_value = clean_odds_text(odds_elements[0])
                bottom_value = clean_odds_text(odds_elements[1])

                # **Eğer oranlardan biri None ise atla**
                if not top_value or not bottom_value:
                    continue  

                match_odds[total_value] = {"Üst": top_value, "Alt": bottom_value}

            except:
                continue

        return {"takim1": takim1, "takim2": takim2, "oranlar": match_odds}

    except Exception as e:
        print(f"⚠️ Hata oluştu (Oran Çekme): {e}")
        return None

# **Tüm Maçları Çek**
def get_all_basketball_matches():
    driver = start_driver()
    if not driver:
        return []

    match_links = get_match_links(driver)
    all_matches = []

    for link in match_links:
        match_data = get_match_odds(driver, link)
        if match_data:
            all_matches.append(match_data)

    driver.quit()
    return all_matches

# **Ana Program**
if __name__ == "__main__":
    matches = get_all_basketball_matches()
    
    print("\n🏀 **Basketbol Maçları & Oranlar**:")
    for match in matches:
        print(f"\n🏆 {match['takim1']} 🆚 {match['takim2']}")
        for total, odds in match["oranlar"].items():
            print(f"📊 {total}  | Üst: {odds['Üst']} | Alt: {odds['Alt']} |")