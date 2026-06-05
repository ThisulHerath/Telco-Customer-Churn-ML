import pandas as pd
from typing import Tuple, List


def validate_telco_data(df) -> Tuple[bool, List[str]]:
    """
    Comprehensive data validation for Telco Customer Churn dataset using Great Expectations.
    
    This function implements critical data quality checks that must pass before model training.
    It validates data integrity, business logic constraints, and statistical properties
    that the ML model expects.
    
    """
    print("🔍 Starting data validation...")

    failed_expectations = []

    def fail(name: str) -> None:
        failed_expectations.append(name)

    print("   📋 Validating schema and required columns...")
    required_columns = [
        "customerID",
        "gender",
        "Partner",
        "Dependents",
        "PhoneService",
        "InternetService",
        "Contract",
        "tenure",
        "MonthlyCharges",
        "TotalCharges",
    ]
    for column in required_columns:
        if column not in df.columns:
            fail(f"missing_column:{column}")

    if "customerID" in df.columns and df["customerID"].isna().any():
        fail("customerID_not_null")

    print("   💼 Validating business logic constraints...")
    if "gender" in df.columns and not set(df["gender"].dropna().unique()) <= {"Male", "Female"}:
        fail("gender_in_set")
    if "Partner" in df.columns and not set(df["Partner"].dropna().unique()) <= {"Yes", "No"}:
        fail("Partner_in_set")
    if "Dependents" in df.columns and not set(df["Dependents"].dropna().unique()) <= {"Yes", "No"}:
        fail("Dependents_in_set")
    if "PhoneService" in df.columns and not set(df["PhoneService"].dropna().unique()) <= {"Yes", "No"}:
        fail("PhoneService_in_set")
    if "Contract" in df.columns and not set(df["Contract"].dropna().unique()) <= {"Month-to-month", "One year", "Two year"}:
        fail("Contract_in_set")
    if "InternetService" in df.columns and not set(df["InternetService"].dropna().unique()) <= {"DSL", "Fiber optic", "No"}:
        fail("InternetService_in_set")

    print("   📊 Validating numeric ranges and business constraints...")
    if "tenure" in df.columns:
        tenure = pd.to_numeric(df["tenure"], errors="coerce")
        if tenure.isna().any():
            fail("tenure_not_null_numeric")
        if not tenure.between(0, 120).all():
            fail("tenure_range")
    if "MonthlyCharges" in df.columns:
        monthly = pd.to_numeric(df["MonthlyCharges"], errors="coerce")
        if monthly.isna().any():
            fail("MonthlyCharges_not_null_numeric")
        if not monthly.between(0, 200).all():
            fail("MonthlyCharges_range")
    if "TotalCharges" in df.columns:
        total = pd.to_numeric(df["TotalCharges"], errors="coerce")
        if (total.dropna() < 0).any():
            fail("TotalCharges_non_negative")

    print("   🔗 Validating data consistency...")
    if {"TotalCharges", "MonthlyCharges"} <= set(df.columns):
        total = pd.to_numeric(df["TotalCharges"], errors="coerce")
        monthly = pd.to_numeric(df["MonthlyCharges"], errors="coerce")
        consistency_ratio = (total.ge(monthly) | total.isna() | monthly.isna()).mean()
        if consistency_ratio < 0.95:
            fail("TotalCharges_ge_MonthlyCharges_mostly")

    total_checks = 14
    passed_checks = total_checks - len(failed_expectations)

    if failed_expectations:
        print(f"❌ Data validation FAILED: {len(failed_expectations)}/{total_checks} checks failed")
        print(f"   Failed expectations: {failed_expectations}")
    else:
        print(f"✅ Data validation PASSED: {passed_checks}/{total_checks} checks successful")

    return len(failed_expectations) == 0, failed_expectations
