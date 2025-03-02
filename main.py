import time
import pandas as pd
import os
from onwin import get_onwin_data
from xbet import get_1xbet_data
from fuzzywuzzy import fuzz
from tabulate import tabulate

# 📌 **Takım isimlerini eşleştirme fonksiyonu**
def match_teams(takim1, takim2, xbet_matches, threshold=80):
    for match in xbet_matches:
        xbet_takim1, xbet_takim2 = match["takim1"].lower(), match["takim2"].lower()
        takim1_norm, takim2_norm = takim1.lower(), takim2.lower()

        # Benzerlik Skoru ve İçerme Kontrolü
        score1 = fuzz.partial_ratio(takim1_norm, xbet_takim1)
        score2 = fuzz.partial_ratio(takim2_norm, xbet_takim2)

        if (score1 > threshold and score2 > threshold) or (takim1_norm in xbet_takim1 and takim2_norm in xbet_takim2):
            return match
    return None

# 📌 **Canlı veri güncelleme döngüsü**
def run_live_updates():
    os.system('clear' if os.name == 'posix' else 'cls')  # Terminali sadece başta temizle

    while True:
        print("\n📊 **Canlı Bahis Analiz Sonuçları** 📊\n")

        # **ONWIN verisini çek ve yazdır**
        print("🔄 Onwin verileri çekiliyor...")
        onwin_data = get_onwin_data()
        print("\n✅ ONWIN Güncellenmiş Veriler:\n")
        for match in onwin_data:
            print(match)

        print("\n" + "-" * 50)  # ONWIN bölümü ile XBET arasına ayırıcı ekleyelim

        # **XBET verisini çek ve yazdır**
        print("\n🔄 1XBET verileri çekiliyor...")
        xbet_data = get_1xbet_data()
        print("\n✅ 1XBET Güncellenmiş Veriler:\n")
        for match in xbet_data:
            print(match)

        print("\n" + "-" * 50)  # XBET bölümü ile tablo arasına ayırıcı ekleyelim

        # **Eşleşen Maçları Analiz Et**
        matched_matches = []
        for onwin_match in onwin_data:
            matched_xbet = match_teams(onwin_match["takim1"], onwin_match["takim2"], xbet_data)

            if matched_xbet:
                toplam_check = "✅ Aynı" if str(onwin_match["toplam"]) == str(matched_xbet["toplam"]) else "❌ Farklı"
                
                # Sonuç hesaplamalarını düzgün formatta gösterelim
                try:
                    sonuc1 = round((1 / float(matched_xbet["alt"])) + (1 / float(onwin_match["ust"])), 2) if toplam_check == "✅ Aynı" else "-"
                    sonuc2 = round((1 / float(matched_xbet["ust"])) + (1 / float(onwin_match["alt"])), 2) if toplam_check == "✅ Aynı" else "-"
                    bahis_uygun = "✅" if toplam_check == "✅ Aynı" and (sonuc1 < 1 or sonuc2 < 1) else "❌"
                except (ValueError, TypeError, ZeroDivisionError):
                    sonuc1, sonuc2, bahis_uygun = "-", "-", "❌"

                matched_matches.append({
                    "takim1": onwin_match["takim1"],
                    "takim2": onwin_match["takim2"],
                    "xbet_toplam": matched_xbet["toplam"],
                    "xbet_alt": matched_xbet["alt"],
                    "xbet_ust": matched_xbet["ust"],
                    "onwin_toplam": onwin_match["toplam"],
                    "onwin_alt": onwin_match["alt"],
                    "onwin_ust": onwin_match["ust"],
                    "toplam_check": toplam_check,
                    "sonuc1": sonuc1,
                    "sonuc2": sonuc2,
                    "bahis_uygun": bahis_uygun
                })

        # 📌 **Tabloyu göster**
        if matched_matches:
            df = pd.DataFrame(matched_matches)

            # Boş değerleri "-" yaparak tabloyu bozmadan gösterelim
            df = df.fillna("-")

            print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
        else:
            print("\n⚠️ Eşleşen maç bulunamadı!\n")

        # 📌 **10 saniye bekleyip tekrar veri çekecek**
        time.sleep(10)

if __name__ == "__main__":
    run_live_updates()