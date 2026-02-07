import pandas as pd
import csv
from collections import Counter, defaultdict
from datetime import datetime

print("Reading CSV file...")
df = pd.read_csv('Industry_workflow_history.csv')

print(f"Total rows: {len(df):,}")
print(f"Total columns: {len(df.columns)}")
print("\n" + "="*80)

# Basic info
print("\nColumn names:")
for col in df.columns:
    print(f"  - {col}")
print("\n" + "="*80)

# 1. Process types (menu_name)
print("\n1. WORKFLOW/PROCESS TYPES (menu_name):")
menu_counts = df['menu_name'].value_counts()
print(f"Total unique processes: {len(menu_counts)}")
print("\nTop 10 processes by record count:")
for i, (menu, count) in enumerate(menu_counts.head(10).items(), 1):
    print(f"  {i:2d}. {menu:45s} - {count:6,} records ({count/len(df)*100:.1f}%)")
print("\n" + "="*80)

# 2. Auth levels
print("\n2. AUTHORITY LEVELS (auth_level):")
auth_levels = sorted(df['auth_level'].unique())
print(f"Unique auth_levels: {auth_levels}")
print(f"Range: {min(auth_levels)} to {max(auth_levels)}")
auth_level_counts = df['auth_level'].value_counts().sort_index()
print("\nDistribution:")
for level, count in auth_level_counts.items():
    print(f"  Level {level:2d}: {count:6,} records ({count/len(df)*100:.1f}%)")
print("\n" + "="*80)

# 3. Auth status
print("\n3. AUTHORITY STATUS (auth_status):")
auth_statuses = sorted(df['auth_status'].unique())
print(f"Unique auth_status values: {auth_statuses}")
auth_status_counts = df['auth_status'].value_counts().sort_index()
print("\nDistribution:")
status_meanings = {
    -1: "Pending",
    0: "Submitted",
    1: "Approved",
    2: "Unknown-2",
    3: "Sent back for review",
    4: "Unknown-4",
    5: "Unknown-5",
    7: "Unknown-7",
    8: "Unknown-8"
}
for status, count in auth_status_counts.items():
    meaning = status_meanings.get(status, "Unknown")
    print(f"  Status {status:2d} ({meaning:25s}): {count:6,} records ({count/len(df)*100:.1f}%)")
print("\n" + "="*80)

# 4. Industry categories
print("\n4. INDUSTRY CATEGORIES:")
category_counts = df['industry_category_name'].value_counts()
print(f"Unique categories: {len(category_counts)}")
print("\nDistribution:")
for i, (cat, count) in enumerate(category_counts.items(), 1):
    print(f"  {i}. {cat:30s} - {count:6,} records ({count/len(df)*100:.1f}%)")
print("\n" + "="*80)

# 5. Roles
print("\n5. ROLES (roleid):")
role_counts = df['roleid'].value_counts().sort_index()
print(f"Unique roles: {len(role_counts)}")
print("\nTop 5 roles by record count:")
for i, (role, count) in enumerate(role_counts.head(5).items(), 1):
    print(f"  Role {role:2d}: {count:6,} records ({count/len(df)*100:.1f}%)")
print("\n" + "="*80)

# 6. Date analysis
print("\n6. DATE/TIME ANALYSIS:")
print("Parsing dates...")
df['workflow_datetime'] = pd.to_datetime(df['workflow_date'], format='%d/%m/%Y %H:%M', errors='coerce')
valid_dates = df['workflow_datetime'].notna().sum()
print(f"Successfully parsed: {valid_dates:,} dates ({valid_dates/len(df)*100:.1f}%)")
print(f"Date range: {df['workflow_datetime'].min()} to {df['workflow_datetime'].max()}")

df['year'] = df['workflow_datetime'].dt.year
year_counts = df['year'].value_counts().sort_index()
print("\nRecords by year:")
for year, count in year_counts.items():
    if not pd.isna(year):
        print(f"  {int(year)}: {count:6,} records")
print("\n" + "="*80)

# 7. Workflow progression analysis
print("\n7. WORKFLOW PROGRESSION ANALYSIS:")
print("Analyzing applications...")

unique_apps = df['table_data_id'].nunique()
print(f"Total unique applications: {unique_apps:,}")

app_steps = df.groupby('table_data_id').size()
print(f"\nWorkflow steps per application:")
print(f"  Average: {app_steps.mean():.2f} steps")
print(f"  Median:  {app_steps.median():.0f} steps")
print(f"  Min:     {app_steps.min()} steps")
print(f"  Max:     {app_steps.max()} steps")

print("\nDistribution of steps (top 15):")
steps_dist = app_steps.value_counts().sort_index()
for steps, count in steps_dist.head(15).items():
    print(f"  {steps:2d} steps: {count:5,} applications ({count/unique_apps*100:.1f}%)")
print("\n" + "="*80)

# 8. Sample workflow progressions
print("\n8. SAMPLE WORKFLOW PROGRESSIONS:")
print("Showing 5 example applications:\n")

# Get applications with different step counts
sample_apps = []
for step_count in [3, 5, 7, 10, 15]:
    apps_with_n_steps = app_steps[app_steps == step_count]
    if len(apps_with_n_steps) > 0:
        sample_apps.append(apps_with_n_steps.index[0])

for app_id in sample_apps[:5]:
    app_data = df[df['table_data_id'] == app_id].sort_values('workflow_datetime')
    print(f"Application ID: {app_id}")
    print(f"Industry: {app_data.iloc[0]['industry_name']}")
    print(f"Process: {app_data.iloc[0]['menu_name']}")
    print(f"Category: {app_data.iloc[0]['industry_category_name']}")
    print(f"Total steps: {len(app_data)}")
    print("\nProgression:")
    for idx, row in app_data.iterrows():
        status_label = status_meanings.get(row['auth_status'], f"Status-{row['auth_status']}")
        date_str = str(row['workflow_date']) if pd.notna(row['workflow_date']) else 'N/A'
        role_str = int(row['roleid']) if pd.notna(row['roleid']) else 'N/A'
        print(f"  {date_str:20s} | Auth Level: {int(row['auth_level']):2d} | {status_label:25s} | Role: {role_str}")
    print("-" * 80 + "\n")

print("="*80)

# 9. Auth level transitions
print("\n9. AUTHORITY LEVEL TRANSITIONS:")
print("Analyzing common transition patterns...\n")

transitions = []
for app_id in df['table_data_id'].unique():
    app_data = df[df['table_data_id'] == app_id].sort_values('workflow_datetime')
    levels = app_data['auth_level'].tolist()
    for i in range(len(levels) - 1):
        transitions.append((levels[i], levels[i+1]))

transition_counts = Counter(transitions)
print("Top 20 most common auth level transitions:")
for i, ((from_level, to_level), count) in enumerate(transition_counts.most_common(20), 1):
    direction = "→" if to_level > from_level else ("←" if to_level < from_level else "=")
    print(f"  {i:2d}. Level {from_level:2d} {direction} Level {to_level:2d}: {count:5,} times")

print("\n" + "="*80)

# 10. Process-specific analysis
print("\n10. PROCESS-SPECIFIC STATISTICS:")
print("Auth level range by process type:\n")

for menu in menu_counts.head(10).index:
    menu_data = df[df['menu_name'] == menu]
    min_level = menu_data['auth_level'].min()
    max_level = menu_data['auth_level'].max()
    avg_steps = menu_data.groupby('table_data_id').size().mean()
    print(f"{menu:45s}")
    print(f"  Auth levels: {min_level} to {max_level} | Avg steps per application: {avg_steps:.1f}")

print("\n" + "="*80)
print("\nExploration complete!")
