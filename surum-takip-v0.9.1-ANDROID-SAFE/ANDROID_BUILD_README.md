# Sürüm 0.5.0 — Android APK üretimi

Yeni: 60 gün kala kuruya ayırma ve tahmini doğum günü bildirimi. Kurulum, sınırlamalar ve cihaz kontrolleri için [HATIRLATMALAR.md](HATIRLATMALAR.md). Android Java alıcısı `android/src` altında, manifest kaydı `android/manifest_application.xml` içindedir; derlemede bu klasörü koruyun. Bu sürümün Android derlemesi ve cihaz teslimi henüz doğrulanmadı.

Bu klasör Android için hazırlanmış Kivy/Buildozer projesidir. Uygulama mantığı yeniden yazılmadı; mevcut Python kodu Android APK içine paketlenir.

## Android için yapılan ayarlar

- `INTERNET` izni: resmi küpe sorgusu için.
- `CAMERA` izni: uygulama içi fotoğraf çekimi için.
- Galeri: Android `ACTION_OPEN_DOCUMENT` kullanır; depolama / tüm fotoğraflara erişim izni istemez.
- Veritabanı: `App.user_data_dir/suru.sqlite3` altında uygulamanın özel alanında tutulur.
- Hedef Android API: 36.
- Minimum Android API: 23 (Android 6.0+).
- Mimari: `arm64-v8a` (güncel 64-bit Android telefonlar).
- NDK: 28c.
- python-for-android: `v2026.05.09`.

## En kolay yöntem — GitHub Actions ile APK

1. Bu klasörün içeriğini yeni bir GitHub deposuna yükleyin.
2. GitHub'da **Actions** sekmesini açın.
3. **Android APK** iş akışını seçin.
4. **Run workflow** düğmesine basın.
5. İşlem başarılı olduğunda çalışmanın altındaki **Artifacts** bölümünden `surum-android-apk` dosyasını indirin.
6. ZIP'i açın; içindeki `.apk` dosyasını Android telefona gönderip kurun.

Workflow dosyası: `.github/workflows/android-apk.yml`

## Windows + WSL ile yerel APK

Buildozer Windows üzerinde doğrudan Android derlemez; WSL2/Ubuntu kullanın.

1. WSL içinde projeyi Linux dosya sistemine kopyalayın, örneğin `~/suru-takip-android`.
2. Proje klasöründe:

```bash
chmod +x BUILD_ANDROID_WSL.sh
./BUILD_ANDROID_WSL.sh
```

Derleme başarılı olduğunda APK `bin/` klasöründe oluşur.

## Telefonda kurulum

Android, Play Store dışından APK kurarken "Bilinmeyen uygulamaları yükleme" izni isteyebilir. Yalnızca kendi ürettiğiniz APK için bu izni verin.

## Test edilenler

Kaynak projedeki 25 Python mantık testi Android paketleme öncesinde başarıyla geçti. Bunlar kayıt/migrasyon, hayvan profili, üreme kuralları, resmi yanıt ayrıştırma, fotoğraf işleme ve temsili görsel mantığını kapsar.

Gerçek cihazda özellikle şu dört akış ayrıca denenmelidir:

1. Uygulamayı kapat/aç — kayıtların kalması.
2. Küpe sorgusu — mobil ağ ve Wi-Fi.
3. Kamera izni + fotoğraf çekimi.
4. Galeriden fotoğraf seçimi.
