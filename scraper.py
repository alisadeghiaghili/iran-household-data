"""
Iranian Household Data Scraper
==============================
Reusable script to fetch, process, and export Iranian household data.

Usage:
    python scraper.py                    # Run full pipeline
    python scraper.py --fetch-only       # Only fetch data (no processing)
    python scraper.py --process-only     # Only process existing raw data
    python scraper.py --validate-only    # Only validate existing processed data
    python scraper.py --output-dir PATH  # Custom output directory
"""

import argparse
import os
import sys
import time
import json
from datetime import datetime

import requests
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

# World Bank API
WB_API_BASE = "https://api.worldbank.org/v2"
WB_COUNTRY = "IRN"  # Iran, Islamic Rep.

# Indicators to fetch (code -> friendly name)
INDICATORS = {
    # Demographics
    "SP.POP.TOTL": "population_total",
    "SP.POP.TOTL.FE.ZS": "population_female_pct",
    "SP.DYN.LE00.IN": "life_expectancy",
    "SP.DYN.TFRT.IN": "fertility_rate",
    "SP.URB.TOTL.IN.ZS": "urban_population_pct",
    "SP.RUR.TOTL.ZS": "rural_population_pct",
    "SP.POP.0014.TO.ZS": "age_0_14_pct",
    "SP.POP.1564.TO.ZS": "age_15_64_pct",
    "SP.POP.65UP.TO.ZS": "age_65_plus_pct",
    
    # Economy
    "NY.GDP.PCAP.CD": "gdp_per_capita_usd",
    "NY.GDP.PCAP.PP.CD": "gdp_per_capita_ppp",
    "SI.POV.DDAY": "poverty_headcount_215",
    "SI.POV.NAHC": "poverty_national",
    "SL.UEM.TOTL.ZS": "unemployment_rate",
    "SL.TLF.CACT.ZS": "labor_force_participation",
    
    # Health
    "SH.H2O.BASW.ZS": "basic_water_access",
    "SH.STA.BRTC.ZS": "births_attended_skilled",
    "SH.DYN.MORT": "child_mortality_under5",
    "SH.IMM.MEAS": "measles_immunization_pct",
    "SH.XPD.CHEX.GD.ZS": "health_expenditure_gdp_pct",
    "SH.MED.PHYS.ZS": "physicians_per_1000",
    "SH.MED.BEDS.ZS": "hospital_beds_per_1000",
    
    # Education
    "SE.ADT.LITR.ZS": "literacy_rate",
    "SE.PRM.ENRR": "primary_enrollment",
    "SE.SEC.ENRR": "secondary_enrollment",
    "SE.TER.ENRR": "tertiary_enrollment",
    "SE.XPD.TOTL.GD.ZS": "education_expenditure_gdp_pct",
    
    # Energy & Environment
    "EG.FEC.RNEW.ZS": "renewable_energy_pct",
    "EG.USE.PCAP.KG.OE": "energy_use_per_capita",
    "EN.ATM.CO2E.PC": "co2_emissions_per_capita",
    "EG.ELC.ACCS.ZS": "electricity_access_pct",
    
    # Migration
    "SM.POP.NETM": "net_migration",
}

# Extended indicators (separate fetch to avoid rate limits)
EXTENDED_INDICATORS = {
    # Population details
    "SP.POP.TOTL.FE.IN": "female_population",
    "SP.POP.TOTL.MA.IN": "male_population",
    "SP.URB.TOTL": "urban_population",
    "SP.RUR.TOTL": "rural_population",
    
    # Mortality
    "SP.DYN.AMRT.MA": "adult_mortality_male",
    "SP.DYN.AMRT.FE": "adult_mortality_female",
    "SP.DYN.IMRT.IN": "infant_mortality",
    
    # Economy
    "NE.CON.TOTL.ZS": "consumption_gdp_pct",
    "NE.EXP.GNFS.ZS": "exports_gdp_pct",
    "NE.IMP.GNFS.ZS": "imports_gdp_pct",
    "NE.GDI.TOTL.ZS": "gross_capital_formation_gdp_pct",
    "GC.XPN.TOTL.GD.ZS": "govt_expenditure_gdp_pct",
    
    # Health
    "SH.XPD.CHEX.PC.CD": "health_expenditure_per_capita",
    "SH.IMM.IDPT": "dpt_immunization_pct",
    "SH.DYN.NMRT": "neonatal_mortality",
    
    # Education
    "SE.XPD.TOTL.GB.ZS": "education_expenditure_govt_pct",
    
    # Water & Sanitation
    "SH.STA.BASW.ZS": "basic_sanitation_access_pct",
    "ER.H2O.INTR.PC": "internal_freshwater_per_capita",
}

# Realistic browser headers to avoid detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Retry configuration
MAX_RETRIES = 5
BASE_DELAY = 1.0
MAX_DELAY = 60.0
BACKOFF_FACTOR = 2.0

# ============================================================
# WHO GLOBAL HEALTH OBSERVATORY
# ============================================================
WHO_API_BASE = "https://ghoapi.azureedge.net/api"
WHO_INDICATORS = {
    "WHOSIS_000001": "who_life_expectancy",
    "WHOSIS_000003": "who_neonatal_mortality",
    "MDG_0000000001": "who_infant_mortality",
    "NCD_BMI_30A": "who_obesity_rate",
    "HWF_0001": "who_physicians_per_10k",
    "HWF_0002": "who_nurses_per_10k",
    "WHS6_102": "who_ncd_mortality",
    "WHS4_544": "who_tobacco_use",
    "WHS3_49": "who_skilled_birth_attendant",
    "MDG_0000000007": "who_hiv_prevalence",
}

# ============================================================
# UNESCO INSTITUTE FOR STATISTICS
# ============================================================
UNESCO_API_BASE = "https://data.uis.unesco.org/ws/rs/sdmx/data/UNESCO,EDUCATION_NERA_GL,1.0"
UNESCO_INDICATORS = {
    "SE.ENR.PRSC.FM.ZS": "unesco_gender_parity_primary",
    "SE.SEC.ENRR.FE": "unesco_secondary_enrollment_female",
    "SE.TER.ENRR.MA": "unesco_tertiary_enrollment_male",
}

# ============================================================
# IMF DATA (disabled - API unreliable)
# ============================================================
# IMF_API_BASE = "https://www.imf.org/external/datamapper/api/v1"
# IMF_INDICATORS = {
#     "NGDPD": "imf_gdp_nominal",
#     "PCPIPCH": "imf_inflation",
# }


# ============================================================
# FETCH FUNCTIONS
# ============================================================

import random

def calculate_backoff(attempt):
    """Calculate backoff delay with jitter."""
    delay = min(BASE_DELAY * (BACKOFF_FACTOR ** attempt), MAX_DELAY)
    jitter = delay * 0.5 * random.random()  # Add 0-50% jitter
    return delay + jitter

def should_retry(status_code, attempt):
    """Determine if we should retry based on status code and attempt."""
    if attempt >= MAX_RETRIES - 1:
        return False
    # Retry on rate limit or server errors
    if status_code in (429, 500, 502, 503, 504):
        return True
    return False

def fetch_indicator(indicator_code, country=WB_COUNTRY, start_year=1960, end_year=None, session=None):
    """Fetch a single indicator from World Bank API with graceful backoff."""
    if end_year is None:
        end_year = datetime.now().year
    
    url = f"{WB_API_BASE}/country/{country}/indicator/{indicator_code}"
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 500,
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            # Use session for connection pooling if provided
            requester = session or requests
            resp = requester.get(url, params=params, headers=HEADERS, timeout=30)
            
            # Handle rate limiting with retry-after header
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", calculate_backoff(attempt)))
                time.sleep(retry_after)
                continue
            
            # Handle server errors with backoff
            if resp.status_code >= 500:
                if should_retry(resp.status_code, attempt):
                    delay = calculate_backoff(attempt)
                    time.sleep(delay)
                    continue
                else:
                    return pd.DataFrame(columns=["year", "value"])
            
            resp.raise_for_status()
            data = resp.json()
            
            if len(data) > 1 and data[1]:
                records = []
                for item in data[1]:
                    if item["value"] is not None:
                        records.append({
                            "year": int(item["date"]),
                            "value": item["value"],
                        })
                return pd.DataFrame(records)
            return pd.DataFrame(columns=["year", "value"])
            
        except requests.exceptions.SSLError:
            delay = calculate_backoff(attempt)
            time.sleep(delay)
        except requests.exceptions.ConnectionError:
            delay = calculate_backoff(attempt)
            time.sleep(delay)
        except requests.exceptions.Timeout:
            delay = calculate_backoff(attempt)
            time.sleep(delay)
        except Exception as e:
            print(f"    Error: {e}")
            return pd.DataFrame(columns=["year", "value"])
    
    return pd.DataFrame(columns=["year", "value"])


def fetch_who_indicator(indicator_code, country="IRN", session=None):
    """Fetch a single indicator from WHO GHO API."""
    url = f"{WHO_API_BASE}/{indicator_code}"
    params = {"$filter": f"SpatialDim eq '{country}'"}
    
    for attempt in range(MAX_RETRIES):
        try:
            requester = session or requests
            resp = requester.get(url, params=params, headers=HEADERS, timeout=30)
            
            if resp.status_code == 429:
                time.sleep(calculate_backoff(attempt))
                continue
            if resp.status_code >= 500:
                if should_retry(resp.status_code, attempt):
                    time.sleep(calculate_backoff(attempt))
                    continue
                return pd.DataFrame(columns=["year", "value"])
            
            resp.raise_for_status()
            data = resp.json()
            
            if "value" in data and data["value"]:
                records = []
                for item in data["value"]:
                    if "NumericValue" in item and item["NumericValue"] is not None:
                        records.append({
                            "year": int(item["TimeDim"]),
                            "value": float(item["NumericValue"]),
                        })
                if records:
                    df = pd.DataFrame(records)
                    # Aggregate by year (take mean if multiple values per year)
                    df = df.groupby("year")["value"].mean().reset_index()
                    return df
            return pd.DataFrame(columns=["year", "value"])
            
        except Exception as e:
            print(f"    WHO Error: {e}")
            return pd.DataFrame(columns=["year", "value"])
    
    return pd.DataFrame(columns=["year", "value"])


def fetch_imf_indicator(indicator_code, session=None):
    """Fetch a single indicator from IMF Data API."""
    url = f"{IMF_API_BASE}/{indicator_code}/IRN"
    
    for attempt in range(MAX_RETRIES):
        try:
            requester = session or requests
            resp = requester.get(url, headers=HEADERS, timeout=30)
            
            if resp.status_code == 429:
                time.sleep(calculate_backoff(attempt))
                continue
            if resp.status_code >= 500:
                if should_retry(resp.status_code, attempt):
                    time.sleep(calculate_backoff(attempt))
                    continue
                return pd.DataFrame(columns=["year", "value"])
            
            resp.raise_for_status()
            data = resp.json()
            
            if "values" in data:
                records = []
                for year, value in data["values"].items():
                    if value is not None:
                        try:
                            records.append({
                                "year": int(year),
                                "value": float(value),
                            })
                        except (ValueError, TypeError):
                            pass
                return pd.DataFrame(records) if records else pd.DataFrame(columns=["year", "value"])
            return pd.DataFrame(columns=["year", "value"])
            
        except Exception as e:
            print(f"    IMF Error: {e}")
            return pd.DataFrame(columns=["year", "value"])
    
    return pd.DataFrame(columns=["year", "value"])


def fetch_all_indicators(indicators, label="indicators"):
    """Fetch multiple indicators and return as combined DataFrame."""
    print(f"\nFetching {label}...")
    
    frames = []
    # Use session for connection pooling
    with requests.Session() as session:
        session.headers.update(HEADERS)
        
        for code, name in indicators.items():
            print(f"  {name} ({code})", end="...")
            df = fetch_indicator(code, session=session)
            
            if not df.empty:
                df = df.rename(columns={"value": name})
                frames.append(df)
                print(f" OK ({len(df)} years)")
            else:
                print(" no data")
            
            # Randomized delay to avoid detection patterns
            delay = 0.5 + random.random() * 1.0  # 0.5-1.5 seconds
            time.sleep(delay)
    
    if not frames:
        return pd.DataFrame()
    
    # Merge all on year
    merged = frames[0]
    for df in frames[1:]:
        merged = merged.merge(df, on="year", how="outer")
    
    return merged.sort_values("year").reset_index(drop=True)


def fetch_all(output_dir):
    """Fetch all data and save to raw directory."""
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    print("=" * 60)
    print("IRANIAN HOUSEHOLD DATA SCRAPER")
    print("=" * 60)
    print(f"Output directory: {output_dir}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Fetch World Bank main indicators
    main_df = fetch_all_indicators(INDICATORS, "World Bank main indicators")
    if not main_df.empty:
        path = os.path.join(raw_dir, "wb_main_indicators.csv")
        main_df.to_csv(path, index=False)
        print(f"\nSaved WB main indicators: {path}")
    
    # Longer pause between batches
    time.sleep(3 + random.random() * 2)
    
    # Fetch World Bank extended indicators
    ext_df = fetch_all_indicators(EXTENDED_INDICATORS, "World Bank extended indicators")
    if not ext_df.empty:
        path = os.path.join(raw_dir, "wb_extended_indicators.csv")
        ext_df.to_csv(path, index=False)
        print(f"\nSaved WB extended indicators: {path}")
    
    time.sleep(3 + random.random() * 2)
    
    # Fetch WHO indicators
    print("\nFetching WHO Global Health Observatory...")
    who_frames = []
    with requests.Session() as session:
        session.headers.update(HEADERS)
        for code, name in WHO_INDICATORS.items():
            print(f"  {name} ({code})", end="...")
            df = fetch_who_indicator(code, session=session)
            if not df.empty:
                df = df.rename(columns={"value": name})
                who_frames.append(df)
                print(f" OK ({len(df)} years)")
            else:
                print(" no data")
            time.sleep(0.5 + random.random() * 0.5)
    
    who_df = pd.DataFrame()
    if who_frames:
        who_df = who_frames[0]
        for df in who_frames[1:]:
            who_df = who_df.merge(df, on="year", how="outer")
        path = os.path.join(raw_dir, "who_indicators.csv")
        who_df.to_csv(path, index=False)
        print(f"\nSaved WHO indicators: {path}")
    
    # Save fetch metadata
    metadata = {
        "fetched_at": datetime.now().isoformat(),
        "country": WB_COUNTRY,
        "sources": {
            "world_bank": {"main": len(main_df), "extended": len(ext_df)},
            "who": len(who_df) if not who_df.empty else 0,
        },
    }
    with open(os.path.join(raw_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "=" * 60)
    print("FETCH COMPLETE!")
    print("=" * 60)
    return main_df, ext_df, who_df


# ============================================================
# PROCESS FUNCTIONS
# ============================================================

def process_data(output_dir):
    """Process raw data into final outputs."""
    raw_dir = os.path.join(output_dir, "raw")
    processed_dir = os.path.join(output_dir, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("PROCESSING DATA")
    print("=" * 60)
    
    # Load all raw data sources
    sources = {}
    source_files = {
        "wb_main": "wb_main_indicators.csv",
        "wb_extended": "wb_extended_indicators.csv",
        "who": "who_indicators.csv",
    }
    
    for name, filename in source_files.items():
        path = os.path.join(raw_dir, filename)
        if os.path.exists(path):
            df = pd.read_csv(path)
            sources[name] = df
            print(f"Loaded {name}: {len(df)} rows x {len(df.columns)} cols")
    
    if not sources:
        print("Error: No raw data found. Run fetch first.")
        return None
    
    # Start with World Bank main indicators
    combined = sources.get("wb_main", pd.DataFrame())
    
    # Merge extended World Bank indicators
    if "wb_extended" in sources:
        ext_df = sources["wb_extended"]
        for col in ext_df.columns:
            if col != "year" and col in combined.columns:
                ext_df = ext_df.rename(columns={col: f"{col}_ext"})
        combined = combined.merge(ext_df, on="year", how="outer")
    
    # Merge WHO indicators
    if "who" in sources:
        who_df = sources["who"]
        for col in who_df.columns:
            if col != "year" and col in combined.columns:
                who_df = who_df.rename(columns={col: f"{col}_who"})
        combined = combined.merge(who_df, on="year", how="outer")
    
    # Remove duplicates and sort
    combined = combined.loc[:, ~combined.columns.duplicated()]
    combined = combined.sort_values("year").reset_index(drop=True)
    
    # Rename for clarity
    rename_map = {
        "age_0_14_pct": "youth_population_pct",
        "age_15_64_pct": "working_age_population_pct",
        "age_65_plus_pct": "elderly_population_pct",
    }
    combined = combined.rename(columns=rename_map)
    
    print(f"\nCombined: {len(combined)} rows x {len(combined.columns)} cols")
    
    # Save outputs
    # CSV
    csv_path = os.path.join(processed_dir, "iran_household_data.csv")
    combined.to_csv(csv_path, index=False)
    print(f"Saved CSV: {csv_path}")
    
    # Excel
    xlsx_path = os.path.join(processed_dir, "iran_household_data.xlsx")
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        combined.to_excel(writer, sheet_name="data", index=False)
        
        # Data dictionary
        dict_data = []
        for col in combined.columns:
            dict_data.append({
                "column": col,
                "dtype": str(combined[col].dtype),
                "non_null_pct": round(combined[col].notna().mean() * 100, 1),
            })
        pd.DataFrame(dict_data).to_excel(writer, sheet_name="dictionary", index=False)
        
        # Summary stats
        numeric = combined.select_dtypes(include=['number'])
        if not numeric.empty:
            numeric.describe().round(4).to_excel(writer, sheet_name="statistics")
    print(f"Saved Excel: {xlsx_path}")
    
    # SQL
    sql_path = os.path.join(processed_dir, "iran_household_data.sql")
    generate_sql(combined, sql_path)
    print(f"Saved SQL: {sql_path}")
    
    return combined


def generate_sql(df, output_path, table_name="iranian_household"):
    """Generate SQL CREATE + INSERT statements."""
    type_map = {
        "int64": "INTEGER",
        "float64": "DECIMAL(12,4)",
        "object": "TEXT",
    }
    
    # Get unique columns
    seen = set()
    cols = []
    for col in df.columns:
        if col not in seen:
            seen.add(col)
            cols.append(col)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"-- Iranian Household Data\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write(f"-- Source: World Bank DataBank\n\n")
        
        # CREATE TABLE
        col_defs = []
        for col in cols:
            dtype = str(df[col].dtype)
            sql_type = type_map.get(dtype, "TEXT")
            nullable = "NULL" if df[col].isna().any() else "NOT NULL"
            col_defs.append(f"    {col} {sql_type} {nullable}")
        
        f.write(f"CREATE TABLE {table_name} (\n")
        f.write("    id INTEGER PRIMARY KEY AUTOINCREMENT,\n")
        f.write(",\n".join(col_defs))
        f.write("\n);\n\n")
        
        # INSERT statements
        for _, row in df.iterrows():
            values = []
            for col in cols:
                val = row[col]
                if pd.isna(val):
                    values.append("NULL")
                elif isinstance(val, str):
                    values.append(f"'{val.replace(chr(39), chr(39)*2)}'")
                else:
                    values.append(str(val))
            
            f.write(f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(values)});\n")


# ============================================================
# VALIDATE FUNCTION
# ============================================================

def validate_data(output_dir):
    """Validate processed data quality."""
    processed_dir = os.path.join(output_dir, "processed")
    csv_path = os.path.join(processed_dir, "iran_household_data.csv")
    
    if not os.path.exists(csv_path):
        print("Error: No processed data found. Run process first.")
        return
    
    print("\n" + "=" * 60)
    print("VALIDATING DATA")
    print("=" * 60)
    
    df = pd.read_csv(csv_path)
    print(f"Dataset: {len(df)} rows x {len(df.columns)} columns")
    
    # Checks
    issues = []
    warnings = []
    
    # Year range
    min_year = df["year"].min()
    max_year = df["year"].max()
    print(f"Year range: {min_year} - {max_year}")
    
    if df["year"].duplicated().any():
        issues.append("Duplicate year entries found")
    
    # Completeness
    print("\nColumn completeness:")
    for col in df.columns:
        pct = df[col].notna().mean() * 100
        status = "OK" if pct > 80 else "LOW" if pct > 50 else "VERY LOW"
        print(f"  {col}: {pct:.1f}% [{status}]")
        if pct < 50:
            warnings.append(f"{col} has {pct:.1f}% completeness")
    
    # Report
    print("\n" + "-" * 40)
    if issues:
        print("ISSUES:")
        for i in issues:
            print(f"  - {i}")
    else:
        print("No critical issues found!")
    
    if warnings:
        print(f"\n{len(warnings)} columns with low completeness")
    
    # Save report
    report_path = os.path.join(output_dir, "summary", "validation_report.txt")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        f.write(f"Validation Report\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Rows: {len(df)}, Columns: {len(df.columns)}\n")
        f.write(f"Year Range: {min_year} - {max_year}\n\n")
        f.write(f"Issues: {len(issues)}\n")
        f.write(f"Warnings: {len(warnings)}\n")
    print(f"\nReport saved: {report_path}")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Iranian Household Data Scraper")
    parser.add_argument("--fetch-only", action="store_true", help="Only fetch data")
    parser.add_argument("--process-only", action="store_true", help="Only process data")
    parser.add_argument("--validate-only", action="store_true", help="Only validate data")
    parser.add_argument("--output-dir", default="data", help="Output directory (default: data)")
    args = parser.parse_args()
    
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Run requested actions
    if args.fetch_only:
        fetch_all(output_dir)
    elif args.process_only:
        process_data(output_dir)
    elif args.validate_only:
        validate_data(output_dir)
    else:
        # Full pipeline
        fetch_all(output_dir)
        process_data(output_dir)
        validate_data(output_dir)
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
