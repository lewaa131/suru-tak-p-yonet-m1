# Sürüm 0.5.0 — Gebelik hatırlatmaları

- Tahmini doğumdan varsayılan **60 gün önce**: **Kuruya ayır**. Gün sayısı ayarlardan değişir.
- Tahmini doğum tarihinde: **Tahmini doğum bugün**.
- Varsayılan saat: telefonun yerel saatine göre **09.00**. Ayarlardan değişir. Android pil yönetimi teslimi geciktirebilir; kesin saat garantisi verilmez.
- Gebelik doğrulanmış ve tohumlama tarihi girilmiş olmalı. Hesap, kayıtlı gebelik süresini kullanır.
- Hayvan kuru döneme alınırsa kuruya ayır uyarısı iptal edilir. Doğum uyarısı devam eder.
- Gebelik kapatılınca, tarih temizlenince veya hayvan silinince ilgili plan ve eski görünür bildirimler kaldırılır.
- Tarih değişikliği planı yeniler. İsim değişikliği aynı uyarıyı tekrar göndermez.
- Her uyarı, ilgili gebelik/tarih için bir kez gönderilir. Kuru dönem tarihi geçmişken kayıt girilirse doğuma kadar kuruya ayır uyarısı yetiştirilir. Doğum günü geçtiyse kaçırılmış uyarı “Tahmini doğum tarihi geçti” olarak bir kez gösterilir.

## Telefonda kullanım

1. Uygulamayı aç, gebe hayvanın tohumlama tarihini kaydet ve **Gebelik doğrulandı** seçeneğini aç.
2. Android bildirim iznini isterse izin ver. Hayvan profilindeki **Hatırlatmalar → Bildirim ayarları** bölümünde durumunu kontrol et. Ana ekranda Hatırlatmalar düğmesi yoktur.
3. Ayarlarda yalnızca **Kuruya ayır · kaç gün önce?** ve **Bildirim saati** bulunur. Kaydet ile plan güncellenir. Deneme düğmesi kaldırıldı.

Bildirim planı telefonda saklanır. Uygulama görünür değilken Android alıcısı çalışır; Python'un sürekli açık tutulması ve internet bağlantısı gerekmez. Yeniden başlatma sonrası telefonun kilidi açıldığında, saat/saat dilimi değiştiğinde ve uygulama güncellendiğinde plan tekrar kurulur.

**Zorla durdur** bildirimleri engeller; devamı için uygulamayı yeniden aç. Bazı telefonların ek pil/otomatik başlatma kısıtları da teslimi etkileyebilir. Windows sürümü Android bildirimi göndermez.

## Doğrulama durumu

Python tarih, plan değişikliği, iptal ve tekrar kurma testleri çalıştırıldı. Yerel bilgisayarda Android SDK/derleme ortamı bulunmadığından Java derlemesi, APK ve gerçek cihaz teslimi doğrulanmadı. Bu paket kaynak koddur.

APK üretildikten sonra Android 13+ bildirim izni, izin reddi/yeniden açma, uygulama kapalıyken deneme, yeniden başlatma, saat dilimi değişimi, kuru dönem iptali, gebelik kapatma, silme ve yinelenen uyarı kontrolü cihazda denenmelidir.

## Uygulama notları

Android AlarmManager `setAndAllowWhileIdle` ile tek bir sonraki alarm kurulur. Manifest alıcısı ve SharedPreferences planı, Python ekranından bağımsızdır. Kesin alarm izni ve sürekli ön plan servisi kullanılmaz. Kullanıcı verileri dış bir servise gönderilmez.

Kaynaklar: [Android alarmları](https://developer.android.com/reference/android/app/AlarmManager#setAndAllowWhileIdle(int,%20long,%20android.app.PendingIntent)), [bildirim izni](https://developer.android.com/develop/ui/compose/notifications/notification-permission), [zorla durdurma](https://developer.android.com/about/versions/15/behavior-changes-all#stopped-state).
