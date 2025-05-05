import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io
import google.generativeai as genai
from dotenv import load_dotenv
import json
import random
import requests
import base64
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# Debug: Çevre değişkenlerini kontrol et
print("Loading environment variables...")
load_dotenv()
print("GOOGLE_API_KEY exists:", bool(os.getenv("GOOGLE_API_KEY")))
print("PIXABAY_API_KEY exists:", bool(os.getenv("PIXABAY_API_KEY")))

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Global kelime havuzu ve sayaç
kelime_havuzu = []
kelime_sayaci = 0

# Yüksek skorları saklamak için basit bir dosya sistemi
HIGH_SCORES_FILE = "high_scores.json"

class ScoreData(BaseModel):
    score: int
    name: Optional[str] = "Anonim"

class ProgressData(BaseModel):
    correct: bool

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

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("page2.html", {"request": request})

@app.get("/reading", response_class=HTMLResponse)
async def reading(request: Request):
    return templates.TemplateResponse("reading.html", {"request": request})

@app.get("/writing", response_class=HTMLResponse)
async def writing(request: Request):
    return templates.TemplateResponse("writing.html", {"request": request})

@app.get("/get-word")
async def get_word():
    global kelime_havuzu, kelime_sayaci
    
    try:
        if not kelime_havuzu:
            print("Kelime havuzu oluşturuluyor...")
            if not kelime_havuzunu_doldur():
                raise HTTPException(status_code=500, detail="Kelime havuzu oluşturulamadı.")
            kelime_sayaci = 0

        kelime = kelime_havuzu[kelime_sayaci]
        kelime_sayaci += 1
        print(f"Sıradaki kelime ({kelime_sayaci}/{len(kelime_havuzu)}):", kelime)

        if kelime_sayaci >= len(kelime_havuzu):
            print("Tüm kelimeler kullanıldı, yeni kelime havuzu oluşturuluyor...")
            if not kelime_havuzunu_doldur():
                raise HTTPException(status_code=500, detail="Kelime havuzu oluşturulamadı.")
            kelime_sayaci = 0

        return {"kelime": kelime}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-score")
async def save_score(data: ScoreData):
    try:
        if save_high_score(data.score, data.name):
            return {"success": True}
        raise HTTPException(status_code=500, detail="Skor kaydedilemedi")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-progress")
async def update_progress(data: ProgressData):
    # Session yerine FastAPI'nin state yönetimi kullanılmalı
    # Bu örnek için basit bir in-memory çözüm gösteriyorum
    current_stars = getattr(app.state, 'stars', 0)
    max_stars = getattr(app.state, 'max_stars', 0)
    
    if data.correct:
        current_stars += 1
        if current_stars > max_stars:
            max_stars = current_stars
            app.state.max_stars = max_stars
    else:
        current_stars = max(0, current_stars - 1)
    
    app.state.stars = current_stars
    
    return {
        'stars': current_stars,
        'max_stars': max_stars
    }

@app.route("/reset-progress", methods=["POST"])
def reset_progress():
    # Tüm skorları sıfırla
    app.state.stars = 0
    app.state.max_stars = 0
    return JSONResponse({
        'stars': 0,
        'max_stars': 0
    })

@app.route("/get-max-stars", methods=["GET"])
def get_max_stars():
    max_stars = getattr(app.state, 'max_stars', 0)
    return JSONResponse({
        'max_stars': max_stars
    })

@app.route("/new-game", methods=["POST"])
def new_game():
    global kelime_havuzu, kelime_sayaci
    # Yeni oyun için yıldızları sıfırla
    max_stars = getattr(app.state, 'max_stars', 0)  # En yüksek yıldız sayısını koru
    app.state.stars = 0  # Mevcut yıldızları sıfırla
    
    # Kelime havuzunu sıfırla
    kelime_havuzu = []
    kelime_sayaci = 0
    
    return JSONResponse({
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

@app.get("/get-word-image")
async def get_word_image(word: str):
    try:
        if not word:
            print("Hata: Kelime parametresi eksik")
            raise HTTPException(status_code=400, detail="Kelime parametresi gerekli.")

        # API anahtarı kontrolü
        if not PIXABAY_API_KEY:
            print("Hata: Pixabay API anahtarı bulunamadı")
            raise HTTPException(status_code=500, detail="API anahtarı yapılandırılmamış.")

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
            "per_page": 20  # Daha fazla resim seçeneği için sayıyı artırdık
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
                    # Rastgele bir resim seç
                    hits = data["hits"]
                    random_image = random.choice(hits)
                    image_url = random_image["webformatURL"]
                    print("Seçilen resim URL'i:", image_url)
                    
                    # Resmi indir ve base64'e çevir
                    print("Resim indiriliyor...")
                    image_response = requests.get(image_url, timeout=10)
                    if image_response.status_code == 200:
                        image_data = base64.b64encode(image_response.content).decode('utf-8')
                        print("Resim başarıyla indirildi ve base64'e çevrildi")
                        return {
                            "image": image_data,
                            "attribution": {
                                "name": "Pixabay",
                                "link": "https://pixabay.com"
                            }
                        }
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
                        # Rastgele bir resim seç
                        hits = data["hits"]
                        random_image = random.choice(hits)
                        image_url = random_image["webformatURL"]
                        image_response = requests.get(image_url, timeout=10)
                        if image_response.status_code == 200:
                            image_data = base64.b64encode(image_response.content).decode('utf-8')
                            return {
                                "image": image_data,
                                "attribution": {
                                    "name": "Pixabay",
                                    "link": "https://pixabay.com"
                                }
                            }
            else:
                print("Pixabay API hatası:", response.status_code)
                print("API yanıtı:", response.text)
        except requests.exceptions.RequestException as e:
            print("API isteği hatası:", str(e))
            raise HTTPException(status_code=500, detail="API isteği başarısız oldu.")
        
        print("Resim bulunamadı")
        raise HTTPException(status_code=404, detail="Resim bulunamadı.")

    except HTTPException as he:
        raise he
    except Exception as e:
        print("Hata oluştu:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-keys")
async def test_keys():
    google_key = os.getenv("GOOGLE_API_KEY")
    pixabay_key = os.getenv("PIXABAY_API_KEY")
    
    return {
        "google_key_exists": bool(google_key),
        "pixabay_key_exists": bool(pixabay_key),
        "google_key_length": len(google_key) if google_key else 0,
        "pixabay_key_length": len(pixabay_key) if pixabay_key else 0
    }

if __name__ == "__main__":
    app.run(debug=True)
