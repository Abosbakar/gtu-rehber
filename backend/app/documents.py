"""data/ klasöründeki belgelerin kataloğu.

Akademik takvim burada yok: tarihleri arama değil, süre hesabı modülü kullanır.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    file: str
    title: str
    code: str
    group: str  # "gtu", "staj" veya "ulusal"


DOCUMENTS: list[Document] = [
    # Temel GTÜ mevzuatı
    Document("yonetmelik.pdf", "GTÜ Ön Lisans ve Lisans Eğitim-Öğretim Yönetmeliği", "YN-0001", "gtu"),
    Document("yaz-ogretimi-yonetmeligi.pdf", "GTÜ Yaz Öğretimi Yönetmeliği", "YN-0015", "gtu"),
    # GTÜ öğrenci yönergeleri
    Document("ingilizce-hazirlik-yonergesi.pdf", "İngilizce Hazırlık Eğitim-Öğretim ve Sınav Yönergesi", "YÖ-0002", "gtu"),
    Document("cift-anadal-yonergesi.pdf", "Çift Anadal Programı Yönergesi", "YÖ-0004", "gtu"),
    Document("dikey-gecis-yonergesi.pdf", "Dikey Geçiş Lisans Uygulama Yönergesi", "YÖ-0005", "gtu"),
    Document("mezuniyet-diploma-yonergesi.pdf", "Mezuniyet Belgesi ve Diploma Düzenleme Esasları", "YÖ-0006", "gtu"),
    Document("muafiyet-intibak-yonergesi.pdf", "Lisans Muafiyet ve İntibak Yönergesi", "YÖ-0007", "gtu"),
    Document("yandal-yonergesi.pdf", "Yan Dal Programı Yönergesi", "YÖ-0012", "gtu"),
    Document("yatay-gecis-yonergesi.pdf", "Önlisans-Lisans Programları Yatay Geçiş Yönergesi", "YÖ-0013", "gtu"),
    Document("kismi-zamanli-calisma-yonergesi.pdf", "Kısmi Zamanlı Öğrenci Çalıştırma Yönergesi", "YÖ-0025", "gtu"),
    Document("erasmus-yonergesi.pdf", "Erasmus Öğrenci ve Personel Değişim Yönergesi", "YÖ-0042", "gtu"),
    Document("engelli-ogrenci-sinav-yonergesi.pdf", "Engelli Öğrenciler Eğitim-Öğretim ve Sınav Uygulamaları Yönergesi", "YÖ-0044", "gtu"),
    Document("psikolojik-danismanlik-yonergesi.pdf", "Psikolojik Danışmanlık ve Rehberlik Hizmetleri Yönergesi", "YÖ-0051", "gtu"),
    Document("ogrenci-danismanligi-yonergesi.pdf", "Önlisans-Lisans Öğrenci Danışmanlığı Yönergesi", "YÖ-0066", "gtu"),
    Document("azami-sure-esaslari.pdf", "Azami Öğrenim Süresini Tamamlayan Öğrenciler İçin Uygulama Esasları", "YÖ-0078", "gtu"),
    Document("muafiyet-sinavi-esaslari.pdf", "Ders Muafiyet Sınavı Uygulama Esasları", "YÖ-0118", "gtu"),
    # Fakülte staj yönergeleri
    Document("staj-muhendislik.pdf", "Mühendislik Fakültesi Staj Yönergesi", "YÖ-0019", "staj"),
    Document("staj-havacilik-uzay.pdf", "Havacılık ve Uzay Bilimleri Fakültesi Staj Yönergesi", "YÖ-0089", "staj"),
    Document("staj-mimarlik.pdf", "Mimarlık Fakültesi Staj Yönergesi", "YÖ-0018", "staj"),
    Document("staj-isletme.pdf", "İşletme Fakültesi Staj Yönergesi", "YÖ-0028", "staj"),
    Document("staj-temel-bilimler.pdf", "Temel Bilimler Fakültesi Staj Yönergesi", "YÖ-0071", "staj"),
    # Bölüm staj uygulama esasları
    Document("staj-esaslari-biyomuhendislik.pdf", "Biyomühendislik Bölümü Staj Uygulama Esasları", "YÖ-0079", "staj"),
    Document("staj-esaslari-elektronik.pdf", "Elektronik Mühendisliği Bölümü Staj Uygulama Esasları", "YÖ-0080", "staj"),
    Document("staj-esaslari-insaat.pdf", "İnşaat Mühendisliği Bölümü Staj Uygulama Esasları", "YÖ-0081", "staj"),
    Document("staj-esaslari-harita.pdf", "Harita Mühendisliği Bölümü Staj Uygulama Esasları", "YÖ-0082", "staj"),
    Document("staj-esaslari-kimya.pdf", "Kimya Mühendisliği Bölümü Staj Uygulama Esasları", "YÖ-0083", "staj"),
    Document("staj-esaslari-makine.pdf", "Makine Mühendisliği Bölümü Staj Uygulama Esasları", "YÖ-0084", "staj"),
    Document("staj-esaslari-cevre.pdf", "Çevre Mühendisliği Bölümü Staj Uygulama Esasları", "YÖ-0085", "staj"),
    Document("staj-esaslari-endustri.pdf", "Endüstri Mühendisliği Bölümü Staj Uygulama Esasları", "YÖ-0086", "staj"),
    Document("staj-esaslari-bilgisayar.pdf", "Bilgisayar Mühendisliği Bölümü Staj Uygulama Esasları", "YÖ-0087", "staj"),
    Document("staj-esaslari-malzeme.pdf", "Malzeme Bilimi ve Mühendisliği Bölümü Staj Uygulama Esasları", "YÖ-0088", "staj"),
    # Ulusal mevzuat
    Document("yok-gecis-ciftanadal-yandal-yonetmeligi.pdf", "YÖK Programlar Arası Geçiş, Çift Anadal, Yan Dal ve Kredi Transferi Yönetmeliği", "RG 27561", "ulusal"),
    Document("kyk-burs-yonetmeligi.pdf", "Gençlik ve Spor Bakanlığı Burs Yönetmeliği", "RG 32358", "ulusal"),
    Document("kyk-kredi-yonetmeligi.pdf", "Gençlik ve Spor Bakanlığı Kredi Yönetmeliği", "RG 32358", "ulusal"),
]

DOCUMENTS_BY_FILE = {d.file: d for d in DOCUMENTS}
