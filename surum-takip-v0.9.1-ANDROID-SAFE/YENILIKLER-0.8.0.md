# Sürüm Takip 0.8.0 — Telefon düzeltmeleri

- Kamera: Android'in kendi tam ekran çekim ekranı açılır. Dikey/yatay yön bilgisi fotoğraf içeri alınırken uygulanır. Geri ile çekimden vazgeçilebilir.
- Ekran: durum çubuğu, kamera deliği, gezinme çubuğu ve klavye için Android'in bildirdiği alan ayrılır. Uygulama bu alanın içinde kalır; sistem çubuklarının zemini yeşildir.
- Dokunma: kart ve buton üzerinden başlayan kaydırma düzenlendi. Metin alanları tek dokunuşla odaklanır; kaydırma sonrası gelen dokunma olayı klavyeyi kapatmaz.
- Geri: klavye, açılır liste, en üst pencere, hayvan profili ve sekme sırasıyla geri alınır. Android 13 ve üzerinin geri hareketi ayrıca bağlandı.
- Tarih: 01092026 yazıldığında 01.09.2026 olur. 1.9.2026 veya 1/9/2026 yapıştırılabilir. Geçersiz günler kaydedilmez.
- Sekmeler: Sürüm, Bugün, Özel, Arşiv. Bugün doğum beklenenler artık Özel içinde; kurular ve gecikenler ayrı listelerdir.
- Görünüm: yeşil tonları, ortak Roboto yazı tipi, yeşil seçim düğmeleri ve açık yeşil pencereler. Hayvan kartlarındaki görsel ve durum yazıları küçültüldü. Sağmal ve Gebe birlikte görünür.
- Marka: gönderilen simge ve açılış görseli pakete eklendi.
- Paketleme: bildirim alıcısı ve kamera sağlayıcısı Android manifestine doğru öğeler olarak eklenir. Mevcut çalışan Python-for-Android sürümü ve Android derleme sürümleri korundu.

## Yapılan kontroller

58 otomatik veri/tarih/fotoğraf/manifest kontrolü geçti. Dört sekme, filtreler, form görünümü, tek dokunuşla odak, butondan kaydırma, iç içe pencerelerin geri ile kapanması ve tarih yazma masaüstü Kivy üzerinde kontrol edildi. Android Java sınıfları API 36 ile derlendi.

Bu paket kaynak koddur. Bu sürümün APK'sı burada derlenmedi ve Honor Magic 7 Pro üzerinde henüz denenmedi. Kamera, sistem çubukları ve Android geri hareketi için cihaz kontrolü yapılmalı.

## Honor üzerinde kısa kontrol

1. Açılışta yeni simge ve görseli kontrol et. Üstteki başlık ve alttaki dört sekme sistem çubuklarının altında kalmamalı.
2. Sağmal kartının üstünden yukarı sürükle. Sayfa kaymalı, filtre yanlışlıkla açılmamalı.
3. Bakım notuna bir kez dokun. Yazı yaz; geri ile önce klavye, tekrar geri ile pencere kapanmalı.
4. Tohumlamada 01092026 yaz. 01.09.2026 görünmeli. Alanı seçip 1.9.2026 yapıştırmayı da dene.
5. Bir hayvanın fotoğrafını dik tutarak çek, ardından yatay çek. İkisi de profilde doğru yönde görünmeli. Çekimden vazgeçince önceki fotoğraf kalmalı.
6. Özel'de bugünkü doğumlar, kurular ve gecikenler ayrı görünmeli. Arşiv listeleri korunmalı.
7. Klavye açıkken Kaydet ve Vazgeç görünür olmalı. Üç düğmeli gezinme ve hareketle gezinmede alt sekmeler rahatça kullanılabilmeli.

## Kaynak güncelleme ve APK

ZIP'i aç. İçindeki proje dosyalarını GitHub deposunun köküne, klasör yapısını koruyarak aktar. Özellikle assets, android ve .github klasörleri ile android_hook.py, android_runtime.py, android_camera.py, app_popup.py, date_entry.py ve theme.py birlikte gitmeli. Yalnızca main.py'yi değiştirmek yeterli değildir.

Mevcut Android APK iş akışı yeni kodu derler. İşlem bitince Actions içindeki surum-android-apk çıktısını indir.

Mevcut hayvan kayıtlarını korumak için uygulamanın verilerini temizleme. Güncelleme aynı paket adı ve aynı imza ile yapılmalıdır. Telefon imza/paket çakışması bildirirse eski uygulamayı silmeden önce dur; mevcut kurulumun imzalama anahtarı gerekir.
