import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("VERIFYING COMPANY REGISTRATION DATE FIELDS")
print("="*80)

# Load data
df = pd.read_csv('companyregistrationnewsystem.csv', low_memory=False)

# Convert dates
df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
df['approved_date'] = pd.to_datetime(df['approved_date'], errors='coerce')
df['registration_date'] = pd.to_datetime(df['registration_date'], errors='coerce')
df['submission_date'] = pd.to_datetime(df['submission_date'], errors='coerce')

print(f"\nTotal records: {len(df):,}")

print("\n" + "-"*80)
print("DATE FIELD ANALYSIS")
print("-"*80)

# Check each date field
date_fields = ['created_date', 'approved_date', 'registration_date', 'submission_date']

for field in date_fields:
    non_null = df[field].notna().sum()
    if non_null > 0:
        min_date = df[field].min()
        max_date = df[field].max()
        print(f"\n{field}:")
        print(f"  Non-null: {non_null:,}")
        print(f"  Min: {min_date}")
        print(f"  Max: {max_date}")

print("\n" + "-"*80)
print("CHECKING REGISTRATION_DATE ISSUE")
print("-"*80)

# Calculate time differences
df['created_to_approved'] = (df['approved_date'] - df['created_date']).dt.total_seconds() / 86400
df['approved_to_registration'] = (df['registration_date'] - df['approved_date']).dt.total_seconds() / 86400
df['created_to_registration'] = (df['registration_date'] - df['created_date']).dt.total_seconds() / 86400

print("\nTime Period Statistics:")
print("-"*80)

periods = {
    'Created → Approved': 'created_to_approved',
    'Approved → Registration': 'approved_to_registration',
    'Created → Registration': 'created_to_registration'
}

for name, col in periods.items():
    valid = df[col].dropna()
    if len(valid) > 0:
        print(f"\n{name}:")
        print(f"  Count: {len(valid):,}")
        print(f"  Mean: {valid.mean():.1f} days")
        print(f"  Median: {valid.median():.1f} days")
        print(f"  Min: {valid.min():.1f} days")
        print(f"  Max: {valid.max():.1f} days")

        # Check for negative values
        negative_count = (valid < 0).sum()
        if negative_count > 0:
            print(f"  ⚠️ NEGATIVE VALUES: {negative_count:,} ({negative_count/len(valid)*100:.1f}%)")

print("\n" + "-"*80)
print("SAMPLE RECORDS WITH REGISTRATION_DATE")
print("-"*80)

# Show some sample records
sample = df[df['registration_date'].notna()][['application_number', 'created_date', 'approved_date',
                                                'registration_date', 'created_to_registration']].head(10)
print("\nFirst 10 records with registration_date:")
print(sample.to_string())

print("\n" + "-"*80)
print("ANALYSIS OF REGISTRATION_DATE PATTERNS")
print("-"*80)

# Check if registration_date is before created_date (historical data)
records_with_reg = df[df['registration_date'].notna()].copy()
historical = records_with_reg[records_with_reg['registration_date'] < records_with_reg['created_date']]

print(f"\nTotal records with registration_date: {len(records_with_reg):,}")
print(f"Registration dates BEFORE creation date: {len(historical):,} ({len(historical)/len(records_with_reg)*100:.1f}%)")

if len(historical) > 0:
    print("\n⚠️ ISSUE DETECTED:")
    print("   The 'registration_date' field contains HISTORICAL DATES (old company registrations)")
    print("   NOT the date when the record was registered in THIS SYSTEM")

    print("\nExamples of historical dates:")
    historical_sample = historical[['application_number', 'created_date', 'registration_date',
                                    'created_to_registration']].head(5)
    print(historical_sample.to_string())

print("\n" + "-"*80)
print("CORRECT TIME PERIODS TO ANALYZE")
print("-"*80)

print("""
✅ VALID METRICS:
   1. Created → Submission: Time for user to prepare and submit application
   2. Created → Approved: Total time from creation to approval
   3. Submission → Approved: Actual review/processing time by system

❌ INVALID METRICS (DO NOT USE):
   1. Approved → Registration: Contains historical dates from OLD SYSTEM
   2. Created → Registration: Contains historical dates from OLD SYSTEM

EXPLANATION:
The 'registration_date' field stores the ORIGINAL company registration date
(e.g., when company was first registered in 1990s-2000s), NOT when the
current application was processed in the new system.

This is why you see:
- 99.77% "same day" for Approved → Registration (data artifact)
- Negative values (registration happened years before system creation)
- Mean of -6297 days (about 17 years in the past!)
""")

# Verify the correct metrics
print("\n" + "-"*80)
print("VERIFIED CORRECT METRICS")
print("-"*80)

df['created_to_submission'] = (df['submission_date'] - df['created_date']).dt.total_seconds() / 86400
df['submission_to_approved'] = (df['approved_date'] - df['submission_date']).dt.total_seconds() / 86400

valid_periods = {
    'Created → Submission': 'created_to_submission',
    'Submission → Approved': 'submission_to_approved',
    'Created → Approved': 'created_to_approved'
}

print("\nCORRECT Time Period Statistics:")
for name, col in valid_periods.items():
    valid = df[col].dropna()
    if len(valid) > 0:
        print(f"\n{name}:")
        print(f"  Count: {len(valid):,}")
        print(f"  Mean: {valid.mean():.1f} days")
        print(f"  Median: {valid.median():.1f} days")
        print(f"  Positive values: {(valid >= 0).sum():,} ({(valid >= 0).sum()/len(valid)*100:.1f}%)")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("""
The charts showing "Approved → Registration" and "Created → Registration (Total)"
are INCORRECT and should be IGNORED or REMOVED from the analysis.

Only use these 3 metrics:
1. Created → Submission (user preparation time)
2. Submission → Approved (system processing time)
3. Created → Approved (total time)

The registration_date field represents the historical company registration date,
not a workflow step in the current system!
""")

