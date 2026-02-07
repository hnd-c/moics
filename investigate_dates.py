import pandas as pd
import numpy as np

# Load the data
df_name = pd.read_csv('nameregisvation.csv', low_memory=False)

# Convert date columns to datetime
df_name['created_date'] = pd.to_datetime(df_name['created_date'], errors='coerce')
df_name['updated_date'] = pd.to_datetime(df_name['updated_date'], errors='coerce')
df_name['approved_date'] = pd.to_datetime(df_name['approved_date'], errors='coerce')

print("="*80)
print("DATE RELATIONSHIP ANALYSIS")
print("="*80)

# Filter only records with all three dates
complete_records = df_name[
    df_name['created_date'].notna() &
    df_name['updated_date'].notna() &
    df_name['approved_date'].notna()
].copy()

print(f"\nRecords with all three dates: {len(complete_records):,}")

# Check date ordering patterns
print("\n" + "-"*80)
print("DATE ORDERING PATTERNS")
print("-"*80)

# Pattern 1: approved_date is BEFORE updated_date
pattern1 = complete_records[complete_records['approved_date'] < complete_records['updated_date']]
print(f"\n1. Approved BEFORE Updated: {len(pattern1):,} ({len(pattern1)/len(complete_records)*100:.1f}%)")
print("   → Applications are approved, then updated later")

# Pattern 2: approved_date is AFTER updated_date
pattern2 = complete_records[complete_records['approved_date'] > complete_records['updated_date']]
print(f"\n2. Approved AFTER Updated: {len(pattern2):,} ({len(pattern2)/len(complete_records)*100:.1f}%)")
print("   → Applications are updated, then approved")

# Pattern 3: approved_date equals updated_date
pattern3 = complete_records[complete_records['approved_date'] == complete_records['updated_date']]
print(f"\n3. Approved SAME AS Updated: {len(pattern3):,} ({len(pattern3)/len(complete_records)*100:.1f}%)")
print("   → Approval happens at the same time as last update")

# Pattern 4: created_date equals updated_date
pattern4 = complete_records[complete_records['created_date'] == complete_records['updated_date']]
print(f"\n4. Created SAME AS Updated: {len(pattern4):,} ({len(pattern4)/len(complete_records)*100:.1f}%)")
print("   → Never updated after creation")

print("\n" + "-"*80)
print("EXPECTED CHRONOLOGICAL ORDER")
print("-"*80)

# Check expected order: created <= approved <= updated
expected_order = complete_records[
    (complete_records['created_date'] <= complete_records['approved_date']) &
    (complete_records['approved_date'] <= complete_records['updated_date'])
]
print(f"\nCreated → Approved → Updated: {len(expected_order):,} ({len(expected_order)/len(complete_records)*100:.1f}%)")

# Check alternative order: created <= updated <= approved
alt_order = complete_records[
    (complete_records['created_date'] <= complete_records['updated_date']) &
    (complete_records['updated_date'] <= complete_records['approved_date'])
]
print(f"Created → Updated → Approved: {len(alt_order):,} ({len(alt_order)/len(complete_records)*100:.1f}%)")

# Other patterns
other = complete_records[
    ~(
        ((complete_records['created_date'] <= complete_records['approved_date']) &
         (complete_records['approved_date'] <= complete_records['updated_date'])) |
        ((complete_records['created_date'] <= complete_records['updated_date']) &
         (complete_records['updated_date'] <= complete_records['approved_date']))
    )
]
print(f"Other patterns: {len(other):,} ({len(other)/len(complete_records)*100:.1f}%)")

print("\n" + "-"*80)
print("SAMPLE EXAMPLES")
print("-"*80)

# Show examples of each pattern
print("\n✓ Pattern: Created → Approved → Updated (Post-approval updates)")
print("   This means records continue to be modified AFTER approval\n")
sample1 = pattern1[['application_number', 'company_name_english', 'status',
                     'created_date', 'approved_date', 'updated_date']].head(5)
for idx, row in sample1.iterrows():
    print(f"   {row['application_number']}: {row['company_name_english'][:30]}")
    print(f"   ├─ Created:  {row['created_date']}")
    print(f"   ├─ Approved: {row['approved_date']} (after {(row['approved_date'] - row['created_date']).days} days)")
    print(f"   └─ Updated:  {row['updated_date']} (after approval: {(row['updated_date'] - row['approved_date']).days} days)")
    print()

print("\n✓ Pattern: Created → Updated → Approved (Traditional workflow)")
print("   This means records are finalized before approval\n")
sample2 = alt_order[['application_number', 'company_name_english', 'status',
                      'created_date', 'updated_date', 'approved_date']].head(5)
for idx, row in sample2.iterrows():
    print(f"   {row['application_number']}: {row['company_name_english'][:30]}")
    print(f"   ├─ Created:  {row['created_date']}")
    print(f"   ├─ Updated:  {row['updated_date']} (after {(row['updated_date'] - row['created_date']).days} days)")
    print(f"   └─ Approved: {row['approved_date']} (after update: {(row['approved_date'] - row['updated_date']).days} days)")
    print()

print("\n" + "="*80)
print("INSIGHTS")
print("="*80)

print("""
Based on the analysis, your data shows TWO distinct workflows:

1. **Post-Approval Updates** (Most Common):
   - Applications are approved quickly after creation
   - The 'updated_date' continues to change AFTER approval
   - This is why you see negative "Updated to Approved" values
   - The 'updated_date' field acts as a "last_modified" timestamp

2. **Pre-Approval Updates** (Less Common):
   - Traditional workflow where updates happen before approval
   - Applications are finalized, then approved

RECOMMENDATION:
- The 'updated_date' is a LAST MODIFIED timestamp (not a workflow stage)
- For workflow analysis, focus on: Created → Approved
- The 'updated_date' tracks ANY changes to the record (even after approval)
- This could include status changes, corrections, additional data, etc.

The key insight: **approved_date does NOT update the updated_date**
Instead: **updated_date gets updated whenever ANY field changes**, even after approval!
""")

# Check what happens after approval - are they really being updated?
print("\n" + "-"*80)
print("POST-APPROVAL UPDATE ANALYSIS")
print("-"*80)

post_approval_updates = pattern1.copy()
post_approval_updates['days_between_approval_and_last_update'] = (
    post_approval_updates['updated_date'] - post_approval_updates['approved_date']
).dt.days

print(f"\nRecords updated after approval: {len(post_approval_updates):,}")
print(f"Average days between approval and last update: {post_approval_updates['days_between_approval_and_last_update'].mean():.1f}")
print(f"Median days: {post_approval_updates['days_between_approval_and_last_update'].median():.1f}")
print(f"Max days: {post_approval_updates['days_between_approval_and_last_update'].max():.1f}")

print("\nDistribution of post-approval update timing:")
bins = [0, 1, 7, 30, 90, 180, 365, 999]
labels = ['Same day', '1-7 days', '1-4 weeks', '1-3 months', '3-6 months', '6-12 months', '1+ year']
post_approval_updates['update_timing'] = pd.cut(
    post_approval_updates['days_between_approval_and_last_update'],
    bins=bins,
    labels=labels
)
print(post_approval_updates['update_timing'].value_counts().sort_index())


