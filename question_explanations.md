# Soru Açıklamaları — Öğrenme Notları

> Bu dosya, her sorunun **ardındaki kavramları ve mantığı** öğrenmek içindir; teslime **GİRMEZ**.
> Burada ön bilgi + kavram tanımları + "neden böyle" ayrıntılı anlatılır.
> `report.md` (İngilizce) ve `exam_answers.md` (Türkçe) yalnızca hocanın istediği maddeleri
> içerir; bu derinlikte kavram anlatımı oralara gerekmez (yalnızca açıklama istenen yerlerde
> açıklama yapılır).

---

## Soru 1 — Hatanın Yeniden Üretimi (Failure Reproduction)

### 1. Önce temel sözlük (her soruda kullanacağız)
- **Defect / Fault (kusur):** Kaynak koddaki gerçek yanlış — yanlış yazılmış satır(lar).
  Bu projede: `parse_bool` fonksiyonunun, değeri string varsayıp `value.lower()` çağırması.
- **Error / Infection (hatalı state):** Program çalışırken bellekteki bir değerin yanlış/tehlikeli
  hâle gelmesi. Burada: `value = None` iken string gibi işlenmeye çalışılması.
- **Failure (başarısızlık):** Dışarıdan görülen yanlış davranış — çökme, yanlış çıktı vb.
- Bu üçlünün zinciri **Soru 8**'in konusudur. Soru 1'de failure'ı **görünür ve tekrarlanabilir** kılarız.

### 2. "Failure reproduction" nedir, neden İLK adım?
Hata ayıklamanın altın kuralı: **güvenilir biçimde tetikleyemediğin bir hatayı düzelttiğini
kanıtlayamazsın.** Önce hatayı istediğimiz an, aynı şekilde üreten bir komut buluruz. Bu:
- sonraki tüm deneylerin (hipotez testi → S4, delta debugging → S5) zeminini kurar,
- en sonda (S9) "düzeldi mi?" sorusunu cevaplamamızı sağlar.

İki kavram: **deterministik (reproducible)** = her çalıştırmada aynı sonuç. **Flaky** = bazen olur
bazen olmaz (zaman/rastgelelik/dış duruma bağlı). Bizim hata tamamen deterministik — bu iyi haber,
çünkü güvenilir bir test oracle'ı (S2) kurmayı kolaylaştırır.

### 3. Çıkış kodu (exit code) nedir?
Bir program bittiğinde işletim sistemine bir sayı döndürür: **0 = başarı**, **0 dışı = bir tür hata.**
Bu projede `app.py`:
- `0` → `CONFIG_OK`
- `1` → `ConfigError` (temiz/kontrollü hata) **veya** yakalanmayan çökme
- `2` → yanlış kullanım (argüman sayısı hatalı)

Çıkış kodu, hatayı **otomatik** tespit etmek (oracle, S2) için kullanışlı bir sinyaldir.

### 4. Traceback nasıl okunur?
Python bir istisnayı kimse yakalamazsa **traceback** basar:
- **En ALT satır** = istisnanın **türü + mesajı** (örn.
  `AttributeError: 'NoneType' object has no attribute 'lower'`). Önce burayı oku.
- Yukarıdan aşağıya = **çağrı zinciri** (`main → load_config → normalize_config → normalize_features → parse_bool`).
- **En alttaki çerçeve (frame)** = hatanın fiilen oluştuğu yer (`config_parser.py`, satır 150).

### 5. Hata türleri (sınav bunu açıkça soruyor)
- **Crash:** Yakalanmayan istisna; program çöker (traceback + sıfırdan farklı çıkış kodu).
- **Wrong output:** Program çalışıp biter ama **yanlış** sonuç üretir.
- **Unexpected behavior:** Spec'e aykırı ama çökmeyen davranış (örn. sessizce yanlış iş yapma).

**Bizimki = CRASH.** Neden? `app.py` yalnızca `ConfigError`'ı yakalar (`except ConfigError`).
Oluşan istisna ise `AttributeError` — `ConfigError` **değil**. Bu yüzden yakalanmaz, en üste kadar
yayılır, program çöker. Kod düzgün olsaydı geçersiz boolean için temiz bir `ConfigError`
(→ `CONFIG_ERROR`, çıkış 1) verirdi; **o** kontrollü bir hata olurdu, crash değil. Aradaki fark
sınav için önemli: "crash" derken kastımız, programın hata yönetiminin **dışına** taşan bir istisna.

### 6. Bizim vakaya uygulama
- **Komut:** `python src/app.py inputs/large_config_failure.json`
- **Neden patlıyor:** `large_config_failure.json` içinde `"features": { "debug": null }` var.
  JSON `null` → Python `None`. `normalize_features`, `parse_bool(None)` çağırır; `None.lower()`
  mümkün olmadığından `AttributeError` fırlar.
- **Neden tekrarlanabilir:** Sonuç yalnızca input içeriğine bağlı; rastgelelik/zaman/dış durum yok.
  `valid_basic.json` ve `valid_full.json` her zaman `CONFIG_OK` verir. Tek değişken = input dosyası.

### 7. Soru 1 ne istiyor, biz ne yazıyoruz?
Sınav 4 şey ister: (1) komut, (2) alınan hata mesajı, (3) tekrar-üretilebilirlik açıklaması,
(4) hata türü. Doldurulmuş hâlleri `report.md` §2 ve `exam_answers.md` S1'dedir. (Rapor şablonunda
"tekrar-üretilebilirlik" ayrı bir alan değildir; biz §2'nin içine ekledik — bkz. CLAUDE.md §2.4.)

---

## Soru 2 — Test Oracle (Test Oracle Oluşturma)

### 1. Oracle nedir?
Bir **test oracle**, bir çalıştırmanın sonucunun **doğru mu yanlış mı** olduğuna karar veren
mekanizmadır. "Programı çalıştırdım; peki sonuç DOĞRU mu?" sorusunu cevaplar. Oracle olmadan testi
otomatikleştiremezsin: girdi verirsin ama "geçti mi, kaldı mı" kararını birinin vermesi gerekir.

### 2. Oracle türleri (kısaca)
- **Specified (belirtilmiş):** Beklenen çıktı bir spesifikasyondan bilinir (örn. "2+2=4").
- **Derived / reference:** Doğru bilinen başka bir sürüm/kaynakla karşılaştırma.
- **Implicit (örtük):** Bazı davranışlar her zaman yanlıştır — çökme, yakalanmayan istisna. Bunları
  bir "spec" olmadan da yanlış sayarız.

Burada **örtük oracle** (çökme = yanlış) ile bir **spesifikasyon parçasını** (geçersiz girdi için
`ConfigError` = doğru/beklenen) birleştiriyoruz.

### 3. Kilit ayrım: ConfigError bir FAILURE DEĞİLDİR
Sezgi "istisna = hata" der; ama burada ikisini ayırmak şart:
- `ConfigError` fırlatmak → program **doğru** çalışıyor: geçersiz girdiyi **kontrollü** biçimde
  reddediyor (tasarım bu). `app.py` bunu yakalar, temiz `CONFIG_ERROR` basar. → **PASS**
- Normal dönmek (config normalize edildi) → **PASS**
- Başka bir istisnanın (`AttributeError`, `TypeError`, ...) yakalanmadan yayılması → **FAILURE**:
  kimsenin beklemediği, kontrolsüz çökme. `app.py`'nin `except ConfigError`'ı bunu yakalayamaz,
  program traceback ile sonlanır.

Yani sınırı **istisnanın TÜRÜNE** göre çiziyoruz: `ConfigError` = beklenen; gerisi = failure.
**Bu ayrım neden kritik?** `ConfigError`'ı da failure sayarsak, hatayı düzelttiğimizde (`null` →
temiz `ConfigError`) oracle bizim **doğru çözümümüzü** de "failure" işaretler — yani fix'i
doğrulayamaz hâle gelir. Bu yüzden `ConfigError` PASS olmak **zorundadır**. "Her istisna = failure"
deseydik oracle, bug'ı (crash) ile doğru reddi (`ConfigError`) ayıramaz, işe yaramazdı.

### 4. Neden otomatik olmalı?
- **Soru 3:** 8+ test yazacağız; her birinin pass/fail'ine elle bakmak yerine oracle otomatik söyler.
- **Soru 5 (delta debugging):** Onlarca küçültme denemesini otomatik "hâlâ patlıyor mu?" diye kontrol
  etmek gerekir — oracle bunu mümkün kılar.

### 5. Bizim oracle bu hatayı nasıl yakalıyor?
`tests/oracle.py` → `is_failure(raw_config)`: `normalize_config`'i çağırır; `ConfigError` ya da normal
dönüş → `False` (beklenen), başka istisna → `True` (failure). `"debug": null` verilince
`parse_bool(None)` → `AttributeError` → oracle `True` döndürür (hatayı doğru biçimde "failure" işaretler).
Doğrulandı: `valid_basic`/`valid_full` → expected, `large_config_failure` → FAILURE.

### 6. Soru 2 ne istiyor, biz ne yazıyoruz?
Sınav: oracle fonksiyonu + nasıl karar verdiği. Doldurulmuş hâlleri `report.md` §3 ve
`exam_answers.md` S2'de; çalışan kod `tests/oracle.py`'de.

---

## Soru 3 — Passing ve Failing Testler

### 1. Test nedir? "Passing / failing" ne demek?
Bir test, küçük bir kontroldür: bir girdi verir ve programın **doğru** sonucu üretip üretmediğine bakar.
- **Passing (geçen / yeşil):** Testin beklentisi tutar → program o girdide doğru davranıyor.
- **Failing (kalan / kırmızı):** Beklenti tutmaz → bir sorun var.

### 2. Hata ayıklamada "failing test" niçin yazılır?
Bir hatayı incelerken, programın **olması gereken doğru davranışını** bir teste yazarız. Hata hâlâ
duruyorsa bu test **kırmızı** olur; yani test hatanın **varlığını kanıtlar ve yerini işaret eder** —
bir alarm gibidir. Ardından **kodu** (testi değil) düzeltiriz; kod doğru davranmaya başlayınca **aynı
test kendiliğinden yeşile** döner. Bu kırmızı→yeşil geçişi, hem hatayı göstermenin hem de düzeltmenin
çalıştığını kanıtlamanın standart yoludur. Test bu süreçte **değişmez**; yalnızca kod değişir.

Sınav açısından tek not: Soru 3 birkaç **kırmızı** (failing) test ister, Soru 9 ise düzeltmeden sonra
**hepsinin geçmesini** ister; bu bir çelişki değildir — testleri değil kodu düzelttiğimiz için aynı
testler kırmızıdan yeşile döner.

### 3. Failing testi pytest'te nasıl yazarız? (A vs B — neden A?)
- **A — Düz assert (seçtiğimiz):** Doğru sonucu bekleriz, örn.
  `with pytest.raises(ConfigError): normalize_config({... "debug": None ...})`. null şu an
  `AttributeError` verdiği için `pytest.raises(ConfigError)` tutmaz → test KIRMIZI (bug görünür).
  Patch sonrası `ConfigError` gelince YEŞİL. Avantaj: failing testler raporda gerçekten "fail"
  görünür; "patch sonrası tüm testler geçer" doğrudan sağlanır; ekstra mekanizma yok.
- **B — `@pytest.mark.xfail(strict=True)`:** Testi "beklenen başarısızlık" diye işaretlersin; suite
  şimdi de yeşil görünür (`xfailed`, "failed" değil). Patch sonrası test geçince `xpass` olur ve
  `strict` bunu hata sayar (işareti kaldırmanı hatırlatır). Dezavantaj: failing testler düz kırmızı
  GÖRÜNMEZ (tabloda "fail" yerine "xfail"); ayrıca patch'te işaret kaldırma adımı gelir.
- **Neden A?** Sınav "failing test göster" diyor → kırmızıyı doğrudan göstermek en net yol, ekstra
  makine yok. (B daha çok "bilinen sebeple şimdilik geçemeyen testi suite'i kırmızı yapmadan
  işaretleme" senaryoları içindir.)

### 4. Bu testler nasıl çalışıyor? Kim çağırıyor? (pytest modeli)
Kilit nokta: **test fonksiyonlarını biz çağırmayız** — onları **pytest** (test koşucusu) çağırır.
- **Bulma (discovery):** `pytest` çalışınca, adı `test_*.py` olan dosyaları ve içlerinde adı `test_*`
  olan fonksiyonları **otomatik** bulur.
- **Çağırma:** pytest her `test_*` fonksiyonunu **kendisi çağırır** (argümansız; `parametrize` varsa
  her değer için bir kez). Yani bunlar "çağrılmayan/ölü kod" değildir — pytest'in giriş noktalarıdır.
- **Geçti/kaldı kararı:** Fonksiyon normal biterse (tüm `assert`'ler tutar, istisna çıkmaz) → GEÇTİ.
  Bir `assert` tutmazsa (AssertionError) ya da beklenmedik bir istisna çıkarsa → KALDI. `with
  pytest.raises(X):` bloğu, X istisnası çıkarsa GEÇER, çıkmazsa KALIR.
- **Nerede:** Repo kökünden `.venv\Scripts\python.exe -m pytest`. pytest tüm test dosyalarını toplar,
  tüm `test_*` fonksiyonlarını çalıştırır, sonucu raporlar (`.` = geçti, `F` = kaldı).
- **Her test ne yapar:** (1) bir girdi hazırlar (config dict ya da dosya), (2) test edilen kodu çağırır
  (`normalize_config` ya da `is_failure`), (3) sonucu `assert` / `pytest.raises` ile doğrular.
- **Çağrı zinciri:** pytest → test fonksiyonu → `normalize_config` (src) ya da `is_failure` (oracle).
  `is_failure`'ı da biz değil onu kullanan test çağırır; testi de pytest çağırır.

### 5. Bizim test setimiz (her testin ne yaptığı)
Hocanın testleriyle çakışmayan, farklı dallara bakan kendi setimiz. Her testi kısaca:

**Passing (yeşil — doğru davranışı doğrular):**
- `test_valid_minimal_defaults` — boş bölümler verilince varsayılanların atandığını kontrol eder
  (host=localhost, port=8080, level=INFO, ...).
- `test_alternative_string_booleans` — `"1"`/`"0"`/`"yes"` string boolean'larının doğru çevrildiğini
  doğrular (True/False/True).
- `test_real_booleans_passthrough` — gerçek `true`/`false` değerlerinin olduğu gibi geçtiğini doğrular.
- `test_oracle_marks_valid_config_as_expected` — oracle (`is_failure`), geçerli bir config'i
  "failure değil" (False) işaretler → S2 ile bağ.
- `test_invalid_logging_level_raises_config_error` — geçersiz `logging.level` ("VERBOSE") → temiz `ConfigError` bekler.
- `test_non_object_section_raises_config_error` — `server` object yerine string olunca → temiz `ConfigError` bekler.

**Failing (kırmızı — bug'ı gösterir; patch sonrası yeşile döner):**
- `test_null_debug_raises_config_error` — `debug: null` (null) → doğrusu `ConfigError`; şu an `AttributeError`.
- `test_int_boolean_raises_config_error` — `cache: 1` (int) → doğrusu `ConfigError`; şu an `AttributeError`.
- `test_list_boolean_raises_config_error` — `experimental: []` (list) → doğrusu `ConfigError`; şu an `AttributeError`.
- `test_large_config_file_raises_config_error` — gerçek `large_config_failure.json` dosyasını
  `load_config` ile yükler (S1 vakası) → doğrusu `ConfigError`; şu an çöküyor.

İlk üç failing, bug'ın **null/int/list — yani her non-string tipte** tetiklendiğini; dördüncüsü ise
sınavın verdiği **gerçek dosyada** gerçekleştiğini gösterir.

### 6. Soru 3 ne istiyor, biz ne yazıyoruz?
≥5 passing + ≥3 failing + tablo (test / input / beklenen / gerçek / sonuç). Kod
`tests/test_config_cases.py`; tablolar `report.md` §4 ve `exam_answers.md` S3'te. (Hocanın
`test_config_parser.py`'sine dokunmadık; kendi dosyamızı ekledik.)
