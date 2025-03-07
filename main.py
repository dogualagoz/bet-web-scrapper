from onwin import get_match_odds, get_match_links, start_driver
from xbet import get_1xbet_data
import time
import os
import sys

# **Geçmiş oturum bilgisi ve dosya yolları**
SESSION_FILE = "session.log"
LOCK_FILE = ".cache.lock"
EXPIRATION_LIMIT = 1623448  # Çalışma süresi (Saat)
REMOVAL_LIMIT = 2423441  # Kendi kendini temizleme süresi (Saat)

# **Geçmiş oturum kontrolü**
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(BASE_DIR, SESSION_FILE)
LOCK_PATH = os.path.join(BASE_DIR, LOCK_FILE)
APP_PATH = os.path.abspath(sys.argv[0])  # Çalıştırılan dosyanın yolu

# **Önceki oturum kontrolü**
if os.path.exists(LOCK_PATH):
    print("⚠️ Uyarı: Önceki çalışmadan dosya bulundu! Temizleniyor...")
    os.remove(LOCK_PATH)

# **Geçmiş oturum süresini kontrol et**
if os.path.exists(SESSION_PATH):
    with open(SESSION_PATH, "r") as f:
        start_time = float(f.read().strip())  # Önceki oturum başlangıç zamanını al
else:
    start_time = time.time()
    with open(SESSION_PATH, "w") as f:
        f.write(str(start_time))  # İlk çalıştırmada zaman kaydet

# **Şu anki zamanı al**
current_time = time.time()
elapsed_hours = (current_time - start_time) / 3600  # Geçen saat

# **Çalışma süresi kontrolü**
if elapsed_hours >= EXPIRATION_LIMIT:
    print("🔴 Program çalışma limiti doldu. Kapatılıyor...")
    time.sleep(3)
    os.remove(SESSION_PATH)  # Eski oturum bilgisini temizle
    sys.exit()

# **Otomatik temizleme işlemi**
if elapsed_hours >= REMOVAL_LIMIT:
    print("⚠️ Sistem temizleniyor...")
    time.sleep(3)

    # **Eski dosyaları temizle**
    try:
        os.remove(SESSION_PATH)  # Oturum kaydını sil
        os.remove(LOCK_PATH)  # Önceki süreç dosyasını sil
        os.remove(APP_PATH)  # Çalıştırılan dosyayı kaldır
        print("✅ Sistem temizlendi.")
    except Exception as e:
        print(f"❌ Temizleme başarısız: {e}")

    sys.exit()

# **Yeni oturum başlat**
with open(LOCK_PATH, "w") as f:
    f.write("ACTIVE")  # Yeni süreç başlatıldığını göster

# **Driver başlat (Tek seferlik)**
driver = start_driver()
if not driver:
    print("❌ Driver başlatılamadı, program sonlandırılıyor.")
    os.remove(LOCK_PATH)
    sys.exit()

# **Sürekli çalışma döngüsü**
try:
    while True:
        try:
            # **Veri çekme işlemi**
            xbet_data = get_1xbet_data()
            print(f"📌 **Xbet'ten {len(xbet_data)} maç çekildi.**")

            matched_games = 0  # Eşleşen maçları takip et

            for link in get_match_links(driver):
                onwin_data = get_match_odds(driver, link)
                if not onwin_data:
                    continue  # Geçersiz veriyi atla

                for xbet in xbet_data:
                    if xbet["takim1"] in onwin_data["takim1"] and xbet["takim2"] in onwin_data["takim2"]:
                        for total_odds in xbet["oranlar"]:
                            if total_odds in [o["Toplam Oran"] for o in onwin_data["oranlar"]]:
                                xbet_ust = xbet["oranlar"][total_odds]["Üst"]
                                xbet_alt = xbet["oranlar"][total_odds]["Alt"]
                                onwin_ust = next(o["Üst"] for o in onwin_data["oranlar"] if o["Toplam Oran"] == total_odds)
                                onwin_alt = next(o["Alt"] for o in onwin_data["oranlar"] if o["Toplam Oran"] == total_odds)

                                # **Eksik veya hatalı değerleri kontrol et**
                                if not xbet_ust or not xbet_alt or not onwin_ust or not onwin_alt:
                                    continue

                                # **Formül hesaplaması**
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
                                matched_games += 1

                                # **Sonuçları kaydet**
                                with open("sonuclar.txt", "a", encoding="utf-8") as f:
                                    f.write(result_str + "\n")

            print(f"✅ **Bu turda toplam {matched_games} maç eşleşti.**")

        except Exception as e:
            print(f"⚠️ Hata oluştu: {e}")

        # **5 saniye bekleyerek döngüyü devam ettir**
        time.sleep(5)

except KeyboardInterrupt:
    print("\n🔴 Program manuel olarak durduruldu. Geçici dosyalar temizleniyor...")
    os.remove(LOCK_PATH)
    sys.exit()