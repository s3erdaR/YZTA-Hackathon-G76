
# Harfi Harfine ✍️📖

**Harfi Harfine**, çocukların yazma ve okuma becerilerini yapay zeka destekli olarak geliştirmelerine yardımcı olmak amacıyla geliştirilmiş bir uygulamadır. Proje, Google Yapay Zeka ve Teknoloji Akademisi AI Hackathonu kapsamında geliştirilmiştir.

## 🔍 Proje Amacı

Uygulamanın amacı, çocukların yazılı ve sözlü dil becerilerini geliştirirken teknolojiyi eğitici ve eğlenceli bir şekilde kullanmalarını sağlamaktır.

---

## ✍️ Yazma Modülü

### 🧠 Nasıl Çalışır?

1. **Cümle Gösterimi:** Kullanıcıya 10-20 adet cümle gösterilir ve bu cümleleri bir kağıda yazmaları istenir.
2. **Fotoğraf Yükleme:** Kullanıcı, yazdığı kağıdın fotoğrafını sisteme yükler.
3. **Yapay Zeka Analizi:** Yüklenen görsel, arka planda **Gemini** (Google AI) tarafından analiz edilir.
4. **Hatalı Harf/Kelime Tespiti:** Yanlış yazılan harf ve kelimeler tespit edilerek kullanıcıya bildirilir.
5. **Geri Bildirim:** Her yanlış harf için ilgili harfin doğru yazılışını gösteren bir **YouTube video** önerisi sunulur.
6. **Tekrar Deneme:** Kullanıcı videoyu izledikten sonra tekrar deneme yapabilir.

### 🏆 Puanlama Sistemi

- Her kullanıcı, yazdığı kelimelerin doğruluğuna göre puanlanır.
- **Doğru/Toplam kelime oranı** temel alınarak bir skor hesaplanır.
- Skorlar tamamen Gemini'nin doğruluk tespitine göre hesaplandığı için küçük sapmalar olabilir.

---

## 📖 Okuma Modülü

### 🧠 Nasıl Çalışır?

1. **Kelime Gösterimi:** Kullanıcıya Gemini tarafından oluşturulan 10-20 kelimenin yazılışı gösterilir.
2. **Sesli Okuma:** Kullanıcı bu kelimeleri sesli bir şekilde telaffuz eder.
3. **Doğruluk Kontrolü:** Kullanıcının sesi, `Speech-to-Text` kütüphaneleri kullanılarak analiz edilir.
4. **Yardım Butonu:** Yanlış telaffuz veya isteğe bağlı olarak kullanıcı, kelimenin resmini görebilir (AI tarafından çocuklara uygun şekilde oluşturulur).
5. **Skor Hesaplama:** Doğru telaffuz edilen kelimelere göre puanlama yapılır.

---

## 🎨 Kullanıcı Arayüzü (Frontend)

- Giriş ekranında **"Yazma"** ve **"Okuma"** modları arasında seçim yapılabilir.
- Uygulama çocuklara uygun tema ve tasarımla geliştirilmiştir.
- Her kullanıcının kolayca kullanabilmesi için sade, anlaşılır ve eğlenceli bir arayüz sunar.

---

## 🛠️ Geliştirme Süreci

- Her ekip üyesi için ayrı bir `branch` oluşturulmuştur.
- Her geliştirici kendi kodlarını ilgili brancha yükler.
- Test edilen ve sorunsuz çalışan kodlar **main branch** ile birleştirilir.
- Bu yöntemle kod karmaşası önlenmiş olur.

---

## 📌 Notlar

- Proje deneyseldir ve AI analizlerinde küçük sapmalar olabilir.
- Geri bildirim ve katkılar için PR (Pull Request) gönderebilirsiniz.

---

## 📄 Lisans

Bu proje eğitim amaçlıdır ve açık kaynaklı olarak paylaşılmaktadır.
