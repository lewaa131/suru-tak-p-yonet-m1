# Sürüm Takip 0.9.0 — Yeni ayarlar

## Takip tercihleri

Her ayar ayrı yeşil/beyaz kartta, tek cümlelik açıklamayla gösterilir. Günler − / + ile değiştirilebilir veya sayıya dokunarak yazılabilir.

- Gebelik takvimi: mevcut çiftlik ayarından alınır; ilk varsayılan 283 gün.
- Gebelik kontrolü: 35 gün ve hatırlatma tercihi.
- Kuruya ayırma: mevcut bildirim ayarından alınır; ilk varsayılan 60 gün ve hatırlatma tercihi.
- Sütten kesme: 100 gün ve hatırlatma tercihi.
- Yeni doğuran takibi: mevcut çiftlik ayarından alınır; ilk varsayılan 60 gün ve hatırlatma tercihi.
- Doğum sonrası bekleme: 60 gün.
- İlk tohumlama yaşı: 420 gün.
- Tohumlama kayıt aralığı: 7 gün; gebelik teşhisi yapıldığı anlamına gelmez.
- Süt kaydı: sabah/akşam veya günlük toplam.
- Takvim: hafta, iki hafta veya ay.
- Hayvan görselleri: göster/gizle tercihi.

## Bu aşamanın kapsamı

Yeni tercihler cycle-settings.json dosyasında kalıcı saklanır. Kaydetmeden Vazgeç veya geri kullanılırsa değişiklikler bırakılır. Geçersiz gün sayısı kaydı engeller; önceki kayıt korunur.

Kullanıcının istediği gibi bu sürüm yalnızca ayar hazırlığıdır. Yeni hatırlatmalar, otomatik durum geçişleri, süt kayıt ekranı, takvim ve görsel tercihlerinin uygulanması sonraki aşamadadır. Ekranın başındaki açıklama ve kayıt mesajı bunu belirtir. Mevcut gebelik hesabı, kuruya ayırma ve doğum bildirimleri önceki ayarlarıyla devam eder. “Şu an çalışan ayarlar” düğmesi mevcut ayarlara erişim sağlar.

## Kontrol

66 otomatik test geçti. Kivy'de gün artırma/azaltma ve sınırlar, aç/kapa ve seçenekler, iptal, kaydetme ve yeniden açma kontrol edildi. Yeni tercihleri kaydetmenin hayvan kayıtlarını ve mevcut bildirim planını değiştirmediği doğrulandı. Telefon üzerinde henüz test edilmedi.

Bu ZIP kaynak projedir; APK değildir. Önceki düzeltmelerin tamamı dahildir. Klasör yapısını koruyarak tüm proje dosyalarını aktar ve yeniden APK oluştur; cycle_settings.py ve settings_ui.py yeni dosyalardır.
