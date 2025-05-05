import os
from flask import Flask, request, render_template, jsonify, session
from PIL import Image
import io
import google.generativeai as genai
from dotenv import load_dotenv
import json
import random
import requests
import base64
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Session için güvenli bir anahtar

# Global kelime havuzu ve sayaç
kelime_havuzu = []
kelime_sayaci = 0

# Yüksek skorları saklamak için basit bir dosya sistemi
HIGH_SCORES_FILE = "high_scores.json"

def load_high_scores():
    try:
        if os.path.exists(HIGH_SCORES_FILE):
            with open(HIGH_SCORES_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print("Yüksek skorlar yüklenirken hata:", str(e))
        return []

def save_high_score(score, name):
    try:
        scores = load_high_scores()
        scores.append({
            "name": name,
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        # Skorları sırala (en yüksekten en düşüğe)
        scores.sort(key=lambda x: x["score"], reverse=True)
        # Sadece en yüksek 10 skoru sakla
        scores = scores[:10]
        
        with open(HIGH_SCORES_FILE, 'w') as f:
            json.dump(scores, f)
        return True
    except Exception as e:
        print("Yüksek skor kaydedilirken hata:", str(e))
        return False

@app.route("/get-high-scores", methods=["GET"])
def get_high_scores():
    try:
        # Session'dan kullanıcının en yüksek skorunu al
        high_score = session.get("high_score", 0)
        return jsonify([{"score": high_score}])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/save-score", methods=["POST"])
def save_score():
    try:
        data = request.get_json()
        score = data.get("score")
        name = data.get("name", "Anonim")
        
        if score is None:
            return jsonify({"error": "Skor gerekli"}), 400
            
        if save_high_score(score, name):
            return jsonify({"success": True})
        return jsonify({"error": "Skor kaydedilemedi"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/update-progress", methods=["POST"])
def update_progress():
    data = request.get_json()
    correct = data.get('correct', False)
    
    # Session'da yıldız yoksa başlat
    if 'stars' not in session:
        session['stars'] = 0
        session['max_stars'] = 0
    
    # Mevcut yıldız sayısını al
    current_stars = session.get('stars', 0)
    max_stars = session.get('max_stars', 0)
    
    # Yıldız sayısını güncelle
    if correct:
        current_stars += 1   # Doğru cevap için 1 yıldız
        # En yüksek yıldız sayısını güncelle
        if current_stars > max_stars:
            max_stars = current_stars
            session['max_stars'] = max_stars
    else:
        current_stars = max(0, current_stars - 1)  # Yanlış cevap için 1 yıldız düşür
    
    # Session'ı güncelle
    session['stars'] = current_stars
    
    return jsonify({
        'stars': current_stars,
        'max_stars': max_stars
    })

@app.route("/reset-progress", methods=["POST"])
def reset_progress():
    # Tüm skorları sıfırla
    session['stars'] = 0
    session['max_stars'] = 0
    return jsonify({
        'stars': 0,
        'max_stars': 0
    })

@app.route("/get-max-stars", methods=["GET"])
def get_max_stars():
    max_stars = session.get('max_stars', 0)
    return jsonify({
        'max_stars': max_stars
    })

@app.route("/new-game", methods=["POST"])
def new_game():
    global kelime_havuzu, kelime_sayaci
    # Yeni oyun için yıldızları sıfırla
    max_stars = session.get('max_stars', 0)  # En yüksek yıldız sayısını koru
    session['stars'] = 0  # Mevcut yıldızları sıfırla
    
    # Kelime havuzunu sıfırla
    kelime_havuzu = []
    kelime_sayaci = 0
    
    return jsonify({
        'stars': 0,
        'max_stars': max_stars
    })

def kelime_havuzunu_doldur():
    global kelime_havuzu
    try:
        # Gemini'den kelime havuzu oluşturma
        text_model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = """
        6-8 yaş arası çocukların kolayca okuyabileceği 20 farklı basit Türkçe kelime üret. Bu kelimeler:
        - Fiil olmayacak (isim olacak)
        - Kolay resmedilebilir somut nesne olacak (örn: elma, araba, ev, ağaç, kuş)
        - Soyut kavram olmayacak (örn: mutluluk, özgürlük)
        - En az 3 harfli olacak
        - Türkçe karakterler içerebilir
        - Birbirinden farklı olacak
        - Unsplash'te kolayca resmi bulunabilecek kelimeler olacak (örn: elma, araba, ev, ağaç, kuş, kedi, köpek, güneş, ay, yıldız, bulut, çiçek, kitap, kalem, masa, sandalye, pencere, kapı, telefon, bilgisayar)
        
        Sonuçları JSON formatında döndür. JSON şu şekilde olmalı:
        {
            "kelimeler": [
                "kelime1",
                "kelime2",
                "kelime3",
                ...
            ]
        }
        """

        print("Kelime havuzu dolduruluyor...")
        response = text_model.generate_content(prompt)
        print("Gemini API yanıtı:", response.text)

        # JSON formatını kontrol et ve ayrıştır
        response_json = response.text.strip()
        if response_json.startswith("```json"):
            response_json = response_json.strip("```json").strip("```")

        json_data = json.loads(response_json)
        kelimeler = json_data.get("kelimeler", [])
        
        # Kelimeleri temizle
        temiz_kelimeler = [kelime.lstrip('*').strip() for kelime in kelimeler if kelime.strip()]
        
        # Tekrar eden kelimeleri kaldır
        kelime_havuzu = list(dict.fromkeys(temiz_kelimeler))
        print("Kelime havuzu dolduruldu. Kelimeler:", kelime_havuzu)
        
        return True
    except Exception as e:
        print("Kelime havuzu doldurma hatası:", str(e))
        return False

# Uygulama başladığında kelime havuzunu doldur
kelime_havuzunu_doldur()

# 1. Gemini API anahtarını ayarla (çevre değişkeninden veya doğrudan yazılabilir)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 2. Gemini modeli (görsel ve metin için)
model = genai.GenerativeModel("gemini-2.0-flash")

# Unsplash API anahtarı
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

# Pixabay API anahtarı
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

@app.route("/")
def index():
    return render_template("page2.html")

@app.route("/reading")
def reading():
    return render_template("reading.html")

@app.route("/writing")
def writing():
    return render_template("writing.html")

@app.route("/get-word", methods=["GET"])
def get_word():
    global kelime_havuzu, kelime_sayaci
    
    try:
        # Eğer kelime havuzu boşsa yeni kelimeler üret
        if not kelime_havuzu:
            print("Kelime havuzu oluşturuluyor...")
            if not kelime_havuzunu_doldur():
                return jsonify({"error": "Kelime havuzu oluşturulamadı."}), 500
            kelime_sayaci = 0

        # Sıradaki kelimeyi al
        kelime = kelime_havuzu[kelime_sayaci]
        kelime_sayaci += 1
        print(f"Sıradaki kelime ({kelime_sayaci}/{len(kelime_havuzu)}):", kelime)

        # Eğer tüm kelimeler kullanıldıysa yeni kelimeler üret
        if kelime_sayaci >= len(kelime_havuzu):
            print("Tüm kelimeler kullanıldı, yeni kelime havuzu oluşturuluyor...")
            if not kelime_havuzunu_doldur():
                return jsonify({"error": "Kelime havuzu oluşturulamadı."}), 500
            kelime_sayaci = 0

        return jsonify({"kelime": kelime})
    except Exception as e:
        print("Hata oluştu:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/get-word-image", methods=["GET"])
def get_word_image():
    try:
        word = request.args.get('word', '')
        if not word:
            print("Hata: Kelime parametresi eksik")
            return jsonify({"error": "Kelime parametresi gerekli."}), 400

        # API anahtarı kontrolü
        if not PIXABAY_API_KEY:
            print("Hata: Pixabay API anahtarı bulunamadı")
            return jsonify({"error": "API anahtarı yapılandırılmamış."}), 500

        print("Çevrilecek kelime:", word)

        # Gemini API ile Türkçe'den İngilizce'ye çeviri
        text_model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        Aşağıdaki Türkçe kelimenin İngilizce karşılığını ver. Sadece İngilizce kelimeyi döndür, başka açıklama ekleme.
        Kelime: {word}
        """

        print("Gemini API'ye çeviri isteği gönderiliyor...")
        response = text_model.generate_content(prompt)
        search_term = response.text.strip()
        print("Çeviri sonucu:", search_term)

        # Pixabay API'den resim getir
        url = "https://pixabay.com/api/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": search_term,
            "image_type": "photo",
            "safesearch": "true",
            "per_page": 3  # Minimum geçerli değer
        }

        print("Pixabay API'ye resim isteği gönderiliyor...")
        print("API URL:", url)
        print("API Parametreleri:", params)
        
        try:
            response = requests.get(url, params=params, timeout=10)
            print("Pixabay API yanıt kodu:", response.status_code)
            print("Pixabay API yanıtı:", response.text)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("totalHits", 0) > 0:
                    image_url = data["hits"][0]["webformatURL"]
                    print("Resim URL'i alındı:", image_url)
                    
                    # Resmi indir ve base64'e çevir
                    print("Resim indiriliyor...")
                    image_response = requests.get(image_url, timeout=10)
                    if image_response.status_code == 200:
                        image_data = base64.b64encode(image_response.content).decode('utf-8')
                        print("Resim başarıyla indirildi ve base64'e çevrildi")
                        return jsonify({
                            "image": image_data,
                            "attribution": {
                                "name": "Pixabay",
                                "link": "https://pixabay.com"
                            }
                        })
                    else:
                        print("Resim indirme hatası:", image_response.status_code)
                        print("Resim indirme yanıtı:", image_response.text)
            elif response.status_code == 400:
                error_data = response.json()
                print("Pixabay API 400 hatası - Detaylar:", error_data)
                # Alternatif arama terimi dene
                alt_params = params.copy()
                alt_params["q"] = search_term.split()[0] if " " in search_term else search_term
                print("Alternatif arama terimi ile deneniyor:", alt_params["q"])
                alt_response = requests.get(url, params=alt_params, timeout=10)
                if alt_response.status_code == 200:
                    data = alt_response.json()
                    if data.get("totalHits", 0) > 0:
                        image_url = data["hits"][0]["webformatURL"]
                        image_response = requests.get(image_url, timeout=10)
                        if image_response.status_code == 200:
                            image_data = base64.b64encode(image_response.content).decode('utf-8')
                            return jsonify({
                                "image": image_data,
                                "attribution": {
                                    "name": "Pixabay",
                                    "link": "https://pixabay.com"
                                }
                            })
            else:
                print("Pixabay API hatası:", response.status_code)
                print("API yanıtı:", response.text)
        except requests.exceptions.RequestException as e:
            print("API isteği hatası:", str(e))
            return jsonify({"error": "API isteği başarısız oldu."}), 500
        
        print("Resim bulunamadı")
        return jsonify({"error": "Resim bulunamadı."}), 404

    except Exception as e:
        print("Hata oluştu:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
