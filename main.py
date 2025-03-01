from onwin import get_onwin_data
from xbet import get_1xbet_data
from fuzzywuzzy import fuzz

# 📌 **Verileri çek**
onwin_data = get_onwin_data()
xbet_data = get_1xbet_data()

# 📌 **Takım isimlerini normalize etme fonksiyonu**
def normalize_name(name):
    return name.lower().strip()

# 📌 **Takım isimlerini eşleştirme fonksiyonu**
def match_teams(takim1, takim2, xbet_matches, threshold=80):
    for match in xbet_matches:
        xbet_takim1, xbet_takim2 = normalize_name(match["takim1"]), normalize_name(match["takim2"])
        takim1_norm, takim2_norm = normalize_name(takim1), normalize_name(takim2)
        
        # Fuzzy matching hesaplama
        score1 = fuzz.partial_ratio(takim1_norm, xbet_takim1)
        score2 = fuzz.partial_ratio(takim2_norm, xbet_takim2)
        
        # İçerme kontrolü
        include_check1 = takim1_norm in xbet_takim1 or xbet_takim1 in takim1_norm
        include_check2 = takim2_norm in xbet_takim2 or xbet_takim2 in takim2_norm
        
        if (score1 > threshold and score2 > threshold) or (include_check1 and include_check2):
            return match
    return None

# 📌 **Verileri eşle ve analiz yap**
matched_matches = []
for onwin_match in onwin_data:
    takim1, takim2 = onwin_match["takim1"], onwin_match["takim2"]
    matched_xbet = match_teams(takim1, takim2, xbet_data)
    
    if matched_xbet:
        # Toplam oranlar karşılaştırılıyor
        if str(onwin_match["toplam"]) == str(matched_xbet["toplam"]):
            toplam_check = "✅ Aynı"
            sonuc1 = (1 / float(matched_xbet["alt"])) + (1 / float(onwin_match["ust"]))
            sonuc2 = (1 / float(matched_xbet["ust"])) + (1 / float(onwin_match["alt"]))
            bahis_uygun = sonuc1 < 1 or sonuc2 < 1
        else:
            toplam_check = "❌ Farklı"
            bahis_uygun = False
            sonuc1, sonuc2 = None, None

        matched_matches.append({
            "takim1": takim1,
            "takim2": takim2,
            "xbet": matched_xbet,
            "onwin": onwin_match,
            "toplam_check": toplam_check,
            "sonuc1": sonuc1,
            "sonuc2": sonuc2,
            "bahis_uygun": bahis_uygun
        })

# 📌 **Sonuçları ekrana yazdır**
print("\n📊 **Bahis Analiz Sonuçları** 📊\n")
for match in matched_matches:
    print(f"🏆 {match['takim1']} vs {match['takim2']}")
    print(f"1xbet:")
    print(f"Toplam: {match['xbet']['toplam']} | Alt: {match['xbet']['alt']} | Üst: {match['xbet']['ust']}")
    print(f"Onwin:")
    print(f"Toplam: {match['onwin']['toplam']} | Alt: {match['onwin']['alt']} | Üst: {match['onwin']['ust']}")
    print(f"Toplam oranlar: {match['toplam_check']}")
    
    if match["toplam_check"] == "✅ Aynı":
        print(f"Sonuç1: {match['sonuc1']:.2f} {'✅' if match['sonuc1'] < 1 else '❌'}")
        print(f"Sonuç2: {match['sonuc2']:.2f} {'✅' if match['sonuc2'] < 1 else '❌'}")
        if match["bahis_uygun"]:
            print("🎯 **Bahis oynanmaya uygun!** ✅")
        else:
            print("⚠️ Bahis oynanmaya uygun değil! ❌")
    else:
        print("⚠️ Bahis oynanmaya uygun değil! ❌")
    print("-" * 50)
