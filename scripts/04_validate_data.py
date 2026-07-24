"""
Validate the processed Iranian household data.
Checks data quality, completeness, and generates validation report.
"""

import pandas as pd
import numpy as np
import os

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
SUMMARY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "summary")
os.makedirs(SUMMARY_DIR, exist_ok=True)

def validate_dataset(df):
    """Run validation checks on the dataset."""
    issues = []
    warnings = []
    
    # Check 1: No duplicate years
    if df["year"].duplicated().any():
        issues.append("Found duplicate year entries")
    
    # Check 2: Year range is reasonable
    min_year = df["year"].min()
    max_year = df["year"].max()
    if min_year < 1950:
        warnings.append(f"Minimum year ({min_year}) seems too early")
    if max_year > 2025:
        warnings.append(f"Maximum year ({max_year}) is in the future")
    
    # Check 3: Check for extreme null percentages
    for col in df.columns:
        if col == "year":
            continue
        null_pct = df[col].isna().sum() / len(df) * 100
        if null_pct > 50:
            warnings.append(f"Column '{col}' has {null_pct:.1f}% missing values")
    
    # Check 4: Check for obvious data errors
    if "total_population" in df.columns:
        pop = df["total_population"].dropna()
        if (pop < 0).any():
            issues.append("Negative population values found")
        if (pop > 200_000_000).any():
            warnings.append("Population values seem unusually high")
    
    if "gdp_per_capita_usd" in df.columns:
        gdp = df["gdp_per_capita_usd"].dropna()
        if (gdp < 0).any():
            issues.append("Negative GDP per capita values found")
    
    if "literacy_rate" in df.columns:
        lit = df["literacy_rate"].dropna()
        if (lit < 0).any() or (lit > 100).any():
            issues.append("Literacy rate values outside 0-100% range")
    
    # Check 5: Data completeness
    completeness = {}
    for col in df.columns:
        non_null = df[col].notna().sum()
        completeness[col] = non_null / len(df) * 100
    
    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "year_range": (int(min_year), int(max_year)),
        "issues": issues,
        "warnings": warnings,
        "completeness": completeness,
    }

def main():
    print("=" * 60)
    print("Validating Iranian Household Data")
    print("=" * 60)
    
    # Load processed data
    csv_path = os.path.join(PROCESSED_DIR, "iran_household_all_years.csv")
    if not os.path.exists(csv_path):
        print(f"Error: Processed data not found at {csv_path}")
        print("Please run 03_process_data.py first.")
        return
    
    df = pd.read_csv(csv_path)
    print(f"\nLoaded dataset: {len(df)} rows x {len(df.columns)} columns")
    
    # Run validation
    results = validate_dataset(df)
    
    # Print results
    print("\n--- Validation Results ---")
    print(f"  Year Range: {results['year_range'][0]} - {results['year_range'][1]}")
    print(f"  Total Rows: {results['total_rows']}")
    print(f"  Total Columns: {results['total_columns']}")
    
    if results["issues"]:
        print("\n  ISSUES (must fix):")
        for issue in results["issues"]:
            print(f"    - {issue}")
    else:
        print("\n  No critical issues found!")
    
    if results["warnings"]:
        print("\n  WARNINGS:")
        for warn in results["warnings"]:
            print(f"    - {warn}")
    
    print("\n--- Data Completeness ---")
    for col, pct in results["completeness"].items():
        status = "OK" if pct > 80 else "LOW" if pct > 50 else "VERY LOW"
        print(f"  {col}: {pct:.1f}% [{status}]")
    
    # Save validation report
    report_path = os.path.join(SUMMARY_DIR, "validation_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("Iranian Household Data - Validation Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Dataset: {csv_path}\n")
        f.write(f"Rows: {results['total_rows']}\n")
        f.write(f"Columns: {results['total_columns']}\n")
        f.write(f"Year Range: {results['year_range'][0]} - {results['year_range'][1]}\n\n")
        
        f.write("ISSUES:\n")
        if results["issues"]:
            for issue in results["issues"]:
                f.write(f"  - {issue}\n")
        else:
            f.write("  None\n")
        
        f.write("\nWARNINGS:\n")
        if results["warnings"]:
            for warn in results["warnings"]:
                f.write(f"  - {warn}\n")
        else:
            f.write("  None\n")
        
        f.write("\nCOMPLETENESS:\n")
        for col, pct in results["completeness"].items():
            f.write(f"  {col}: {pct:.1f}%\n")
    
    print(f"\nValidation report saved to: {report_path}")
    
    # Also generate a quick preview of latest data
    latest_year = int(df["year"].max())
    latest = df[df["year"] == latest_year]
    if not latest.empty:
        preview_path = os.path.join(SUMMARY_DIR, "latest_year_preview.csv")
        latest.to_csv(preview_path, index=False)
        print(f"\nLatest year ({latest_year}) preview saved to: {preview_path}")
    
    print("\n" + "=" * 60)
    print("Validation Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
