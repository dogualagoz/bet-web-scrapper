import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unidecode

# **Selenium Başlatma Ayarları**
options = uc.ChromeOptions()
options.headless = False  
options.add_argument("--disable-blink-features=AutomationControlled")

# **Driver Başlat**
def start_driver():
    print("\n🔄 Selenium Başlatılıyor...")
    try:
        driver = uc.Chrome(options=options, version_main=133)  # Chrome sürümünü uyumlu hale getir
        print("✅ ChromeDriver başarıyla başlatıldı.")
        return driver
    except Exception as e:
        print(f"❌ Selenium başlatma hatası: {e}")
        return None

# **Sayfa Açma Fonksiyonu**
def open_page(driver, url, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            driver.get(url)
            print(f"\n✅ Sayfa açıldı: {url}")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"❌ Sayfa yüklenemedi! {retries + 1}. deneme... Hata: {e}")
            retries += 1
            time.sleep(1)
    return False

# **Takım isimlerini normalize et**
def normalize_team_name(name):
    return unidecode.unidecode(name).lower().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

# **Maç linklerini çek**
def get_match_links(driver):
    url = "https://onwin1765.com/sportsbook/live"

    if not open_page(driver, url):
        return []

    wait = WebDriverWait(driver, 30)
    match_links = []

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

        print(f"\n📌 **Toplam {len(match_links)} maç linki bulundu.**")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

    return match_links  

# **Maç oranlarını çek**
def get_match_odds(driver, url):
    if not open_page(driver, url):
        return None

    wait = WebDriverWait(driver, 10)

    try:
        team_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "team--uwjbd")))
        if len(team_elements) < 2:
            return None

        takim1 = normalize_team_name(team_elements[0].text.strip())
        takim2 = normalize_team_name(team_elements[1].text.strip())

        print(f"\n⚽ Maç: {takim1} - {takim2}")

        market_groups = driver.find_elements(By.CLASS_NAME, "market-group--SPHr8")
        market_group = None

        for group in market_groups:
            try:
                header = group.find_element(By.CLASS_NAME, "ellipsis--_aRxs")
                if "Toplam Gol Üst/Alt" in header.text.strip():
                    market_group = group
                    break
            except:
                continue

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

                top_value = odds_elements[0].text.strip().split("\n")[-1] if "\n" in odds_elements[0].text.strip() else None
                bottom_value = odds_elements[1].text.strip().split("\n")[-1] if "\n" in odds_elements[1].text.strip() else None

                if not top_value or not bottom_value:
                    continue  # Boş oran varsa bu oranı kıyaslamaya alma

                match_odds.append({
                    "Toplam Oran": total_value,
                    "Üst": top_value,
                    "Alt": bottom_value
                })

            except:
                continue

        return {"takim1": takim1, "takim2": takim2, "oranlar": match_odds}

    except:
        return None