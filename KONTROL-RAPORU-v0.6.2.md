# Sürüm v0.6.2 — Kontrol sonucu

10 Eylül 2026

## Düzeltilen hatalar

- Küpe alanı doluyken başa veya araya rakam girilmesi son rakamı silebiliyordu. Artık fazla giriş eklenmeden engellenir; seçili metnin değiştirilmesi ve 12 rakam sınırı korunur.
- Ekran her dakika yeniden kuruluyor, kaydırılan profil ve özel listeler başa dönebiliyordu. Yenileme gün değişiminde yapılır; kaydırma konumu korunur.
- Bir tohumlama tarihine geri dönmek geçmişte aynı günü tekrar oluşturabiliyordu. Tekil kayıt kuralı eklendi; mevcut yinelenen günler birleştirilir.
- Yeni tohumlamanın son kayıtlı doğumdan önce başlaması engellendi.
- Sürüye geri alma tarihinin satış/arşiv tarihinden önce olması engellendi.
- Resmi doğum tarihi mevcut tohumlama geçmişinden sonraya gelirse çelişkili güncelleme reddedilir; kayıt korunur.
- Fotoğraf değiştirildiğinde, kaldırıldığında veya hayvan silindiğinde kullanılmayan uygulama kopyası temizlenir. Galerideki asıl fotoğraf ve başka kayıtların kullandığı fotoğraf silinmez.
- Kapanmış uygulamaya geç dönen sorgu/fotoğraf yanıtlarının kayıt ekranını güncellemesi engellendi.
- Bildirim izni değiştiğinde profildeki izin durumu yenilenir.
- Bildirim belgesindeki kaldırılmış deneme düğmesi ve sabit saat açıklamaları güncellendi.

## İstenen özelliklerin durumu

| Özellik | Durum |
|---|---|
| Sabit TR, yalnızca 12 rakam, yapıştırma sınırı | Uygulandı; masaüstünde çalıştırılarak sınandı |
| Uzun basma/seçim için Türkçe metin menüsü | Uygulandı; menü masaüstünde açılıp kontrol edildi. Android dokunması ayrıca denenmeli |
| Sağ tıkta dokunma simülasyonunu kapatma | Başlangıç ayarı mevcut |
| Ayrı bilgi kutuları ve simgeli beş alt sekme | Uygulandı; sekmeler ve profil açıldı |
| Bugün, doğum, kurular ve gecikenler | Liste filtreleri ve tarih sınırları test edildi |
| Kuruya ayırdım ve Doğum yaptı | Durum değişimi, geçmiş ve bildirim iptali test edildi |
| Satılan, ölen, arşivlenen ayrı listeler; geri alma | Kayıtlar korunarak taşıma, yeniden açılış ve bildirim planı test edildi |
| Hayvan silme | Onay ekranı, ilişkili geçmişin silinmesi ve işlem geri alma testleri mevcut |
| Ana ekrandan Hatırlatmalar düğmesinin kaldırılması | Tamamlandı |
| Bildirim ayarlarında yalnızca gün ve saat | Tamamlandı; iki alanlı ekran ve ayarların saklanması test edildi |
| Arka plan bildirimi ve yeniden başlatma alıcısı | Kod ve Android derleme bağlantıları mevcut; gerçek cihaz teslimi henüz doğrulanmadı |
| Kurulabilir APK | Henüz üretilmedi. Verilen dosya kaynak ZIP’idir |

## Yapılan kontroller

- **51 otomatik veri/mantık testi başarılı.** Kayıt, göç, gebelik, tarih, arşiv, fotoğraf ve bildirim planını kapsar.
- Kivy 2.3.1 ile Windows üzerinde uygulama açıldı. Beş sekme, profil, bildirim ayarları ve Türkçe metin menüsü çalıştırıldı. Küpede yapıştırma, seçili metni değiştirme ve taşma sınandı.
- Android bildirim alıcısı Android API 36 kitaplığına karşı Java olarak derlendi. Derleme hatası yok; eski Android sürümlerini destekleyen bildirim kurucusu için bir kullanım dışı API uyarısı var.
- Tam Android APK derlemesi yapılmadı. Android'de kamera, galeri, sayısal klavye, uzun basma, yeniden başlatma ve uyku hâlinde bildirim teslimi cihaz testi bekliyor.
- Resmi küpe sorgu sayfasının erişilebilirliği önceki incelemede kontrol edildi. Gerçek hayvan verisiyle uçtan uca sorgulama yapılmadı; sayfa değişirse bağlantı etkilenebilir. Mevcut kayıtları kullanmak internet gerektirmez, yeni resmi sorgu gerektirir.

## Henüz eklenmeyen fikirler

Bunlar konuşmada önerildi; tamamlandıkları söylenmemeli:

- Yedekleme ve yeni telefona geri yükleme.
- Sabah/akşam süt kaydı ve verim grafikleri.
- Doğumdan otomatik buzağı kaydı ve anne–buzağı bağlantısı. Şu an Doğum yaptı yalnızca annenin gebeliğini kapatır ve doğum tarihini saklar.
- Kullanıcının ekleyebildiği aşı, tedavi ve veteriner takvimi. Şu an resmi sorgudan gelen aşılar görüntülenir; bakım notu tutulabilir.
- Gelir–gider ve toplu işlem.

Önerilen sıra: önce APK ve gerçek cihaz kontrolü, ardından yedekleme/geri yükleme, anne–buzağı bağlantısı ve süt takibi.
