from onwin_manual import get_match_odds, get_match_links, start_driver
from xbet import get_1xbet_data
import time
import os
import sys
import difflib
import unidecode
from rapidfuzz import fuzz

SESSION_FILE = "session.log"
LOCK_FILE = ".cache.lock"
EXPIRATION_LIMIT = 7 * 24  
REMOVAL_LIMIT = EXPIRATION_LIMIT + 24  

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(BASE_DIR, SESSION_FILE)
LOCK_PATH = os.path.join(BASE_DIR, LOCK_FILE)
APP_PATH = os.path.abspath(sys.argv[0])  

if os.path.exists(LOCK_PATH):
    print("⚠️ Uyarı: Önceki çalışmadan dosya bulundu! Temizleniyor...")
    os.remove(LOCK_PATH)

if os.path.exists(SESSION_PATH):
    with open(SESSION_PATH, "r") as f:
        start_time = float(f.read().strip())  
else:
    start_time = time.time()
    with open(SESSION_PATH, "w") as f:
        f.write(str(start_time))  

current_time = time.time()
elapsed_hours = (current_time - start_time) / 3600  
if elapsed_hours >= EXPIRATION_LIMIT:
    print("🔴 Program çalışma limiti doldu. Kapatılıyor...")
    time.sleep(3)
    os.remove(SESSION_PATH)  
    sys.exit()

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

with open(LOCK_PATH, "w") as f:
    f.write("ACTIVE")  

driver = start_driver()
if not driver:
    print("❌ Driver başlatılamadı, program sonlandırılıyor.") 
    os.remove(LOCK_PATH)
    sys.exit()

def normalize_team_name(name):
    if not name:
        return ""
    name = unidecode.unidecode(name).lower()
    name = name.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    for word in ["sc", "cf", "afc", "cfc", "club", "team"]:
        name = name.replace(word, "")
    return name

def match_teams(team1, team2):
    ratio1 = difflib.SequenceMatcher(None, normalize_team_name(team1), normalize_team_name(team2)).ratio()
    ratio2 = fuzz.ratio(normalize_team_name(team1), normalize_team_name(team2)) / 100  
    return max(ratio1, ratio2) > 0.65  

checked_links = set()
match_counter = 0
# ... (üst kısım aynı kalıyor)

try:
    while True:
        try:
            matched_games = set()
            
            if match_counter % 5 == 0 or match_counter == 0:
                new_onwin_links = get_match_links(driver)   
                new_links = [link for link in new_onwin_links if link not in checked_links]
                
                if new_links:
                    print(f"📌 **{len(new_links)} yeni maç eklendi.**")
                
                checked_links.update(new_links)
                print(f"📌 **Yeni maç listesi güncellendi: {len(checked_links)} maç var.**")

            for link in checked_links.copy():
                onwin_data = get_match_odds(driver, link)
                if not onwin_data or not onwin_data.get("oranlar"):
                   
                    continue

                xbet_data = get_1xbet_data()  # 🔁 HER MAÇTA XBET VERİSİNİ GÜNCELLE
                matched = False

                for xbet in xbet_data:
                    if match_teams(xbet["takim1"], onwin_data["takim1"]) and match_teams(xbet["takim2"], onwin_data["takim2"]):
                        matched = True
                        for total_odds in xbet["oranlar"]:
                            if total_odds in [o["Toplam Oran"] for o in onwin_data["oranlar"]]:
                                xbet_ust = xbet["oranlar"][total_odds]["Üst"]
                                xbet_alt = xbet["oranlar"][total_odds]["Alt"]
                                onwin_ust = next((o["Üst"] for o in onwin_data["oranlar"] if o["Toplam Oran"] == total_odds), None)
                                onwin_alt = next((o["Alt"] for o in onwin_data["oranlar"] if o["Toplam Oran"] == total_odds), None)

                                if not xbet_ust or not xbet_alt or not onwin_ust or not onwin_alt:
                                    continue

                                try:
                                    result1 = 1/float(xbet_alt) + 1/float(onwin_ust)
                                    result2 = 1/float(xbet_ust) + 1/float(onwin_alt)
                                except ValueError:
                                    continue

                                print(f"{xbet['takim1']} - {xbet['takim2']} | Toplam Oran: {total_odds} | "
                                      f"xbet Alt: {xbet_alt} | onwin Üst: {onwin_ust} | "
                                      f"xbet Üst: {xbet_ust} | onwin Alt: {onwin_alt} | "
                                      f"Sonuç1: {result1:.2f} ({'✅ Uygun' if result1 < 1 else '❌ Uygun Değil'}) | "
                                      f"Sonuç2: {result2:.2f} ({'✅ Uygun' if result2 < 1 else '❌ Uygun Değil'})")

                                if result1 < 0.98 or result2 < 0.98:
                                    print(f"⏳ Oran düşük, 30 saniye izleniyor...")
                                    start_time = time.time()
                                    
                                    while time.time() - start_time < 30:
                                        time.sleep(1)

                                        # 🔁 XBET ve ONWIN VERİSİNİ YENİDEN AL
                                        updated_xbet_data = get_1xbet_data()
                                        updated_onwin = get_match_odds(driver, link)

                                        # 🔄 Maçı eşleştir ve oranları tekrar çek
                                        for updated_xbet in updated_xbet_data:
                                            if match_teams(updated_xbet["takim1"], xbet["takim1"]) and match_teams(updated_xbet["takim2"], xbet["takim2"]):
                                                updated_oranlar = updated_xbet["oranlar"].get(total_odds)
                                                if not updated_oranlar:
                                                    continue

                                                xbet_alt = updated_oranlar["Alt"]
                                                xbet_ust = updated_oranlar["Üst"]
                                                break  # eşleşen maçı bulunca çık

                                        if updated_onwin:
                                            updated_onwin_ust = next((o["Üst"] for o in updated_onwin["oranlar"] if o["Toplam Oran"] == total_odds), None)
                                            updated_onwin_alt = next((o["Alt"] for o in updated_onwin["oranlar"] if o["Toplam Oran"] == total_odds), None)

                                            if updated_onwin_ust and updated_onwin_alt:
                                                try:
                                                    result1 = 1/float(xbet_alt) + 1/float(updated_onwin_ust)
                                                    result2 = 1/float(xbet_ust) + 1/float(updated_onwin_alt)

                                                    print(f"🔁 Güncelleme | Toplam Oran: {total_odds} | "
                                                          f"xbet Alt: {xbet_alt} | onwin Üst: {updated_onwin_ust} | "
                                                          f"xbet Üst: {xbet_ust} | onwin Alt: {updated_onwin_alt} | "
                                                          f"Sonuç1: {result1:.2f} ({'✅' if result1 < 1 else '❌'}) | "
                                                          f"Sonuç2: {result2:.2f} ({'✅' if result2 < 1 else '❌'})")

                                                    if result1 >= 0.99 and result2 >= 0.99:
                                                        print("❌ Oran uygunluğu bozuldu. İzleme sonlandırıldı.")
                                                        break

                                                except:
                                                    break
                                        else:
                                            print("⚠️ Oran verisi alınamadı, izleme sonlandırıldı.")
                                            break

                if not matched:
                    
                    continue

            match_counter += 1

        except Exception as e:
            print(f"⚠️ Hata oluştu: {e}")

except KeyboardInterrupt:
    print("\n🔴 Program manuel olarak durduruldu. Geçici dosyalar temizleniyor...")
    os.remove(LOCK_PATH)
    sys.exit()