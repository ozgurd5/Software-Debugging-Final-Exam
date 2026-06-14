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
