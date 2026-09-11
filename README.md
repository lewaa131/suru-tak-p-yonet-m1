# Sürüm Takip 0.9.1

0.9.1 genel kontrol düzeltmeleri: [KONTROL-RAPORU-0.9.1.md](KONTROL-RAPORU-0.9.1.md).

Yeni ayarlar: kısa açıklamalı yeşil kartlar, gün sayacı ve görünüm tercihleri. Tercihler kalıcı kaydedilir; yeni otomatik döngü bağlantısı henüz yapılmadı. Ayrıntılar: [YENILIKLER-0.9.0.md](YENILIKLER-0.9.0.md).

Android için Kivy tabanlı sürü takip uygulaması. Bu klasör kaynak projedir; kurulabilir APK değildir.

Tohumlama geçmişindeki tarihlerin sağında × düğmesi bulunur. Silme işlemi onay ister. Aktif tarih siliniyorsa gebelik ve bağlı hatırlatmaların kaldırılacağı belirtilir.

Kamera, ekran boşlukları, geri tuşu, dokunma ve tarih girişi düzenlendi. Arayüz yeşil temaya geçti; alt menü Sürüm, Bugün, Özel ve Arşiv oldu. Simge ve açılış görseli eklendi.

0.8.2: Vazgeç tek basışta kapatır; formlar üst üste birikmez. Buton üzerinde bekleyerek başlayan kaydırma desteklenir. Açılışta uygulama simgesi kullanılır, ikinci açılış penceresi yoktur.

Değişiklikler ve cihaz kontrol adımları: [YENILIKLER-0.8.0.md](YENILIKLER-0.8.0.md).

## APK oluşturma

Projenin tamamını klasör yapısıyla GitHub deposunun köküne aktar. Android APK işi tamamlanınca surum-android-apk çıktısını indir.

Yerel Linux/WSL derlemesi: `buildozer -v android debug`. Java 17, Buildozer ve gerekli Linux paketleri kurulmuş olmalıdır. APK bin/ altında oluşur. buildozer.spec içindeki çalışan Android/NDK/p4a sürümlerini ve p4a.hook ayarını koru.

## Bilgisayarda açma

Proje klasöründe CMD ile:

```cmd
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

Telefonun kendi kamera ekranı, sistem çubuğu boşlukları ve yerel bildirimler Android'de çalışır.

## Kontroller

```cmd
.venv\Scripts\python -m unittest discover -s tests -v
```

Hayvan kayıtları ve fotoğraflar uygulamanın özel veri klasöründe saklanır. Resmi küpe sorgusu internet ister. Gebelik, sağmal durumundan ayrı tutulur. Tahmini doğum ve kuruya ayırma planı aktif, doğrulanmış gebelik üzerinden hesaplanır.
