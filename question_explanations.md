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

---

## Soru 4 — Scientific Debugging (Bilimsel Hata Ayıklama)

### 1. Nedir?
Rastgele deneme yapmak yerine **bilimsel yöntemi** uygularız:
1. **Hipotez:** Hatanın nedeni hakkında test edilebilir bir iddia ("Hata X yüzünden oluyor").
2. **Deney:** İddiayı sınamak için **tek bir değişkeni** değiştirip programı çalıştır.
3. **Gözlem:** Ne olduğunu kaydet (OK / temiz hata / crash).
4. **Sonuç:** Gözlem hipotezi destekliyor mu? → **Kabul** ya da **Ret**.

### 2. Kontrollü deney = tek değişken
Güvenilir sonuç için her deneyde **yalnızca bir şeyi** değiştir, gerisini sabit tut. "null mı
tetikliyor?" derken sadece `debug`'ı null↔false arasında değiştir, kalan her şey aynı kalsın; böylece
sonucu **kesin olarak** o değişkene bağlayabilirsin.

### 3. Ret de Kabul kadar değerlidir
İyi hata ayıklama, yanlış nedenleri **elemeyi** de içerir. "Eksik alan mı?", "iç içe yapı mı?" gibi
makul ama yanlış hipotezleri deneyle çürütmek (Ret), gerçek nedeni daraltır.

### 4. Tümevarım: tekil gözlemden genel nedene
Tek bir vakadan ("debug=null çöküyor") genel bir kurala ("string olmayan HER değer çöküyor") deneyle
geçilir (int/list/float deneyerek). Bu, kök nedeni (parse_bool'un `.lower()` varsayımı) açığa çıkarır.

### 5. Bizim 4 hipotezimiz (özet)
- **H1 (Kabul):** null tetikler (debug=null → crash; debug=false → OK).
- **H2 (Kabul):** null'a özel değil; int/list/float de tetikler — kök neden parse_bool'un string varsayması.
- **H3 (Ret):** eksik alan crash'e yol açmaz; temiz `ConfigError` verir.
- **H4 (Ret):** iç içe/büyük yapı tetikleyici değil; parser onları yok sayar — belirleyici olan null.

Doldurulmuş tablo `report.md` §5 ve `exam_answers.md` S4'te. Çalıştırılabilir deney kanıtı:
`debugging_logs/hypothesis_experiments.py` (gerçek `large_config_failure.json`'dan türetilmiş, her
deney `# Hn` ile etiketli) ve çıktısı `debugging_logs/hypothesis_experiments_output.md`.

---

## Soru 5 — Delta Debugging / Input Minimization

### 1. Nedir?
Büyük, hatayı tetikleyen bir girdiyi alıp **sistematik küçültüp**, hatayı hâlâ tetikleyen **en küçük
parçayı** bulma yöntemi. "Bu kocaman dosyanın HANGİ parçası hatayı yapıyor?" sorusunu, gereksiz her
şeyi atarak cevaplar.

### 2. Temel döngü: her elemanı dene → karar ver
Her parçayı sırayla **silmeyi dene**, oracle ile **test et**:
- Crash **hâlâ sürüyorsa** → parça gereksiz, **silinmiş bırak** (REMOVED).
- Crash **kayboluyor/değişiyorsa** → parça gerekli, **yerinde bırak** (ESSENTIAL).
Tek geçişte tüm elemanları gez; kalan = minimum (ESSENTIAL'lar), silinenler = gürültü.

### 3. "Minimal" / "1-minimal" ne demek?
- **Minimal input:** hatayı hâlâ tetikleyen, daha fazla küçültülemeyen girdi.
- **1-minimal:** Daha kesin tanım — **kalan herhangi tek bir elemanı** çıkardığında hata **kaybolur**
  (ya da değişir). Yani tek hamlede daha fazla küçültülemez. Tek geçişte **ESSENTIAL** işaretlenen her
  eleman tam da bunu gösterir (çıkarılınca crash gider/değişir) → kalan çekirdek 1-minimaldir. Bu,
  mutlak en küçüğü (global optimum) garanti etmez ama pratikte yeterince küçüktür.

### 4. Algoritmamız (prosedürel)
`debugging_logs/delta_debugging.py`:
- `removable_paths(cfg)` — config'teki **her anahtarın yolunu** (her derinlikte) listeler.
- `without(cfg, path)` — o yoldaki elemanı silinmiş bir **kopya** döndürür (orijinali bozmaz).
- `describe(cfg)` — bir silmenin sonucunu adlandırır: `still crashes` / `clean ConfigError` / `normalizes OK`.
- `minimize(cfg)` — **tek annotasyonlu geçiş:** her yolu sırayla dener; `without` sonrası hâlâ crash ise
  silmeyi tutar (**REMOVED**), değilse elemanı yerinde bırakır (**ESSENTIAL**). Geçiş bitince kalan = minimum.
Karar her adımda oracle (`is_failure`) ile verilir; `describe` yalnızca çıktıyı açıklar.

### 5. Neden oracle şart?
Onlarca küçültme denemesini elle "hâlâ patlıyor mu?" diye kontrol etmek yorucu ve hataya açık.
Oracle (`is_failure`, S2) bu kararı **otomatik** verir — delta debugging'in motorudur.

### 6. Bizim sonucumuz
`large_config_failure.json` (≈61 satır) → tek geçişte **13 eleman REMOVED** (metadata; server/limits
içerikleri; features'ın diğer anahtarları; logging; services; security) ve **4 eleman ESSENTIAL**:
`server`, `features`, `limits` (silince temiz `ConfigError`) ve `features.debug` (silince normalize —
tetikleyici). ESSENTIAL çekirdek hem minimum hem 1-minimal:
`{"server": {}, "features": {"debug": null}, "limits": {}}`. Çalıştırılabilir kanıt:
`debugging_logs/delta_debugging.py` (+ `_output.md`); tablo report.md §6 / exam_answers.md S5.

---

## Soru 6 — Trace / Logging Analizi

### 1. Trace / logging nedir?
Program çalışırken **ne yaptığını** (hangi fonksiyon çağrıldı, hangi değer neydi) adım adım kaydetmek.
Statik (gözle) okumanın aksine, **gerçek çalışmada** ne olduğunu — özellikle çöküşe giden yolu — gösterir.

### 2. Instrumentation: koda dokunmadan izleme
Bir yol, koda geçici `print` eklemektir; ama biz hocanın koduna dokunmadan (Kural 9) **çalışma anında
fonksiyonları sardık** (monkeypatch): orijinali çağırmadan önce log basan bir "sarmalayıcı" ile
değiştirdik. Böylece kaynak tertemiz kalır, izleme tamamen dışarıdan yapılır.

### 3. `trace_run.py` nasıl çalışır? (adım adım)
Fikir: parser fonksiyonlarını, **log basıp sonra orijinali çağıran** ince kopyalarıyla değiştirmek.

1. **Modülü nesne gibi al:** `import src.config_parser as cp`. Artık `cp` bir modül nesnesidir;
   fonksiyonları onun **öznitelikleri**dir (`cp.parse_bool`, `cp.normalize_features`, ...).
2. **Orijinalleri sakla:** `original_parse_bool = cp.parse_bool`. Wrapper'ın gerçek işi yapabilmesi için
   orijinal fonksiyonun referansını bir kenara koyarız.
3. **Düz wrapper'lar tanımla:** her `traced_*` önce log basar, sonra sakladığı orijinali çağırır:
   ```python
   def traced_parse_bool(value):
       ...   # value ve type'ı logla, yanlış tipi işaretle
       return original_parse_bool(value)
   ```
4. **Değiştir (monkeypatch):** `cp.parse_bool = traced_parse_bool`. Modülün özniteliğini kendi
   wrapper'ımıza yönlendiririz — **kaynak dosyaya hiç dokunmadan**.
5. **Neden içerideki çağrılar da yakalanır? (kilit nokta):** `normalize_config`, içinde
   `normalize_features(...)` ya da `parse_bool(...)` yazdığında, bu ismi **çağrı anında** modülün global
   isim alanında arar. Biz o globali (modül özniteliğini) değiştirdiğimiz için, içerideki çağrılar artık
   bizim wrapper'a düşer. Kaynağı düzenlemeden iç çağrıları yakalamamızın sebebi budur.
6. **Çalıştır ve yakala:** `cp.load_config(path)` gerçek boru hattını (artık izlenen) çalıştırır.
   `try/except` iki sonucu ayırır: `ConfigError` (kontrollü) vs. başka istisna (çöküş). Çöküşte,
   `traceback.extract_tb(...)[-1]` ile **en son kare** (gerçekten çökülen yer = `parse_bool`, satır 150)
   alınıp fonksiyon + satır basılır.
7. **Neden limits/logging sarılmadı?** `normalize_config` sırası server → features → limits → logging'dir.
   Çöküş `features`'ta olduğu için limits/logging hiç çalışmaz; sarsak da bir şey basmazlardı — bu yüzden
   yalnızca server + features + parse_bool sarıldı (gereksiz kod yok, Kural 15).

### 4. Ne gözlemledik (sınavın istediği 4 şey)?
- **Hangi bölümler işlendi:** `normalize_config` yalnız server/features/limits/logging'i işler;
  metadata/services/security **yok sayılır** (hiç okunmaz). Bu çalıştırmada server → features; çöküş
  features'ta olduğundan limits/logging'e ulaşılmadı.
- **Hangi alanlar normalize edildi:** önce `normalize_server` server.host/server.port'u doğrular; sonra
  features'ta cache, debug → `parse_bool` ile.
- **Hangi değer beklenen tipte değil:** `debug=None` → `NoneType` (bool/str değil).
- **Çöküş öncesi durum:** `parse_bool`, `value=None`, `config_parser.py:150` (`value.lower()`).

### 5. Neden değerli?
Trace, defect→infection→failure zincirini (S8) **gözle görülür** kılar: tam olarak nerede, hangi
değerle, hangi satırda çökülmüş ve hangi bölümlere ulaşılmamış. Bu hem kök nedeni doğrular hem de
patch'in (S9) nereye gerektiğini gösterir.

### 6. Bizim çıktımız
`debugging_logs/trace_run.py` (sarmalayıcı tracer) + `debugging_logs/trace_output.md`. Doldurulmuş
analiz `report.md` §7 ve `exam_answers.md` S6'da.

---

## Soru 7 — Program Slicing / Dependency Analysis

### 1. Program slicing nedir?
Bir programın, belirli bir noktadaki belirli bir **değişkenin değerini etkileyen** ifadelerinin kümesini
çıkarmak. "Bu değişken NEDEN bu değerde?" sorusunu, ilgisiz kodu eleyerek cevaplar.

### 2. Backward (geri) slice vs forward (ileri) slice
- **Backward slice:** bir noktadan **geriye** bakar — "bu değişkenin buradaki değerine hangi ifadeler
  katkıda bulundu?" Çöküşü incelerken kullandığımız budur: `value`'nun (parse_bool, s.150) `None`
  olmasına yol açan ifadeleri geriye doğru izleriz.
- **Forward slice:** tersidir — "bu değişkeni DEĞİŞTİRİRSEM hangi satırlar etkilenir?"

### 3. Veri bağımlılığı (data dependency)
Slice'ın iskeleti veri bağımlılığıdır: bir ifade, kullandığı değeri başka bir ifade ürettiği için ona
bağımlıdır. Bizdeki zincir: `json.load` `None`'u üretir → `normalize_features` onu `parse_bool`'a verir
→ `parse_bool` `.lower()`'da kullanır. Her ok bir veri bağımlılığı.

### 4. Bu hatadaki slice (nasıl çıkardık)
S6 trace'i + kodu okuyarak `value`'nun kaynağını geriye izledik:
- **Kritik değişken:** `value` (parse_bool, `None`).
- **Input alanı:** `features.debug` = `null`.
- **Fonksiyonlar:** load_config → json.load → normalize_config → normalize_features → parse_bool.
- **Kritik incelik (s.73):** `features.get("debug", False)` — varsayılan `False`, anahtar **yokken**
  devreye girer; ama anahtar `null` **değerle var olduğu** için `.get` `None` döndürür. Yani varsayılan
  burada korumaz.

### 5. Neden değerli?
Slice, "kocaman programın hangi birkaç satırı bu çöküşe yol açtı?" sorusunu cevaplar. İlgisiz onlarca
satırı eleyip dikkati kritik bağımlılık zincirine odaklar ve patch'i (S9) tam doğru yere koymamızı
sağlar: zincirin neresini düzeltmeliyiz (`parse_bool`'un tip varsayımı).

---

## Soru 8 — Defect–Infection–Failure Chain

### 1. Üç kavram neden ayrı?
Bir hatanın üç farklı 'katmanı' vardır; karıştırılırsa yanlış yeri düzeltirsin:
- **Defect:** koddaki YANLIŞ (statik — dosyada duran kusur).
- **Infection:** o kusurun çalışınca ürettiği YANLIŞ DURUM (runtime — bellekteki/akıştaki hatalı hâl).
- **Failure:** o yanlış durumun DIŞARIDAN görülen sonucu (yanlış çıktı / çöküş).

### 2. Neden hepsi aynı şey değil?
- Defect her zaman infection üretmez: kusurlu satıra hiç **uğranmazsa** (ya da uğranıp durum yine de
  doğru kalırsa) infection olmaz. Bizde `bool` veya geçerli string gelseydi defect uykuda kalırdı.
- Infection her zaman failure üretmez: yanlış durum dışarı yansımadan **maskelenebilir/düzelebilir**.
  Bizde ise infection anı (`.lower()`) doğrudan çöküşe döndüğü için failure hemen geliyor.

### 3. Bu hatadaki zincir
- **Defect:** `parse_bool` s.150 `value.lower()` — `bool` olmayan her şeyi string sayar (s.147–149 yorum).
- **Infection:** `value=None` ile s.150'ye ulaşılır; `None` üzerinde string işlemi yapılmak üzere.
- **Propagation:** `AttributeError` çağrı yığınında yukarı yakalanmadan yayılır (`app.py` yalnız
  `ConfigError` yakalar).
- **Failure:** traceback + çıkış kodu 1 (CRASH); temiz `CONFIG_ERROR` değil.

### 4. Neden değerli?
Zinciri ayırmak, düzeltmenin **nereye** gideceğini söyler: failure'ı (çöküşü) değil, **defect'i**
(`parse_bool`'un tip varsayımı) düzeltiriz. `app.py`'de istisnayı yakalamak failure'ı gizlerdi ama defect
yerinde kalırdı — semptomu örtmek gibi. Doğru patch (S9) defect'i kaynağında giderir.

---

## Soru 9 — Patch ve Doğrulama

### 1. İyi bir patch neyi hedefler?
- **Kökü düzelt, semptomu değil:** defect'i (S8) kaynağında gider; çöküşü maskeleme. `app.py`'de
  `AttributeError` yakalamak failure'ı gizlerdi ama `parse_bool`'un kusuru kalırdı.
- **Sözleşmeye uy:** `parse_bool`'un docstring'i "diğer her değer ConfigError" der; doğru davranışın
  ölçütü budur (oracle, S2).
- **Geçerli girdileri bozma:** `True`, `"yes"`, `"1"` çalışmaya devam etmeli.
- **En yalın çözüm (Kural 15):** tek bir tip-kontrolü guard'ı yeter, fazlası değil.

### 2. Red → Green (regresyon güvenliği)
S3'te yazdığımız 4 failing test patch'ten ÖNCE kırmızıydı (kod `AttributeError` veriyordu, `ConfigError`
beklenirken). Patch'ten SONRA yeşile döndüler; aynı anda eski geçen testler kırmızıya dönmedi.
"Kırmızı→yeşil ve hiçbir yeşil kırmızıya dönmedi" = doğru patch'in kanıtı.

### 3. Neden testi değil kodu düzeltiriz?
Test, doğru davranışı (null → ConfigError) ifade eder; başarısızlık testin değil **kodun** yanlış
olduğunu gösterir. Testi gevşetmek (beklentiyi crash'e çevirmek) hatayı gizlerdi. Bu yüzden S9'da yalnız
`config_parser.py` değişir; testler aynı kalır.

### 4. Bizim patch'imiz
`parse_bool` içinde, `bool` kontrolünden sonra: `value` `str` değilse `ConfigError`. Düzeltme **eklemeli**
(yalnızca guard); yorumlanan/çıkarılan satır yok — `value.lower()` zaten doğruydu, sadece string girdi
gerekiyordu. Doğrulama: `pytest` → 16 passed (Bonus A regression dahil); geçerli config'ler CONFIG_OK;
bozuk config temiz CONFIG_ERROR. Detay `report.md` §10–§11 / `exam_answers.md` S9.

---

## Bonus A — Regression Test

### 1. Regression test nedir?
Düzeltilen bir hatanın **geri gelmesini** (regression) önleyen testtir. Hata düzeltildikten sonra, onu
tetikleyen senaryoyu alıp artık **doğru** olan davranışı bekler. Biri ileride fix'i bozarsa test kırmızı
olur ve hatayı yakalar — fix'i kalıcı olarak "kilitler".

### 2. Neden değerli?
Bir hatayı bir kez düzeltmek yetmez; refactor/yeni özellik sırasında geri gelebilir. Regression testi bu
riski otomatikleştirir: hata her döndüğünde pytest kırmızı yanar.

### 3. Bizim regression testimiz
`tests/test_regression.py`: S5'in minimal girdisini (`{"server":{},"features":{"debug":None},"limits":{}}`)
S2 oracle'ı ile kontrol eder — `assert is_failure(raw) is False`.
- Bozuk kodda: `is_failure` → `True` (crash) → test **kırmızı** (hatayı yakalar).
- Yamalı kodda: `is_failure` → `False` (temiz `ConfigError`) → test **yeşil**.
Detay `report.md` §12 / `exam_answers.md` Bonus A.

### 4. Neden ayrı bir test (S3'tekiler varken)?
S3 testleri analiz sırasında, hatayı **bulmak** için yazıldı. Bu regression testi düzeltmeyi **korumak**
için; ayrıca S2 oracle'ı + S5 minimal girdiyi birleştirip farklı bir açıdan (oracle üzerinden) sabitler —
`test_null_debug`'ın birebir kopyası değil.

---

## Bonus B — Mutation Testing

### 1. Mutation testing nedir?
Testlerin **kalitesini** ölçer. Fikir: koda kasıtlı küçük hatalar (mutant) enjekte et, testleri çalıştır,
testler bu hatayı **yakalıyor mu** bak. İyi bir suite, anlamlı bir mutasyonu en az bir testin kırmızıya
dönmesiyle yakalar.

### 2. Killed / Survived / mutation score
- **Killed:** mutant uygulanınca **en az bir test başarısız** olur → suite hatayı yakaladı (iyi).
- **Survived:** tüm testler hâlâ geçer → mutant fark edilmedi → suite'te **boşluk** (o davranış test
  edilmiyor).
- **Mutation score** = killed / toplam mutant. Yüksek skor = güçlü suite (test *sayısı* değil, testlerin
  ne kadar yakaladığı önemli).

### 3. Neden baseline yeşil olmalı?
Mutasyondan önce tüm testler geçmeli; yoksa "test kırmızı oldu" sinyalinin mutanttan mı yoksa zaten kırık
bir testten mi geldiğini ayıramayız. Bizde baseline = 16 passed (yamalı kod).

### 4. Bizim sonucumuz
`debugging_logs/mutation_test.py` 6 mutant uyguladı → **5 killed, 1 survived** (skor 5/6 ≈ %83).
- **Killed:** M1 (fix'i geri alma), M2 (`"1"` çıkarma), M3 (VERBOSE kabul), M4 (presence check ters),
  M6 (cache varsayılanı) — her biri ilgili bir testçe yakalandı.
- **Survived:** M5 (port `>` → `>=`) — yalnız `port==65535` sınırını değiştirir, o değer test edilmediği
  için kaçar. Boşluğu kapatmak: `server.port = 65535`'i başarı bekleyen bir test.
Detay `report.md` §13 / `exam_answers.md` Bonus B.

### 5. Neden değerli?
"Testlerim geçiyor" yetmez — testler **gerçekten hata yakalıyor mu?** Mutation testing bunu nicel ölçer
ve test boşluklarını (M5 gibi) somut gösterir. S3 testlerinin bug'ı yakaladığını (M1) bağımsızca doğrular.
