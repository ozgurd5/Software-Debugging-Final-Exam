# Sınav Kağıdı Cevapları

> Yazılı sınav kağıdına geçirilecek cevapların kaynağı. Sınav, dijital rapora (`report.md`) ek
> olarak elden teslim edilen yazılı bir kağıt da ister; bu dosya o yazılı kağıdın içeriğini hazırlar.
> **Özet değildir** — raporla aynı derinlikte, her sorunun istediği maddeleri eksiksiz içerir.
> `report.md` ile tutarlıdır; ancak sınav soruları ile rapor şablonu bazı noktalarda (örn. S1, S5,
> S6, S9) farklı şeyler istediğinden birebir aynı değildir.

---

## Soru 1 — Hatanın Yeniden Üretimi
- **Çalıştırma komutu:** (proje kökünden) `python src/app.py inputs/large_config_failure.json`
- **Alınan hata mesajı / yanlış çıktı:** Program `CONFIG_OK` ya da temiz bir `CONFIG_ERROR`
  yerine yakalanmayan bir istisnayla **çöküyor** (çıkış kodu 1). İlgili traceback:
  ```text
  ...
  File "src/config_parser.py", line 73, in normalize_features
      debug = parse_bool(features.get("debug", False))
  File "src/config_parser.py", line 150, in parse_bool
      lowered = value.lower()
  AttributeError: 'NoneType' object has no attribute 'lower'
  ```
- **Tekrar üretilebilirlik (kısa açıklama):** Komut her çalıştırıldığında aynı satırda
  (`config_parser.py:150`, `parse_bool` içinde) aynı traceback ile **%100 deterministik** olarak
  başarısız olur; sonuç yalnızca input dosyasına bağlıdır (rastgelelik/zaman/dış durum yok).
  `valid_basic.json` ve `valid_full.json` her zaman `CONFIG_OK` verir → tek değişken input
  dosyasıdır, hata güvenilir biçimde yeniden üretilebilir.
- **Hata türü** (crash / wrong output / beklenmeyen davranış): **Crash** — yakalanmayan `AttributeError`. `app.py` 
  yalnızca `ConfigError` yakaladığı için (satır 17) bu istisna yakalanmaz, en üste yayılır ve program traceback ile 
  çöker. Yanlış çıktı değildir (ne `CONFIG_OK` ne temiz `CONFIG_ERROR`); mevcut tasarımda `ConfigError` 
  beklendiğinden "beklenmeyen davranış" olarak nitelenir.

---

## Soru 2 — Test Oracle
- **Oracle fonksiyonu:** `tests/oracle.py` içindeki `is_failure(raw_config)`:
  ```python
  from src.config_parser import normalize_config, ConfigError
  def is_failure(raw_config):
      try:
          normalize_config(raw_config)
      except ConfigError:
          return False   # kontrollü ret -> beklenen
      except Exception:
          return True    # kontrolsüz çökme -> FAILURE
      return False       # başarıyla normalize -> beklenen
  ```
- **Nasıl karar veriyor** (pass mi fail mi): `normalize_config` ya normal döner (kabul) ya da temiz
  bir `ConfigError` fırlatır (kontrollü ret) → ikisi de **beklenen = PASS**. Bunların dışında bir
  istisna (örn. `AttributeError`) yakalanmadan yayılırsa → **FAILURE** (kontrolsüz çökme; `app.py`'nin
  `except ConfigError`'ı yakalayamaz). Program düzeyinde: PASS = çıkış 0 (`CONFIG_OK`) veya çıkış 1
  + `CONFIG_ERROR:`; FAIL = yakalanmamış traceback ile çöküş.

---

## Soru 3 — Passing ve Failing Testler (≥5 passing, ≥3 failing)
Testler `tests/test_config_cases.py`'de (hocanın `test_config_parser.py`'sine dokunulmadı). Testler,
hocanın baktığından **farklı** dalları sınar (logging.level ve bölüm-tipi doğrulaması, alternatif
boolean biçimleri, oracle, 4 bug vakası) — tekrar değil. Güncel çalıştırma (bu analiz suite'i): **11 passed, 4 failed**. Bonus A regression testi
(ayrı dosya) de fix öncesi kırmızı → tam `pytest` koşusu fix öncesi **11 passed / 5 failed**, sonrası
**16 passed** (tam çıktı: `debugging_logs/test_results.md`).
4 failing test doğru davranışı (temiz `ConfigError`) bekler; yalnızca bug yüzünden kırmızıdır, S9
patch'inden sonra yeşile döner.

| Test adı | Input özeti | Beklenen sonuç | Gerçek sonuç | Passing/Failing |
|---|---|---|---|---|
| test_valid_minimal_defaults | boş server/features/limits | varsayılanlarla normalize dict (port 8080, level INFO, ...) | beklenen gibi | Passing |
| test_alternative_string_booleans | cache="1", debug="0", experimental="yes" | True, False, True | beklenen gibi | Passing |
| test_real_booleans_passthrough | cache=true, debug=false | cache=True, debug=False | beklenen gibi | Passing |
| test_oracle_marks_valid_config_as_expected | geçerli bir config dict (oracle ile) | is_failure → False | False | Passing |
| test_invalid_logging_level_raises_config_error | logging.level = "VERBOSE" | ConfigError | ConfigError | Passing |
| test_non_object_section_raises_config_error | server = "localhost" (string, object değil) | ConfigError | ConfigError | Passing |
| test_null_debug_raises_config_error | features.debug = null | ConfigError (temiz ret) | AttributeError ('NoneType'de 'lower' yok) | **Failing** |
| test_int_boolean_raises_config_error | features.cache = 1 (int) | ConfigError | AttributeError ('int'de 'lower' yok) | **Failing** |
| test_list_boolean_raises_config_error | features.experimental = [] (list) | ConfigError | AttributeError ('list'te 'lower' yok) | **Failing** |
| test_large_config_file_raises_config_error | gerçek inputs/large_config_failure.json (debug=null) | ConfigError | AttributeError çökme (config_parser.py:150) | **Failing** |

---

## Soru 4 — Scientific Debugging (≥3 hipotez)
Her hipotez **kontrollü bir deneyle** sınandı: gerçek failing input
`inputs/large_config_failure.json`'dan başlayıp **tek bir şeyi** değiştirerek sonucu gözledik
(sorunsuz normalize / temiz `ConfigError` / kontrolsüz crash). Deneyler
`debugging_logs/hypothesis_experiments.py` ile çalıştırılabilir. Çalıştırma çıktısı:

```text
H1  real file as-is (debug=null)             -> CRASH: AttributeError
H1  real file, debug=false (control)         -> OK (normalized)
H2  real file, debug=int 1                   -> CRASH: AttributeError
H2  real file, debug=list []                 -> CRASH: AttributeError
H2  real file, debug=float 1.5               -> CRASH: AttributeError
H3  real file minus 'limits'                 -> ConfigError (controlled)
H4  real file, nested removed (debug=null)   -> CRASH: AttributeError
H4  real file, nested kept, debug=false      -> OK (normalized)
```

| Hipotez | Gözlem | Deney | Sonuç | Kabul/Ret |
|---|---|---|---|---|
| **H1** — Boolean bir alandaki JSON `null` (Python `None`) hatayı tetikler. | Crash, yalnızca string'lerde olan `.lower()`'dan gelen bir `AttributeError`; hatalı dosyada değeri string-karşılığı olmayan tek alan `features.debug` = `null`, diğer tüm değerler normal string/int/bool. Bu, `null`'u baş şüpheli yapar. | Dosyayı olduğu gibi çalıştır (`debug: null`); sonra **yalnızca** `features.debug`'ı `false` yapıp tekrar çalıştır. | Olduğu gibi → kontrolsüz `AttributeError` (crash); `false` ile → normalize, çıkış 0. Tek alan crash↔başarıyı çeviriyor; tetikleyici `null`. | **Kabul** |
| **H2** — Tetikleyici null'a özel değil: bool/string **olmayan her** değer (int, list, float) aynı şekilde çökertir. | `parse_bool` yalnız `bool`'u özel-durum yapıp koşulsuz `value.lower()` çağırır — hiçbir yeri `null`'a özel değil; `null` sadece string değil, int/float/list de değil. | Gerçek dosyada `features.debug`'ı sırayla `1` (int), `[]` (list), `1.5` (float) yap. | Üçü de aynı: `AttributeError: '<tip>' object has no attribute 'lower'`. Tetikleyici, yalnız `null` değil, bool/string olmayan herhangi bir değer. | **Kabul** |
| **H3** — Hata, kötü bir değerden değil, **eksik** bir zorunlu bölümden kaynaklanır. | Tek bir failing input var ve geçerli dosyalardan aynı anda birçok yönden farklı; "zorunlu bölüm eksik" rakip açıklaması, değeri suçlamadan önce elenmeli. | Gerçek dosyadan `limits` bölümünü tümüyle çıkar ve çalıştır. | Temiz `ConfigError: Missing required section: limits` (çıkış 1, traceback yok) — kontrollü ret, crash değil. Eksik bölüm doğru ele alınıyor; neden bu değil. | **Ret** |
| **H4** — Hata, büyük / derin iç içe yapıdan (`services`, `security`, `metadata`, ...) kaynaklanır. | Hatalı dosya ~60 satır ve derin iç içe; geçerli dosyalar küçük ve düz — değeri suçlamadan önce kontrol edilmesi gereken bir boyut/yuvalama confound'u. | İki çalıştırma: (a) nested bölümleri çıkar ama `debug: null` kalsın; (b) nested kalsın ama `debug: false` yap. | (a) yine crash; (b) sorunsuz normalize. Sonuç `debug` değerini izliyor, yapıyı değil — parser o bölümlere hiç bakmıyor bile. | **Ret** |

Sonuç: crash, `parse_bool`'un string olmayan bir değere `.lower()` çağırmasından doğuyor — H1 ile
daraltıldı (`features.debug`'daki `null`), H2 ile genelleştirildi (bool/string olmayan her değer).
Eksik bölümden (H3) ve büyük/iç içe yapıdan (H4) **bağımsız**.

---

## Soru 5 — Delta Debugging / Input Minimization
1. **Başlangıç input büyüklüğü:** `large_config_failure.json` ≈61 satır, 7 üst bölüm (metadata,
   server, features, limits, logging, services, security); features'ta 5 anahtar.
2. **Küçültme — tek annotasyonlu geçiş:** **Greedy minimizer** (`debugging_logs/delta_debugging.py`,
   orijinal bozuk parser üzerinde) her elemanı tek tek siler: crash sürerse silmeyi tutar
   (**REMOVED** — alakasız), sürmezse elemanı yerinde bırakır (**ESSENTIAL** — silince sonuç değişir).
   Karar S2 oracle'ı (`is_failure`) ile. Aşağıdaki tablo **tam izdir**; ESSENTIAL satırlar indirgenemez
   çekirdektir → sonuç 1-minimal (birini daha çıkarınca crash kaybolur).

| # | Silinen | Sonuç | Karar |
|---|---|---|---|
| 1 | `metadata` | hâlâ çöküyor | REMOVED |
| 2 | `server` | temiz `ConfigError` | **ESSENTIAL** (tutuldu) |
| 3 | `server.host` | hâlâ çöküyor | REMOVED |
| 4 | `server.port` | hâlâ çöküyor | REMOVED |
| 5 | `features` | temiz `ConfigError` | **ESSENTIAL** (tutuldu) |
| 6 | `features.cache` | hâlâ çöküyor | REMOVED |
| 7 | `features.debug` | sorunsuz normalize | **ESSENTIAL** (tetikleyici) |
| 8 | `features.experimental` | hâlâ çöküyor | REMOVED |
| 9 | `features.recommendations` | hâlâ çöküyor | REMOVED |
| 10 | `features.new_checkout` | hâlâ çöküyor | REMOVED |
| 11 | `limits` | temiz `ConfigError` | **ESSENTIAL** (tutuldu) |
| 12 | `limits.max_users` | hâlâ çöküyor | REMOVED |
| 13 | `limits.timeout` | hâlâ çöküyor | REMOVED |
| 14 | `limits.retries` | hâlâ çöküyor | REMOVED |
| 15 | `logging` | hâlâ çöküyor | REMOVED |
| 16 | `services` | hâlâ çöküyor | REMOVED |
| 17 | `security` | hâlâ çöküyor | REMOVED |

3. **Çıkarınca failure DEVAM eden (REMOVED → alakasız):** 13 eleman (yukarıdaki REMOVED satırları).
4. **Çıkarınca failure KAYBOLAN (ESSENTIAL → tutuldu):** 4 eleman — `server`/`features`/`limits`
   (silince temiz `ConfigError` → zorunlu bölüm) ve `features.debug` (silince `null` gider, program
   normalize olur → tetikleyici). Her biri çıkarılınca sonuç değişir → **1-minimal**.
5. **Minimum failure-inducing input** (1-minimal — bir eleman daha çıkarılırsa failure kaybolur):
   ```json
   {"server": {}, "features": {"debug": null}, "limits": {}}
   ```
6. **Neden failure üretiyor:** `server`/`features`/`limits` anahtarları bulunmalı (yoksa
   `validate_required_sections` temiz `ConfigError` verir — crash değil). Üçü de varken
   `normalize_features`, `parse_bool(features["debug"])` = `parse_bool(None)` çağırır; `None.lower()`
   → `AttributeError`. `null` boolean değeri tek indirgenemez tetikleyici; gerisi gürültü.

---

## Soru 6 — Trace / Logging Analizi
Trace, `debugging_logs/trace_run.py` ile üretildi: parser fonksiyonları çalışma anında **sarılarak**
(hocanın kodu değiştirilmeden) her bölüm/alan işlenirken loglandı ve çöküş anı yakalandı. Tam çıktı:
`debugging_logs/trace_output.md`.
- **İşlenen ana bölümler:** `normalize_config` sırasıyla `server`, `features`, `limits`, `logging`'i
  işler; `metadata`, `services`, `security` **yok sayılır** (hiç okunmaz). Burada `server` başarıyla
  normalize edildi, `features` başladı; çöküş `features` içinde olduğundan `limits` ve `logging`'e
  **hiç ulaşılmadı**.
- **Normalize edilen alanlar:** `features`'tan önce `normalize_server`, `server.host` ve `server.port`'u
  okuyup doğrular (ikisi de geçerli). Sonra `features` içinde her boolean bayrak için `parse_bool`
  çağrıldı: `cache=True` (sorunsuz), sonra `debug=None`.
- **Beklenen tipte olmayan değer:** `debug=None` (JSON `null`) → `NoneType`; ne `bool` ne `str`, yani
  `parse_bool`'un string varsayımı tutmuyor.
- **Çöküşten hemen önceki fonksiyon çağrısı + değişken değerleri:** son çağrı `parse_bool(value=None)`;
  `config_parser.py:150`'de `lowered = value.lower()` satırında çöküyor (`None`'un `.lower()`'ı yok →
  `AttributeError`).
- **İlgili trace (kısa):**
  ```text
  [section]    processing 'server'  (keys = ['host', 'port'])
  [section]    processing 'features' (keys = ['cache', 'debug', 'experimental', ...])
  [parse_bool]  value=True  type=bool
  [parse_bool]  value=None  type=NoneType   <-- NOT bool/str: unexpected type!
  !! CRASH: AttributeError -> parse_bool() at config_parser.py:150 (lowered = value.lower())
  ```

---

## Soru 7 — Program Slicing / Dependency Analysis
1. **Failure anındaki kritik değişken:** `parse_bool`'un `value` parametresi (`config_parser.py:131`).
   Çöküş anında `None` tutar; `value.lower()` (satır 150) `AttributeError`'ı fırlatan ifadedir.
2. **Hangi input alanından geliyor:** Config'teki `features.debug` — `large_config_failure.json`'da
   `null`. JSON `null`, parse edilince Python `None` olur.
3. **Hangi fonksiyonlarda işlendi (backward slice):**
   `load_config` (s.9) → `json.load` (s.14, `null`→`None`) → `normalize_config` (s.24) →
   `normalize_features` (s.73: `parse_bool(features.get("debug", False))`) → `parse_bool` (s.131 → 150).
4. **Üzerinde yapılan varsayım:** `parse_bool`, `bool` olmayan her değeri **string-benzeri** sayar
   (`.lower()`'ı olduğunu varsayar) — kendi yorumunda yazılı (s.147–149). `None` ne `bool` ne `str`;
   satır 144'ten geçer, satır 150'de çöker.
5. **Slice'taki en önemli satırlar:**

| Satır | İfade | Slice'taki rolü |
|---|---|---|
| 14 | `raw_config = json.load(f)` | JSON `null` → Python `None` |
| 24 | `features = normalize_features(config.get("features", {}))` | features dict'ini iletir |
| 73 | `debug = parse_bool(features.get("debug", False))` | `None`, `parse_bool`'a ulaşır (bkz. not) |
| 144 | `if isinstance(value, bool):` | yalnızca `bool` işlenir; `None` düşmez |
| 150 | `lowered = value.lower()` | **çöküş** — `value`'yu string varsayar |

**Not (satır 73):** `features.get("debug", False)` bu hatayı **engellemez**. Varsayılan `False` yalnızca
`debug` anahtarı **yokken** döner; burada anahtar `null` **değerle var**, yani `.get` `None` döndürür ve
bu `parse_bool`'a geçer.

---

## Soru 8 — Defect–Infection–Failure Chain
- **Defect (kusur):** Koddaki statik hata — `parse_bool` (`config_parser.py:150`) yalnızca `bool`'u
  özel-durum yapıp (s.144) ardından `value.lower()` çağırır; `bool` olmayan her değeri string-benzeri
  varsayar, `None`/başka tip için kontrol yok (kendi yorumunda yazılı, s.147–149). Tetiklenene dek uykuda.
- **Infection (enfeksiyon):** Çalışma anında kusura `value = None` ile ulaşılır (`features.debug: null`).
  Program hatalı duruma girer: kontrol satır 150'de, `None` üzerinde `.lower()` çağırmak üzere — bu tip
  için geçersiz işlem. (`None`'un buraya nasıl geldiği §7 slice'ı: `json.load` → `normalize_features`
  s.73 → `parse_bool`.)
- **Propagation (yayılım):** `None.lower()` `AttributeError` fırlatır; bu **çağrı yığınında yukarı,
  yakalanmadan** yayılır: `parse_bool` → `normalize_features` (s.73) → `normalize_config` (s.24) →
  `load_config` (s.16) → `app.py main`. `app.py` yalnızca `ConfigError` yakaladığı için `AttributeError`'a
  hiçbir şey müdahale etmez.
- **Failure (başarısızlık):** Dışarıdan gözlemlenen sonuç — program, temiz bir `CONFIG_ERROR: ...`
  mesajı yerine yakalanmayan istisna traceback'i ve çıkış kodu **1** ile çöker. Kullanıcının gördüğü budur.

---

## Soru 9 — Patch ve Doğrulama
1. **Değişen dosya/fonksiyon:** `src/config_parser.py` → `parse_bool` (projedeki tek değişen dosya).
   `bool` kontrolünden sonra **eklenen tek koruma**: `value` `str` değilse `ConfigError`. Düzeltme
   tamamen **eklemeli** — hiçbir satır çıkarılmadı/yorumlanmadı; `value.lower()` zaten yanlış değildi,
   yalnızca string girdi gerekiyordu, onu da guard garantiliyor.
2. **Bu değişiklik neden doğru:** Defect'i **kökünden** giderir — `parse_bool`'un "bool olmayan = string"
   varsayımını. Fonksiyonun kendi docstring'i *"Any other value should raise ConfigError"* der; patch
   tam bunu yapar: `null`/`int`/`list` gibi geçersiz tipler artık **temiz `ConfigError`** verir (çöküş
   değil). `app.py`'de istisnayı yakalamak semptomu gizlerdi ama defect yerinde kalırdı (S8).
3. **Başka geçerli config'leri bozar mı:** Hayır. `True/False` satır 144'teki `bool` kontrolünden döner;
   `"true"/"yes"/"1"` gibi geçerli string'ler `str` olduğundan korumadan geçip eskisi gibi çalışır.
   Doğrulama: `valid_basic.json` ve `valid_full.json` → patch sonrası **CONFIG_OK** (çıkış 0), değişmedi.
4. **Hangi testlerle doğrulandı (tüm testler geçti mi):** Tüm suite —
   `.venv\Scripts\python.exe -m pytest -q` → **16 passed** (fix öncesi/sonrası tam çıktı:
   `debugging_logs/test_results.md`). Patch öncesi 11 passed / 5 failed idi; S3'teki 4 failing test
   (`null`/`int`/`list`/large-file → `ConfigError` bekleyen) ve Bonus A regression testi artık
   **geçiyor**, geçenler bozulmadı. Ayrıca `large_config_failure.json` → `CONFIG_ERROR: Invalid boolean value: None` (traceback yok).

---

## Bonus A — Regression Test
- **Test:** S5'in bulduğu **minimal failing input**'u — `{"server": {}, "features": {"debug": null},
  "limits": {}}` — alıp parser'a yeniden verir ve artık **çökmediğini** doğrular. Kontrol S2 oracle'ı
  ile yapılır: bu girdi için `is_failure` artık `False` dönmeli (geçersiz boolean → **kontrollü**
  `ConfigError`, kontrolsüz crash değil). Test Python kodu olduğundan girdi Python sözdiziminde yazılır
  — JSON `null`, Python'da `None`'dır:
  ```python
  def test_regression_minimal_input_no_longer_fails():
      raw = {"server": {}, "features": {"debug": None}, "limits": {}}   # JSON null = Python None
      assert is_failure(raw) is False
  ```
- **Neden regression test:** S9'da düzelttiğimiz hatayı tetikleyen **orijinal girdiyi (S5 minimal)**
  yeniden üretip **düzeltilmiş** davranışı kalıcı kılar. Yamasız kodda **kırmızı** olur: `is_failure`
  `True` döner (`AttributeError` crash) → hatayı gerçekten yakalar. Yama sonrası **yeşil**. Fix ileride
  yanlışlıkla geri alınırsa test yeniden kırmızıya döner → aynı hata fark edilmeden geri dönemez.

---

## Bonus B — Mutation Testing (≥5 mutant)

| Mutant | Değişiklik | Testler yakaladı mı? | Açıklama |
|---|---|---|---|
| | | | |
