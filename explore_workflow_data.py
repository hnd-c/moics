import pandas as pd
import numpy as np
from datetime import datetime

# Read the CSV file
print("Reading CSV file...")
df = pd.read_csv('Industry_workflow_history.csv')

print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print("\n" + "="*80)

# Basic info about the dataset
print("\nColumn names and types:")
print(df.dtypes)
print("\n" + "="*80)

# 1. Explore menu_name (processes/workflows)
print("\n1. PROCESSES/WORKFLOWS (menu_name):")
print(f"Total unique processes: {df['menu_name'].nunique()}")
print("\nProcess distribution:")
menu_counts = df['menu_name'].value_counts()
print(menu_counts)
print("\n" + "="*80)

# 2. Explore auth_level
print("\n2. AUTHORITY LEVELS (auth_level):")
print(f"Unique auth_levels: {sorted(df['auth_level'].unique())}")
auth_level_counts = df['auth_level'].value_counts().sort_index()
print("\nAuth level distribution:")
print(auth_level_counts)
print("\n" + "="*80)

# 3. Explore auth_status
print("\n3. AUTHORITY STATUS (auth_status):")
print(f"Unique auth_status values: {sorted(df['auth_status'].unique())}")
auth_status_counts = df['auth_status'].value_counts().sort_index()
print("\nAuth status distribution:")
print(auth_status_counts)
print("\n" + "="*80)

# 4. Explore industry categories
print("\n4. INDUSTRY CATEGORIES:")
print(f"Unique categories: {df['industry_category_name'].nunique()}")
category_counts = df['industry_category_name'].value_counts()
print("\nCategory distribution:")
print(category_counts)
print("\n" + "="*80)

# 5. Explore roles
print("\n5. ROLES (roleid):")
print(f"Unique roles: {sorted(df['roleid'].unique())}")
role_counts = df['roleid'].value_counts().sort_index()
print("\nRole distribution:")
print(role_counts)
print("\n" + "="*80)

# 6. Explore sections
print("\n6. SECTIONS (sectionid):")
print(f"Unique sections: {sorted(df['sectionid'].unique())}")
section_counts = df['sectionid'].value_counts().sort_index()
print("\nSection distribution:")
print(section_counts)
print("\n" + "="*80)

# 7. Parse and explore dates
print("\n7. DATE/TIME ANALYSIS:")
print("Parsing workflow_date column...")
# Try to parse dates (they appear to be in DD/MM/YYYY HH:MM format)
try:
    df['workflow_datetime'] = pd.to_datetime(df['workflow_date'], format='%d/%m/%Y %H:%M', errors='coerce')
    print(f"Successfully parsed {df['workflow_datetime'].notna().sum()} dates")
    print(f"Date range: {df['workflow_datetime'].min()} to {df['workflow_datetime'].max()}")
    
    # Extract year, month
    df['year'] = df['workflow_datetime'].dt.year
    df['month'] = df['workflow_datetime'].dt.month
    
    print("\nRecords by year:")
    print(df['year'].value_counts().sort_index())
    
except Exception as e:
    print(f"Error parsing dates: {e}")
print("\n" + "="*80)

# 8. Analyze workflow progression per application
print("\n8. WORKFLOW PROGRESSION ANALYSIS:")
print("Grouping by table_data_id (unique application ID)...")

# Group by table_data_id to see workflow progression
# Fix: convert auth_level to numeric explicitly
df['auth_level'] = pd.to_numeric(df['auth_level'], errors='coerce')
df['auth_status'] = pd.to_numeric(df['auth_status'], errors='coerce')

workflow_progression = df.groupby('table_data_id').agg(
    auth_level_min=('auth_level', 'min'),
    auth_level_max=('auth_level', 'max'),
    step_count=('auth_level', 'count'),
    workflow_date_min=('workflow_date', 'min'),
    workflow_date_max=('workflow_date', 'max'),
    menu_name=('menu_name', 'first'),
    industry_name=('industry_name', 'first')
).reset_index()

print(f"\nTotal unique applications: {df['table_data_id'].nunique()}")
print(f"Average workflow steps per application: {df.groupby('table_data_id').size().mean():.2f}")
print(f"Max workflow steps for any application: {df.groupby('table_data_id').size().max()}")
print(f"Min workflow steps for any application: {df.groupby('table_data_id').size().min()}")

# Distribution of workflow steps
print("\nDistribution of workflow steps per application:")
steps_dist = df.groupby('table_data_id').size().value_counts().sort_index()
print(steps_dist.head(20))
print("\n" + "="*80)

# 9. Sample workflow progression for a few applications
print("\n9. SAMPLE WORKFLOW PROGRESSIONS:")
print("Showing 3 example applications with their complete workflow:")

sample_apps = df['table_data_id'].value_counts().head(3).index
for app_id in sample_apps:
    app_data = df[df['table_data_id'] == app_id].sort_values('workflow_date')
    print(f"\nApplication ID: {app_id}")
    print(f"Industry: {app_data.iloc[0]['industry_name']}")
    print(f"Process: {app_data.iloc[0]['menu_name']}")
    print(f"Total steps: {len(app_data)}")
    print("\nWorkflow progression:")
    for idx, row in app_data.iterrows():
        print(f"  {row['workflow_date']} | Auth Level: {row['auth_level']} | Auth Status: {row['auth_status']} | Role: {row['roleid']}")
    print("-" * 80)

print("\n" + "="*80)

# 10. Time duration analysis preparation
print("\n10. TIME DURATION PATTERNS:")
print("Analyzing time gaps between workflow steps...")

# For each application, calculate time between steps
time_gaps = []
for app_id in df['table_data_id'].unique()[:1000]:  # Sample first 1000 apps for quick analysis
    app_data = df[df['table_data_id'] == app_id].sort_values('workflow_date')
    if len(app_data) > 1:
        try:
            app_data_copy = app_data.copy()
            app_data_copy['workflow_datetime'] = pd.to_datetime(app_data_copy['workflow_date'], format='%d/%m/%Y %H:%M')
            app_data_copy = app_data_copy.sort_values('workflow_datetime')
            
            for i in range(len(app_data_copy) - 1):
                time_gap = (app_data_copy.iloc[i+1]['workflow_datetime'] - app_data_copy.iloc[i]['workflow_datetime']).total_seconds() / 3600  # hours
                time_gaps.append({
                    'app_id': app_id,
                    'from_auth_level': app_data_copy.iloc[i]['auth_level'],
                    'to_auth_level': app_data_copy.iloc[i+1]['auth_level'],
                    'from_auth_status': app_data_copy.iloc[i]['auth_status'],
                    'to_auth_status': app_data_copy.iloc[i+1]['auth_status'],
                    'hours': time_gap,
                    'days': time_gap / 24
                })
        except:
            continue

if time_gaps:
    time_gaps_df = pd.DataFrame(time_gaps)
    print(f"\nAnalyzed {len(time_gaps)} transitions (sample of 1000 applications)")
    print("\nTime gap statistics (in days):")
    print(time_gaps_df['days'].describe())
    
    print("\nAverage time by auth level transition:")
    level_transitions = time_gaps_df.groupby(['from_auth_level', 'to_auth_level'])['days'].agg(['mean', 'median', 'count'])
    print(level_transitions.sort_values('count', ascending=False).head(15))

print("\n" + "="*80)
print("\nExploration complete! Check the generated markdown file for full findings.")
