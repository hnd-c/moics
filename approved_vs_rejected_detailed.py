import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (20, 12)

print("="*80)
print("LOADING DATA")
print("="*80)

# Load data
df = pd.read_csv('nameregisvation.csv', low_memory=False)

# Convert dates
df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
df['approved_date'] = pd.to_datetime(df['approved_date'], errors='coerce')
df['updated_date'] = pd.to_datetime(df['updated_date'], errors='coerce')

# Calculate processing time (created to approved)
df['processing_days'] = (df['approved_date'] - df['created_date']).dt.total_seconds() / 86400

# Filter for APPROVED and REJECTED with valid processing days
approved = df[(df['status'] == 'APPROVED') & (df['processing_days'].notna())].copy()
rejected = df[(df['status'] == 'REJECTED') & (df['processing_days'].notna())].copy()

print(f"\nAPPROVED records with processing time: {len(approved):,}")
print(f"REJECTED records with processing time: {len(rejected):,}")
print(f"Total analyzed: {len(approved) + len(rejected):,}")

# Clean remarks
for df_subset in [approved, rejected]:
    df_subset['remarks_clean'] = df_subset['latest_remarks'].fillna('No remarks')
    df_subset['remarks_clean'] = df_subset['remarks_clean'].str.strip()
    df_subset['remarks_clean'] = df_subset['remarks_clean'].replace(['', ' '], 'No remarks')

print("\n" + "="*80)
print("TIME PERIOD DISTRIBUTION BINS")
print("="*80)

# Define time bins for analysis
bins = [-np.inf, 0, 1, 3, 7, 14, 30, 60, 90, 180, 365, np.inf]
labels = ['Same day', '1 day', '2-3 days', '4-7 days', '1-2 weeks',
          '2-4 weeks', '1-2 months', '2-3 months', '3-6 months', '6-12 months', '1+ year']

approved['time_bin'] = pd.cut(approved['processing_days'], bins=bins, labels=labels)
rejected['time_bin'] = pd.cut(rejected['processing_days'], bins=bins, labels=labels)

# Calculate distributions
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
# VISUALIZATION 1: Main Distribution Comparison with Annotations
# ============================================================================
print("\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

fig, axes = plt.subplots(2, 2, figsize=(22, 14))
fig.suptitle('APPROVED vs REJECTED - Time Period Distribution Analysis',
             fontsize=18, fontweight='bold', y=0.995)

# 1. APPROVED Histogram with annotations
ax1 = axes[0, 0]
counts, bin_edges, patches = ax1.hist(approved['processing_days'], bins=50,
                                       edgecolor='black', alpha=0.7, color='green')

# Add statistics lines
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

# Add text box with summary stats
stats_text = f'Statistics:\n' \
             f'Mean: {mean_val:.1f} days\n' \
             f'Median: {median_val:.1f} days\n' \
             f'Std Dev: {approved["processing_days"].std():.1f} days\n' \
             f'Min: {approved["processing_days"].min():.1f} days\n' \
             f'Max: {approved["processing_days"].max():.1f} days'
ax1.text(0.97, 0.55, stats_text, transform=ax1.transAxes, fontsize=9,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

# 2. REJECTED Histogram with annotations
ax2 = axes[0, 1]
counts, bin_edges, patches = ax2.hist(rejected['processing_days'], bins=50,
                                       edgecolor='black', alpha=0.7, color='red')

# Add statistics lines
mean_val = rejected['processing_days'].mean()
median_val = rejected['processing_days'].median()
ax2.axvline(mean_val, color='darkred', linestyle='--', linewidth=2.5,
            label=f'Mean: {mean_val:.1f} days', zorder=5)
ax2.axvline(median_val, color='blue', linestyle='--', linewidth=2.5,
            label=f'Median: {median_val:.1f} days', zorder=5)

# Add percentile annotations
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

# Add text box with summary stats
stats_text = f'Statistics:\n' \
             f'Mean: {mean_val:.1f} days\n' \
             f'Median: {median_val:.1f} days\n' \
             f'Std Dev: {rejected["processing_days"].std():.1f} days\n' \
             f'Min: {rejected["processing_days"].min():.1f} days\n' \
             f'Max: {rejected["processing_days"].max():.1f} days'
ax2.text(0.97, 0.55, stats_text, transform=ax2.transAxes, fontsize=9,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))

# 3. Binned comparison with percentages
ax3 = axes[1, 0]

# Prepare data for grouped bar chart
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

# Add percentage labels on bars
for bars, pcts, counts in [(bars1, approved_pcts, approved_counts),
                            (bars2, rejected_pcts, rejected_counts)]:
    for bar, pct, count in zip(bars, pcts, counts):
        height = bar.get_height()
        if height > 0.5:  # Only show label if bar is visible
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

# 4. Cumulative distribution comparison
ax4 = axes[1, 1]

# Calculate cumulative percentages
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

# Add percentage annotations
for i, (a_pct, r_pct) in enumerate(zip(approved_cumsum, rejected_cumsum)):
    if i % 2 == 0:  # Annotate every other point to avoid crowding
        ax4.text(i, a_pct + 2, f'{a_pct:.1f}%', ha='center', fontsize=8,
                color='green', fontweight='bold')
        ax4.text(i, r_pct - 4, f'{r_pct:.1f}%', ha='center', fontsize=8,
                color='red', fontweight='bold')

ax4.set_xlabel('Time Period', fontsize=11, fontweight='bold')
ax4.set_ylabel('Cumulative Percentage', fontsize=11, fontweight='bold')
ax4.set_title('Cumulative Distribution Comparison\n(What % are processed by each period)',
              fontweight='bold', fontsize=14)
ax4.set_xticks(x)
ax4.set_xticklabels(labels, rotation=45, ha='right')
ax4.legend(fontsize=11)
ax4.grid(True, alpha=0.3)
ax4.set_ylim([0, 105])
ax4.axhline(50, color='gray', linestyle='--', alpha=0.5, linewidth=1)
ax4.axhline(90, color='gray', linestyle='--', alpha=0.5, linewidth=1)

plt.tight_layout()
plt.savefig('approved_vs_rejected_distribution_detailed.png', dpi=300, bbox_inches='tight')
print("✓ Saved: approved_vs_rejected_distribution_detailed.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: Rejection Remarks Analysis
# ============================================================================
print("\nAnalyzing rejection remarks...")

print("\n" + "="*80)
print("REJECTION REMARKS ANALYSIS")
print("="*80)

# Get top rejection reasons
top_reasons = rejected['remarks_clean'].value_counts().head(15)
print(f"\nTop 15 Rejection Reasons (out of {len(rejected):,} rejections):")
print("-"*80)
print(f"{'Rank':<6} {'Count':>8} {'Percentage':>12} {'Reason'}")
print("-"*80)
for rank, (reason, count) in enumerate(top_reasons.items(), 1):
    pct = (count / len(rejected)) * 100
    reason_short = reason[:60] + '...' if len(reason) > 60 else reason
    print(f"{rank:<6} {count:>8,} {pct:>11.2f}% {reason_short}")

# Create visualization for top rejection reasons
fig, axes = plt.subplots(2, 2, figsize=(22, 16))
fig.suptitle('REJECTION ANALYSIS - Reasons and Time Patterns',
             fontsize=18, fontweight='bold', y=0.995)

# 1. Top rejection reasons
ax1 = axes[0, 0]
reasons_to_plot = top_reasons.head(10)
y_pos = np.arange(len(reasons_to_plot))

# Shorten labels for display
short_labels = []
for reason in reasons_to_plot.index:
    if len(reason) > 50:
        short_labels.append(reason[:47] + '...')
    else:
        short_labels.append(reason)

bars = ax1.barh(y_pos, reasons_to_plot.values, color='red', alpha=0.7, edgecolor='black')
ax1.set_yticks(y_pos)
ax1.set_yticklabels(short_labels, fontsize=10)
ax1.set_xlabel('Number of Rejections', fontsize=11, fontweight='bold')
ax1.set_title('Top 10 Rejection Reasons', fontweight='bold', fontsize=14)
ax1.invert_yaxis()

# Add count and percentage labels
for i, (bar, count) in enumerate(zip(bars, reasons_to_plot.values)):
    pct = (count / len(rejected)) * 100
    ax1.text(count, i, f' {count:,} ({pct:.1f}%)',
             va='center', fontsize=9, fontweight='bold')

ax1.grid(True, alpha=0.3, axis='x')

# 2. Processing time by rejection reason (top 10)
ax2 = axes[0, 1]

top_reasons_list = top_reasons.head(10).index.tolist()
data_to_plot = []
labels_to_plot = []

for reason in top_reasons_list:
    reason_data = rejected[rejected['remarks_clean'] == reason]['processing_days'].dropna()
    if len(reason_data) > 0:
        data_to_plot.append(reason_data)
        # Short label
        if len(reason) > 30:
            labels_to_plot.append(reason[:27] + '...')
        else:
            labels_to_plot.append(reason)

bp = ax2.boxplot(data_to_plot, labels=labels_to_plot, patch_artist=True, vert=False)
for patch in bp['boxes']:
    patch.set_facecolor('lightcoral')

ax2.set_xlabel('Days from Creation to Rejection', fontsize=11, fontweight='bold')
ax2.set_ylabel('Rejection Reason', fontsize=11, fontweight='bold')
ax2.set_title('Processing Time by Rejection Reason', fontweight='bold', fontsize=14)
ax2.grid(True, alpha=0.3, axis='x')

# Add mean values
for i, data in enumerate(data_to_plot):
    mean_val = data.mean()
    ax2.plot([mean_val], [i+1], 'r*', markersize=12, zorder=5)
    ax2.text(mean_val, i+1, f' {mean_val:.1f}d', va='center', fontsize=8)

# 3. Time distribution for top 3 rejection reasons
ax3 = axes[1, 0]

top_3_reasons = top_reasons.head(3).index.tolist()
colors = ['darkred', 'orangered', 'lightcoral']

for reason, color in zip(top_3_reasons, colors):
    reason_data = rejected[rejected['remarks_clean'] == reason]['processing_days']
    label = (reason[:30] + '...') if len(reason) > 30 else reason
    ax3.hist(reason_data, bins=30, alpha=0.5, label=label, color=color, edgecolor='black')

ax3.set_xlabel('Days from Creation to Rejection', fontsize=11, fontweight='bold')
ax3.set_ylabel('Number of Applications', fontsize=11, fontweight='bold')
ax3.set_title('Time Distribution for Top 3 Rejection Reasons', fontweight='bold', fontsize=14)
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)

# 4. Percentage breakdown in pie chart
ax4 = axes[1, 1]

# Group smaller reasons
top_5 = top_reasons.head(5)
others_count = len(rejected) - top_5.sum()

plot_data = list(top_5.values) + [others_count]
plot_labels = []
for reason in top_5.index:
    label = (reason[:25] + '...') if len(reason) > 25 else reason
    plot_labels.append(label)
plot_labels.append('Others')

colors_pie = ['#ff6b6b', '#ee5a6f', '#c44569', '#a53860', '#862a5c', '#666666']
explode = [0.05, 0.02, 0.02, 0.02, 0.02, 0.05]

wedges, texts, autotexts = ax4.pie(plot_data, labels=plot_labels, autopct='%1.1f%%',
                                     colors=colors_pie, explode=explode,
                                     startangle=90, textprops={'fontsize': 10})

# Make percentage text bold
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(9)

ax4.set_title('Rejection Reasons Distribution\n(Percentage Breakdown)',
              fontweight='bold', fontsize=14)

plt.tight_layout()
plt.savefig('rejection_reasons_detailed.png', dpi=300, bbox_inches='tight')
print("✓ Saved: rejection_reasons_detailed.png")
plt.close()

# ============================================================================
# VISUALIZATION 3: Company Type Analysis
# ============================================================================
print("\nAnalyzing by company type...")

fig, axes = plt.subplots(2, 2, figsize=(22, 14))
fig.suptitle('Company Type Analysis - APPROVED vs REJECTED',
             fontsize=18, fontweight='bold', y=0.995)

# Get top company types
top_types = df['company_type_id'].value_counts().head(10).index

# 1. Approval rate by company type
ax1 = axes[0, 0]

approval_rates = []
type_labels = []
total_counts = []

for ctype in top_types:
    total = len(df[(df['company_type_id'] == ctype) &
                   (df['status'].isin(['APPROVED', 'REJECTED']))])
    approved_count = len(df[(df['company_type_id'] == ctype) &
                           (df['status'] == 'APPROVED')])
    if total > 0:
        rate = (approved_count / total) * 100
        approval_rates.append(rate)
        type_labels.append(f'Type {ctype}')
        total_counts.append(total)

y_pos = np.arange(len(approval_rates))
bars = ax1.barh(y_pos, approval_rates)

# Color bars based on approval rate
for bar, rate in zip(bars, approval_rates):
    if rate >= 95:
        bar.set_color('darkgreen')
    elif rate >= 90:
        bar.set_color('green')
    elif rate >= 85:
        bar.set_color('yellow')
    else:
        bar.set_color('red')

ax1.set_yticks(y_pos)
ax1.set_yticklabels(type_labels)
ax1.set_xlabel('Approval Rate (%)', fontsize=11, fontweight='bold')
ax1.set_title('Approval Rate by Company Type', fontweight='bold', fontsize=14)
ax1.invert_yaxis()
ax1.set_xlim([0, 100])

# Add labels
for i, (rate, count) in enumerate(zip(approval_rates, total_counts)):
    ax1.text(rate, i, f' {rate:.1f}% (n={count:,})',
             va='center', fontsize=9, fontweight='bold')

ax1.grid(True, alpha=0.3, axis='x')

# 2. Processing time by company type - APPROVED
ax2 = axes[0, 1]

data_to_plot = []
labels_to_plot = []

for ctype in top_types:
    type_data = approved[approved['company_type_id'] == ctype]['processing_days'].dropna()
    if len(type_data) > 10:  # Only include if sufficient data
        data_to_plot.append(type_data)
        labels_to_plot.append(f'Type {ctype}')

bp = ax2.boxplot(data_to_plot, labels=labels_to_plot, patch_artist=True)
for patch in bp['boxes']:
    patch.set_facecolor('lightgreen')

ax2.set_ylabel('Days from Creation to Approval', fontsize=11, fontweight='bold')
ax2.set_xlabel('Company Type', fontsize=11, fontweight='bold')
ax2.set_title('APPROVED - Processing Time by Company Type', fontweight='bold', fontsize=14)
ax2.grid(True, alpha=0.3, axis='y')

# 3. Processing time by company type - REJECTED
ax3 = axes[1, 0]

data_to_plot = []
labels_to_plot = []

for ctype in top_types:
    type_data = rejected[rejected['company_type_id'] == ctype]['processing_days'].dropna()
    if len(type_data) > 5:  # Only include if sufficient data
        data_to_plot.append(type_data)
        labels_to_plot.append(f'Type {ctype}')

if data_to_plot:
    bp = ax3.boxplot(data_to_plot, labels=labels_to_plot, patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor('lightcoral')

    ax3.set_ylabel('Days from Creation to Rejection', fontsize=11, fontweight='bold')
    ax3.set_xlabel('Company Type', fontsize=11, fontweight='bold')
    ax3.set_title('REJECTED - Processing Time by Company Type', fontweight='bold', fontsize=14)
    ax3.grid(True, alpha=0.3, axis='y')

# 4. Count comparison
ax4 = axes[1, 1]

approved_counts = []
rejected_counts = []

for ctype in top_types:
    approved_counts.append(len(approved[approved['company_type_id'] == ctype]))
    rejected_counts.append(len(rejected[rejected['company_type_id'] == ctype]))

x = np.arange(len(top_types))
width = 0.35

bars1 = ax4.bar(x - width/2, approved_counts, width, label='Approved',
                color='green', alpha=0.7, edgecolor='black')
bars2 = ax4.bar(x + width/2, rejected_counts, width, label='Rejected',
                color='red', alpha=0.7, edgecolor='black')

# Add count labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}',
                    ha='center', va='bottom', fontsize=8, fontweight='bold')

ax4.set_xlabel('Company Type ID', fontsize=11, fontweight='bold')
ax4.set_ylabel('Number of Applications', fontsize=11, fontweight='bold')
ax4.set_title('Application Count by Company Type and Status', fontweight='bold', fontsize=14)
ax4.set_xticks(x)
ax4.set_xticklabels([f'Type {t}' for t in top_types], rotation=45, ha='right')
ax4.legend(fontsize=11)
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('company_type_approved_vs_rejected.png', dpi=300, bbox_inches='tight')
print("✓ Saved: company_type_approved_vs_rejected.png")
plt.close()

# ============================================================================
# Export detailed statistics
# ============================================================================
print("\n" + "="*80)
print("EXPORTING DETAILED STATISTICS")
print("="*80)

# Time period distribution export
export_data = []
for label in labels:
    approved_count = (approved['time_bin'] == label).sum()
    rejected_count = (rejected['time_bin'] == label).sum()
    approved_pct = (approved_count / approved_total) * 100
    rejected_pct = (rejected_count / rejected_total) * 100

    export_data.append({
        'Time_Period': label,
        'Approved_Count': approved_count,
        'Approved_Percentage': approved_pct,
        'Rejected_Count': rejected_count,
        'Rejected_Percentage': rejected_pct,
        'Ratio_Approved_to_Rejected': approved_count / rejected_count if rejected_count > 0 else np.inf
    })

time_dist_df = pd.DataFrame(export_data)
time_dist_df.to_csv('time_period_distribution_comparison.csv', index=False)
print("✓ Saved: time_period_distribution_comparison.csv")

# Rejection reasons export
rejection_reasons_df = rejected['remarks_clean'].value_counts().reset_index()
rejection_reasons_df.columns = ['Rejection_Reason', 'Count']
rejection_reasons_df['Percentage'] = (rejection_reasons_df['Count'] / len(rejected)) * 100

# Add average processing time for each reason
avg_times = []
for reason in rejection_reasons_df['Rejection_Reason']:
    avg_time = rejected[rejected['remarks_clean'] == reason]['processing_days'].mean()
    avg_times.append(avg_time)
rejection_reasons_df['Average_Processing_Days'] = avg_times

rejection_reasons_df.to_csv('rejection_reasons_summary.csv', index=False)
print("✓ Saved: rejection_reasons_summary.csv")

# Company type analysis export
company_type_data = []
for ctype in top_types:
    total = len(df[(df['company_type_id'] == ctype) &
                   (df['status'].isin(['APPROVED', 'REJECTED']))])
    approved_count = len(approved[approved['company_type_id'] == ctype])
    rejected_count = len(rejected[rejected['company_type_id'] == ctype])

    approved_avg_time = approved[approved['company_type_id'] == ctype]['processing_days'].mean()
    rejected_avg_time = rejected[rejected['company_type_id'] == ctype]['processing_days'].mean()

    approval_rate = (approved_count / total * 100) if total > 0 else 0

    company_type_data.append({
        'Company_Type_ID': ctype,
        'Total_Applications': total,
        'Approved_Count': approved_count,
        'Rejected_Count': rejected_count,
        'Approval_Rate': approval_rate,
        'Avg_Approval_Time_Days': approved_avg_time,
        'Avg_Rejection_Time_Days': rejected_avg_time
    })

company_type_df = pd.DataFrame(company_type_data)
company_type_df.to_csv('company_type_analysis.csv', index=False)
print("✓ Saved: company_type_analysis.csv")

print("\n" + "="*80)
print("KEY INSIGHTS SUMMARY")
print("="*80)

print(f"""
1. PROCESSING TIME COMPARISON:
   - APPROVED: Mean = {approved['processing_days'].mean():.1f} days, Median = {approved['processing_days'].median():.1f} days
   - REJECTED: Mean = {rejected['processing_days'].mean():.1f} days, Median = {rejected['processing_days'].median():.1f} days
   - Difference: Rejections take {rejected['processing_days'].mean() - approved['processing_days'].mean():.1f} days longer on average

2. APPROVAL RATE:
   - Overall: {(approved_total / (approved_total + rejected_total) * 100):.1f}%
   - Total Approved: {approved_total:,}
   - Total Rejected: {rejected_total:,}

3. QUICK PROCESSING:
   - Approved same day: {(approved['time_bin'] == 'Same day').sum():,} ({((approved['time_bin'] == 'Same day').sum() / approved_total * 100):.1f}%)
   - Approved within 1 week: {approved[approved['processing_days'] <= 7].shape[0]:,} ({(approved[approved['processing_days'] <= 7].shape[0] / approved_total * 100):.1f}%)

4. TOP REJECTION REASON:
   - {top_reasons.index[0]}: {top_reasons.iloc[0]:,} rejections ({(top_reasons.iloc[0] / len(rejected) * 100):.1f}%)
   - Average processing time: {rejected[rejected['remarks_clean'] == top_reasons.index[0]]['processing_days'].mean():.1f} days

5. FILES GENERATED:
   ✓ approved_vs_rejected_distribution_detailed.png
   ✓ rejection_reasons_detailed.png
   ✓ company_type_approved_vs_rejected.png
   ✓ time_period_distribution_comparison.csv
   ✓ rejection_reasons_summary.csv
   ✓ company_type_analysis.csv
""")

print("="*80)
print("ANALYSIS COMPLETE!")
print("="*80)


