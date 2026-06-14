# CLAUDE.md — Proje Hafızası ve Çalışma Rehberi

> Bu dosya bu deponun kalıcı hafızasıdır. Claude Code ve diğer AI modelleri her oturumda
> buradan bağlam alır. İki bölüm: **(1) Projeye Genel Bakış ve Mimari**, **(2) Çalışma Kuralları**.
> Buradaki her olgu **doğrulanmıştır** (komut çıktısı / dosya içeriği). Tahmin yok.

---

## 1. Projeye Genel Bakış ve Mimari

### 1.1 Bu repo nedir?
"Yazılımlarda Hata Ayıklama" dersinin **take-home final sınavı**. Görev: hatalı bir
**JSON configuration parser**'ı **sistematik hata ayıklama teknikleriyle** incelemek,
hatayı yeniden üretmek, daraltmak, açıklamak ve düzeltmek.

> ⚠️ Notlandırma esas olarak **sürece** (hipotez/deney/analiz/raporlama) bakar, sadece
> düzeltmeye değil. "Sadece hatayı düzeltmek yeterli ve öncelikli değildir." (sınav "Önemli Not")

Kaynak belgeler:
- `FINAL_QUESTION.md` — 9 soru + 2 bonusun tam metni (repo kökünde).
- `Yazilimlarda_..._Sinav_Kagidi.docx.md` — resmî sınav kağıdı (markdown'a çevrilmiş).
- `docs/rubric.md` — puanlama cetveli (100 + bonuslar).
- `docs/report_template.md` — rapor şablonu (DEĞİŞTİRİLMEZ; rapor buna birebir uyar).

### 1.2 Hata (DOĞRULANMIŞ)
- **Yer:** `src/config_parser.py` → `parse_bool()` (mevcut kodda ≈150. satır).
- **Kök neden:** `value.lower()` çağrılırken değer string varsayılıyor. JSON `null` → Python `None`;
  `None.lower()` → `AttributeError: 'NoneType' object has no attribute 'lower'`.
- **Tetikleyici:** `inputs/large_config_failure.json` içindeki `"features": { "debug": null }`.
- **Hata türü:** CRASH (yakalanmayan `AttributeError`). `app.py` yalnızca `ConfigError` yakaladığı
  için bu istisna yakalanmaz; program traceback + çıkış kodu 1 ile çöker.
- Defekt kodda bilerek bırakılmış, yorumla işaretli ("Intentional defect").

### 1.3 Dizin haritası
```
Software-Debugging-Final-Exam/   <- repo kökü = PyCharm Project Root + Source Root (tek kök)
│  ─────── TESLİME GİRENLER (zip'in köküne BUNLAR konur) ───────
├─ src/
│  ├─ config_parser.py    <- asıl mantık (HATA burada)
│  └─ app.py              <- CLI giriş noktası
├─ tests/test_config_parser.py   <- mevcut 5 test
├─ inputs/                <- valid_basic.json, valid_full.json, large_config_failure.json (HATALI)
├─ report.md             <- RAPOR (İngilizce, report_template.md ile birebir)
├─ debugging_logs/       <- trace/log (markdown), Soru 6'da doldurulur
├─ README.md             <- hocadan (İÇERİĞİ değişmez)
│  ─────── TESLİME GİRMEYENLER ───────
├─ docs/                 <- hoca referans: report_template.md, rubric.md
├─ FINAL_QUESTION.md     <- hoca: soru metni
├─ CLAUDE.md             <- bu dosya (hafıza)
├─ exam_answers.md       <- sınav kağıdı cevapları (Türkçe)
├─ claude_mistakes.md    <- hata günlüğü + sayaç
├─ question_explanations.md <- soru başına öğrenme notları (kavram/ön bilgi)
├─ make_submission.ps1   <- teslim zip'ini üretir (yalnızca yerel)
├─ requirements.txt      <- pytest (yalnızca yerel)
├─ .venv/  .idea/  .pytest_cache/  .git/  .gitignore
└─ Yazilimlarda_..._Sinav_Kagidi.docx.md
```

### 1.4 Parser akışı (kontrol akışı)
```
app.py: main()
  └─ load_config(path)                         # config_parser.py
       ├─ json.load(f)                          # ham dict
       └─ normalize_config(raw)
            ├─ validate_required_sections()     # server/features/limits zorunlu
            ├─ normalize_server()               # host(str), port(1..65535 int)
            ├─ normalize_features()             # cache/debug/experimental -> parse_bool()  <-- HATA YOLU
            ├─ normalize_limits()               # max_users/timeout/retries (pozitif int)
            └─ normalize_logging()              # level, destination
  -> başarı: "CONFIG_OK" + dict, çıkış 0
  -> ConfigError: "CONFIG_ERROR: ...", çıkış 1
  -> başka istisna (AttributeError): YAKALANMAZ -> crash, çıkış 1
```

### 1.5 Ortam (DOĞRULANMIŞ)
- **Python:** 3.13.2.
- **Komutlar:** En güvenlisi `py` (uygulama) ve `.venv\Scripts\python.exe` (testler) — her kabukta
  çalışır. User PATH'te gerçek Python 3.13.2 ilk sırada olduğu için yeni açılan kabuklarda
  `python`/`pip` de çalışır (`python3` Store kısayoluna düşebilir; `python` veya `py` kullan).
- **venv:** repo kökünde `.venv` (Python 3.13.2 + **pytest 9.1.0**). PyCharm bunu kullanır.
  Global `py`'de pytest YOK → testleri venv python'u ile çalıştır.
- **PyCharm:** Project Root = repo kökü; repo kökü Source Root olarak işaretli
  (`.idea/*.iml`: `sourceFolder = $MODULE_DIR$`). Repo kökü sys.path'te olduğu için testteki
  `from src.config_parser import ...` çalışır.

### 1.6 Nasıl çalıştırılır (DOĞRULANMIŞ — hepsi repo kökünden)
```powershell
# Uygulama:
py src\app.py inputs\valid_basic.json            # CONFIG_OK, çıkış 0
py src\app.py inputs\large_config_failure.json   # CRASH (AttributeError), çıkış 1

# Testler (venv python'u ile, repo kökünden):
.\.venv\Scripts\python.exe -m pytest -q          # 5 passed

# Teslim zip'i:
powershell -ExecutionPolicy Bypass -File .\make_submission.ps1   # 2022280084_ozgurdalbeler_final.zip
```

---

## 2. Çalışma Kuralları

Bağlayıcıdır.

1. **Adım adım, kullanıcı güdümlü.** Soruları sırayla yaparız. Kullanıcı açıkça "başla / devam et"
   demeden bir sonraki soruya GEÇME. Hız değil, anlamak öncelikli.
2. **Tahmin etme, varsayma.** Her olguyu araştır, kaynağını (kod/komut/belge) bul. Bulamıyorsan **SOR**.
   En kritik kural.
3. **Çelişkiyi sorgula.** Kullanıcının/belgelerin isteklerinde mantık hatası, iç çelişki veya
   sınavla çelişki görürsen körü körüne uygulama — **SOR/uyar**.
4. **Karar verme, SOR.** Birden çok geçerli seçenek (yapı/tasarım/yerleşim) varsa kendin seçme;
   **karşılaştırmalı tablo + paragraf** sun ve AskUserQuestion ile sor. Kullanıcı seçmeden uygulama.
5. **Olgu ≠ nedensellik.** Bir "çünkü/için" iddiasını ancak doğruladıysan yaz. Olguyu (doğruladığın)
   ve nedeni (varsayım olabilir) birbirine karıştırma.
6. **Rapor:** `report.md`, **İNGİLİZCE**, `docs/report_template.md` ile **birebir** (13 bölüm). Sapma.
7. **Sınav kağıdı cevapları:** `exam_answers.md`, Türkçe. **ÖZET DEĞİL** — raporla **aynı
   genişlik/derinlik**. Sınav soruları ile rapor şablonu birebir örtüşmez (farklar: S1
   tekrar-üretilebilirlik, S5 "neden failure" + kaldı/kayboldu, S6 spesifik gözlemler, S9 "diğer
   config'leri bozar mı"). Burada sınav sorularının her maddesini eksiksiz cevapla.
8. **Dosya biçimi:** Sınav özel istemediyse `.txt` ÜRETME — **markdown**. Loglar da `.md`.
9. **Hocanın dosyalarının İÇERİĞİNİ değiştirme** (kod/JSON/metin, import path'leri dahil).
   Taşıma/klasörleme serbest. Tek içerik değişikliği: Soru 9 patch'i (`config_parser.py`), kullanıcı onayıyla.
10. **Doğrula.** İddiaları kodu çalıştırarak kanıtla (venv python, repo kökünden pytest). Patch
    sonrası TÜM testler geçmeli.
11. **Dosyalar kendi başına anlaşılır olmalı.** Hiçbir dosya bu sohbeti veya projenin evrimini
    (neyin değiştiğini/kaldırıldığını/kararını) anlatmaz. Yalnızca **güncel durumu** mutlak biçimde
    yaz; "kaldırıldı", "sonra", "artık", "karar verildi" gibi geçmiş/değişim ifadeleri kullanma.
    Hedef: bu projeyi ve bu konuşmayı hiç bilmeyen bir insan/AI dosyayı okuyup anlayabilsin.
12. **Hata günlüğü (`claude_mistakes.md`).** Kullanıcı seni her düzelttiğinde: hatayı, neden saçma
    olduğunu, neyi gözden kaçırdığını yaz; en üstteki **hata sayacını +1** artır. Hata kullanıcının
    zamanını çalar ve güvenilirliğini düşürür.
13. **Satır sarma (markdown).** Uzun satırları ~100 karakterde elle böl (hard wrap) ki IDE'de
    kaynak olarak yatay kaydırmadan okunsun. Liste maddelerinin devam satırlarını 2 boşluk girintile.
    (PyCharm'da Settings → Editor → General → Soft Wraps ile de açılabilir.)

### 2.1 Teslim formatı
Zip'in **içi DÜZ** olmalı: kökünde doğrudan `src/ tests/ inputs/ report.md README.md debugging_logs/`
(sarmalayıcı klasör YOK). Zip adı: **`2022280084_ozgurdalbeler_final.zip`**, `make_submission.ps1` ile üretilir.
- **Girenler:** `src/`, `tests/`, `inputs/`, `report.md`, `README.md`, `debugging_logs/`
- **GİRMEYENLER:** `docs/`, `FINAL_QUESTION.md` (hoca ref); `CLAUDE.md`, `exam_answers.md`,
  `claude_mistakes.md`, `question_explanations.md`, `make_submission.ps1`, `requirements.txt` (çalışma); `.venv/ .idea/ .pytest_cache/ .git/ .gitignore`, `.docx`
- **Ayrıca** yazılı sınav kağıdı resmî sınav tarihinde elden; **tutanakta imza zorunlu** (yoksa girmemiş sayılır).

### 2.2 Bilinen tutarsızlıklar (sınav belgeleri arası)
- **`debugging_logs/`**: `.docx` teslim listesinde VAR, `FINAL_QUESTION.md`'de YOK → teslime **DAHİL** edilir.
- **Bonus puanları**: `FINAL_QUESTION.md` A:+5 / B:+10; `rubric.md` +10 / +10 / +10 (Genel Beğeni)
  → notlamada **rubric.md** esas; ikisi de yapılır.
- **README komutları** (`python`, `pytest`) bu ortamda çalışmaz → `py` + venv.

### 2.3 İlerleme
9 soru + 2 bonus + final derleme görev listesinde takip edilir. Her sorunun çıktısı üç dosyaya işlenir:
`report.md` (İngilizce, teslim), `exam_answers.md` (Türkçe, teslim) ve `question_explanations.md`
(Türkçe, yalnızca öğrenme için — kavram/ön bilgi anlatımı; teslime girmez). İlgili loglar
`debugging_logs/` içine kaydedilir.

### 2.4 Rapor (report.md) ↔ Sınav (exam_answers.md) gereksinim farkları
İkisi de tam ve aynı derinliktedir; yalnızca düzenleri farklı. `report.md` 13 başlığı (template)
izler; `exam_answers.md` 9 soru + 2 bonusu izler. Sınav, şablonda **alanı olmayan** bazı şeyleri
ister; bunlar report.md'de ilgili bölümün **içine** eklenir (yeni üst başlık açmadan):

| Şablon bölümü | Sınav | Şablonda olmayan ekstra istek |
|---|---|---|
| §2 Failure Reproduction | S1 | **Tekrar-üretilebilirlik açıklaması** |
| §6 Delta Debugging | S5 | **"Neden failure üretiyor"** + kaldı/kayboldu ayrımı |
| §7 Trace/Logging | S6 | 4 spesifik gözlem: işlenen bölümler · normalize alanlar · **yanlış tipteki değer** · çöküş öncesi fonksiyon+değişken değerleri |
| §10+§11 Patch+Validation | S9 | **"Diğer geçerli config'leri bozar mı?"** (ayrıca sınav patch+doğrulamayı tek soruda birleştirir) |

Küçük farklar: sayı şartları (S3 ≥5 pass/≥3 fail, Bonus B ≥5 mutant); S7'nin açık "varsayım"
maddesi; Bonus A'nın "neden regresyon testi" açıklaması; §1 ortam-bilgisi ↔ sınav kağıdı imza bloğu.
Tam örtüşenler: S2/§3, S4/§5, S8/§9.
