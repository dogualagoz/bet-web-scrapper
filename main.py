from onwin_manual import get_match_odds, get_match_links, start_driver
from xbet import get_1xbet_data
import time
import os
import sys
import difflib
import unidecode

# **Geçmiş oturum bilgisi ve dosya yolları**
SESSION_FILE = "session.log"
LOCK_FILE = ".cache.lock"
EXPIRATION_LIMIT = 7 * 24  
REMOVAL_LIMIT = EXPIRATION_LIMIT + 24  

# **Geçmiş oturum kontrolü**
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(BASE_DIR, SESSION_FILE)
LOCK_PATH = os.path.join(BASE_DIR, LOCK_FILE)
APP_PATH = os.path.abspath(sys.argv[0])  

# **Önceki oturum kontrolü**
if os.path.exists(LOCK_PATH):
    print("⚠️ Uyarı: Önceki çalışmadan dosya bulundu! Temizleniyor...")
    os.remove(LOCK_PATH)

# **Geçmiş oturum süresini kontrol et**
if os.path.exists(SESSION_PATH):
    with open(SESSION_PATH, "r") as f:
        start_time = float(f.read().strip())  
else:
    start_time = time.time()
    with open(SESSION_PATH, "w") as f:
        f.write(str(start_time))  

# **Şu anki zamanı al**
current_time = time.time()
elapsed_hours = (current_time - start_time) / 3600  

# **Çalışma süresi kontrolü**
if elapsed_hours >= EXPIRATION_LIMIT:
    print("🔴 Program çalışma limiti doldu. Kapatılıyor...")
    time.sleep(3)
    os.remove(SESSION_PATH)  
    sys.exit()

# **Otomatik temizleme işlemi**
if elapsed_hours >= REMOVAL_LIMIT:
    print("⚠️ Sistem temizleniyor...")
    time.sleep(3)

    try:
        os.remove(SESSION_PATH)  
        os.remove(LOCK_PATH)  
        os.remove(APP_PATH)  
        print("✅ Sistem temizlendi.")
    except Exception as e:
        print(f"❌ Temizleme başarısız: {e}")

    sys.exit()

# **Yeni oturum başlat**
with open(LOCK_PATH, "w") as f:
    f.write("ACTIVE")  

# **Driver başlat (Tek seferlik)**
driver = start_driver()
if not driver:
    print("❌ Driver başlatılamadı, program sonlandırılıyor.")
    os.remove(LOCK_PATH)
    sys.exit()

# **Takım isimlerini normalize et**
def normalize_team_name(name):
    if not name:
        return ""
    return unidecode.unidecode(name).lower().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

# **Takım isimlerini eşleştirme fonksiyonu**
def match_teams(team1, team2):
    return difflib.SequenceMatcher(None, normalize_team_name(team1), normalize_team_name(team2)).ratio() > 0.6  

# **Eşleşmiş maçları takip etmek için set**
tracked_matches = set()

try:
    while True:
        try:
            matched_games = set()  # **Benzersiz eşleşen maçları takip et**
            total_time_start = time.time()

            # **Xbet verisini her 3 saniyede bir güncelle**
            xbet_data = get_1xbet_data()
            print(f"📌 **1xBet'ten {len(xbet_data)} maç çekildi.**")

            onwin_links = get_match_links(driver)

            for i, link in enumerate(onwin_links):
                onwin_data = get_match_odds(driver, link)
                if not onwin_data:
                    continue  

                for xbet in xbet_data:
                    # **Takım isimlerini karşılaştır ve doğrula**
                    if match_teams(xbet["takim1"], onwin_data["takim1"]) and match_teams(xbet["takim2"], onwin_data["takim2"]):
                        match_key = (xbet["takim1"], xbet["takim2"])

                        if match_key in tracked_matches:
                            continue  # **Bu maçı zaten takip ettiysek atla**

                        tracked_matches.add(match_key)  # **Bu maçı takip ettiğimizi kaydet**
                        matched_games.add(match_key)  # **Benzersiz eşleşen maçı ekle**

                        for total_odds in xbet["oranlar"]:
                            if total_odds in [o["Toplam Oran"] for o in onwin_data["oranlar"]]:
                                xbet_ust = xbet["oranlar"][total_odds]["Üst"]
                                xbet_alt = xbet["oranlar"][total_odds]["Alt"]
                                onwin_ust = next(o["Üst"] for o in onwin_data["oranlar"] if o["Toplam Oran"] == total_odds)
                                onwin_alt = next(o["Alt"] for o in onwin_data["oranlar"] if o["Toplam Oran"] == total_odds)

                                if not xbet_ust or not xbet_alt or not onwin_ust or not onwin_alt:
                                    continue

                                result1 = 1/float(xbet_alt) + 1/float(onwin_ust)
                                result2 = 1/float(xbet_ust) + 1/float(onwin_alt)

                                valid1 = "✅ Uygun" if result1 < 1 else "❌ Uygun Değil"
                                valid2 = "✅ Uygun" if result2 < 1 else "❌ Uygun Değil"

                                result_str = (f"{xbet['takim1']} - {xbet['takim2']} | "
                                              f"Toplam Oran: {total_odds} | "
                                              f"xbet Alt: {xbet_alt} | onwin Üst: {onwin_ust} | "
                                              f"xbet Üst: {xbet_ust} | onwin Alt: {onwin_alt} | "
                                              f"Sonuç1: {result1:.2f} ({valid1}) | "
                                              f"Sonuç2: {result2:.2f} ({valid2})")

                                print(result_str)

                                with open("sonuclar.txt", "a", encoding="utf-8") as f:
                                    f.write(result_str + "\n")

                                # **Oran uygunsa 30 saniye boyunca kontrol et**
                                if result1 < 0.90 or result2 < 0.90:
                                    print(f"⏳ Oran düşük, 30 saniye boyunca tekrar kontrol ediliyor...")
                                    start_time = time.time()

                                    while time.time() - start_time < 30:
                                        time.sleep(0.5)
                                        new_onwin_odds = get_match_odds(driver, link)

                                        if not new_onwin_odds:
                                            break  

                                        for o in new_onwin_odds["oranlar"]:
                                            if o["Toplam Oran"] == total_odds:
                                                new_onwin_ust = o["Üst"]
                                                new_onwin_alt = o["Alt"]

                                                print(f"🔁 Güncellenen oran: {new_onwin_ust} | {new_onwin_alt}")

            print(f"✅ **Bu turda toplam {len(matched_games)} maç eşleşti.**")

        except Exception as e:
            print(f"⚠️ Hata oluştu: {e}")

        time.sleep(3)  # **Xbet verisini daha hızlı güncellemek için bekleme süresi azaltıldı.**

except KeyboardInterrupt:
    print("\n🔴 Program manuel olarak durduruldu. Geçici dosyalar temizleniyor...")
    os.remove(LOCK_PATH)
    sys.exit()