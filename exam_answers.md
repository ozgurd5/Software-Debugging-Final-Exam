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

| Hipotez | Gözlem | Deney | Sonuç | Kabul/Ret |
|---|---|---|---|---|
| H1 | | | | |
| H2 | | | | |
| H3 | | | | |

---

## Soru 5 — Delta Debugging / Input Minimization
- **Başlangıç input büyüklüğü:**
- **Küçültme adımları:**

| Adım | Denenen değişiklik | Failure devam etti mi? | Sonuç |
|---|---|---|---|
| | | | |

- **Failure devam eden / kaybolan parçalar:**
- **Minimum (veya minimuma yakın) failure-inducing input:**
- **Neden failure üretiyor:**

---

## Soru 6 — Trace / Logging Analizi
- **İşlenen ana bölümler:**
- **Normalize edilen alanlar:**
- **Beklenen tipte olmayan değer(ler):**
- **Çöküşten hemen önceki fonksiyon çağrısı ve değişken değerleri:**
- **İlgili trace (kısa):**

---

## Soru 7 — Program Slicing / Dependency Analysis
1. **Failure anındaki kritik değişken:**
2. **Hangi input alanından geliyor:**
3. **Hangi fonksiyonlarda işlendi:**
4. **Üzerinde yapılan varsayım:**
5. **Slice'taki en önemli satırlar:**

---

## Soru 8 — Defect–Infection–Failure Chain
- **Defect:**
- **Infection:**
- **Propagation:**
- **Failure:**

---

## Soru 9 — Patch ve Doğrulama
1. **Değişen dosya/fonksiyon:**
2. **Bu değişiklik neden doğru:**
3. **Başka geçerli config'leri bozar mı:**
4. **Hangi testlerle doğrulandı (tüm testler geçti mi):**

---

## Bonus A — Regression Test
- **Test:**
- **Neden regression test:**

---

## Bonus B — Mutation Testing (≥5 mutant)

| Mutant | Değişiklik | Testler yakaladı mı? | Açıklama |
|---|---|---|---|
| | | | |
