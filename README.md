Learnify Kids ✍️📖

Learnify Kids, çocukların yazma ve okuma becerilerini yapay zekâ destekli olarak geliştirmelerine yardımcı olmak amacıyla geliştirilmiş bir uygulamadır. Bu proje, Google Yapay Zeka ve Teknoloji Akademisi AI Hackathonu kapsamında oluşturulmuştur.

🔍 Proje Amacı

Uygulama, çocukların dil gelişimini desteklemek amacıyla yazma ve okuma pratiğini teknolojik araçlarla daha etkili ve eğlenceli hâle getirmeyi hedefler.

✍️ Yazma Modülü

Nasıl Çalışır?

Kullanıcıya 10-20 cümle gösterilir, bu cümleleri kağıda yazması istenir.

Kullanıcı, yazdığı kağıdın fotoğrafını yükler.

Görsel, Gemini (Google AI) ile analiz edilir.

Hatalı harfler ve kelimeler tespit edilir.

Her yanlış harf için doğru yazımı gösteren YouTube videoları önerilir.

Kullanıcı bu videoları izleyip tekrar deneyebilir.

Puanlama

Skor, Doğru / Toplam kelime oranına göre hesaplanır.

Analiz, Gemini API üzerinden yapıldığından küçük sapmalar olabilir.

📖 Okuma Modülü

Not: Okuma modülünü kullanmak için okuma adlı branch’i indirmeniz gerekmektedir.

Nasıl Çalışır?

Kullanıcıya sistem tarafından 10-20 kelime gösterilir.

Kullanıcı bu kelimeleri sesli olarak telaffuz eder.

Speech-to-Text kütüphaneleri ile ses kaydı yazıya çevrilir ve doğruluğu kontrol edilir.

Yanlış telaffuzlarda, kelimenin görseli (çocuklara uygun olarak AI tarafından üretilmiş) destek olarak gösterilir.

Doğru telaffuz edilen kelimeler üzerinden puanlama yapılır.

🎨 Arayüz

Giriş ekranında Yazma ve Okuma modları seçilebilir.

Arayüz, çocuk dostu ve sade bir tasarımla oluşturulmuştur.

Kullanımı kolay, renkli ve etkileşimli bir deneyim sunar.

⚙️ Sistem Gereksinimleri

Yazılım Gereksinimleri

Python 3.10+

Node.js 18+ (frontend için)

pip / virtualenv (Python paket yönetimi için)

Python Kütüphaneleri

Aşağıdaki komutla gerekli kütüphaneleri yükleyebilirsiniz:

pip install -r requirements.txt

Başlıca kütüphaneler:

streamlit – Web arayüzü

google-cloud-vision – Görsel analiz

speechrecognition – Sesli okuma analizi

pytube – YouTube video entegrasyonu

dotenv – API anahtarlarını ortamdan çekmek için

API Anahtarları (.env)

Projeyi çalıştırmadan önce proje dizininde bir .env dosyası oluşturarak aşağıdaki değişkenleri tanımlayın:

GOOGLE_APPLICATION_CREDENTIALS=./path_to_service_account.json
OPENAI_API_KEY=your_openai_api_key_here  # Opsiyonel

GOOGLE_APPLICATION_CREDENTIALS, Google Cloud Console'dan aldığınız servis hesabı dosyasının yolunu göstermelidir.

🛠️ Geliştirme Sücreci

Her geliştirici için ayrı bir branch oluşturulmuştur.

Özellikler kendi branch'lerinde geliştirilir.

Testten geçen kodlar main branch’e merge edilir.

Kod bütünlüğü ve sürüm kontrolü bu şekilde sağlanır.

## 📌 Notlar

- Proje deneyseldir ve AI analizlerinde küçük sapmalar olabilir.
- Geri bildirim ve katkılar için PR (Pull Request) gönderebilirsiniz.
- Okuma modülü için lütfen okuma branch’ine geçiş yapmayı unutmayın.

---

## 📄 Lisans

Bu proje eğitim amaçlıdır ve açık kaynaklı olarak paylaşılmaktadır.

