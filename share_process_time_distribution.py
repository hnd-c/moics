import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")

print("Creating share process time period distribution charts...")

# Load data
df = pd.read_csv('shareData.csv', low_memory=False)

# Convert dates
df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
df['updated_date'] = pd.to_datetime(df['updated_date'], errors='coerce')
df['submission_date'] = pd.to_datetime(df['submission_date'], errors='coerce')

# Today's date for in-process calculations
today = pd.Timestamp('2026-01-25')

# Define time bins
bins = [-np.inf, 0, 1, 3, 7, 14, 30, 60, 90, 180, 365, np.inf]
labels = ['Same day', '1 day', '2-3 days', '4-7 days', '1-2 weeks',
          '2-4 weeks', '1-2 months', '2-3 months', '3-6 months', '6-12 months', '1+ year']

# Filter records with submission_date
df_with_submission = df[df['submission_date'].notna()].copy()

# Category 1: VERIFIED (Submission → Verification)
df_verified = df_with_submission[df_with_submission['post_event_process_status'] == 'VERIFIED'].copy()
df_verified['time_days'] = (df_verified['updated_date'] - df_verified['submission_date']).dt.total_seconds() / 86400

# Category 2: REJECTED (Submission → Rejection)
df_rejected = df_with_submission[df_with_submission['post_event_process_status'] == 'REJECTED'].copy()
df_rejected['time_days'] = (df_rejected['updated_date'] - df_rejected['submission_date']).dt.total_seconds() / 86400

# Category 3: In-Process (Submission → Today)
# Include: UNVERIFIED, SUBMITTED, RE_SUBMITTED, VERIFIED_AND_FORWARD (exclude DRAFT)
in_process_statuses = ['UNVERIFIED', 'SUBMITTED', 'RE_SUBMITTED', 'VERIFIED_AND_FORWARD']
df_in_process = df_with_submission[df_with_submission['post_event_process_status'].isin(in_process_statuses)].copy()
df_in_process['time_days'] = (today - df_in_process['submission_date']).dt.total_seconds() / 86400

# Create categories dictionary
categories = {
    'Verified': df_verified,
    'Rejected': df_rejected,
    'In-Process': df_in_process
}

# Colors for each category
color_map = {
    'Verified': '#2ecc71',      # Green
    'Rejected': '#e74c3c',      # Red
    'In-Process': '#3498db'     # Blue
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
print(f"  VERIFIED: {all_data['Verified']['total']:,} records")
print(f"  REJECTED: {all_data['Rejected']['total']:,} records")
print(f"  IN-PROCESS: {all_data['In-Process']['total']:,} records")

# ============================================================================
# CHART 1: Combined chart with all three categories side by side
# ============================================================================
fig, ax = plt.subplots(1, 1, figsize=(20, 10))

x = np.arange(len(labels))
width = 0.25

bars_verified = ax.bar(x - width, all_data['Verified']['percentages'], width,
                       label=f"Verified (n={all_data['Verified']['total']:,})",
                       color=color_map['Verified'], alpha=0.8, edgecolor='black', linewidth=1.5)

bars_rejected = ax.bar(x, all_data['Rejected']['percentages'], width,
                       label=f"Rejected (n={all_data['Rejected']['total']:,})",
                       color=color_map['Rejected'], alpha=0.8, edgecolor='black', linewidth=1.5)

bars_in_process = ax.bar(x + width, all_data['In-Process']['percentages'], width,
                         label=f"In-Process (n={all_data['In-Process']['total']:,})",
                         color=color_map['In-Process'], alpha=0.8, edgecolor='black', linewidth=1.5)

# Add labels on bars
for bars, cat_name in zip([bars_verified, bars_rejected, bars_in_process],
                          ['Verified', 'Rejected', 'In-Process']):
    for i, bar in enumerate(bars):
        height = bar.get_height()
        if height > 1:  # Only show if visible
            count = all_data[cat_name]['counts'][i]
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%\n({count:,})',
                   ha='center', va='bottom', fontsize=8, fontweight='bold')

ax.set_xlabel('Time Period', fontsize=13, fontweight='bold')
ax.set_ylabel('Percentage of Applications', fontsize=13, fontweight='bold')
ax.set_title('Time Period Distribution for Share Purchase and Sales Process\nSubmission to Final Status',
            fontweight='bold', fontsize=16, pad=20)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=11)
ax.legend(fontsize=12, loc='upper right')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('share_process_time_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: share_process_time_comparison.png")
plt.close()

# ============================================================================
# CHARTS 2-4: Three separate figures (1 of 3, 2 of 3, 3 of 3)
# ============================================================================

categories_list = [
    ('Verified', 'Submission → Verification'),
    ('Rejected', 'Submission → Rejection'),
    ('In-Process', 'Submission → In-Process (as of Jan 25, 2026)')
]

for idx, (cat_name, cat_title) in enumerate(categories_list):
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))

    # Add annotation in top-right corner
    fig.text(0.98, 0.98, f'{idx + 1} of 3',
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
    ax.set_title(f'Time Period Distribution for Share Purchase and Sales Process\n{cat_title} (Total: {total:,})',
                fontweight='bold', fontsize=14, pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    filename = f'share_process_time_distribution_{idx + 1}_of_3.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {filename}")
    plt.close()

print("\n" + "="*80)
print("SHARE PROCESS TIME DISTRIBUTION CHARTS COMPLETE!")
print("="*80)
print("""
Generated Files:
  1. share_process_time_comparison.png (combined comparison chart)
  2. share_process_time_distribution_1_of_3.png (Verified)
  3. share_process_time_distribution_2_of_3.png (Rejected)
  4. share_process_time_distribution_3_of_3.png (In-Process)

Summary:
  - VERIFIED records: Submission → Updated (approval date)
  - REJECTED records: Submission → Updated (rejection date)
  - IN-PROCESS records: Submission → Today (Jan 25, 2026)
  - Excluded statuses: DRAFT, CANCELED
""")
