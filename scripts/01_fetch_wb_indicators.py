"""
Fetch Iranian household-related indicators from World Bank DataBank API.
Covers: demographics, income, expenditure, housing, education, health, energy, migration.
"""

import requests
import pandas as pd
import json
import os
import time

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# Key indicators for Iranian household analysis
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
    
    # Income & Economy
    "NY.GDP.PCAP.CD": "gdp_per_capita_usd",
    "NY.GDP.PCAP.PP.CD": "gdp_per_capita_ppp",
    "SI.POV.DDAY": "poverty_headcount_215",
    "SI.POV.NAHC": "poverty_national",
    "NY.GNI.PCAP.CD": "gni_per_capita",
    "SL.UEM.TOTL.ZS": "unemployment_rate",
    "SL.TLF.CACT.ZS": "labor_force_participation",
    
    # Housing & Living Standards
    "EN.ELEC.ACCS.ZS": "electricity_access_pct",
    "SH.H2O.BASW.ZS": "basic_water_access",
    "SH.STA.BRTC.ZS": "births_attended_skilled",
    
    # Education
    "SE.ADT.LITR.ZS": "literacy_rate",
    "SE.PRM.ENRR": "primary_enrollment",
    "SE.SEC.ENRR": "secondary_enrollment",
    "SE.TER.ENRR": "tertiary_enrollment",
    "SE.XPD.TOTL.GD.ZS": "education_expenditure_gdp_pct",
    
    # Health
    "SH.XPD.CHEX.GD.ZS": "health_expenditure_gdp_pct",
    "SH.MED.PHYS.ZS": "physicians_per_1000",
    "SH.MED.BEDS.ZS": "hospital_beds_per_1000",
    "SH.DYN.MORT": "child_mortality_under5",
    "SH.IMM.MEAS": "measles_immunization_pct",
    
    # Energy
    "EG.FEC.RNEW.ZS": "renewable_energy_pct",
    "EG.USE.PCAP.KG.OE": "energy_use_per_capita",
    "EN.ATM.CO2E.PC": "co2_emissions_per_capita",
    "EG.ELC.ACCS.ZS": "electricity_access_pct2",
    
    # Migration & Urbanization
    "SM.POP.NETM": "net_migration",
    "EN.URB.MCTY.TL.ZS": "population_in_large_cities_pct",
    
    # Household specific (where available)
    "SP.HOU.FENS.ZS": "female_headed_households_pct",
}

COUNTRY = "IRN"  # Iran, Islamic Rep.
BASE_URL = "https://api.worldbank.org/v2"

def fetch_indicator(indicator_code, country=COUNTRY, start_year=1960, end_year=2024):
    """Fetch a single indicator for Iran."""
    url = f"{BASE_URL}/country/{country}/indicator/{indicator_code}"
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 500,
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if len(data) > 1 and data[1]:
            records = []
            for item in data[1]:
                records.append({
                    "year": int(item["date"]),
                    "value": item["value"],
                    "indicator_code": indicator_code,
                })
            return records
        return []
    except Exception as e:
        print(f"  Error fetching {indicator_code}: {e}")
        return []

def main():
    print("=" * 60)
    print("Fetching World Bank indicators for Iran")
    print("=" * 60)
    
    all_data = {}
    
    for code, name in INDICATORS.items():
        print(f"  Fetching: {name} ({code})")
        records = fetch_indicator(code)
        all_data[name] = records
        print(f"    Got {len(records)} data points")
        time.sleep(0.3)  # Be nice to the API
    
    # Convert to DataFrames and save
    frames = []
    for name, records in all_data.items():
        if records:
            df = pd.DataFrame(records)
            df = df.rename(columns={"value": name})
            df["year"] = df["year"].astype(int)
            frames.append(df[["year", name]].dropna(subset=[name]))
    
    if frames:
        # Merge all indicators on year
        merged = frames[0]
        for df in frames[1:]:
            merged = merged.merge(df, on="year", how="outer")
        
        merged = merged.sort_values("year").reset_index(drop=True)
        
        # Save raw data
        csv_path = os.path.join(RAW_DIR, "wb_indicators_iran.csv")
        merged.to_csv(csv_path, index=False)
        print(f"\nSaved {len(merged)} rows x {len(merged.columns)} columns to {csv_path}")
        
        # Also save a summary
        summary_path = os.path.join(RAW_DIR, "wb_indicators_summary.json")
        summary = {}
        for col in merged.columns:
            if col != "year":
                non_null = merged[col].dropna()
                if len(non_null) > 0:
                    summary[col] = {
                        "min_year": int(non_null.index.min()),
                        "max_year": int(non_null.index.max()),
                        "count": len(non_null),
                        "latest_value": float(non_null.iloc[-1]),
                    }
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Summary saved to {summary_path}")
    else:
        print("\nNo data fetched!")

if __name__ == "__main__":
    main()
