# Genel kontrol — Sürüm Takip 0.9.1

## Düzeltilen hatalar

1. Satış, ölüm, arşiv ve doğum gibi işlem pencerelerinde hayvan kimliği beyaz zeminde beyaz yazıyordu. Koyu yeşil metne çevrildi.
2. Tarihte bir nokta silindikten sonra alan odağı değişince yıl kırpılabiliyordu. Ayraçlar yeniden oluşturulurken tarih rakamları korunuyor.
3. Tohumlama geçmişi silinince resmi doğum tarihi eski doğum/arşiv işlem tarihinden sonraya güncellenebiliyordu. Resmi güncelleme artık işlem geçmişini de kontrol ediyor; çelişki varsa kayıt korunuyor.
4. Tohumlama tarihi bilinmeyen gebelikte yeni doğum, önceki doğumla aynı veya daha eski bir tarihe kaydedilebiliyordu. Bu işlem artık reddediliyor.
5. Kamera dönüşünde dosya bulunamaması veya geçici iznin kaldırılamaması hataları yakalanmıyordu. Hata mesajı ve birbirinden bağımsız dosya/izin temizliği eklendi.

## Doğrulama

72 otomatik test geçti. Kayıt kalıcılığı, arşiv/silme, gebelik ve doğum hesapları, tarih girişi, fotoğraf yönü, kamera hata yolları, manifest ve ayar doğrulamaları kapsandı. Kamera hata testleri Android çağrılarını taklit eder; cihazda çekim testi değildir.

Masaüstü Kivy'de butonda 800 ms bekleyip kaydırma, normal buton dokunuşu, odaklı alandan tek basışta Vazgeç, tek form/tek Vazgeç, tek dokunuşla yazma, geri ile klavye/pencere kapatma, tarih yazma ve iç içe bilgi penceresi kontrol edildi.

Bu kontrol APK derlemesi veya gerçek Honor testi içermiyor. Kamera yönü, sistem çubuğu boşlukları, Android geri hareketi, kapalı uygulamaya bildirim ve telefon yeniden başlatıldıktan sonraki bildirim davranışı cihaz üzerinde doğrulanmalı.

## Kalan kapsam ve eksikler

- Yeni döngü tercihleri kaydediliyor; otomatik durum geçişlerine henüz bağlı değil. Bu, önce ayarların hazırlanması yönündeki isteğe uygun. Yeni sütten kesme/gebelik kontrolü/yeni doğuran hatırlatmaları, süt giriş modu, takvim ve görsel tercihi henüz uygulanmıyor. Mevcut doğum/kuru dönem hatırlatmaları ayrı mevcut ayarları kullanır.
- Uygulamada kullanıcıya açık yedekleme, dışa aktarma ve geri yükleme yok. Telefona geçiş veya yeniden kurulum için kayıt aktarımı eksik. Android otomatik yedek ayarı da kapalı. Bir sonraki geliştirmede veri yedekleme ele alınmalı.
- Yeni hayvan eklemek resmi küpe sorgusunun başarılı olmasına bağlı. Çevrimdışı manuel kayıt akışı yok. Kayıtlı hayvanların yerel takibi internetten bağımsızdır. Bu kontrolde canlı resmi sorgu yapılmadı.
- APK güncellemesi mevcut kurulumla aynı imzalama anahtarını kullanmalı. Mevcut iş akışında kalıcı imza anahtarını saklayan bir adım görülmedi; önceki APK'nın imzası bu kontrolde incelenmedi.

## Güncelleme

0.9.1 ZIP'i tam kaynak projedir, APK değildir. Önceki tüm özellikler ve düzeltmeler dahildir. Tüm dosyaları klasör yapısıyla aktararak APK'yı yeniden oluştur. Kurulu uygulamanın verilerini temizleme veya uygulamayı kaldırma; mevcut kayıtların yedeği yoksa kaybolabilir.
