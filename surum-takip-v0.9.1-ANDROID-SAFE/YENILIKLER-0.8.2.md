# Sürüm Takip 0.8.2

- Vazgeç, parmak basıldığı anda açık formu ve klavye odağını kapatır. Parmağı kaldırırken ekran boyutunun değişmesi işlemi iptal etmez.
- Formlar birbirinin yerine açılır. Önceki form ve Vazgeç düğmesi altta kalmaz. Pencere geçişindeki bekleme animasyonları kaldırıldı.
- Buton üstünde parmak bekletildikten sonra da sayfa kaydırılabilir. Butonlarda dokunma kararı hareket veya parmağın kaldırılmasıyla verilir. Yazı alanlarında uzun basma ve yapıştırma korunur.
- Android sistem açılışı ve Python yüklemesi aynı simgeyi kullanır. Sonradan açılan ayrı açılış penceresi kaldırıldı. Android'in sistem animasyonu bulunabilir; farklı bir görsele geçiş yoktur.

Masaüstü Kivy dokunma kontrolleri: buton üzerinde 800 ms bekleyip sürükleme, normal filtre dokunuşu, odaklı yazı alanından tek basışta Vazgeç, art arda form açılışlarında tek pencere ve tek Vazgeç. Tümü geçti. Bu sürümün APK'sı burada derlenmedi; Honor üzerinde son kontrol gereklidir.

Bu ZIP kaynak projenin tamamıdır; 0.8.1 tohumlama silme özelliği ve önceki düzeltmeler dahildir. Tüm dosyaları klasör yapısını koruyarak güncelle ve yeniden APK oluştur. Yeni touch_scroll.py dosyası ile buildozer.spec birlikte aktarılmalı.
