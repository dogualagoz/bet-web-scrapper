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

# **Oranları Çekme Fonksiyonu**
def get_match_odds(driver, url):
    if not open_page(driver, url):
        print("🚨 Siteye erişilemedi, program duruyor!")
        driver.quit()
        return []

    wait = WebDriverWait(driver, 10)

    # **Doğru Market Bölgesini XPath ile Seçiyoruz**
    try:
        market_group = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id='sportsbook-center-scroll']/div/div/div[2]/div/div[5]/div[2]/div[2]/div[6]")
        ))
        print("\n✅ Doğru Market bölgesi bulundu.")
        time.sleep(2)  # Ekstra bekleme süresi (sayfanın tam yüklenmesi için)
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
                continue  # Eğer eksik veri varsa atla

            # **İlk eleman Üst, ikinci eleman Alt oranlarını içerir**
            top_odds_element = outcome_wrappers[0]
            bottom_odds_element = outcome_wrappers[1]

            # **Toplam Oran'ı Al (`parameter--JXoWS` içindeki değeri)**
            try:
                total_value = outcome.find_element(By.CLASS_NAME, "parameter--JXoWS").text.strip()
            except:
                total_value = "Bilinmiyor"

            # **Oranları Çek ve `\n`'den Sonra Gelen Değerleri Kullan**
            try:
                top_value = top_odds_element.find_element(By.CLASS_NAME, "odds--YbHFY").text.strip()
                top_value = top_value.split("\n")[-1]  # Sadece `\n` sonrası kısmı al
            except:
                top_value = "Bilinmiyor"

            try:
                bottom_value = bottom_odds_element.find_element(By.CLASS_NAME, "odds--YbHFY").text.strip()
                bottom_value = bottom_value.split("\n")[-1]  # Sadece `\n` sonrası kısmı al
            except:
                bottom_value = "Bilinmiyor"

            # **Sonuçları Kaydet**
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
    url = "https://onwin1764.com/sportsbook/live/event/ac_milan-ss_lazio%20roma/01907dcb-ab01-7f78-828b-ad063993a523"
    
    odds_data = get_match_odds(driver, url)
    driver.quit()

    # **Sonuçları Göster**
    print("\n✅ Çekilen Oranlar:")
    for data in odds_data:
        print(data)