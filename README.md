# GTÜ Rehber

> 🎬 **Demo videosu:** _(Gün 4'te eklenecek)_

> ⚠️ Bu README bir taslaktır; son hali 27 Ekim 2026'da tamamlanacaktır.

GTÜ öğrencilerinin akademik süreçlerdeki sorularını yönetmeliğe, akademik takvime ve diğer öğrencilerin deneyimlerine dayanarak yanıtlayan, gerekli dilekçeyi hazırlayan yerel yapay zekâ asistanı.

## Problem

Öğrenciler hastalık, ders ekle-bırak, kayıt dondurma, staj ya da not itirazı gibi durumlarda hangi yönetmelik maddesinin geçerli olduğunu, son başvuru gününü ve hangi belgelerin gerektiğini bulmakta zorlanır. Bilgi farklı PDF'lere dağılmıştır ve süre kaçırıldığında hak kaybı yaşanır.

## Çözüm

Öğrenci durumunu doğal dille yazar (ör. _"Hastalandım, AERO408 vizesine giremedim"_). GTÜ Rehber:

1. Durumu sınıflandırır (aşağıdaki kapsam tablosu). Emin olmadığında öğrenci işlerine yönlendirir.
2. Yönetmelik ve yönergelerdeki ilgili maddeyi bulup gösterir (BM25 arama).
3. Akademik takvime göre son başvuru gününü hesaplar.
4. Diğer öğrencilerin onaylanmış deneyimlerini **"resmi değil"** etiketiyle ekler.
5. Gerekli belgeleri listeler ve doldurulmuş dilekçeyi PDF olarak verir.
6. Öğrenci kendi deneyimini paylaşabilir; isimler kayıttan önce silinir, yönetici onayından sonra yayınlanır.

## Kapsam

| Seviye | Konular | Asistan ne verir |
|---|---|---|
| **Tam destek** | Mazeret sınavı, ders ekle-bırak, kayıt dondurma, staj başvurusu, not itirazı | Madde + son başvuru günü + deneyimler + belge listesi + doldurulmuş dilekçe PDF |
| **Bilgi desteği** | Yatay/dikey geçiş, çift anadal, yandal, yaz okulu, ders muafiyeti ve intibak, muafiyet sınavı, İngilizce hazırlık, Erasmus, azami süre ve ek sınav, mezuniyet ve diploma, KYK burs/kredi, kısmi zamanlı çalışma, engelli öğrenci sınav düzenlemeleri, danışmanlık | Madde + takvimde varsa tarih + deneyimler |

Staj sorularında fakülte ve bölüme özel staj esasları kullanılır. Kayıt dondurma gibi durumlarda KYK burs/kredi üzerindeki etkisi de hatırlatılır. Tüm kaynakların listesi: [`data/KAYNAKLAR.md`](data/KAYNAKLAR.md).

## Mimari

| Parça | Görev | Teknoloji |
|---|---|---|
| `frontend/` | Tarayıcı arayüzü | React + Vite, nginx ile derlenmiş halde |
| `backend/` | API ve iş mantığı (`/health`, `/ask`, `/experiences`, `/petition`) | Python, FastAPI |
| Yapay zekâ | Sınıflandırma, bilgi çıkarma, kısa cevap | Qwen2.5-1.5B-Instruct (GGUF, Q4_K_M), llama-cpp-python, sadece CPU |
| Arama | Yönetmelik maddesini bulma | BM25 |
| Veritabanı | Öğrenci deneyimleri | SQLite (Docker volume) |
| Dilekçe | Şablondan PDF üretimi | reportlab, DejaVu fontu |

Hiçbir bulut yapay zekâ servisi kullanılmaz; model Docker konteynerinin içinde yerel çalışır.

## Çalıştırma

_(Taslak — Gün 3'te test edilip kesinleşecek.)_

```bash
cp .env.example .env
docker compose up --build
```

- Ön yüz: http://localhost:3000
- API: http://localhost:8000 (sağlık kontrolü: http://localhost:8000/health)

## Klasör yapısı

```
backend/    FastAPI arka uç
frontend/   React + Vite ön yüz
data/       GTÜ yönetmelik/yönergeleri, staj esasları, akademik takvim, YÖK ve KYK yönetmelikleri
docs/       Geliştirme notları
```

## Geliştirici

- Abdullah Bakar

## Yapay zekâyı nasıl kullandık

_(Gün 4'te `docs/gelistirme-notlari.md` dosyasındaki notlardan yazılacak.)_
