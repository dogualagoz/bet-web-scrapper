import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unidecode
import re

options = uc.ChromeOptions()
options.headless = False  
options.add_argument("--disable-blink-features=AutomationControlled")

def start_driver():
    print("\n🔄 Selenium Başlatılıyor...")
    try:
        driver = uc.Chrome(options=options, version_main=133)
        print("✅ ChromeDriver başarıyla başlatıldı.")
        driver.get("https://onwin1772.com/sportsbook/live")
        print("⚠️ Captcha'yı geçmek için 15 saniye bekleniyor...")
        time.sleep(15)
        print("✅ Captcha süresi sona erdi, devam ediliyor...")
        return driver
    except Exception as e:
        print(f"❌ Selenium başlatma hatası: {e}")
        return None

def normalize_team_name(name):
    if not name:
        return ""
    name = unidecode.unidecode(name).lower()
    return unidecode.unidecode(name).lower().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

def get_match_links(driver):
    wait = WebDriverWait(driver, 5)
    match_links = []

    try:
        ligler = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//*[@id='sportsbook-center-scroll']/div/div/div[1]/div/div[2]/div[3]")
        ))

        for lig in ligler:
            maclar = lig.find_elements(By.XPATH, ".//a[contains(@class, 'sb__reset_link')]")
            for mac in maclar:
                durum = "Tanımlanmadı"
                try:
                    minute = mac.find_element(By.CLASS_NAME, "minute--biLWm").text.strip()
                    if minute == "":
                        durum = "Devre Arası"
                except:
                    pass

                link = mac.get_attribute("href")
                if link:
                    match_links.append((link, durum))

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

    print(f"📌 **Toplam {len(match_links)} basketbol maçı bulundu**")
    return match_links

def wait_for_page_load(driver, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "basketball-live-widget--KtoTV"))
        )
        return True
    except:
        return False

def get_team_names(driver):
    try:
        widget = driver.find_element(By.CLASS_NAME, "basketball-live-widget--KtoTV")
        table = widget.find_element(By.CLASS_NAME, "basketball-table--RtybO")
        rows = table.find_elements(By.CLASS_NAME, "basket-row--M1fgV")
        if len(rows) < 2:
            return None, None
        t1 = rows[0].find_element(By.CLASS_NAME, "basket-name--dy3fi").text.strip()
        t2 = rows[1].find_element(By.CLASS_NAME, "basket-name--dy3fi").text.strip()
        return t1, t2
    except:
        return None, None

def clean_odds_text(element):
    text = element.text.strip()
    parts = text.split("\n")
    if len(parts) < 2:
        return None
    return parts[-1]

def get_match_odds(driver, url):
    try:
        print(f"🔍 Maç işleniyor: {url}")
        driver.get(url)

        if not wait_for_page_load(driver, timeout=5):
            print(f"⚠️ Sayfa yüklenmedi, atlanıyor: {url}")
            return None

        takim1, takim2 = get_team_names(driver)
        if not takim1 or not takim2:
            return None

        market_groups = driver.find_elements(By.CLASS_NAME, "market-group--SPHr8")
        match_odds = []

        for group in market_groups:
            try:
                header = group.find_element(By.CLASS_NAME, "ellipsis--_aRxs")
                if "Toplam Sayı Üst/ Alt" != header.text.strip():
                    continue

                outcomes = group.find_elements(By.CLASS_NAME, "outcomes--HBEPX")
                for outcome in outcomes:
                    try:
                        total_value = outcome.find_element(By.CLASS_NAME, "parameter--JXoWS").text.strip()
                        if not total_value.endswith(".5"):
                            continue
                        odds_elements = outcome.find_elements(By.CLASS_NAME, "odds--YbHFY")
                        if len(odds_elements) < 2:
                            continue
                        top = clean_odds_text(odds_elements[0])
                        bottom = clean_odds_text(odds_elements[1])
                        if top and bottom:
                            match_odds.append({
                                "Toplam Oran": total_value,
                                "Üst": top,
                                "Alt": bottom
                            })
                    except:
                        continue
            except:
                continue

        return {"takim1": takim1, "takim2": takim2, "oranlar": match_odds}

    except Exception as e:
        print(f"⚠️ Hata oluştu (Oran Çekme): {e}")
        return None