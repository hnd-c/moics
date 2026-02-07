import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (20, 12)

print("="*80)
print("LOADING DATASETS AND ALIGNING DATE RANGES")
print("="*80)

# Load company registration data to get earliest date
print("\n1. Loading company registration data...")
df_company = pd.read_csv('companyregistrationnewsystem.csv', low_memory=False)
df_company['created_date'] = pd.to_datetime(df_company['created_date'], errors='coerce')

earliest_company_date = df_company['created_date'].min()
latest_company_date = df_company['created_date'].max()

print(f"   Company Registration Date Range:")
print(f"   - Earliest: {earliest_company_date}")
print(f"   - Latest: {latest_company_date}")
print(f"   - Total records: {len(df_company):,}")

# Load name reservation data
print("\n2. Loading name registration data...")
df_name = pd.read_csv('nameregisvation.csv', low_memory=False)

# Convert dates
df_name['created_date'] = pd.to_datetime(df_name['created_date'], errors='coerce')
df_name['approved_date'] = pd.to_datetime(df_name['approved_date'], errors='coerce')
df_name['updated_date'] = pd.to_datetime(df_name['updated_date'], errors='coerce')

print(f"   Name Registration Full Date Range:")
print(f"   - Earliest: {df_name['created_date'].min()}")
print(f"   - Latest: {df_name['created_date'].max()}")
print(f"   - Total records: {len(df_name):,}")

# Filter name registration to match company registration date range
print(f"\n3. Filtering name registration data to match date range...")
print(f"   Filtering for records >= {earliest_company_date}")

df_name_filtered = df_name[df_name['created_date'] >= earliest_company_date].copy()

print(f"   Filtered Name Registration:")
print(f"   - Earliest: {df_name_filtered['created_date'].min()}")
print(f"   - Latest: {df_name_filtered['created_date'].max()}")
print(f"   - Total records: {len(df_name_filtered):,}")
print(f"   - Records removed: {len(df_name) - len(df_name_filtered):,}")

# Status distribution
print(f"\n4. Status distribution in filtered data:")
status_dist = df_name_filtered['status'].value_counts()
for status, count in status_dist.items():
    pct = (count / len(df_name_filtered)) * 100
    print(f"   - {status}: {count:,} ({pct:.1f}%)")

# Calculate processing time
df_name_filtered['processing_days'] = (df_name_filtered['approved_date'] - df_name_filtered['created_date']).dt.total_seconds() / 86400

# Separate approved and rejected
approved = df_name_filtered[(df_name_filtered['status'] == 'APPROVED') &
                            (df_name_filtered['processing_days'].notna())].copy()
rejected = df_name_filtered[(df_name_filtered['status'] == 'REJECTED') &
                            (df_name_filtered['processing_days'].notna())].copy()

print(f"\n5. Records with processing time data:")
print(f"   - APPROVED: {len(approved):,}")
print(f"   - REJECTED: {len(rejected):,}")
print(f"   - Total analyzed: {len(approved) + len(rejected):,}")

# ============================================================================
# TIME PERIOD ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("TIME PERIOD DISTRIBUTION ANALYSIS (ALIGNED DATE RANGE)")
print("="*80)

# Define time bins
bins = [-np.inf, 0, 1, 3, 7, 14, 30, 60, 90, 180, 365, np.inf]
labels = ['Same day', '1 day', '2-3 days', '4-7 days', '1-2 weeks',
          '2-4 weeks', '1-2 months', '2-3 months', '3-6 months', '6-12 months', '1+ year']

approved['time_bin'] = pd.cut(approved['processing_days'], bins=bins, labels=labels)
rejected['time_bin'] = pd.cut(rejected['processing_days'], bins=bins, labels=labels)

# Print distributions
print("\nAPPROVED - Time Distribution:")
print("-"*80)
approved_dist = approved['time_bin'].value_counts().sort_index()
approved_total = len(approved)
print(f"{'Time Period':<15} {'Count':>12} {'Percentage':>12} {'Cumulative':>12}")
print("-"*80)
cumulative = 0
for period, count in approved_dist.items():
    pct = (count / approved_total) * 100
    cumulative += pct
    print(f"{str(period):<15} {count:>12,} {pct:>11.2f}% {cumulative:>11.2f}%")

print("\nREJECTED - Time Distribution:")
print("-"*80)
rejected_dist = rejected['time_bin'].value_counts().sort_index()
rejected_total = len(rejected)
print(f"{'Time Period':<15} {'Count':>12} {'Percentage':>12} {'Cumulative':>12}")
print("-"*80)
cumulative = 0
for period, count in rejected_dist.items():
    pct = (count / rejected_total) * 100
    cumulative += pct
    print(f"{str(period):<15} {count:>12,} {pct:>11.2f}% {cumulative:>11.2f}%")

# ============================================================================
# VISUALIZATION 1: Main Distribution Comparison
# ============================================================================

print("\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

fig, axes = plt.subplots(2, 2, figsize=(22, 14))
fig.suptitle(f'Name Registration - APPROVED vs REJECTED (Aligned Date Range)\nFrom {earliest_company_date.strftime("%Y-%m-%d")} onwards',
             fontsize=18, fontweight='bold', y=0.995)

# 1. APPROVED Histogram
ax1 = axes[0, 0]
counts, bin_edges, patches = ax1.hist(approved['processing_days'], bins=50,
                                       edgecolor='black', alpha=0.7, color='green')

mean_val = approved['processing_days'].mean()
median_val = approved['processing_days'].median()
ax1.axvline(mean_val, color='red', linestyle='--', linewidth=2.5,
            label=f'Mean: {mean_val:.1f} days', zorder=5)
ax1.axvline(median_val, color='blue', linestyle='--', linewidth=2.5,
            label=f'Median: {median_val:.1f} days', zorder=5)

# Add percentile annotations
percentiles = [50, 75, 90, 95]
y_max = counts.max()
for i, pct in enumerate(percentiles):
    val = np.percentile(approved['processing_days'], pct)
    ax1.axvline(val, color='orange', linestyle=':', linewidth=1.5, alpha=0.7)
    ax1.text(val, y_max * (0.95 - i*0.08), f'{pct}th: {val:.1f}d',
             rotation=0, fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

ax1.set_title(f'APPROVED Applications (n={len(approved):,})\nProcessing Time Distribution',
              fontweight='bold', fontsize=14)
ax1.set_xlabel('Days from Creation to Approval', fontsize=11, fontweight='bold')
ax1.set_ylabel('Number of Applications', fontsize=11, fontweight='bold')
ax1.legend(loc='upper right', fontsize=10)
ax1.grid(True, alpha=0.3)

stats_text = f'Statistics:\n' \
             f'Mean: {mean_val:.1f} days\n' \
             f'Median: {median_val:.1f} days\n' \
             f'Std Dev: {approved["processing_days"].std():.1f} days\n' \
             f'Min: {approved["processing_days"].min():.1f} days\n' \
             f'Max: {approved["processing_days"].max():.1f} days'
ax1.text(0.97, 0.55, stats_text, transform=ax1.transAxes, fontsize=9,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

# 2. REJECTED Histogram
ax2 = axes[0, 1]
counts, bin_edges, patches = ax2.hist(rejected['processing_days'], bins=50,
                                       edgecolor='black', alpha=0.7, color='red')

mean_val = rejected['processing_days'].mean()
median_val = rejected['processing_days'].median()
ax2.axvline(mean_val, color='darkred', linestyle='--', linewidth=2.5,
            label=f'Mean: {mean_val:.1f} days', zorder=5)
ax2.axvline(median_val, color='blue', linestyle='--', linewidth=2.5,
            label=f'Median: {median_val:.1f} days', zorder=5)

y_max = counts.max()
for i, pct in enumerate(percentiles):
    val = np.percentile(rejected['processing_days'], pct)
    ax2.axvline(val, color='orange', linestyle=':', linewidth=1.5, alpha=0.7)
    ax2.text(val, y_max * (0.95 - i*0.08), f'{pct}th: {val:.1f}d',
             rotation=0, fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

ax2.set_title(f'REJECTED Applications (n={len(rejected):,})\nProcessing Time Distribution',
              fontweight='bold', fontsize=14)
ax2.set_xlabel('Days from Creation to Rejection', fontsize=11, fontweight='bold')
ax2.set_ylabel('Number of Applications', fontsize=11, fontweight='bold')
ax2.legend(loc='upper right', fontsize=10)
ax2.grid(True, alpha=0.3)

stats_text = f'Statistics:\n' \
             f'Mean: {mean_val:.1f} days\n' \
             f'Median: {median_val:.1f} days\n' \
             f'Std Dev: {rejected["processing_days"].std():.1f} days\n' \
             f'Min: {rejected["processing_days"].min():.1f} days\n' \
             f'Max: {rejected["processing_days"].max():.1f} days'
ax2.text(0.97, 0.55, stats_text, transform=ax2.transAxes, fontsize=9,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))

# 3. Binned comparison
ax3 = axes[1, 0]

x = np.arange(len(labels))
width = 0.35

approved_counts = []
rejected_counts = []
for label in labels:
    approved_counts.append((approved['time_bin'] == label).sum())
    rejected_counts.append((rejected['time_bin'] == label).sum())

approved_pcts = [(c / approved_total) * 100 for c in approved_counts]
rejected_pcts = [(c / rejected_total) * 100 for c in rejected_counts]

bars1 = ax3.bar(x - width/2, approved_pcts, width, label='Approved',
                color='green', alpha=0.7, edgecolor='black')
bars2 = ax3.bar(x + width/2, rejected_pcts, width, label='Rejected',
                color='red', alpha=0.7, edgecolor='black')

for bars, pcts, counts in [(bars1, approved_pcts, approved_counts),
                            (bars2, rejected_pcts, rejected_counts)]:
    for bar, pct, count in zip(bars, pcts, counts):
        height = bar.get_height()
        if height > 0.5:
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{pct:.1f}%\n({count:,})',
                    ha='center', va='bottom', fontsize=7, fontweight='bold')

ax3.set_xlabel('Time Period', fontsize=11, fontweight='bold')
ax3.set_ylabel('Percentage of Applications', fontsize=11, fontweight='bold')
ax3.set_title('Time Period Distribution Comparison\n(Percentage with Counts)',
              fontweight='bold', fontsize=14)
ax3.set_xticks(x)
ax3.set_xticklabels(labels, rotation=45, ha='right')
ax3.legend(fontsize=11)
ax3.grid(True, alpha=0.3, axis='y')

# 4. Cumulative distribution
ax4 = axes[1, 1]

approved_cumsum = []
rejected_cumsum = []
cumsum_a = 0
cumsum_r = 0

for label in labels:
    cumsum_a += (approved['time_bin'] == label).sum()
    cumsum_r += (rejected['time_bin'] == label).sum()
    approved_cumsum.append((cumsum_a / approved_total) * 100)
    rejected_cumsum.append((cumsum_r / rejected_total) * 100)

ax4.plot(x, approved_cumsum, marker='o', linewidth=3, markersize=8,
         label='Approved', color='green')
ax4.plot(x, rejected_cumsum, marker='s', linewidth=3, markersize=8,
         label='Rejected', color='red')

for i, (a_pct, r_pct) in enumerate(zip(approved_cumsum, rejected_cumsum)):
    if i % 2 == 0:
        ax4.text(i, a_pct + 2, f'{a_pct:.1f}%', ha='center', fontsize=8,
                color='green', fontweight='bold')
        ax4.text(i, r_pct - 4, f'{r_pct:.1f}%', ha='center', fontsize=8,
                color='red', fontweight='bold')

ax4.set_xlabel('Time Period', fontsize=11, fontweight='bold')
ax4.set_ylabel('Cumulative Percentage', fontsize=11, fontweight='bold')
ax4.set_title('Cumulative Distribution Comparison', fontweight='bold', fontsize=14)
ax4.set_xticks(x)
ax4.set_xticklabels(labels, rotation=45, ha='right')
ax4.legend(fontsize=11)
ax4.grid(True, alpha=0.3)
ax4.set_ylim([0, 105])
ax4.axhline(50, color='gray', linestyle='--', alpha=0.5, linewidth=1)
ax4.axhline(90, color='gray', linestyle='--', alpha=0.5, linewidth=1)

plt.tight_layout()
plt.savefig('name_registration_aligned_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: name_registration_aligned_comparison.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: Side-by-side comparison with Company Registration
# ============================================================================

# Calculate company registration stats for comparison
df_company['approved_date'] = pd.to_datetime(df_company['approved_date'], errors='coerce')
df_company['processing_days'] = (df_company['approved_date'] - df_company['created_date']).dt.total_seconds() / 86400
company_valid = df_company['processing_days'].dropna()

fig, axes = plt.subplots(2, 2, figsize=(22, 14))
fig.suptitle('Comparison: Name Registration vs Company Registration\n(Aligned Date Range)',
             fontsize=18, fontweight='bold', y=0.995)

# 1. Processing time comparison
ax1 = axes[0, 0]

data_to_plot = [
    approved['processing_days'].dropna(),
    rejected['processing_days'].dropna(),
    company_valid
]
labels_plot = ['Name Reg\n(Approved)', 'Name Reg\n(Rejected)', 'Company Reg\n(All Approved)']
colors_box = ['lightgreen', 'lightcoral', 'lightblue']

bp = ax1.boxplot(data_to_plot, labels=labels_plot, patch_artist=True)
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)

ax1.set_ylabel('Days from Creation to Approval', fontsize=11, fontweight='bold')
ax1.set_title('Processing Time Comparison', fontweight='bold', fontsize=14)
ax1.grid(True, alpha=0.3, axis='y')

# Add mean markers
for i, data in enumerate(data_to_plot):
    mean_val = data.mean()
    ax1.plot([i+1], [mean_val], 'r*', markersize=15, zorder=5)
    ax1.text(i+1, mean_val, f' {mean_val:.1f}d', va='center', fontsize=9, fontweight='bold')

# 2. Mean processing time bar chart
ax2 = axes[0, 1]

means = [data.mean() for data in data_to_plot]
bars = ax2.bar(range(len(means)), means, color=colors_box, edgecolor='black', alpha=0.8)

for i, (bar, mean) in enumerate(zip(bars, means)):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{mean:.1f} days',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax2.set_xticks(range(len(labels_plot)))
ax2.set_xticklabels(labels_plot)
ax2.set_ylabel('Average Processing Days', fontsize=11, fontweight='bold')
ax2.set_title('Average Processing Time Comparison', fontweight='bold', fontsize=14)
ax2.grid(True, alpha=0.3, axis='y')

# 3. Volume comparison
ax3 = axes[1, 0]

volumes = [len(approved), len(rejected), len(company_valid)]
bars = ax3.bar(range(len(volumes)), volumes, color=colors_box, edgecolor='black', alpha=0.8)

for i, (bar, vol) in enumerate(zip(bars, volumes)):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
            f'{vol:,}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax3.set_xticks(range(len(labels_plot)))
ax3.set_xticklabels(labels_plot)
ax3.set_ylabel('Number of Records', fontsize=11, fontweight='bold')
ax3.set_title('Volume Comparison', fontweight='bold', fontsize=14)
ax3.grid(True, alpha=0.3, axis='y')

# 4. Approval rate and summary stats
ax4 = axes[1, 1]
ax4.axis('off')

approval_rate = (len(approved) / (len(approved) + len(rejected))) * 100

summary_text = f"""
SUMMARY STATISTICS (Aligned Date Range)
{'='*50}

Date Range: {earliest_company_date.strftime('%Y-%m-%d')} to {latest_company_date.strftime('%Y-%m-%d')}

NAME REGISTRATION:
  Total Records: {len(df_name_filtered):,}
  • Approved: {len(approved):,} ({approval_rate:.1f}%)
  • Rejected: {len(rejected):,} ({100-approval_rate:.1f}%)

  Approved Processing:
    - Mean: {approved['processing_days'].mean():.1f} days
    - Median: {approved['processing_days'].median():.1f} days

  Rejected Processing:
    - Mean: {rejected['processing_days'].mean():.1f} days
    - Median: {rejected['processing_days'].median():.1f} days

COMPANY REGISTRATION:
  Total Records: {len(df_company):,}
  • All Approved: {len(company_valid):,}

  Processing Time:
    - Mean: {company_valid.mean():.1f} days
    - Median: {company_valid.median():.1f} days

COMPARISON:
  • Name Reg (Approved) is {abs(approved['processing_days'].mean() - company_valid.mean()):.1f} days
    {'FASTER' if approved['processing_days'].mean() < company_valid.mean() else 'SLOWER'} than Company Reg

  • Name Reg volume is {len(df_name_filtered) / len(df_company):.1f}x
    {'HIGHER' if len(df_name_filtered) > len(df_company) else 'LOWER'} than Company Reg
"""

ax4.text(0.1, 0.95, summary_text, transform=ax4.transAxes, fontsize=10,
         verticalalignment='top', horizontalalignment='left',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
         family='monospace')

plt.tight_layout()
plt.savefig('name_vs_company_registration_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: name_vs_company_registration_comparison.png")
plt.close()

# ============================================================================
# Export Summary Statistics
# ============================================================================

print("\n" + "="*80)
print("EXPORTING STATISTICS")
print("="*80)

# Time distribution export
export_data = []
for label in labels:
    approved_count = (approved['time_bin'] == label).sum()
    rejected_count = (rejected['time_bin'] == label).sum()
    approved_pct = (approved_count / approved_total) * 100 if approved_total > 0 else 0
    rejected_pct = (rejected_count / rejected_total) * 100 if rejected_total > 0 else 0

    export_data.append({
        'Time_Period': label,
        'Approved_Count': approved_count,
        'Approved_Percentage': approved_pct,
        'Rejected_Count': rejected_count,
        'Rejected_Percentage': rejected_pct,
        'Dataset': 'Name Registration (Aligned)'
    })

dist_df = pd.DataFrame(export_data)
dist_df.to_csv('name_registration_aligned_distribution.csv', index=False)
print("✓ Saved: name_registration_aligned_distribution.csv")

# Summary comparison export
summary_data = {
    'Metric': [],
    'Name_Reg_Approved': [],
    'Name_Reg_Rejected': [],
    'Company_Reg': []
}

metrics = [
    ('Count', len(approved), len(rejected), len(company_valid)),
    ('Mean (days)', approved['processing_days'].mean(), rejected['processing_days'].mean(), company_valid.mean()),
    ('Median (days)', approved['processing_days'].median(), rejected['processing_days'].median(), company_valid.median()),
    ('Std Dev (days)', approved['processing_days'].std(), rejected['processing_days'].std(), company_valid.std()),
    ('Min (days)', approved['processing_days'].min(), rejected['processing_days'].min(), company_valid.min()),
    ('Max (days)', approved['processing_days'].max(), rejected['processing_days'].max(), company_valid.max()),
    ('25th percentile', approved['processing_days'].quantile(0.25), rejected['processing_days'].quantile(0.25), company_valid.quantile(0.25)),
    ('75th percentile', approved['processing_days'].quantile(0.75), rejected['processing_days'].quantile(0.75), company_valid.quantile(0.75)),
    ('90th percentile', approved['processing_days'].quantile(0.90), rejected['processing_days'].quantile(0.90), company_valid.quantile(0.90))
]

for metric, val_a, val_r, val_c in metrics:
    summary_data['Metric'].append(metric)
    summary_data['Name_Reg_Approved'].append(val_a)
    summary_data['Name_Reg_Rejected'].append(val_r)
    summary_data['Company_Reg'].append(val_c)

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv('aligned_comparison_summary.csv', index=False)
print("✓ Saved: aligned_comparison_summary.csv")

print("\n" + "="*80)
print("KEY INSIGHTS (ALIGNED DATE RANGE)")
print("="*80)

print(f"""
DATE ALIGNMENT:
  • Analysis period: {earliest_company_date.strftime('%Y-%m-%d')} to {latest_company_date.strftime('%Y-%m-%d')}
  • Name registration records filtered: {len(df_name) - len(df_name_filtered):,} removed
  • Both datasets now cover the same time period

NAME REGISTRATION (APPROVED):
  • Records: {len(approved):,}
  • Mean processing: {approved['processing_days'].mean():.1f} days
  • Median processing: {approved['processing_days'].median():.1f} days
  • Same-day approvals: {(approved['time_bin'] == 'Same day').sum():,} ({(approved['time_bin'] == 'Same day').sum() / approved_total * 100:.1f}%)
  • Within 1 week: {approved[approved['processing_days'] <= 7].shape[0]:,} ({approved[approved['processing_days'] <= 7].shape[0] / approved_total * 100:.1f}%)

NAME REGISTRATION (REJECTED):
  • Records: {len(rejected):,}
  • Mean processing: {rejected['processing_days'].mean():.1f} days
  • Median processing: {rejected['processing_days'].median():.1f} days
  • Rejection rate: {(len(rejected) / (len(approved) + len(rejected)) * 100):.1f}%

COMPANY REGISTRATION:
  • Records: {len(company_valid):,}
  • Mean processing: {company_valid.mean():.1f} days
  • Median processing: {company_valid.median():.1f} days
  • Approval rate: 100% (only approved records in system)

COMPARISON:
  • Name reg (approved) vs Company reg:
    Difference: {abs(approved['processing_days'].mean() - company_valid.mean()):.1f} days
    Name reg is {'FASTER' if approved['processing_days'].mean() < company_valid.mean() else 'SLOWER'}

  • Volume ratio: {len(df_name_filtered) / len(df_company):.2f}:1
    ({len(df_name_filtered):,} name registrations vs {len(df_company):,} company registrations)

  • Efficiency:
    Name reg approval rate: {approval_rate:.1f}%
    Name reg rejections take {rejected['processing_days'].mean() - approved['processing_days'].mean():.1f} days longer than approvals

FILES GENERATED:
  ✓ name_registration_aligned_comparison.png
  ✓ name_vs_company_registration_comparison.png
  ✓ name_registration_aligned_distribution.csv
  ✓ aligned_comparison_summary.csv
""")

print("="*80)
print("ANALYSIS COMPLETE!")
print("="*80)

