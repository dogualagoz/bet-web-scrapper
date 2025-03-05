from onwin import get_match_odds, get_match_links, start_driver
from xbet import get_1xbet_data
import time

# **Driver başlat**
driver = start_driver()
if not driver:
    print("❌ Driver başlatılamadı, program duruyor.")
    exit()

while True:
    try:
        # **Xbet verilerini çek ve kaç maç bulunduğunu yazdır**
        xbet_data = get_1xbet_data()
        print(f"📌 **Xbet'ten {len(xbet_data)} maç çekildi.**")

        # **Onwin maçlarını çek ve anında kıyaslama yap**
        for link in get_match_links(driver):
            onwin_data = get_match_odds(driver, link)
            if not onwin_data:
                continue  # Geçersiz veri geldiyse atla

            for xbet in xbet_data:
                if xbet["takim1"] in onwin_data["takim1"] and xbet["takim2"] in onwin_data["takim2"]:
                    for toplam_oran in xbet["oranlar"]:
                        if toplam_oran in [o["Toplam Oran"] for o in onwin_data["oranlar"]]:
                            xbet_ust = xbet["oranlar"][toplam_oran]["Üst"]
                            xbet_alt = xbet["oranlar"][toplam_oran]["Alt"]
                            onwin_ust = next(o["Üst"] for o in onwin_data["oranlar"] if o["Toplam Oran"] == toplam_oran)
                            onwin_alt = next(o["Alt"] for o in onwin_data["oranlar"] if o["Toplam Oran"] == toplam_oran)

                            # **Boş oranları kontrol et, boşsa işlem yapma**
                            if not xbet_ust or not xbet_alt or not onwin_ust or not onwin_alt:
                                continue

                            # **Formülü uygula**
                            sonuc1 = 1/float(xbet_alt) + 1/float(onwin_ust)
                            sonuc2 = 1/float(xbet_ust) + 1/float(onwin_alt)
                            uygunluk1 = "✅ Uygun" if sonuc1 < 1 else "❌ Uygun Değil"
                            uygunluk2 = "✅ Uygun" if sonuc2 < 1 else "❌ Uygun Değil"

                            sonuc_str = (f"{xbet['takim1']} - {xbet['takim2']} | "
                                         f"Toplam Oran: {toplam_oran} | "
                                         f"xbet Alt: {xbet_alt} | onwin Üst: {onwin_ust} | "
                                         f"xbet Üst: {xbet_ust} | onwin Alt: {onwin_alt} | "
                                         f"Sonuç1: {sonuc1:.2f} ({uygunluk1}) | "
                                         f"Sonuç2: {sonuc2:.2f} ({uygunluk2})")

                            print(sonuc_str)

                            # **Sonuçları dosyaya kaydet**
                            with open("sonuclar.txt", "a", encoding="utf-8") as f:
                                f.write(sonuc_str + "\n")

    except Exception as e:
        print(f"⚠️ Hata oluştu: {e}")

    # **5 saniye bekleyip tekrar döngüye gir**
    time.sleep(5)