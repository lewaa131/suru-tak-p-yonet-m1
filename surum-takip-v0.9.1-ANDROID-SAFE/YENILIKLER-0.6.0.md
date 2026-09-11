# Sürüm 0.6.0

Alt menüde simgeli beş sekme var:

- **Sürüm:** Aktif hayvanlar, arama, filtreleme ve hayvan ekleme.
- **Bugün:** Doğum kontrolü gerekenler ve kuruya ayrılacaklar.
- **Doğum:** Tahmini doğum tarihi bugün olanlar ve tarihi geçenler ayrı listelerde.
- **Özel:** Kurular ve doğumu gecikenler ayrı listelerde. Kuru ve gecikmiş bir hayvan iki listede de yer alabilir.
- **Arşiv:** Satılanlar, ölenler ve arşivlenenler ayrı listelerde.

Ana ekrandaki Hatırlatmalar düğmesi kaldırıldı. Bildirimler çalışmaya devam eder; ayarlar hayvan profilindedir.

**Kuruya ayırdım:** İşlem tarihiyle kuru döneme geçirir. Doğum bildirimi devam eder.

**Doğum yaptı:** Doğum tarihini saklar, gebeliği kapatır ve durumu Sağmal yapar. Bu işlem otomatik buzağı kaydı oluşturmaz.

**Satıldı / Öldü / Arşiv:** Hayvanı ilgili listeye taşır. Notları, fotoğrafı, gebelik ve tohumlama geçmişi korunur; aktif işler ve bildirimlerden çıkarılır.

**Sürüye geri al:** Tarihli onayla hayvanı aktif sürüye taşır. Saklanan gebelik kaydı hâlâ aktifse bildirimleri yeniden planlanır; geri alırken kaydı kontrol edin.

Mevcut kayıtlar ilk açılışta Aktif olarak korunur. 43 mantık testi geçti. Simgeler uygulama içinde çizilir. Kivy ekranları ve Android cihaz davranışı bu bilgisayarda doğrulanmadı; paket kaynak ZIP’idir, APK değildir.
