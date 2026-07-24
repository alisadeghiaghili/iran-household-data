"""
Process and combine all raw Iranian household data into unified datasets.
Outputs: CSV, Excel, and SQL.
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

def load_csv(filename):
    """Load a CSV file from raw directory."""
    path = os.path.join(RAW_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

def create_data_dictionary(df):
    """Create a data dictionary describing all columns."""
    dictionary = []
    seen_cols = set()
    for col in df.columns:
        # Skip duplicate columns
        if col in seen_cols:
            continue
        seen_cols.add(col)
        
        try:
            # Handle potential duplicate column names
            if list(df.columns).count(col) > 1:
                # Get the first occurrence
                col_data = df[col].iloc[:, 0] if hasattr(df[col], 'columns') else df[col]
            else:
                col_data = df[col]
            
            dtype = str(col_data.dtype)
            non_null = col_data.notna().sum()
            total = len(df)
            description = get_column_description(col)
            dictionary.append({
                "column": col,
                "dtype": dtype,
                "non_null_count": int(non_null),
                "null_pct": round((1 - non_null / total) * 100, 2) if total > 0 else 0,
                "description": description,
            })
        except Exception as e:
            print(f"  Warning: Could not process column {col}: {e}")
    return pd.DataFrame(dictionary)

def get_column_description(col):
    """Get human-readable description for a column."""
    descriptions = {
        "year": "Calendar year",
        "province": "Iranian province name",
        "province_code": "Province code (ISO 3166-2:IR)",
        "urban_rural": "Urban or Rural area",
        "household_size": "Number of people in household",
        "head_age": "Age of household head (years)",
        "head_gender": "Gender of household head (M/F)",
        "total_income": "Total household income (IRR/month)",
        "income_per_capita": "Income per household member (IRR/month)",
        "total_expenditure": "Total household expenditure (IRR/month)",
        "expenditure_per_capita": "Expenditure per household member (IRR/month)",
        "food_expenditure": "Food & beverage expenditure",
        "housing_expenditure": "Housing & utilities expenditure",
        "health_expenditure": "Healthcare expenditure",
        "education_expenditure": "Education expenditure",
        "transport_expenditure": "Transportation expenditure",
        "clothing_expenditure": "Clothing expenditure",
        "recreation_expenditure": "Recreation & culture expenditure",
        "housing_type": "Type of dwelling (apartment, house, etc.)",
        "housing_area": "Floor area of dwelling (sq meters)",
        "rooms_count": "Number of rooms",
        "ownership": "Ownership status (owned, rented, etc.)",
        "education_level": "Head's education level",
        "literacy": "Head's literacy status",
        "employment_status": "Head's employment status",
        "health_insurance": "Has health insurance coverage",
        "water_source": "Primary water source",
        "sanitation_type": "Sanitation facility type",
        "cooking_fuel": "Primary cooking fuel",
        "heating_fuel": "Primary heating fuel",
        "has_electricity": "Has electricity connection",
        "has_gas": "Has piped gas connection",
        "has_telephone": "Has telephone/phone",
        "has_internet": "Has internet access",
        "has_car": "Owns a motor vehicle",
        "has_washing_machine": "Owns a washing machine",
        "has_refrigerator": "Owns a refrigerator",
        "has_television": "Owns a television",
        "poverty_status": "Below poverty line (Yes/No)",
        "dependency_ratio": "Non-working members / working members",
        "fertility_rate": "Total fertility rate (births per woman)",
        "life_expectancy": "Life expectancy at birth (years)",
        "gdp_per_capita_usd": "GDP per capita (current USD)",
        "gdp_per_capita_ppp": "GDP per capita (PPP, current international $)",
        "urban_population_pct": "Population living in urban areas (%)",
        "poverty_headcount_215": "Poverty headcount at $2.15/day (%)",
        "poverty_national": "National poverty headcount (%)",
        "unemployment_rate": "Unemployment rate (%)",
        "labor_force_participation": "Labor force participation rate (%)",
        "literacy_rate": "Adult literacy rate (%)",
        "primary_enrollment": "Primary school enrollment (%)",
        "secondary_enrollment": "Secondary school enrollment (%)",
        "tertiary_enrollment": "Tertiary school enrollment (%)",
        "education_expenditure_gdp_pct": "Education expenditure (% of GDP)",
        "health_expenditure_gdp_pct": "Health expenditure (% of GDP)",
        "physicians_per_1000": "Physicians per 1,000 population",
        "hospital_beds_per_1000": "Hospital beds per 1,000 population",
        "child_mortality_under5": "Under-5 mortality rate (per 1,000 live births)",
        "renewable_energy_pct": "Renewable energy consumption (% of total)",
        "energy_use_per_capita": "Energy use per capita (kg oil equivalent)",
        "co2_emissions_per_capita": "CO2 emissions per capita (metric tons)",
        "net_migration": "Net migration (people)",
    }
    return descriptions.get(col, "")

def generate_sql_create_table(df, table_name="iranian_household"):
    """Generate SQL CREATE TABLE statement."""
    type_map = {
        "int64": "INTEGER",
        "float64": "DECIMAL(12,4)",
        "object": "VARCHAR(255)",
        "bool": "BOOLEAN",
    }
    
    columns = []
    seen_cols = set()
    for col in df.columns:
        if col in seen_cols:
            continue
        seen_cols.add(col)
        
        try:
            if list(df.columns).count(col) > 1:
                col_data = df[col].iloc[:, 0] if hasattr(df[col], 'columns') else df[col]
            else:
                col_data = df[col]
            
            dtype = str(col_data.dtype)
            sql_type = type_map.get(dtype, "TEXT")
            nullable = "NULL" if col_data.isna().any() else "NOT NULL"
            columns.append(f"    {col} {sql_type} {nullable}")
        except Exception as e:
            print(f"  Warning: Could not process column {col} for SQL: {e}")
    
    col_defs = ",\n".join(columns)
    return f"""CREATE TABLE {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
{col_defs}
);"""

def generate_sql_inserts(df, table_name="iranian_household", max_rows=1000):
    """Generate SQL INSERT statements."""
    # Get unique column names in order
    seen_cols = set()
    unique_cols = []
    for col in df.columns:
        if col not in seen_cols:
            seen_cols.add(col)
            unique_cols.append(col)
    
    sql_lines = []
    for idx, row in df.head(max_rows).iterrows():
        values = []
        for col in unique_cols:
            try:
                if list(df.columns).count(col) > 1:
                    val = row[col] if not isinstance(row[col], pd.Series) else row[col].iloc[0]
                else:
                    val = row[col]
                
                if pd.isna(val):
                    values.append("NULL")
                elif isinstance(val, str):
                    values.append(f"'{val.replace(chr(39), chr(39)+chr(39))}'")
                elif isinstance(val, bool):
                    values.append("TRUE" if val else "FALSE")
                else:
                    values.append(str(val))
            except:
                values.append("NULL")
        sql_lines.append(f"INSERT INTO {table_name} ({', '.join(unique_cols)}) VALUES ({', '.join(values)});")
    
    return "\n".join(sql_lines)

def main():
    print("=" * 60)
    print("Processing Iranian Household Data")
    print("=" * 60)
    
    # Load all raw datasets
    datasets = {}
    for name in ["population", "expenditure", "housing", "education_health"]:
        df = load_csv(f"wb_{name}_iran.csv")
        if df is not None:
            datasets[name] = df
            print(f"  Loaded {name}: {len(df)} rows x {len(df.columns)} cols")
    
    wb_main = load_csv("wb_indicators_iran.csv")
    if wb_main is not None:
        datasets["main"] = wb_main
        print(f"  Loaded main indicators: {len(wb_main)} rows x {len(wb_main.columns)} cols")
    
    # Merge all datasets on year
    print("\nMerging datasets...")
    
    # Start with main indicators
    if "main" in datasets:
        combined = datasets["main"].copy()
    else:
        combined = pd.DataFrame({"year": range(1960, 2025)})
    
    for name, df in datasets.items():
        if name == "main":
            continue
        # Ensure year column exists and is integer
        if "year" in df.columns:
            df["year"] = df["year"].astype(int)
            # Add suffix to avoid duplicate column names
            cols_to_rename = {col: f"{col}_{name}" for col in df.columns if col != "year" and col in combined.columns}
            if cols_to_rename:
                df = df.rename(columns=cols_to_rename)
            combined = combined.merge(df, on="year", how="outer")
    
    # Sort and clean
    combined = combined.sort_values("year").reset_index(drop=True)
    
    # Remove duplicate columns
    combined = combined.loc[:, ~combined.columns.duplicated()]
    
    # Rename columns for consistency
    column_renames = {
        "population_total": "total_population",
        "population_female_pct": "female_population_pct",
        "age_0_14_pct": "youth_population_pct",
        "age_15_64_pct": "working_age_population_pct",
        "age_65_plus_pct": "elderly_population_pct",
    }
    combined = combined.rename(columns=column_renames)
    
    print(f"  Combined dataset: {len(combined)} rows x {len(combined.columns)} cols")
    
    # Create household-level features (where possible)
    # Since we have aggregate data, we derive household-relevant features
    if "total_population" in combined.columns and "gdp_per_capita_usd" in combined.columns:
        try:
            combined["total_gdp_usd"] = combined["total_population"].astype(float) * combined["gdp_per_capita_usd"].astype(float)
        except Exception as e:
            print(f"  Warning: Could not calculate total GDP: {e}")
    
    # Save processed data
    print("\nSaving processed data...")
    
    # CSV
    csv_path = os.path.join(PROCESSED_DIR, "iran_household_all_years.csv")
    combined.to_csv(csv_path, index=False)
    print(f"  CSV: {csv_path}")
    
    # Excel
    xlsx_path = os.path.join(PROCESSED_DIR, "iran_household_all_years.xlsx")
    
    # Remove duplicate columns for cleaner output
    combined_clean = combined.loc[:, ~combined.columns.duplicated()]
    
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        combined_clean.to_excel(writer, sheet_name="data", index=False)
        
        # Add data dictionary sheet
        dict_df = create_data_dictionary(combined_clean)
        dict_df.to_excel(writer, sheet_name="data_dictionary", index=False)
        
        # Add summary statistics sheet (only numeric columns)
        numeric_cols = combined_clean.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary = combined_clean[numeric_cols].describe().round(4)
            summary.to_excel(writer, sheet_name="summary_statistics")
    print(f"  Excel: {xlsx_path}")
    
    # SQL
    sql_path = os.path.join(PROCESSED_DIR, "iran_household_all_years.sql")
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("-- Iranian Household Data - SQL Export\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write(f"-- Source: World Bank DataBank + SCI\n")
        f.write("-- Time Range: 1960-2024\n\n")
        
        # Create table
        f.write("-- Create table\n")
        f.write(generate_sql_create_table(combined))
        f.write("\n\n-- Insert data\n")
        
        # Insert data
        f.write(generate_sql_inserts(combined))
    print(f"  SQL: {sql_path}")
    
    # Data dictionary as markdown
    dict_df = create_data_dictionary(combined)
    md_path = os.path.join(PROCESSED_DIR, "data_dictionary.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Iranian Household Data Dictionary\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Rows:** {len(combined)}\n")
        f.write(f"**Total Columns:** {len(combined.columns)}\n")
        f.write(f"**Time Range:** {int(combined['year'].min())} - {int(combined['year'].max())}\n\n")
        f.write("## Column Definitions\n\n")
        f.write("| Column | Type | Non-Null % | Description |\n")
        f.write("|--------|------|-----------|-------------|\n")
        for _, row in dict_df.iterrows():
            non_null_pct = 100 - row["null_pct"]
            f.write(f"| `{row['column']}` | {row['dtype']} | {non_null_pct:.1f}% | {row['description']} |\n")
    print(f"  Data Dictionary: {md_path}")
    
    # Summary report
    summary_path = os.path.join(PROCESSED_DIR, "summary_report.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# Iranian Household Data - Summary Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Dataset Overview\n\n")
        f.write(f"- **Time Period:** {int(combined['year'].min())} - {int(combined['year'].max())}\n")
        f.write(f"- **Total Observations:** {len(combined)}\n")
        f.write(f"- **Variables:** {len(combined_clean.columns)}\n\n")
        f.write("## Key Statistics (Latest Available Year)\n\n")
        latest_year = int(combined["year"].max())
        latest = combined_clean[combined_clean["year"] == latest_year].iloc[0] if latest_year in combined_clean["year"].values else None
        if latest is not None:
            f.write(f"**Year {latest_year}:**\n\n")
            for col in combined_clean.columns:
                if col != "year":
                    try:
                        val = latest[col]
                        if pd.notna(val):
                            if isinstance(val, (int, float)):
                                f.write(f"- **{col}:** {val:,.2f}\n")
                            else:
                                f.write(f"- **{col}:** {val}\n")
                    except:
                        pass
        f.write("\n## Data Completeness\n\n")
        for col in combined_clean.columns:
            non_null = combined_clean[col].notna().sum()
            pct = non_null / len(combined_clean) * 100
            f.write(f"- `{col}`: {pct:.1f}% complete\n")
    print(f"  Summary Report: {summary_path}")
    
    print("\n" + "=" * 60)
    print("Processing Complete!")
    print("=" * 60)
    print(f"\nAll outputs saved to: {PROCESSED_DIR}")

if __name__ == "__main__":
    main()
