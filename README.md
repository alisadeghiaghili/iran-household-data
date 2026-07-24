<div align="center">

# 🇮🇷 Iran Household Data

**Comprehensive Iranian household indicators (1960–2025) for prediction tasks**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Data](https://img.shields.io/badge/Data-World%20Bank-orange.svg)](https://data.worldbank.org)

[English](#english) | [فارسی](#persian) | [Deutsch](#german)

</div>

---

## English

### Overview

This repository provides comprehensive Iranian household data extracted from the World Bank DataBank API. The dataset covers **65+ years** (1960–2025) of demographic, economic, health, education, energy, and migration indicators suitable for prediction tasks and statistical analysis.

### Quick Start

```bash
# Clone the repository
git clone https://github.com/alisadeghiaghili/iran-household-data.git
cd iran-household-data

# Install dependencies
pip install requests pandas openpyxl

# Run the scraper (fetches fresh data from World Bank)
python scraper.py
```

### Usage

```bash
# Full pipeline: fetch → process → validate
python scraper.py

# Individual steps
python scraper.py --fetch-only      # Only fetch from API
python scraper.py --process-only    # Only process raw data
python scraper.py --validate-only   # Only validate output

# Custom output directory
python scraper.py --output-dir my_data
```

### Dataset

| Property | Value |
|----------|-------|
| **Time Range** | 1960 – 2025 |
| **Rows** | 66 (one per year) |
| **Columns** | 40 indicators |
| **Source** | World Bank DataBank API |
| **Updates** | Run `python scraper.py` to refresh |

### Key Variables

#### Demographics (Age & Population Structure)
| Column | Description |
|--------|-------------|
| `population_total` | Total population |
| `population_female_pct` | Female population percentage |
| `youth_population_pct` | Age 0–14 (%) |
| `working_age_population_pct` | Age 15–64 (%) |
| `elderly_population_pct` | Age 65+ (%) |
| `urban_population_pct` | Urban population (%) |
| `fertility_rate` | Births per woman |

#### Economic
| Column | Description |
|--------|-------------|
| `gdp_per_capita_usd` | GDP per capita (current USD) |
| `gdp_per_capita_ppp` | GDP per capita (PPP) |
| `unemployment_rate` | Unemployment (%) |
| `consumption_gdp_pct` | Household consumption (% of GDP) |
| `exports_gdp_pct` | Exports (% of GDP) |
| `imports_gdp_pct` | Imports (% of GDP) |

#### Health
| Column | Description |
|--------|-------------|
| `life_expectancy` | Life expectancy at birth (years) |
| `infant_mortality` | Infant mortality rate |
| `neonatal_mortality` | Neonatal mortality rate |
| `physicians_per_1000` | Physicians per 1,000 people |
| `hospital_beds_per_1000` | Hospital beds per 1,000 people |

#### Education
| Column | Description |
|--------|-------------|
| `literacy_rate` | Adult literacy rate (%) |
| `secondary_enrollment` | Secondary school enrollment (%) |
| `tertiary_enrollment` | Tertiary enrollment (%) |
| `dpt_immunization_pct` | DPT immunization coverage |

#### Energy & Environment
| Column | Description |
|--------|-------------|
| `energy_use_per_capita` | Energy use per capita (kg oil eq.) |
| `electricity_access_pct` | Electricity access (%) |
| `internal_freshwater_per_capita` | Freshwater per capita (m³) |

#### Migration
| Column | Description |
|--------|-------------|
| `net_migration` | Net migration (people) |

### Output Formats

| File | Format | Description |
|------|--------|-------------|
| `data/processed/iran_household_data.csv` | CSV | Main dataset |
| `data/processed/iran_household_data.xlsx` | Excel | Multi-sheet workbook |
| `data/processed/iran_household_data.sql` | SQL | Database import script |

### Data Completeness

```
100% ████████████████████  year, population, GDP, urbanization, migration
 80% ████████████████      life_expectancy, fertility, mortality
 50% ██████████            education, energy, immunization
 <50% █████                some health/poverty indicators
```

### Example: Python

```python
import pandas as pd

df = pd.read_csv("data/processed/iran_household_data.csv")

# Recent years
recent = df[df["year"] >= 2015]

# Key prediction features
features = [
    "year", "population_total", "youth_population_pct",
    "working_age_population_pct", "gdp_per_capita_usd",
    "urban_population_pct", "life_expectancy"
]

print(recent[features].to_string(index=False))
```

### Example: SQL

```sql
-- Import into SQLite
sqlite3 iran_household.db < data/processed/iran_household_data.sql

-- Query
SELECT year, population_total, gdp_per_capita_usd
FROM iranian_household
WHERE year >= 2020;
```

### Data Protection

All data files are **excluded from git** via `.gitignore`. Only the scraper script and documentation are tracked. To commit data, temporarily remove the data rules from `.gitignore`.

### Contributing

Contributions welcome! Areas for improvement:
- Additional indicators from SCI (amar.org.ir)
- Province-level disaggregation
- Monthly/quarterly granularity
- Additional data sources (UN, IMF)

### License

MIT License - see [LICENSE](LICENSE) for details.

---

## فارسی (Persian)

### نمای کلی

این مخزن داده‌های جامع خانوارهای ایرانی را از API بانک جهانی استخراج می‌کند. مجموعه داده بیش از **۶۵ سال** (۱۳۳۹–۱۴۰۴) شاخص‌های جمعیت‌شناختی، اقتصادی، بهداشتی، آموزشی، انرژی و مهاجرت را برای وظایف پیش‌بینی و تحلیل آماری پوشش می‌دهد.

### شروع سریع

```bash
# کلون کردن مخزن
git clone https://github.com/alisadeghiaghili/iran-household-data.git
cd iran-household-data

# نصب وابستگی‌ها
pip install requests pandas openpyxl

# اجرای اسکرپر (دریافت داده تازه از بانک جهانی)
python scraper.py
```

### استفاده

```bash
# خط لوله کامل: دریافت → پردازش → اعتبارسنجی
python scraper.py

# مراحل جداگانه
python scraper.py --fetch-only      # فقط دریافت از API
python scraper.py --process-only    # فقط پردازش داده خام
python scraper.py --validate-only   # فقط اعتبارسنجی خروجی

# پوشه خروجی سفارشی
python scraper.py --output-dir my_data
```

### مجموعه داده

| ویژگی | مقدار |
|--------|-------|
| **بازه زمانی** | ۱۳۳۹ – ۱۴۰۴ |
| **ردیف‌ها** | ۶۶ (یکی برای هر سال) |
| **ستون‌ها** | ۴۰ شاخص |
| **منبع** | API بانک جهانی |
| **به‌روزرسانی** | `python scraper.py` را اجرا کنید |

### متغیرهای کلیدی

#### جمعیت‌شناختی (سن و ساختار جمعیت)
| ستون | توضیح |
|------|-------|
| `population_total` | جمعیت کل |
| `population_female_pct` | درصد جمعیت زن |
| `youth_population_pct` | سن ۰-۱۴ سال (٪) |
| `working_age_population_pct` | سن ۱۵-۶۴ سال (٪) |
| `elderly_population_pct` | سن ۶۵+ سال (٪) |
| `urban_population_pct` | جمعیت شهری (٪) |
| `fertility_rate` | نرخ باروری (تولد در هر زن) |

#### اقتصادی
| ستون | توضیح |
|------|-------|
| `gdp_per_capita_usd` | تولید ناخالص داخلی سرانه (دلار) |
| `gdp_per_capita_ppp` | تولید ناخالص داخلی سرانه (PPP) |
| `unemployment_rate` | نرخ بیکاری (٪) |
| `consumption_gdp_pct` | مصرف خانوار (٪ تولید ناخالص) |

#### بهداشت
| ستون | توضیح |
|------|-------|
| `life_expectancy` | امید به زندگی (سال) |
| `infant_mortality` | نرخ مرگ و میر نوزاد |
| `physicians_per_1000` | پزشک به ازای هر ۱۰۰۰ نفر |

#### آموزش
| ستون | توضیح |
|------|-------|
| `literacy_rate` | نرخ سواد (٪) |
| `secondary_enrollment` | ثبت‌نام متوسطه (٪) |
| `tertiary_enrollment` | ثبت‌نام عالی (٪) |

#### انرژی و محیط زیست
| ستون | توضیح |
|------|-------|
| `energy_use_per_capita` | مصرف انرژی سرانه |
| `electricity_access_pct` | دسترسی به برق (٪) |

#### مهاجرت
| ستون | توضیح |
|------|-------|
| `net_migration` | مهاجرت خالص (نفر) |

### فرمت‌های خروجی

| فرمت | فایل | توضیح |
|------|------|-------|
| CSV | `data/processed/iran_household_data.csv` | مجموعه داده اصلی |
| Excel | `data/processed/iran_household_data.xlsx` | کاربرگ چند صفحه‌ای |
| SQL | `data/processed/iran_household_data.sql` | اسکریپت وارد کردن به پایگاه داده |

### نمونه کد

```python
import pandas as pd

df = pd.read_csv("data/processed/iran_household_data.csv")

# سال‌های اخیر
recent = df[df["year"] >= 2015]

# ویژگی‌های پیش‌بینی
print(recent[["year", "population_total", "gdp_per_capita_usd"]].to_string(index=False))
```

---

## Deutsch (German)

### Übersicht

Dieses Repository enthält umfassende iranische Haushaltsindikatoren, die über die World Bank DataBank API extrahiert wurden. Der Datensatz umfasst **über 65 Jahre** (1960–2025) demografische, wirtschaftliche, Gesundheits-, Bildungs-, Energie- und Migrationsindikatoren für Vorhersageaufgaben und statistische Analysen.

### Schnellstart

```bash
# Repository klonen
git clone https://github.com/alisadeghiaghili/iran-household-data.git
cd iran-household-data

# Abhängigkeiten installieren
pip install requests pandas openpyxl

# Scraper ausführen (frische Daten von der Weltbank)
python scraper.py
```

### Verwendung

```bash
# Vollständige Pipeline: Abruf → Verarbeitung → Validierung
python scraper.py

# Einzelne Schritte
python scraper.py --fetch-only      # Nur von API abrufen
python scraper.py --process-only    # Nur Rohdaten verarbeiten
python scraper.py --validate-only   # Nur Ausgabe validieren

# Benutzerdefiniertes Ausgabeverzeichnis
python scraper.py --output-dir my_data
```

### Datensatz

| Eigenschaft | Wert |
|-------------|------|
| **Zeitraum** | 1960 – 2025 |
| **Zeilen** | 66 (eine pro Jahr) |
| **Spalten** | 40 Indikatoren |
| **Quelle** | World Bank DataBank API |
| **Aktualisierung** | `python scraper.py` ausführen |

### Schlüsselvariablen

#### Demografie (Alter & Bevölkerungsstruktur)
| Spalte | Beschreibung |
|--------|--------------|
| `population_total` | Gesamtbevölkerung |
| `population_female_pct` | Weiblicher Bevölkerungsanteil |
| `youth_population_pct` | Alter 0–14 (%) |
| `working_age_population_pct` | Alter 15–64 (%) |
| `elderly_population_pct` | Alter 65+ (%) |
| `urban_population_pct` | Stadtbevölkerung (%) |
| `fertility_rate` | Geburten pro Frau |

#### Wirtschaft
| Spalte | Beschreibung |
|--------|--------------|
| `gdp_per_capita_usd` | BIP pro Kopf (aktuelle USD) |
| `gdp_per_capita_ppp` | BIP pro Kopf (PPP) |
| `unemployment_rate` | Arbeitslosenquote (%) |
| `consumption_gdp_pct` | Haushaltskonsum (% des BIP) |

#### Gesundheit
| Spalte | Beschreibung |
|--------|--------------|
| `life_expectancy` | Lebenserwartung bei Geburt (Jahre) |
| `infant_mortality` | Säuglingssterblichkeitsrate |
| `physicians_per_1000` | Ärzte pro 1.000 Einwohner |

#### Bildung
| Spalte | Beschreibung |
|--------|--------------|
| `literacy_rate` | Alphabetisierungsrate (%) |
| `secondary_enrollment` | Sekundarschul-Einschreibung (%) |
| `tertiary_enrollment` | Hochschul-Einschreibung (%) |

#### Energie & Umwelt
| Spalte | Beschreibung |
|--------|--------------|
| `energy_use_per_capita` | Energieverbrauch pro Kopf |
| `electricity_access_pct` | Stromzugang (%) |

#### Migration
| Spalte | Beschreibung |
|--------|--------------|
| `net_migration` | Nettomigration (Personen) |

### Ausgabeformate

| Format | Datei | Beschreibung |
|--------|-------|--------------|
| CSV | `data/processed/iran_household_data.csv` | Hauptdatensatz |
| Excel | `data/processed/iran_household_data.xlsx` | Mehrseitige Arbeitsmappe |
| SQL | `data/processed/iran_household_data.sql` | Datenbank-Import-Skript |

### Codebeispiel

```python
import pandas as pd

df = pd.read_csv("data/processed/iran_household_data.csv")

# Letzte Jahre
recent = df[df["year"] >= 2015]

# Vorhersagefeatures
features = ["year", "population_total", "gdp_per_capita_usd", "urban_population_pct"]
print(recent[features].to_string(index=False))
```

### Datenqualität

```
100% ████████████████████  Jahr, Bevölkerung, BIP, Urbanisierung, Migration
 80% ████████████████      Lebenserwartung, Fruchtbarkeit, Sterblichkeit
 50% ██████████            Bildung, Energie, Immunisierung
 <50% █████                Einige Gesundheits-/Armutsindikatoren
```

---

<div align="center">

### Citation

If you use this dataset in your research, please cite:

```
Sadeghi Aghili, A. (2025). Iran Household Data: Comprehensive Iranian household 
indicators (1960-2025). GitHub. https://github.com/alisadeghiaghili/iran-household-data
```

---

**Made for prediction tasks and research**

</div>
