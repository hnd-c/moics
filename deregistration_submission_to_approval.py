import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")

print("Creating deregistration time period distribution charts...")
print("Chart 1: Submitted → Approved/In-Process (by Type and Status)")

# Load data
df = pd.read_csv('deregidtration(Liquidation-Cancelation of registration).csv', low_memory=False)

# Convert dates
df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
df['submitted_date'] = pd.to_datetime(df['submitted_date'], errors='coerce')
df['approved_date'] = pd.to_datetime(df['approved_date'], errors='coerce')
df['updated_date'] = pd.to_datetime(df['updated_date'], errors='coerce')

# Today's date for pending calculations
today = pd.Timestamp('2026-01-25')

# Define time bins
bins = [-np.inf, 0, 1, 3, 7, 14, 30, 60, 90, 180, 365, np.inf]
labels = ['Same day', '1 day', '2-3 days', '4-7 days', '1-2 weeks',
          '2-4 weeks', '1-2 months', '2-3 months', '3-6 months', '6-12 months', '1+ year']

# Check for rejected records
rejected_count = len(df[df['application_status'] == 'REJECTED'])
print(f"\nRejected records found: {rejected_count}")

# Filter for LIQUIDATION and FORCED types with APPROVED status
df_liquidation_approved = df[(df['de_registration_type'] == 'LIQUIDATION') &
                             (df['application_status'] == 'APPROVED') &
                             (df['submitted_date'].notna()) &
                             (df['approved_date'].notna())].copy()
df_forced_approved = df[(df['de_registration_type'] == 'FORCED') &
                        (df['application_status'] == 'APPROVED') &
                        (df['submitted_date'].notna()) &
                        (df['approved_date'].notna())].copy()

# Filter for LIQUIDATION and FORCED with pending/in-process status
# (payment_verification_status = IN_PROCESS or payment_status = PENDING but still APPROVED)
df_liquidation_pending = df[(df['de_registration_type'] == 'LIQUIDATION') &
                            (df['application_status'] == 'APPROVED') &
                            (df['submitted_date'].notna()) &
                            ((df['payment_verification_status'] == 'IN_PROCESS') |
                             (df['payment_status'] == 'PENDING'))].copy()
df_forced_pending = df[(df['de_registration_type'] == 'FORCED') &
                       (df['application_status'] == 'APPROVED') &
                       (df['submitted_date'].notna()) &
                       ((df['payment_verification_status'] == 'IN_PROCESS') |
                        (df['payment_status'] == 'PENDING'))].copy()

# Calculate time periods
# For approved: submitted to approved
df_liquidation_approved['time_days'] = (df_liquidation_approved['approved_date'] - df_liquidation_approved['submitted_date']).dt.total_seconds() / 86400
df_forced_approved['time_days'] = (df_forced_approved['approved_date'] - df_forced_approved['submitted_date']).dt.total_seconds() / 86400

# For pending: submitted to today
df_liquidation_pending['time_days'] = (today - df_liquidation_pending['submitted_date']).dt.total_seconds() / 86400
df_forced_pending['time_days'] = (today - df_forced_pending['submitted_date']).dt.total_seconds() / 86400

# Create categories dictionary
categories = {
    'Liquidation - Completed': df_liquidation_approved,
    'Forced - Completed': df_forced_approved,
    'Liquidation - Pending': df_liquidation_pending,
    'Forced - Pending': df_forced_pending
}

# Colors for each category
color_map = {
    'Liquidation - Completed': '#3498db',  # Blue
    'Forced - Completed': '#e74c3c',       # Red
    'Liquidation - Pending': '#9b59b6',    # Purple
    'Forced - Pending': '#f39c12'          # Orange
}

# Function to calculate distribution
def calculate_distribution(df_cat, bins, labels):
    if len(df_cat) == 0:
        return [0] * len(labels), [0] * len(labels)

    df_cat['time_bin'] = pd.cut(df_cat['time_days'], bins=bins, labels=labels)
    dist = df_cat['time_bin'].value_counts().sort_index()
    total = len(df_cat)

    counts = []
    percentages = []
    for label in labels:
        if label in dist.index:
            count = dist[label]
            counts.append(count)
            percentages.append((count / total) * 100)
        else:
            counts.append(0)
            percentages.append(0)

    return counts, percentages

# Calculate distributions for all categories
all_data = {}
for cat_name, df_cat in categories.items():
    counts, percentages = calculate_distribution(df_cat, bins, labels)
    all_data[cat_name] = {
        'counts': counts,
        'percentages': percentages,
        'total': len(df_cat)
    }

print(f"\nData Summary:")
print(f"  LIQUIDATION - Completed: {all_data['Liquidation - Completed']['total']:,} records")
print(f"  FORCED - Completed: {all_data['Forced - Completed']['total']:,} records")
print(f"  LIQUIDATION - Pending: {all_data['Liquidation - Pending']['total']:,} records")
print(f"  FORCED - Pending: {all_data['Forced - Pending']['total']:,} records")

# ============================================================================
# CHART 1: Combined chart with all four categories side by side
# ============================================================================
fig, ax = plt.subplots(1, 1, figsize=(22, 10))

x = np.arange(len(labels))
width = 0.2

bars_liq_comp = ax.bar(x - 1.5*width, all_data['Liquidation - Completed']['percentages'], width,
                       label=f"Liquidation - Completed (n={all_data['Liquidation - Completed']['total']:,})",
                       color=color_map['Liquidation - Completed'], alpha=0.8, edgecolor='black', linewidth=1.5)

bars_forced_comp = ax.bar(x - 0.5*width, all_data['Forced - Completed']['percentages'], width,
                          label=f"Forced - Completed (n={all_data['Forced - Completed']['total']:,})",
                          color=color_map['Forced - Completed'], alpha=0.8, edgecolor='black', linewidth=1.5)

bars_liq_pend = ax.bar(x + 0.5*width, all_data['Liquidation - Pending']['percentages'], width,
                       label=f"Liquidation - Pending (n={all_data['Liquidation - Pending']['total']:,})",
                       color=color_map['Liquidation - Pending'], alpha=0.8, edgecolor='black', linewidth=1.5)

bars_forced_pend = ax.bar(x + 1.5*width, all_data['Forced - Pending']['percentages'], width,
                          label=f"Forced - Pending (n={all_data['Forced - Pending']['total']:,})",
                          color=color_map['Forced - Pending'], alpha=0.8, edgecolor='black', linewidth=1.5)

# Add labels on bars
for bars, cat_name in zip([bars_liq_comp, bars_forced_comp, bars_liq_pend, bars_forced_pend],
                          ['Liquidation - Completed', 'Forced - Completed', 'Liquidation - Pending', 'Forced - Pending']):
    for i, bar in enumerate(bars):
        height = bar.get_height()
        if height > 1:  # Only show if visible
            count = all_data[cat_name]['counts'][i]
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%\n({count:,})',
                   ha='center', va='bottom', fontsize=7, fontweight='bold')

ax.set_xlabel('Time Period', fontsize=13, fontweight='bold')
ax.set_ylabel('Percentage of Applications', fontsize=13, fontweight='bold')
ax.set_title('Company Deregistration: Time from Submission to Approval/In-Process\nLiquidation vs Forced (Completed vs Pending)',
            fontweight='bold', fontsize=16, pad=20)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=11)
ax.legend(fontsize=10, loc='upper right')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('deregistration_submission_to_approval_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: deregistration_submission_to_approval_comparison.png")
plt.close()

# ============================================================================
# CHARTS 2-5: Four separate figures (1 of 4, 2 of 4, 3 of 4, 4 of 4)
# ============================================================================

categories_list = [
    ('Liquidation - Completed', 'Voluntary Liquidation - Completed', 'Submitted → Approved'),
    ('Forced - Completed', 'Forced Deregistration - Completed', 'Submitted → Approved'),
    ('Liquidation - Pending', 'Voluntary Liquidation - Pending', 'Submitted → In-Process (as of Jan 25, 2026)'),
    ('Forced - Pending', 'Forced Deregistration - Pending', 'Submitted → In-Process (as of Jan 25, 2026)')
]

for idx, (cat_name, cat_title, time_desc) in enumerate(categories_list):
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))

    # Add annotation in top-right corner
    fig.text(0.98, 0.98, f'{idx + 1} of 4',
             fontsize=16, fontweight='bold',
             ha='right', va='top',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))

    x_pos = np.arange(len(labels))
    percentages = all_data[cat_name]['percentages']
    counts = all_data[cat_name]['counts']
    total = all_data[cat_name]['total']

    bars = ax.bar(x_pos, percentages, color=color_map[cat_name],
                 edgecolor='black', alpha=0.8, linewidth=1.5)

    # Add count and percentage labels
    for i, (bar, pct, count) in enumerate(zip(bars, percentages, counts)):
        height = bar.get_height()
        if height > 0.5:  # Only show label if bar is visible
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{pct:.1f}%\n({count:,})',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
    ax.set_ylabel('Percentage of Applications', fontsize=12, fontweight='bold')
    ax.set_title(f'Company Deregistration: {time_desc}\n{cat_title} (Total: {total:,})',
                fontweight='bold', fontsize=14, pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    filename = f'deregistration_submission_to_approval_{idx + 1}_of_4.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {filename}")
    plt.close()

# Calculate and display summary statistics
print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

for cat_name in ['Liquidation - Completed', 'Forced - Completed', 'Liquidation - Pending', 'Forced - Pending']:
    df_cat = categories[cat_name]
    if len(df_cat) > 0:
        time_days = df_cat['time_days']

        print(f"\n{cat_name.upper()}:")
        print(f"  Total records: {len(df_cat):,}")
        print(f"  Mean time: {time_days.mean():.1f} days")
        print(f"  Median time: {time_days.median():.1f} days")
        print(f"  Min time: {time_days.min():.1f} days")
        print(f"  Max time: {time_days.max():.1f} days")
        print(f"  Std deviation: {time_days.std():.1f} days")

print("\n" + "="*80)
print("DEREGISTRATION SUBMISSION TO APPROVAL CHARTS COMPLETE!")
print("="*80)
print("""
Generated Files:
  1. deregistration_submission_to_approval_comparison.png (combined chart)
  2. deregistration_submission_to_approval_1_of_4.png (Liquidation - Completed)
  3. deregistration_submission_to_approval_2_of_4.png (Forced - Completed)
  4. deregistration_submission_to_approval_3_of_4.png (Liquidation - Pending)
  5. deregistration_submission_to_approval_4_of_4.png (Forced - Pending)

Analysis:
  - Completed: submission_date to approved_date
  - Pending: submission_date to Jan 25, 2026 (today)
  - Comparing Liquidation (voluntary) vs Forced (compulsory) processes
  - Comparing Completed vs Pending status
""")
