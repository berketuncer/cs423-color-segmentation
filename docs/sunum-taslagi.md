# CS423 — Renk tabanlı segmentasyon ve sayım  
## Sunum taslağı (slayt akışı + konuşmacı notları)

Okuyan kişi: tek bakışta “ne var, neden var, sonuç ne”yi görsün diye sıra ve her slaytta **ne söyleneceği** yazıldı. Kendi ekip isimlerinizi ve gerçek rakamlarınızı ilgili slaytlara ekleyin.

---

## Slayt 1 — Kapak

**Başlık:** Renk tabanlı nesne segmentasyonu ve sayım (CS423)  
**Alt başlık:** Klasik görüntü işleme hattı — RGB / HSV, morfoloji, bağlı bileşen  
**Üzerinde:** Proje adı, ders, tarih, isimler.

**Söyle:** “Bu projede derin öğrenme yok; tamamen klasik yöntemlerle renge göre nesneleri ayırıp sayıyoruz. Çıktıları ölçülebilir ve tekrarlanabilir tutmak için veri ve ayarları JSON ile versiyonluyoruz.”

---

## Slayt 2 — Problem nedir?

**Madde:**
- Girdi: Renkli nesneler içeren **fotoğraflar**.
- Çıktı: Hedef renkteki bölgelerin **maskesi** ve **nesne sayısı**.
- Zorluk: Işık, arka plan, gölgeler, nesnelerin üst üste binmesi sayımı bozar.

**Söyle:** “Amacımız ‘bu görüntüde kırmızı (veya mavi vb.) kaç ayrı nesne var?’ sorusuna otomatik cevap. Gerçek performansı ölçmek için her fotoğrafta **elle sayılmış doğru sayı** (`expected_count`) metadata’da duruyor.”

---

## Slayt 3 — Neden klasik CV, neden “basit” pipeline?

**Madde:**
- **Tercih:** Eşikleme + morfoloji + bağlı bileşen — anlaşılır, hızlı, donanım dostu.
- **Vazgeçilen (kapsam dışı):** Derin öğrenme (YOLO, U-Net vb.), karmaşık örüntü tanıma.
- **Gerekçe:** Ders projesi olarak her adımın **matematiksel ve kod karşılığı** net; hata analizi yapılabilir.

**Söyle:** “Akıllı ama kara kutu değil; hocanın soracağı ‘burada ne yaptınız?’ her satırda cevaplanabilir.”

---

## Slayt 4 — Veri: ne topladık, ne etiketledik?

**Madde:**
- **Görüntüler:** `data/real/raw/` (veya sample: `data/sample/`).
- **Metadata (`dataset.json`):** Her görüntü için zorunlu alanlar:
  - `image_id`, `image_path`, **`target_color`**, **`expected_count`**
  - **`lighting`** (controlled / dim / bright)
  - **`background`** (plain / cluttered)
  - **`overlap`** (none / mild / heavy)
- **Profil dosyası ayrı:** `configs/profiles/v1/...json` — veri ile karışmıyor, sürüm (`profile_set_version`) var.

**Söyle:** “Aynı görüntü farklı renk hedefleriyle tekrar kullanılabilir; doğruluk karşılaştırması metadata’daki gerçek sayıya göre.”

---

## Slayt 5 — Sistem şeması (bir slayt, kutu diyagram)

**Akış (soldan sağa):**
`Fotoğraf (RGB)` → `Renk eşiği (RGB veya HSV)` → `İkili maske` → `Morfoloji (opening → closing)` → `İsteğe bağlı kenar destekli ince ayar` → `Bağlı bileşen sayımı` → `Tahmin sayısı`

**Alt not:** Ayrıca **kontur tabanlı** sayım üretilir; raporda karşılaştırma için.

**Söyle:** “Tek satırda: renk seç → gürültüyü temizle → parçaları birleştir → kaç ayrı beyaz bölge var say.”

---

## Slayt 6 — RGB eşiği: ne, artı/eksi?

**Ne:** Her piksel için R, G, B kanallarının **alt/üst sınırlar** içinde olması (kutu içinde mi?).

**Artıları:**
- Sezgisel, ayarlaması kolay, hesap ucuz.

**Eksileri:**
- **Işık değişince** aynı nesnenin RGB değeri kayar; sabit kutu kolayca kaçırır veya arka planı içeri alır.
- Kırmızı–turuncu–kahverengi ayrımı zor olabilir.

**Söyle:** “RGB’yi **baseline** ve karşılaştırma için tuttuk; ‘en basit yöntem ne kadar idare eder?’ sorusunun cevabı.”

---

## Slayt 7 — HSV eşiği: ne, artı/eksi? (ÖNEMLİ SLAYT)

**Ne:** Önce görüntü **HSV’ye** çevrilir; **H (ton), S (doygunluk), V (parlaklık/değer)** için aralık(lar). Kırmızı gibi ton dairesel olduğu için genelde **iki aralık** (ör. düşük hue + yüksek hue uçları).

**Artıları:**
- Renk kararı **ton** üzerinden; parlaklık çoğu zaman **V** kanalında, ayırım biraz daha stabil.
- Düşük doygunluklu (soluk) bölgeleri **S** eşiğiyle elemek mümkün.

**Eksileri:**
- HSV dönüşümü ve aralık seçimi yanlışsa yine hata.
- Gürültülü kamera / sıkışık arka planda yine birleşme veya kopma olur.

**Söyle:** “Projede **ana tercih mantığı**: aynı veri setinde çoğu zaman **HSV ile daha tutarlı sayım**; RGB özellikle zor ışıkta geride kalıyor. Bu yüzden sunumda **HSV’yi ‘birincil yöntem’**, RGB’yi **‘referans / karşılaştırma’** olarak konumlandırıyoruz.”

*(Kendi `presentation-bundle` rakamlarınızı buraya koyun: örn. gerçek veride HSV profilleri hedef renk filtresiyle tam isabet; RGB’de kısmi hata — bunu tablo veya tek grafikle gösterin.)*

---

## Slayt 8 — RGB vs HSV: karşılaştırma tablosu (slayt üstü)

| Ölçüt | RGB | HSV |
|--------|-----|-----|
| Sezgisellik | Yüksek | Orta (aralık + çift kırmızı aralığı) |
| Işık değişimine dayanıklılık | Genelde düşük | Genelde daha iyi |
| Ayar maliyeti | Düşük başlangıç | Biraz daha fazla (özellikle H aralığı) |
| Bu projede rol | Baseline | Ana önerilen profiller |

**Söyle:** “Vazgeçtiğimiz şey ‘tek kanallı RGB ile idare etmek’ değil; **sadece RGB’ye güvenmek** — çünkü metrikler bunu desteklemiyor.”

---

## Slayt 9 — Morfoloji ve `min_component_size`

**Opening:** Önce erozyon sonra genişletme — küçük gürültü/nozları azaltır.  
**Closing:** Önce genişletme sonra erozyon — küçük delikleri kapatır, kopukları birleştirmeye yardım eder.  
**`min_component_size`:** Piksel sayısı bu eşiğin altındaki bölgeleri sayıma **katmaz** — tuzu biberi gürültüyü atar; çok büyük seçilirse küçük nesneler **silinir** (trade-off).

**Söyle:** “Her şey `configs/...json` içinde; aynı veriyle farklı profiller denenebilir.”

---

## Slayt 10 — Sayım: bağlı bileşen (CCL) vs kontur

**CCL (4-komşu BFS):** Maske üzerinde ayrı “adalar” sayılır → **raporlanan ana sayı** bu.  
**Kontur:** Sınır takibiyle alternatif sayım; raporda **karşılaştırma** için.

**Söyle:** “İkisi aynı fikri farklı klasik yöntemle doğruluyor; anlaşmazlık varsa maskeye bakarız.”

---

## Slayt 11 — Değerlendirme: metrikler ve adil karşılaştırma

**Metrikler:**
- **Tam isabet oranı:** Tahmin = `expected_count` olan görüntü oranı.
- **MAE:** Ortalama mutlak hata (|tahmin − gerçek|).
- **FP / FN:** Fazla sayılan / eksik sayılan piksel mantığında toplu özet.

**Önemli tasarım (anlat):** Profil adı `rgb_kırmızı` / `hsv_kırmızı` biçimindeyse, özet **sadece `target_color` o renk olan** fotoğraflarda hesaplanır. Böylece “mavi profili kırmızı fotoğrafta neden kötü?” gibi **saçma cezalar** oluşmaz.

**Söyle:** “Çok renkli veri setinde bu ayrım olmadan metrikler yanıltıcı olur; biz düzelttik / bilinçli tasarladık.”

---

## Slayt 12 — Araçlar: kim ne yapar? (roller — isimleri siz doldurun)

| Rol | Ne yapar? |
|-----|-----------|
| Veri | Fotoğraf, metadata, `expected_count` doğruluğu |
| Konfigürasyon | `configs/profiles/...json` eşik ve morfoloji |
| Kod / test | `src/cs423_segmentation/`, `pytest`, `ruff` |
| Rapor | `make generate-report`, `build-*-bundle`, `results/` |

**Söyle:** “Tek kişiyseniz: ‘Ben tüm zinciri yürüttüm; şu kısımda ekip arkadaşım X veri topladı’ diye net söyleyin.”

---

## Slayt 13 — `results/` klasörü (1 dakika)

**Kısa ağaç:**
- `results/datasets/<sample|real>/`
  - **`quick-eval/`** — hızlı JSON özetleri  
  - **`full-report/`** veya **`presentation-bundle/`** — tablolar, grafikler, `json-details`, önizleme görselleri  
  - **`threshold-tuning/`** — birkaç eşik varyantının sıralaması  

**`results/README.md`:** Klasör rehberi (repoda tutulur).

**Söyle:** “Çıktılar kodla birlikte commit edilmez; `make` ile yeniden üretilir.”

---

## Slayt 14 — Tuning: ne yapıyor, ne yapmıyor?

**Yapıyor:** Seçili profil etrafında **önceden tanımlı birkaç varyant** (ör. daha gevşek / daha sıkı HSV) dener, veri setinde skorlar ve **sıralar**.  
**Yapmıyor:** Sonsuz arama / otomatik en iyi global optimum garantisi.

**Söyle:** “İlk ayarları insan verir; tuning ‘hangi küçük değişiklik daha iyi?’ sorusuna hızlı cevap.”

---

## Slayt 15 — Sonuçlar (kendi rakamlarınızı koyun)

**Önerilen içerik:**
- Bir tablo: profil başına tam isabet, MAE (gerçek veri).
- İki görsel: **kötü** ve **iyi** örnek — maske + overlay (`image-previews/`).
- Bir cümle: “HSV ile … RGB ile …”

**Söyle:** “Hata çoğunlukla eksik tespit veya birleşik nesne; bunu maske üzerinde gösteriyorum.”

---

## Slayt 16 — Sınırlamalar ve gelecek iş (dürüstlük puanı)

**Sınırlamalar:**
- Sabit eşikler; sahne değişince yeniden ayar gerekebilir.
- Örtüşen nesneler tek bileşen gibi görünebilir.
- Benzer renkli arka plan false positive üretebilir.

**Gelecek (vazgeçmediğimiz ama sonraki adım):** LAB renk uzayı, adaptif eşik, watershed, veya derin öğrenme tabanlı instance segmentation.

**Söyle:** “%100 her koşulda klasik yöntemle vaat etmiyoruz; ama veri ve metrik tasarımı doğruysa sonuçlar güvenilir ve geliştirilebilir.”

---

## Slayt 17 — Demo (opsiyonel 1–2 dk)

Canlı veya kayıtlı:
```bash
PYTHONPATH=src python3 -m cs423_segmentation evaluate \
  --metadata data/real/metadata/dataset.json \
  --profile hsv_red \
  --output /tmp/out.json
```
veya `make build-real-bundle` sonrası bir `profile-summary.csv` göstermek.

---

## Slayt 18 — Soru–cevap hazırlığı (kısa)

| Soru | Cevap yönü |
|------|------------|
| Neden OpenCV yok? | HSV ve morfoloji NumPy ile; bağımlılık ve şeffaflık. |
| HSV’de kırmızı neden iki aralık? | Ton dairesel; 0° ve 180° yakını birleştirilir. |
| MAE ile accuracy farkı? | Accuracy tam eşleşme; MAE büyük hataları cezalandırır. |
| FP vs FN? | Fazla nesne / eksik nesne. |
| Tuning %100 garanti eder mi? | Hayır; birkaç aday arasından sıralama. |

---

## Zaman önerisi (≈12–15 dk + soru)

| Blok | Süre |
|------|------|
| Problem + veri | 2 dk |
| Pipeline | 2 dk |
| **RGB vs HSV** | **3–4 dk** |
| Değerlendirme + sonuç | 2–3 dk |
| Araçlar + results | 1–2 dk |
| Sınırlama + demo | 2 dk |

---

## Sunumu okuyan biri “şak diye” ne anlamalı?

1. **Ne:** Renge göre maske + sayı.  
2. **Nasıl:** Eşik → morfoloji → (isteğe bağlı) ince ayar → bağlı bileşen.  
3. **Neden HSV:** Aynı veride genelde daha stabil; RGB karşılaştırma baseline’ı.  
4. **Doğruluk:** Metadata’daki gerçek sayı; çok renkte profil–renk eşlemesi adil metrik.  
5. **Çıktı:** `results/` + JSON/CSV/SVG; tekrarlanabilir `make` komutları.

Bu metni slaytlara bölüp başlıkları kısaltın; rakam ve görselleri kendi `presentation-bundle` çıktınızdan alın.
