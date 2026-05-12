# `results/` klasörü — ne nerede?

Bu dizin **program çalıştıkça üretilen** tablolar, grafikler, JSON ve görüntüleri tutar. Kaynak kod `src/`, veri tanımı `data/` içindedir; **sayısal ve görsel sonuçlar** burada toplanır.

## Üst düzey yapı

```text
results/
  README.md                 ← bu dosya (açıklama, repoda tutulur)
  datasets/
    sample/                 ← örnek veri kümesi (data/sample/...)
    real/                   ← gerçek foto veri kümesi (data/real/...)
```

Her veri kümesi altında **aynı anlamlı alt klasör adları** kullanılır; böylece `sample` ile `real` arasında kafa karışıklığı olmaz.

## `datasets/<sample|real>/` altındaki klasörler

| Klasör | Makefile / komut | İçerik (kısaca) |
|--------|------------------|-----------------|
| **`quick-eval/`** | `make evaluate-rgb`, `evaluate-hsv`, `run-experiments` | Tek profil veya tüm profiller için **özet JSON** (`rgb_red.json`, `experiment-summary.json`, …). Hızlı sayısal sonuç. |
| **`full-report/`** | `make generate-report` | Tam rapor: `tables/` (CSV/MD), `charts/` (SVG), `json-details/` (ham JSON), `image-previews/masks|overlays/` (PNG). |
| **`threshold-tuning/<profil_adı>/`** | `make tune-sample-rgb` vb. | O profil için birkaç eşik varyantının **sıralı listesi** (`tuning-results.json`, `.csv`, `.md`). |
| **`presentation-bundle/`** | `make build-sample-bundle` / `build-real-bundle` | **Sunum ve teslime uygun tek paket**: yukarıdaki `full-report` ile aynı iç yapı + `threshold-tuning/` + kökte `README.md`. |

## `full-report` ve `presentation-bundle` içindeki ortak yapı

Program bu isimleri **bilerek** seçti; İngilizce ama anlamı sabit:

```text
tables/              ← Excel’de açılabilir özetler + Markdown tablolar
charts/              ← Sunum slaytına atılabilir SVG grafikler
json-details/        ← experiment-summary.json, <profil>-detail.json
image-previews/
  masks/             ← Siyah-beyaz segmentasyon maskesi (her görüntü × profil)
  overlays/          ← Orijinal + maske vurgusu
threshold-tuning/    ← Sadece presentation-bundle içinde (build-bundle tuning açıkken)
```

## Nereden başlamalıyım?

1. **Sadece “kaç doğru?”** → `quick-eval/experiment-summary.json` veya tek profil `quick-eval/hsv_red.json`.
2. **Tablo + grafik + maskeler** → `full-report/` (veya paket için `presentation-bundle/`).
3. **Eşik ayarı hangi varyant kazandı?** → `threshold-tuning/<profil>/tuning-results.md`.

Detaylı alan adları ve metrikler için proje kökündeki `README.md` dosyasına bakın.
