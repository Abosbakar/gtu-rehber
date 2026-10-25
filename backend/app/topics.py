"""Asistanın tanıdığı konular.

"tam" seviyesindeki konularda süre hesabı ve dilekçe de verilir;
"bilgi" seviyesindekilerde ilgili madde ve takvim bilgisi gösterilir.
Anahtar kelimeler sınıflandırmada, arama sorgusu ise madde aramada kullanılır.
"""

from dataclasses import dataclass, field

YONETMELIK = "yonetmelik.pdf"
KYK = {"kyk-burs-yonetmeligi.pdf", "kyk-kredi-yonetmeligi.pdf"}
STAJ_FILES = {
    "staj-muhendislik.pdf", "staj-havacilik-uzay.pdf", "staj-mimarlik.pdf",
    "staj-isletme.pdf", "staj-temel-bilimler.pdf",
    "staj-esaslari-biyomuhendislik.pdf", "staj-esaslari-elektronik.pdf",
    "staj-esaslari-insaat.pdf", "staj-esaslari-harita.pdf", "staj-esaslari-kimya.pdf",
    "staj-esaslari-makine.pdf", "staj-esaslari-cevre.pdf", "staj-esaslari-endustri.pdf",
    "staj-esaslari-bilgisayar.pdf", "staj-esaslari-malzeme.pdf",
}


@dataclass(frozen=True)
class Topic:
    id: str
    name: str
    level: str  # "tam" | "bilgi"
    description: str  # Dil modeline verilen kısa açıklama
    strong: tuple[str, ...]  # Tek başına konuyu belirleyen ifadeler
    weak: tuple[str, ...]  # Konuya işaret eden ama yetmeyen kelimeler
    query: str  # Arama sorgusunu zenginleştiren resmi ifadeler
    files: frozenset[str]
    required_documents: tuple[str, ...] = ()
    office: str = ""  # Başvurunun yapılacağı birim
    side_search: tuple[str, frozenset[str], str] | None = None  # (sorgu, belgeler, not)
    notes: tuple[str, ...] = field(default=())
    # Dil modeline verilen kısa kural özeti (madde metninin kendisi aramadan gelir)
    key_facts: tuple[str, ...] = ()


TOPICS: list[Topic] = [
    Topic(
        "mazeret_sinavi", "Mazeret sınavı", "tam",
        "sınava (vize, ara sınav, final) hastalık, kaza veya başka geçerli bir nedenle giremeyen öğrenci",
        strong=("mazeret", "giremedim", "giremeyece", "kaçırdım sınav", "sağlık raporu", "rapor aldım"),
        weak=("hasta", "vize", "ara sınav", "final", "sınav", "kaza", "ameliyat", "cenaze", "vefat", "rapor"),
        query="mazeret sınavı haklı ve geçerli nedenlerle sınavlarına giremeyen öğrenciler mazeret dilekçesi",
        files=frozenset({YONETMELIK}),
        required_documents=(
            "Mazeret sınavı dilekçesi (GTÜ Rehber doldurup PDF olarak verir)",
            "Mazereti kanıtlayan belge (ör. sağlık raporu, kaza tutanağı, resmi yazı)",
            "Girilemeyen sınavın ders kodu ve tarihi",
        ),
        office="Kayıtlı olduğunuz bölüm başkanlığı",
        notes=("Yarıyıl sonu sınavında FF alınınca yapılan D sınavının mazeret sınavı yoktur (Madde 25).",),
        key_facts=(
            "Haklı ve geçerli bir nedenle sınava giremeyen öğrenciye mazeret sınavı hakkı verilebilir (Madde 29).",
            "Mazeret dilekçesi, sınav tarihinden itibaren 5 iş günü içinde kayıtlı olunan bölüm başkanlığına teslim edilir (Madde 29).",
        ),
    ),
    Topic(
        "ders_ekle_birak", "Ders ekle-bırak", "tam",
        "dönem başında ders eklemek, dersi bırakmak ya da ders kaydını değiştirmek isteyen öğrenci",
        strong=("ders ekle", "ders bırak", "dersi bırak", "ders çıkar", "dersten çekil", "ekle bırak", "add drop"),
        weak=("ekle", "bırak", "çıkar", "ders seçim", "ders kayd", "çekil"),
        query="ders ekleme-çıkarma akademik takvimdeki ders ekleme-çıkarma günleri danışmanının onayı",
        files=frozenset({YONETMELIK}),
        required_documents=(
            "Danışman onayı (ders ekleme-çıkarma OBS üzerinden yapılır)",
            "Süre geçtiyse gerekçeli dilekçe (GTÜ Rehber doldurup PDF olarak verir)",
        ),
        office="Danışmanınız (OBS) / süre dışı talepler için bölüm başkanlığı",
        key_facts=(
            "Ders ekleme-çıkarma, akademik takvimdeki ders ekleme-çıkarma günlerinde danışman onayıyla yapılır (Madde 17).",
            "Eklenen dersin ön şart ve kredi yükü şartlarını sağlaması ve ders programında çakışma olmaması gerekir (Madde 17).",
        ),
    ),
    Topic(
        "kayit_dondurma", "Kayıt dondurma (yarıyıl izni)", "tam",
        "sağlık, askerlik, maddi veya ailevi nedenle bir dönem ara vermek, kaydını dondurmak isteyen öğrenci",
        strong=("kayıt dondur", "kaydımı dondur", "kaydını dondur", "yarıyıl izni", "dönem izni", "ara vermek"),
        weak=("dondur", "izin", "askerlik", "maddi", "ailevi", "ara ver"),
        query="yarıyıl izni kayıt dondurma sağlık askerlik maddi ailevi olağan dışı durumlar izin başvurusu",
        files=frozenset({YONETMELIK}),
        required_documents=(
            "Kayıt dondurma dilekçesi (GTÜ Rehber doldurup PDF olarak verir)",
            "Gerekçeyi gösteren belge (ör. sağlık kurulu raporu, askerlik belgesi, maddi/ailevi durumu gösteren belge)",
        ),
        office="Kayıtlı olduğunuz fakülte dekanlığı (bölüm başkanlığı üzerinden)",
        side_search=(
            "öğrenimine ara veren kayıt donduran öğrencinin bursu kredisi kesilir",
            frozenset(KYK),
            "KYK burs veya kredisi alıyorsanız kayıt dondurma bu ödemeleri etkileyebilir.",
        ),
        key_facts=(
            "Sağlık, askerlik, maddi, ailevi veya olağan dışı durumlarda fakülte yönetim kurulu kararıyla bir seferde en fazla iki yarıyıl izin alınabilir (Madde 19).",
            "İzin başvurusu en geç ilgili yarıyılın ders ekleme-bırakma süresi bitimine kadar yapılır; gerekçe bu süreden sonra ortaya çıktıysa sonradan da başvurulabilir (Madde 19).",
        ),
    ),
    Topic(
        "staj_basvurusu", "Staj başvurusu", "tam",
        "zorunlu ya da isteğe bağlı staj yapmak, staj yeri, staj belgesi veya staj sigortası hakkında soru soran öğrenci",
        strong=("staj",),
        weak=("intern", "işyeri", "sigorta", "staj defter"),
        query="staj başvurusu staj yeri kabul belgesi staj komisyonu staj süresi sigorta",
        files=frozenset(STAJ_FILES),
        required_documents=(
            "Staj başvuru dilekçesi (GTÜ Rehber doldurup PDF olarak verir)",
            "Staj yerinden alınan kabul yazısı",
            "Staj sigortası için istenen belgeler (bölüm staj komisyonunun formu)",
            "Staj bittikten sonra staj defteri / raporu",
        ),
        office="Bölüm staj komisyonu",
        key_facts=(
            "Staj yerini öğrenci bulur; staj yerinin uygunluğuna Bölüm Staj Komisyonu karar verir.",
            "Başvuru, staj yerinden alınan kabul belgesiyle staj başlamadan önce Bölüm Staj Komisyonu'na yapılır; ayrıntılar fakülte staj yönergesi ve bölüm staj esaslarındadır.",
        ),
    ),
    Topic(
        "not_itirazi", "Not itirazı", "tam",
        "sınav notuna veya harf notuna itiraz etmek, notunda hata olduğunu düşünen öğrenci",
        strong=("itiraz", "notum yanlış", "notuma", "maddi hata", "sınav kağıd"),
        weak=("not", "harf notu", "puan", "düşük"),
        query="nota itiraz sınav sonuçlarına notun ilan edilmesinden itibaren 5 iş günü bölüm başkanlığına yazılı",
        files=frozenset({YONETMELIK}),
        required_documents=(
            "Not itirazı dilekçesi (GTÜ Rehber doldurup PDF olarak verir)",
            "İtiraz edilen dersin kodu ve notun ilan tarihi",
        ),
        office="Dersin bağlı olduğu bölüm başkanlığı",
        key_facts=(
            "Öğrenci, notun ilan edilmesinden itibaren 5 iş günü içinde ilgili bölüm başkanlığına yazılı olarak itiraz edebilir (Madde 28).",
            "İtiraz öğretim elemanına iletilir ve 5 iş günü içinde değerlendirilir (Madde 28).",
        ),
    ),
    # Bilgi desteği verilen konular
    Topic(
        "yatay_gecis", "Yatay geçiş", "bilgi",
        "başka bir bölüme veya üniversiteye yatay geçiş yapmak isteyen öğrenci",
        strong=("yatay geçiş",), weak=("geçiş", "bölüm değiştir", "transfer"),
        query="yatay geçiş başvuru şartları kontenjan not ortalaması",
        files=frozenset({"yatay-gecis-yonergesi.pdf", "yok-gecis-ciftanadal-yandal-yonetmeligi.pdf"}),
    ),
    Topic(
        "dikey_gecis", "Dikey geçiş", "bilgi",
        "ön lisanstan lisansa dikey geçişle gelen öğrenci",
        strong=("dikey geçiş",), weak=("dgs",),
        query="dikey geçiş intibak ders muafiyet",
        files=frozenset({"dikey-gecis-yonergesi.pdf"}),
    ),
    Topic(
        "cift_anadal", "Çift anadal", "bilgi",
        "ikinci bir bölümden çift anadal diploması almak isteyen öğrenci",
        strong=("çift anadal", "cap"), weak=("ikinci bölüm", "ikinci diploma"),
        query="çift anadal programı başvuru genel not ortalaması şartları",
        files=frozenset({"cift-anadal-yonergesi.pdf", "yok-gecis-ciftanadal-yandal-yonetmeligi.pdf"}),
    ),
    Topic(
        "yandal", "Yandal", "bilgi",
        "başka bir bölümden yandal sertifikası almak isteyen öğrenci",
        strong=("yandal", "yan dal"), weak=("sertifika",),
        query="yan dal programı başvuru şartları sertifika",
        files=frozenset({"yandal-yonergesi.pdf", "yok-gecis-ciftanadal-yandal-yonetmeligi.pdf"}),
    ),
    Topic(
        "yaz_okulu", "Yaz okulu", "bilgi",
        "yaz öğretiminde (yaz okulu) ders almak isteyen öğrenci",
        strong=("yaz okulu", "yaz öğretim", "yaz döne"), weak=("yaz",),
        query="yaz öğretimi ders alma kredi sınırı başvuru başka üniversite",
        files=frozenset({"yaz-ogretimi-yonetmeligi.pdf"}),
    ),
    Topic(
        "muafiyet_intibak", "Ders muafiyeti ve intibak", "bilgi",
        "daha önce aldığı derslerden muaf olmak, ders saydırmak isteyen öğrenci",
        strong=("muaf", "intibak", "ders saydır", "saydırma"), weak=("denklik",),
        query="ders muafiyeti intibak daha önce alınan dersler başvuru",
        files=frozenset({"muafiyet-intibak-yonergesi.pdf", "muafiyet-sinavi-esaslari.pdf"}),
    ),
    Topic(
        "ingilizce_hazirlik", "İngilizce hazırlık", "bilgi",
        "İngilizce hazırlık sınıfı, yeterlik sınavı veya hazırlıktan muafiyet hakkında soru soran öğrenci",
        strong=("hazırlık", "yeterlik sınav", "proficiency"), weak=("ingilizce", "toefl", "ielts", "yds"),
        query="ingilizce hazırlık yeterlik sınavı muafiyet devam başarı",
        files=frozenset({"ingilizce-hazirlik-yonergesi.pdf"}),
    ),
    Topic(
        "erasmus", "Erasmus", "bilgi",
        "Erasmus öğrenci değişim programına katılmak isteyen öğrenci",
        strong=("erasmus",), weak=("yurtdışı", "değişim"),
        query="erasmus öğrenim hareketliliği başvuru değerlendirme dil puanı",
        files=frozenset({"erasmus-yonergesi.pdf"}),
    ),
    Topic(
        "azami_sure", "Azami süre ve ek sınav", "bilgi",
        "azami öğrenim süresini dolduran ya da ek sınav hakkı soran öğrenci",
        strong=("azami süre", "ek sınav", "azami öğrenim"), weak=("süre doldu", "atıl"),
        query="azami öğrenim süresini tamamlayan öğrenciler ek sınav hakkı",
        files=frozenset({"azami-sure-esaslari.pdf", YONETMELIK}),
    ),
    Topic(
        "mezuniyet_diploma", "Mezuniyet ve diploma", "bilgi",
        "mezuniyet şartları, geçici mezuniyet belgesi veya diploma hakkında soru soran öğrenci",
        strong=("diploma", "mezuniyet belge", "geçici mezuniyet"), weak=("mezun",),
        query="mezuniyet belgesi diploma düzenlenmesi kayıp diploma",
        files=frozenset({"mezuniyet-diploma-yonergesi.pdf", YONETMELIK}),
    ),
    Topic(
        "kyk_burs_kredi", "KYK burs ve kredi", "bilgi",
        "KYK bursu veya öğrenim kredisi, kesilmesi ya da geri ödemesi hakkında soru soran öğrenci",
        strong=("kyk", "öğrenim kredisi", "burs kesil", "kredi borc"), weak=("burs", "kredi"),
        query="burs kredi kesilmesi başarı şartı geri ödeme",
        files=frozenset(KYK),
    ),
    Topic(
        "kismi_zamanli", "Kısmi zamanlı çalışma", "bilgi",
        "üniversitede kısmi zamanlı (part-time) çalışmak isteyen öğrenci",
        strong=("kısmi zamanlı", "part time", "parttime", "yarı zamanlı"), weak=("çalışmak", "iş"),
        query="kısmi zamanlı öğrenci çalıştırma başvuru şartları ücret",
        files=frozenset({"kismi-zamanli-calisma-yonergesi.pdf"}),
    ),
    Topic(
        "engelli_ogrenci", "Engelli öğrenci düzenlemeleri", "bilgi",
        "engelli öğrenciler için sınav ve eğitim düzenlemeleri hakkında soru soran öğrenci",
        strong=("engelli", "engel durum"), weak=("ek süre", "erişilebilir"),
        query="engelli öğrenciler sınav uygulamaları ek süre düzenleme",
        files=frozenset({"engelli-ogrenci-sinav-yonergesi.pdf"}),
    ),
    Topic(
        "danismanlik", "Akademik danışmanlık", "bilgi",
        "akademik danışmanı, danışman değişikliği veya danışman onayı hakkında soru soran öğrenci",
        strong=("danışman",), weak=("danışmanım",),
        query="danışman görevleri danışman değişikliği öğrenci danışmanlığı",
        files=frozenset({"ogrenci-danismanligi-yonergesi.pdf"}),
    ),
    Topic(
        "psikolojik_destek", "Psikolojik danışmanlık", "bilgi",
        "stres, kaygı veya kişisel sorunları için psikolojik destek arayan öğrenci",
        strong=("psikolojik", "psikolog", "rehberlik"), weak=("stres", "kaygı", "depresyon", "moral"),
        query="psikolojik danışmanlık ve rehberlik hizmetleri başvuru",
        files=frozenset({"psikolojik-danismanlik-yonergesi.pdf"}),
    ),
]

TOPICS_BY_ID = {t.id: t for t in TOPICS}

# Staj sorularında bölüme özel belgeleri seçmek için
DEPARTMENT_STAJ_FILES: dict[str, set[str]] = {
    "bilgisayar": {"staj-esaslari-bilgisayar.pdf", "staj-muhendislik.pdf"},
    "elektronik": {"staj-esaslari-elektronik.pdf", "staj-muhendislik.pdf"},
    "makine": {"staj-esaslari-makine.pdf", "staj-muhendislik.pdf"},
    "inşaat": {"staj-esaslari-insaat.pdf", "staj-muhendislik.pdf"},
    "harita": {"staj-esaslari-harita.pdf", "staj-muhendislik.pdf"},
    "kimya müh": {"staj-esaslari-kimya.pdf", "staj-muhendislik.pdf"},
    "çevre": {"staj-esaslari-cevre.pdf", "staj-muhendislik.pdf"},
    "endüstri": {"staj-esaslari-endustri.pdf", "staj-muhendislik.pdf"},
    "malzeme": {"staj-esaslari-malzeme.pdf", "staj-muhendislik.pdf"},
    "biyomühendis": {"staj-esaslari-biyomuhendislik.pdf", "staj-muhendislik.pdf"},
    "havacılık": {"staj-havacilik-uzay.pdf"},
    "uzay": {"staj-havacilik-uzay.pdf"},
    "uçak": {"staj-havacilik-uzay.pdf"},
    "mimar": {"staj-mimarlik.pdf"},
    "şehir ve bölge": {"staj-mimarlik.pdf"},
    "işletme": {"staj-isletme.pdf"},
    "fizik": {"staj-temel-bilimler.pdf"},
    "matematik": {"staj-temel-bilimler.pdf"},
    "moleküler biyoloji": {"staj-temel-bilimler.pdf"},
    "kimya bölüm": {"staj-temel-bilimler.pdf"},
}
