from onwin import get_match_odds, get_match_links, start_driver, open_page
from xbet import get_1xbet_data
import time

# **Driver başlat**
driver = start_driver()

if not driver:
    print("❌ Driver başlatılamadı, program duruyor.")
    exit()

while True:
    try:
        # **Verileri çek**
        xbet_data = get_1xbet_data()
        onwin_data = [get_match_odds(driver, link) for link in get_match_links(driver)]

        ortak_maclar = []
        for xbet in xbet_data:
            for onwin in onwin_data:
                if not onwin:
                    continue  # Hatalı veri gelirse atla

                if xbet["takim1"] in onwin["takim1"] and xbet["takim2"] in onwin["takim2"]:
                    for toplam_oran in xbet["oranlar"]:
                        if toplam_oran in [o["Toplam Oran"] for o in onwin["oranlar"]]:
                            xbet_ust = xbet["oranlar"][toplam_oran]["Üst"]
                            xbet_alt = xbet["oranlar"][toplam_oran]["Alt"]
                            onwin_ust = next(o["Üst"] for o in onwin["oranlar"] if o["Toplam Oran"] == toplam_oran)
                            onwin_alt = next(o["Alt"] for o in onwin["oranlar"] if o["Toplam Oran"] == toplam_oran)

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
                            ortak_maclar.append(sonuc_str)

        # **Sonuçları dosyaya yaz**
        with open("sonuclar.txt", "w", encoding="utf-8") as f:
            for mac in ortak_maclar:
                f.write(mac + "\n")

    except Exception as e:
        print(f"⚠️ Hata oluştu: {e}")

    time.sleep(5)