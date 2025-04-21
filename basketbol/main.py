from onwin import get_match_odds, get_match_links, start_driver, restart_driver
from xbet import get_basketball_data
import time
import os
import sys
import difflib
import unidecode
from rapidfuzz import fuzz
import re

SESSION_FILE = "session_basket.log"
LOCK_FILE = ".cache_basket.lock"
EXPIRATION_LIMIT = 7 * 24
REMOVAL_LIMIT = EXPIRATION_LIMIT + 24

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(BASE_DIR, SESSION_FILE)
LOCK_PATH = os.path.join(BASE_DIR, LOCK_FILE)
APP_PATH = os.path.abspath(sys.argv[0])

if os.path.exists(LOCK_PATH):
    print("⚠️ Önceki oturum kilidi bulundu. Temizleniyor...")
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
    print("🔴 Çalışma süresi doldu. Program kapatılıyor.")
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
    except Exception as e:
        print(f"❌ Temizlik hatası: {e}")
    sys.exit()

with open(LOCK_PATH, "w") as f:
    f.write("ACTIVE")

driver = start_driver()
if not driver:
    print("❌ Driver başlatılamadı.")
    os.remove(LOCK_PATH)
    sys.exit()

def normalize_team_name(name):
    name = unidecode.unidecode(name or "").lower()
    return re.sub(r"\s|-|\(.*?\)|u\d+|reserves|women|w\b", "", name)

def find_best_match(onwin_team1, onwin_team2, xbet_data, threshold=0.6):
    def score(n1, n2):
        n1 = normalize_team_name(n1)
        n2 = normalize_team_name(n2)
        return max(difflib.SequenceMatcher(None, n1, n2).ratio(), fuzz.ratio(n1, n2) / 100)

    best_match, best_score = None, 0
    for x in xbet_data:
        s1 = score(onwin_team1, x["takim1"])
        s2 = score(onwin_team2, x["takim2"])
        if s1 >= threshold and s2 >= threshold and (s1 + s2)/2 > best_score:
            best_match = x
            best_score = (s1 + s2)/2
    return best_match

checked_links = set()
match_counter = 0

try:
    while True:
        try:
            if match_counter > 0 and match_counter % 50 == 0:
                print("♻️ 50 maç kontrol edildi. Driver resetleniyor...")
                driver.quit()
                driver = restart_driver()
                checked_links.clear()

            if match_counter % 5 == 0 or match_counter == 0:
                try:
                    new_links = get_match_links(driver)
                    new_links = [l for l in new_links if l not in checked_links]
                    if new_links:
                        print(f"📌 {len(new_links)} yeni devre arası maçı bulundu.")
                    checked_links.update(new_links)
                    print(f"📌 Toplam {len(checked_links)} devre arası maç işleniyor.")
                except Exception as e:
                    print(f"⚠️ Link alınamadı: {e}")
                    time.sleep(3)
                    continue

            if not checked_links:
                print("⌛ Devre arası maç yok. 30 saniye bekleniyor...")
                time.sleep(30)
                continue

            for link in list(checked_links):
                try:
                    onwin_data = get_match_odds(driver, link)
                    if not onwin_data or not onwin_data.get("oranlar"):
                        continue

                    xbet_data = get_basketball_data()
                    if not xbet_data:
                        continue

                    matched = find_best_match(onwin_data["takim1"], onwin_data["takim2"], xbet_data)
                    if not matched:
                        continue

                    for total in matched["oranlar"]:
                        if total in [o["Toplam Oran"] for o in onwin_data["oranlar"]]:
                            x_u = matched["oranlar"][total]["Üst"]
                            x_a = matched["oranlar"][total]["Alt"]
                            o_u = next((o["Üst"] for o in onwin_data["oranlar"] if o["Toplam Oran"] == total), None)
                            o_a = next((o["Alt"] for o in onwin_data["oranlar"] if o["Toplam Oran"] == total), None)

                            if not x_u or not x_a or not o_u or not o_a:
                                continue

                            try:
                                r1 = 1/float(x_a) + 1/float(o_u)
                                r2 = 1/float(x_u) + 1/float(o_a)
                            except:
                                continue

                            print(f"{matched['takim1']} - {matched['takim2']} | Toplam: {total} | "
                                  f"xbet Alt: {x_a} | onwin Üst: {o_u} | "
                                  f"xbet Üst: {x_u} | onwin Alt: {o_a} | "
                                  f"Sonuç1: {r1:.2f} ({'✅' if r1 < 1 else '❌'}) | "
                                  f"Sonuç2: {r2:.2f} ({'✅' if r2 < 1 else '❌'})")

                            if r1 < 0.98 or r2 < 0.98:
                                print("⏳ İzleme başlatıldı...")
                                start = time.time()
                                while time.time() - start < 30:
                                    try:
                                        xbet_new = get_basketball_data()
                                        onwin_new = get_match_odds(driver, link)
                                        matched_new = find_best_match(matched["takim1"], matched["takim2"], xbet_new)
                                        if not onwin_new or not matched_new:
                                            break

                                        update = matched_new["oranlar"].get(total)
                                        if not update:
                                            continue

                                        x_a = update["Alt"]
                                        x_u = update["Üst"]
                                        o_u = next((o["Üst"] for o in onwin_new["oranlar"] if o["Toplam Oran"] == total), None)
                                        o_a = next((o["Alt"] for o in onwin_new["oranlar"] if o["Toplam Oran"] == total), None)

                                        if not x_a or not x_u or not o_u or not o_a:
                                            continue

                                        r1 = 1/float(x_a) + 1/float(o_u)
                                        r2 = 1/float(x_u) + 1/float(o_a)

                                        print(f"🔁 Güncelleme | xbet Alt: {x_a} | onwin Üst: {o_u} | "
                                              f"xbet Üst: {x_u} | onwin Alt: {o_a} | "
                                              f"Sonuç1: {r1:.2f} ({'✅' if r1 < 1 else '❌'}) | "
                                              f"Sonuç2: {r2:.2f} ({'✅' if r2 < 1 else '❌'})")

                                        if r1 >= 0.99 and r2 >= 0.99:
                                            print("❌ Oran bozuldu. İzleme bitirildi.")
                                            break
                                    except:
                                        break
                                    time.sleep(1)

                except Exception as err:
                    print(f"⚠️ Maç işleme hatası: {err}")
                    continue

            match_counter += 1

        except Exception as err:
            print(f"⚠️ Döngü hatası: {err}")
            time.sleep(3)

except KeyboardInterrupt:
    print("\n🔴 Durduruldu. Temizlik yapılıyor...")
    os.remove(LOCK_PATH)
    sys.exit()