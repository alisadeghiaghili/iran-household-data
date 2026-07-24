"""
Attempt to fetch data from Statistical Center of Iran (SCI) - amar.org.ir.
Downloads available tables, reports, and summary statistics.
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import json
import time
import re

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

SCI_BASE = "https://www.amar.org.ir"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
}

# Known SCI data endpoints and pages
SCI_PAGES = {
    "english_index": "/english/",
    "population_census": "/english/Population-and-Housing-Censuses",
    "household_expenditure": "/english/Statistical-Household-Survey-Iran",
    "labor_force": "/english/Results-of-Labor-Force-Survey",
    "statistical_tables": "/english/Statistical-Tables",
}

def try_fetch_page(url, timeout=30):
    """Try to fetch a page from SCI."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp
    except Exception as e:
        return None

def extract_links_from_page(html_content, base_url):
    """Extract relevant links from an SCI page."""
    soup = BeautifulSoup(html_content, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        # Look for data-related links
        if any(keyword in href.lower() or keyword in text.lower() 
               for keyword in ["excel", "download", "pdf", "statist", "household", 
                               "population", "census", "survey", "data", "table"]):
            if not href.startswith("http"):
                href = base_url + href
            links.append({"text": text, "url": href})
    return links

def try_fetch_population_data():
    """Try to get population/demographic summary data."""
    print("\n--- Attempting Population Data ---")
    
    # Try World Bank detailed population data as fallback
    indicators = {
        "SP.POP.TOTL.FE.IN": "female_population",
        "SP.POP.TOTL.MA.IN": "male_population",
        "SP.POP.TOTL": "total_population",
        "SP.URB.TOTL": "urban_population",
        "SP.RUR.TOTL": "rural_population",
    }
    
    all_records = []
    for code, name in indicators.items():
        url = f"https://api.worldbank.org/v2/country/IRN/indicator/{code}"
        params = {"format": "json", "date": "1960:2024", "per_page": 500}
        try:
            resp = requests.get(url, params=params, timeout=30)
            data = resp.json()
            if len(data) > 1 and data[1]:
                for item in data[1]:
                    if item["value"] is not None:
                        all_records.append({
                            "year": int(item["date"]),
                            "indicator": name,
                            "value": item["value"],
                        })
        except:
            pass
        time.sleep(0.2)
    
    if all_records:
        df = pd.DataFrame(all_records)
        pivot = df.pivot(index="year", columns="indicator", values="value")
        pivot = pivot.sort_index()
        return pivot
    return None

def try_fetch_expenditure_data():
    """Try to get expenditure/consumption data from World Bank."""
    print("\n--- Attempting Expenditure Data ---")
    
    indicators = {
        "NE.CON.TOTL.CD": "consumption_total_usd",
        "NE.CON.TOTL.ZS": "consumption_gdp_pct",
        "NE.EXP.GNFS.ZS": "exports_gdp_pct",
        "NE.IMP.GNFS.ZS": "imports_gdp_pct",
        "NE.GDI.TOTL.ZS": "gross_capital_formation_gdp_pct",
        "GC.XPN.TOTL.GD.ZS": "govt_expenditure_gdp_pct",
        "SP.DYN.IMRT.IN": "infant_mortality",
        "SP.DYN.AMRT.MA": "adult_mortality_male",
        "SP.DYN.AMRT.FE": "adult_mortality_female",
        "SH.XPD.CHEX.PC.CD": "health_expenditure_per_capita",
        "SE.XPD.TOTL.GB.ZS": "education_expenditure_govt_pct",
    }
    
    all_records = []
    for code, name in indicators.items():
        url = f"https://api.worldbank.org/v2/country/IRN/indicator/{code}"
        params = {"format": "json", "date": "1960:2024", "per_page": 500}
        try:
            resp = requests.get(url, params=params, timeout=30)
            data = resp.json()
            if len(data) > 1 and data[1]:
                for item in data[1]:
                    if item["value"] is not None:
                        all_records.append({
                            "year": int(item["date"]),
                            "indicator": name,
                            "value": item["value"],
                        })
        except:
            pass
        time.sleep(0.2)
    
    if all_records:
        df = pd.DataFrame(all_records)
        pivot = df.pivot(index="year", columns="indicator", values="value")
        pivot = pivot.sort_index()
        return pivot
    return None

def try_fetch_housing_data():
    """Try to get housing and living standards data."""
    print("\n--- Attempting Housing Data ---")
    
    indicators = {
        "EN.ELEC.ACCS.ZS": "electricity_access_pct",
        "SH.H2O.BASW.ZS": "basic_water_access_pct",
        "SH.STA.BASW.ZS": "basic_sanitation_access_pct",
        "EG.FEC.RNEW.ZS": "renewable_energy_consumption_pct",
        "EN.ATM.CO2E.PC": "co2_emissions_per_capita",
        "EG.USE.PCAP.KG.OE": "energy_use_per_capita",
        "ER.H2O.INTR.PC": "internal_freshwater_per_capita",
        "AG.LND.ARBL.ZS": "arable_land_pct",
    }
    
    all_records = []
    for code, name in indicators.items():
        url = f"https://api.worldbank.org/v2/country/IRN/indicator/{code}"
        params = {"format": "json", "date": "1960:2024", "per_page": 500}
        try:
            resp = requests.get(url, params=params, timeout=30)
            data = resp.json()
            if len(data) > 1 and data[1]:
                for item in data[1]:
                    if item["value"] is not None:
                        all_records.append({
                            "year": int(item["date"]),
                            "indicator": name,
                            "value": item["value"],
                        })
        except:
            pass
        time.sleep(0.2)
    
    if all_records:
        df = pd.DataFrame(all_records)
        pivot = df.pivot(index="year", columns="indicator", values="value")
        pivot = pivot.sort_index()
        return pivot
    return None

def try_fetch_education_health_data():
    """Try to get education and health indicators."""
    print("\n--- Attempting Education & Health Data ---")
    
    indicators = {
        "SE.ADT.LITR.ZS": "adult_literacy_rate",
        "SE.ADT.LITR.MA.ZS": "male_literacy_rate",
        "SE.ADT.LITR.FE.ZS": "female_literacy_rate",
        "SE.PRM.ENRR": "primary_enrollment_pct",
        "SE.SEC.ENRR": "secondary_enrollment_pct",
        "SE.TER.ENRR": "tertiary_enrollment_pct",
        "SH.DYN.MORT": "under5_mortality_rate",
        "SH.DYN.NMRT": "neonatal_mortality_rate",
        "SH.MED.BEDS.ZS": "hospital_beds_per_1000",
        "SH.MED.PHYS.ZS": "physicians_per_1000",
        "SP.DYN.LE00.IN": "life_expectancy_at_birth",
        "SP.DYN.AMRT.IN": "adult_mortality_rate",
        "SH.IMM.MEAS": "measles_immunization_pct",
        "SH.IMM.IDPT": "dpt_immunization_pct",
        "SP.DYN.CONU.ZS": "contraceptive_prevalence_pct",
    }
    
    all_records = []
    for code, name in indicators.items():
        url = f"https://api.worldbank.org/v2/country/IRN/indicator/{code}"
        params = {"format": "json", "date": "1960:2024", "per_page": 500}
        try:
            resp = requests.get(url, params=params, timeout=30)
            data = resp.json()
            if len(data) > 1 and data[1]:
                for item in data[1]:
                    if item["value"] is not None:
                        all_records.append({
                            "year": int(item["date"]),
                            "indicator": name,
                            "value": item["value"],
                        })
        except:
            pass
        time.sleep(0.2)
    
    if all_records:
        df = pd.DataFrame(all_records)
        pivot = df.pivot(index="year", columns="indicator", values="value")
        pivot = pivot.sort_index()
        return pivot
    return None

def main():
    print("=" * 60)
    print("Fetching Iranian Household Data (Extended Indicators)")
    print("=" * 60)
    
    # Try to access SCI website
    print("\nAttempting to access SCI website...")
    resp = try_fetch_page(SCI_BASE)
    if resp:
        print(f"  SCI accessible: {resp.status_code}")
        links = extract_links_from_page(resp.text, SCI_BASE)
        if links:
            print(f"  Found {len(links)} relevant links")
            # Save links for reference
            with open(os.path.join(RAW_DIR, "sci_links.json"), "w") as f:
                json.dump(links, f, indent=2)
    else:
        print("  SCI not accessible from this network (expected - will use World Bank as primary)")
    
    # Fetch comprehensive data from World Bank
    datasets = {}
    
    pop_data = try_fetch_population_data()
    if pop_data is not None:
        datasets["population"] = pop_data
    
    exp_data = try_fetch_expenditure_data()
    if exp_data is not None:
        datasets["expenditure"] = exp_data
    
    housing_data = try_fetch_housing_data()
    if housing_data is not None:
        datasets["housing"] = housing_data
    
    edu_health_data = try_fetch_education_health_data()
    if edu_health_data is not None:
        datasets["education_health"] = edu_health_data
    
    # Save individual datasets
    for name, df in datasets.items():
        path = os.path.join(RAW_DIR, f"wb_{name}_iran.csv")
        df.to_csv(path)
        print(f"\nSaved {name}: {len(df)} years x {len(df.columns)} indicators")
    
    print(f"\nAll raw data saved to {RAW_DIR}")

if __name__ == "__main__":
    main()
