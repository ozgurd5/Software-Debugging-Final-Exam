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
boolean biçimleri, oracle, 4 bug vakası) — tekrar değil. Güncel çalıştırma: **11 passed, 4 failed**.
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
`debugging_logs/hypothesis_experiments.py` ile çalıştırılabilir; çıktısı
`debugging_logs/hypothesis_experiments_output.md`'de.

| Hipotez | Gözlem | Deney | Sonuç | Kabul/Ret |
|---|---|---|---|---|
| **H1** — Boolean bir alandaki JSON `null` (Python `None`) hatayı tetikler. | `large_config_failure.json`'da `features.debug` = `null`; traceback çöküşün tam bu alan `parse_bool` içinde işlenirken olduğunu gösterir. | Gerçek dosyayı olduğu gibi çalıştır (`debug: null`), sonra **sadece** `features.debug`'ı `false` yap (kontrol). | Olduğu gibi → crash (`AttributeError`); `false` ile → normalize. Tek değişen `debug` olduğundan tetikleyici `null`'dur. | **Kabul** |
| **H2** — null'a özel değil: bool/string OLMAYAN **her** değer (int, list, float) aynı şekilde çökertir; `parse_bool` string varsayar. | `isinstance(value, bool)` kontrolünden sonra yalnızca string'lerin desteklediği `value.lower()` çağrılıyor. | Gerçek dosyada `features.debug`'ı sırayla `1` (int), `[]` (list), `1.5` (float) yap. | Üçü de `AttributeError: '<tip>' object has no attribute 'lower'` ile çöker. Neden "bool/string olmayan her değer"e genelleşir. | **Kabul** |
| **H3** — Hata eksik bir zorunlu bölümden kaynaklanır (kötü bir değerden değil). | Dosyada birçok bölüm var; eksik biri makul bir alternatif neden olabilir. | Gerçek dosyadan `limits` bölümünü çıkar ve çalıştır. | Temiz bir `ConfigError: Missing required section: limits` — **kontrollü** ret, crash değil. Eksik bölüm doğru ele alınır; neden bu değil. | **Ret** |
| **H4** — Hata, büyük / derin iç içe yapıdan (`services`, `security`, `metadata`, ...) kaynaklanır. | Hatalı dosya, küçük geçerli dosyaların aksine büyük ve iç içe; yapı makul bir alternatif neden olabilir. | Gerçek dosyada: (a) nested bölümleri çıkar ama `debug=null` kalsın; (b) nested kalsın ama `debug=false` yap. | (a) yine crash; (b) normalize. Parser bu nested bölümleri tamamen yok sayar; iç içe yapı değiştirmez — belirleyici olan `null`. | **Ret** |

Sonuç: crash, `parse_bool`'un string olmayan bir değere `.lower()` çağırmasından doğuyor — H1 ile
daraltıldı (`features.debug`'daki `null`), H2 ile genelleştirildi (bool/string olmayan her değer).
Eksik bölümden (H3) ve büyük/iç içe yapıdan (H4) **bağımsız**.

---

## Soru 5 — Delta Debugging / Input Minimization
1. **Başlangıç input büyüklüğü:** `large_config_failure.json` ≈61 satır, 7 üst bölüm (metadata,
   server, features, limits, logging, services, security); features'ta 5 anahtar.
2. **Küçültme adımları:** **Sistematik greedy minimizer** (`debugging_logs/delta_debugging.py`),
   config'in **her elemanını** (her derinlikteki her anahtar) tek tek silmeyi dener; failure
   (`is_failure`) korunuyorsa silmeyi tutar, fixpoint'e kadar tekrarlar. Tam iz
   `debugging_logs/delta_debugging_output.md`'de. **Faz 1 — her adımda tek eleman:**

| Adım | Çıkarılan | Failure devam etti mi? | Sonuç |
|---|---|---|---|
| 1 | `metadata` | Evet | alakasız → çıkarıldı |
| 2 | `server.host` | Evet | alakasız → çıkarıldı |
| 3 | `server.port` | Evet | `server` artık `{}` → çıkarıldı |
| 4 | `features.cache` | Evet | tetikleyici değil → çıkarıldı |
| 5 | `features.experimental` | Evet | tetikleyici değil → çıkarıldı |
| 6 | `features.recommendations` | Evet | kullanılmıyor → çıkarıldı |
| 7 | `features.new_checkout` | Evet | kullanılmıyor → çıkarıldı |
| 8 | `limits.max_users` | Evet | alakasız → çıkarıldı |
| 9 | `limits.timeout` | Evet | alakasız → çıkarıldı |
| 10 | `limits.retries` | Evet | `limits` artık `{}` → çıkarıldı |
| 11 | `logging` | Evet | alakasız → çıkarıldı |
| 12 | `services` | Evet | alakasız → çıkarıldı |
| 13 | `security` | Evet | alakasız → çıkarıldı |

3. **Çıkarınca failure DEVAM eden parçalar (alakasız → çıkarıldı):** yukarıdaki 13 eleman.
4. **Çıkarınca failure KAYBOLAN parçalar (kritik → tutuldu) — Faz 2 (1-minimallik kontrolü):** kalan
   her eleman tek tek çıkarıldı; hepsinde failure kayboluyor, yani hiçbiri daha fazla küçültülemez:

| Çıkarılan | Failure devam etti mi? | Sonuç |
|---|---|---|
| `server` | Hayır (temiz `ConfigError`) | zorunlu bölüm → tutuldu |
| `features` | Hayır (temiz `ConfigError`) | zorunlu bölüm → tutuldu |
| `features.debug` | Hayır (sorunsuz normalize) | **tetikleyici** (null) → tutuldu |
| `limits` | Hayır (temiz `ConfigError`) | zorunlu bölüm → tutuldu |
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
- **İşlenen ana bölümler:** `server` başarıyla normalize edildi, sonra `features` başladı; `limits` ve
  `logging`'e **hiç ulaşılmadı** — çöküş `features` içinde.
- **Normalize edilen alanlar:** `features` içinde her boolean bayrak için `parse_bool` çağrıldı:
  `cache=True` (bool, sorunsuz), sonra `debug=None`.
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
   `.venv\Scripts\python.exe -m pytest -q` → **15 passed**. Patch öncesi 11 passed / 4 failed idi; S3'teki
   4 failing test (`null`/`int`/`list`/large-file → `ConfigError` bekleyen) artık **geçiyor**, geçenler
   bozulmadı. Ayrıca `large_config_failure.json` → `CONFIG_ERROR: Invalid boolean value: None` (traceback yok).

---

## Bonus A — Regression Test
- **Test:**
- **Neden regression test:**

---

## Bonus B — Mutation Testing (≥5 mutant)

| Mutant | Değişiklik | Testler yakaladı mı? | Açıklama |
|---|---|---|---|
| | | | |
