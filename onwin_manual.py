import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unidecode

# **Selenium Ayarları**
options = uc.ChromeOptions()
options.headless = False  
options.add_argument("--disable-blink-features=AutomationControlled")

# **Driver Başlat**
def start_driver():
    print("\n🔄 Selenium Başlatılıyor...")
    try:
        driver = uc.Chrome(options=options, version_main=135)
        print("✅ ChromeDriver başarıyla başlatıldı.")
        driver.get("https://onwin1774.com/sportsbook/live")
        print("⚠️ Captcha'yı geçmek için 15 saniye bekleniyor...")
        time.sleep(15)  
        print("✅ Captcha süresi sona erdi, devam ediliyor...")
        return driver
    except Exception as e:
        print(f"❌ Selenium başlatma hatası: {e}")
        return None

# **Takım isimlerini normalize et**

def restart_driver():
    global driver, checked_links, match_counter
    print("♻️ Sistem sıfırlanıyor...")

    try:
        driver.quit()
    except:
        pass

    driver = start_driver()
    checked_links = set()
    match_counter = 0

    if not driver:
        print("❌ Yeni driver başlatılamadı.")
        sys.exit()

        
def normalize_team_name(name):
    if not name:
        return ""
    return unidecode.unidecode(name).lower().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

# **Maç linklerini çek**
def get_match_links(driver):
    wait = WebDriverWait(driver, 5)
    match_links = []
    start_time = time.time()

    try:
        ligler = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//*[@id='sportsbook-center-scroll']/div/div/div[1]/div/div[2]/div[2]/div[contains(@class, 'menu-category--DcdaK')]")
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
    print(f"📌 **Toplam {len(match_links)} maç linki bulundu ({elapsed_time:.2f} saniye)**")

    return match_links  

# **Sayfanın yüklendiğini kontrol et**
def wait_for_page_load(driver, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "team--uwjbd"))
        )
        return True
    except:
        return False

# **Oran verisini temizleme fonksiyonu (GÜNCELLENDİ)**
def clean_odds_text(element):
    text = element.text.strip()
    parts = text.split("\n")
    
    # **Eğer oran yoksa, None döndür**
    if len(parts) < 2:
        return None  
    return parts[-1]  # **Sadece sayıyı al**

# **Maç oranlarını çek (GÜNCELLENDİ)**
def get_match_odds(driver, url, track_for_seconds=0):
    try:
        driver.get(url)  
        if not wait_for_page_load(driver, timeout=5):
            print(f"⚠️ Sayfa yüklenmedi, atlanıyor: {url}")
            return None

        # Takım isimlerini çekmeye çalış
        team_elements = []
        retry_start = time.time()
        while time.time() - retry_start < 3:
            team_elements = driver.find_elements(By.CLASS_NAME, "team--uwjbd")
            if len(team_elements) >= 2:
                break
            time.sleep(0.5)

        if len(team_elements) < 2:
            
            return None

        takim1 = normalize_team_name(team_elements[0].text.strip())
        takim2 = normalize_team_name(team_elements[1].text.strip())

        # Market grubunu çekmeye çalış
        market_group = None
        retry_start = time.time()
        while time.time() - retry_start < 3:
            market_groups = driver.find_elements(By.CLASS_NAME, "market-group--SPHr8")
            for group in market_groups:
                try:
                    header = group.find_element(By.CLASS_NAME, "ellipsis--_aRxs")
                    if header.text.strip() == "Toplam Gol Üst/Alt":
                        market_group = group
                        break
                except:
                    continue
            if market_group:
                break
            time.sleep(0.5)

        if not market_group:
          
            return None

        match_odds = []
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

                if not top_value or not bottom_value:
                    continue

                match_odds.append({
                    "Toplam Oran": total_value,
                    "Üst": top_value,
                    "Alt": bottom_value,
                    "Üst Element": odds_elements[0],
                    "Alt Element": odds_elements[1]
                })

            except:
                continue

        if not match_odds:
            
            return None

        # İzleme modu (değişmedi)
        if track_for_seconds > 0:
            ...
            # burası senin mevcut kodunda aynen kalabilir

        return {"takim1": takim1, "takim2": takim2, "oranlar": match_odds}

    except Exception as e:
        print(f"⚠️ Hata oluştu (Oran Çekme): {e}")
        return None