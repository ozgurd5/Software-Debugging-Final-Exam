# Yazılımlarda Hata Ayıklama — Take-Home Final

## Final Başlığı

**Systematic Debugging of a JSON Configuration Parser**

## Süre

Bu take-home final için teslim tarihi resmi final tarihidir. Dijital dosyalar online.deu.edu.tr de açılacak ödeve yüklenirken yazılı sınav resmi sinav tarihinde getirelecektir. SINAVI getirmeyenler ve SINAV TUTANAĞINDA imzası olmayanlar sınava girmemiş olarak sayılacaktır.  

## Amaç

Bu finalde sizden yalnızca bir bug düzeltmeniz beklenmemektedir. Asıl amaç, bir yazılım hatasını sistematik olarak incelemek, hatayı güvenilir biçimde yeniden üretmek, hataya neden olan koşulları daraltmak, program davranışını analiz etmek ve düzeltmenin doğruluğunu açık biçimde göstermektir.

Bu çalışmada aşağıdaki hata ayıklama tekniklerinden yararlanmanız beklenmektedir:

- Failure reproduction
- Test oracle oluşturma
- Scientific debugging: hipotez, deney, gözlem, sonuç
- Tracing / logging
- Delta debugging veya systematic input minimization
- Program slicing veya dependency analysis
- Defect–infection–failure chain açıklaması
- Patch geliştirme ve doğrulama

Regression testing ve mutation testing derste ana konu olarak işlenmediği için **bonus** olarak değerlendirilecektir.

---

# Verilen Proje

Size hatalı çalışan küçük bir JSON configuration parser verilmiştir.

Proje dizin yapısı şöyledir:

```text
student_package/
  src/
    config_parser.py
    app.py
  tests/
    test_config_parser.py
  inputs/
    valid_basic.json
    valid_full.json
    large_config_failure.json
  docs/
    report_template.md
    rubric.md
  README.md
```

Program bir JSON config dosyasını okuyup doğrulamakta ve uygulama ayarlarına dönüştürmektedir. Bazı config dosyaları doğru çalışırken, verilen büyük config dosyasında program hata üretmektedir.

---

# Sorular

## Soru 1 — Hatanın Yeniden Üretimi

Verilen projeyi çalıştırınız ve hatanın hangi input ile ortaya çıktığını gösteriniz.

Raporunuzda ve sınav kağıdınızda şunlar bulunmalıdır:

1. Hatanın çalıştırma komutu
2. Alınan hata mesajı veya yanlış çıktı
3. Hatanın tekrar üretilebilir olduğunu gösteren kısa açıklama
4. Hatanın crash mi, wrong output mu, yoksa beklenmeyen davranış mı olduğunu belirtiniz

---

## Soru 2 — Test Oracle Oluşturma

Hatanın oluşup oluşmadığını otomatik olarak belirleyen bir test oracle yazınız.

Oracle şu soruya cevap vermelidir:

> Bu config dosyası işlendiğinde program beklenen biçimde çalışıyor mu, yoksa failure mı oluşuyor?

Oracle fonksiyonu raporda ve sınav kağıdında açıklanmalıdır.

---

## Soru 3 — Passing ve Failing Testler

En az:

- 5 passing test
- 3 failing test

hazırlayınız.

Testlerinizde sadece hazır input dosyalarını kullanmak zorunda değilsiniz. Yeni küçük JSON input dosyaları veya doğrudan Python dictionary nesneleri oluşturabilirsiniz.

Her test için şu bilgileri rapora ve sınav kağıdına ekleyiniz:

| Test adı | Input özeti | Beklenen sonuç | Gerçek sonuç | Passing/Failing |
|---|---|---|---|---|

---

## Soru 4 — Scientific Debugging

Hata hakkında en az **3 hipotez** kurunuz.

Her hipotez için aşağıdaki tabloyu doldurunuz(raporda ve sınav kağıdında olacak):

| Hipotez | Gözlem | Deney | Sonuç | Kabul/Ret |
|---|---|---|---|---|

Örnek hipotez türleri:

- Hata belirli bir JSON alanı eksik olduğunda oluşuyor olabilir.
- Hata boolean değerlerin işlenmesinde oluşuyor olabilir.
- Hata nested object yapılarında oluşuyor olabilir.
- Hata `null` değerlerin işlenmesinde oluşuyor olabilir.
- Hata belirli bir validasyon sırasından kaynaklanıyor olabilir.

---

## Soru 5 — Delta Debugging / Input Minimization

Verilen büyük input dosyası `inputs/large_config_failure.json` içinden hatayı tetikleyen minimum veya minimuma yakın input parçasını bulunuz.

Bunu elle sistematik olarak yapabilir veya kendi küçük delta debugging aracınızı yazabilirsiniz.

Raporunuzda ve sınav kağıdında şunları gösteriniz:

1. Başlangıç input büyüklüğü
2. Denenen küçültme adımları
3. Hangi parçalar çıkarıldığında failure devam etti?
4. Hangi parçalar çıkarıldığında failure kayboldu?
5. Elde edilen minimum veya minimuma yakın failure-inducing input
6. Bu input’un neden failure ürettiği

Örnek tablo:

| Adım | Denenen değişiklik | Failure devam etti mi? | Sonuç |
|---|---|---|---|

---

## Soru 6 — Trace / Logging Analizi

Programın execution trace’ini çıkarınız.

En az şu bilgileri gözlemlemeye çalışınız:

- Config dosyasının hangi ana bölümleri işleniyor?
- Hangi alanlar normalize ediliyor?
- Hangi değerler beklenen tipte değil?
- Hata oluşmadan hemen önceki fonksiyon çağrısı ve değişken değerleri nelerdir?

Trace/log çıktılarınızı rapora ve sınav kağıdına ekleyiniz. Gereksiz uzun log yerine hataya götüren ilgili bölümleri seçiniz.

---

## Soru 7 — Program Slicing veya Dependency Analysis

Hatalı sonuca veya crash’e neden olan değişkeni seçiniz.

Bu değişkenin değerinin hangi fonksiyonlardan, satırlardan ve input alanlarından etkilendiğini açıklayınız.

Raporunuzda ve sınav kağıdınızda şu sorulara cevap veriniz:

1. Failure anındaki kritik değişken hangisidir?
2. Bu değişken hangi input alanından gelmektedir?
3. Bu değişken hangi fonksiyonlarda işlenmiştir?
4. Bu değişken üzerinde hangi varsayım yapılmıştır?
5. Slice içinde yer alan en önemli satırlar hangileridir?

---

## Soru 8 — Defect–Infection–Failure Chain

Aşağıdaki kavramları kullanarak hatayı açıklayınız:

- **Defect:** Programdaki gerçek kod hatası nedir?
- **Infection:** Program state’i ilk nerede yanlış veya tehlikeli hale geliyor?
- **Propagation:** Bu hatalı state program içinde nasıl ilerliyor?
- **Failure:** Kullanıcının gördüğü hata nedir?

Raporunuzda ve sınav kağıdınızda zinciri açıkça yazınız.

Örnek format:

```text
Defect:
...

Infection:
...

Propagation:
...

Failure:
...
```

---

## Soru 9 — Patch ve Doğrulama

Hatayı düzeltiniz.

Patch’inizi açıklayınız:

1. Hangi dosya/fonksiyon değişti?
2. Neden bu değişiklik doğru?
3. Bu değişiklik başka geçerli config dosyalarını bozar mı?
4. Hangi testlerle doğruladınız?

Tüm testlerin geçtiğini gösteriniz Tüm bunları raporda ve ve sınav kağıdında gösteriniz.

---

# Bonus Sorular

## Bonus A — Regression Test

Bulduğunuz bug’ın ileride tekrar oluşmasını engelleyecek özel bir regression test yazınız.

Bu testin neden regression test olduğunu açıklayınız.

**Bonus:** +5 puan

---

## Bonus B — Mutation Testing

Test setinizin kalitesini değerlendirmek için en az 5 küçük mutant tanımlayınız.

Örnek mutant türleri:

- `==` yerine `!=`
- `is None` kontrolünü kaldırma
- Varsayılan değer değiştirme
- Boolean dönüşümünü tersine çevirme
- Bir validasyon koşulunu silme

Her mutant için şu tabloyu doldurunuz:

| Mutant | Değişiklik | Testler mutantı yakaladı mı? | Açıklama |
|---|---|---|---|

**Bonus:** +10 puan

---

# Teslim Formatı

Aşağıdakileri tek bir `.zip` dosyası olarak teslim ediniz:

```text
student_no_name_final.zip
  src/
  tests/
  inputs/
  report.pdf veya report.md
  README.md
```

Kod çalıştırılabilir olmalıdır.

Ayrıca tüm sorular ve bonusların da açıklamalarının olduğu yazılı sınavıda teslim edeceksiniz. 

---

# Önemli Not

Sadece hatayı düzeltmek yeterli değildir. Notlandırma esas olarak sistematik hata ayıklama sürecine, deneylerin kalitesine, raporlamaya ve hatanın açıklanmasına göre yapılacaktır.
