import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (20, 12)

print("="*80)
print("LOADING COMPANY REGISTRATION DATA")
print("="*80)

# Load data
df = pd.read_csv('companyregistrationnewsystem.csv', low_memory=False)

print(f"\nDataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}\n")

# Convert date columns to datetime
date_columns = ['created_date', 'updated_date', 'approved_date', 'registration_date', 'submission_date']
for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        print(f"{col} - Non-null values: {df[col].notna().sum():,}")

print("\n" + "="*80)
print("CALCULATING TIME PERIODS")
print("="*80)

# Calculate time differences (in days)
df['created_to_submission_days'] = (df['submission_date'] - df['created_date']).dt.total_seconds() / 86400
df['created_to_approved_days'] = (df['approved_date'] - df['created_date']).dt.total_seconds() / 86400
df['submission_to_approved_days'] = (df['approved_date'] - df['submission_date']).dt.total_seconds() / 86400
df['approved_to_registration_days'] = (df['registration_date'] - df['approved_date']).dt.total_seconds() / 86400
df['created_to_registration_days'] = (df['registration_date'] - df['created_date']).dt.total_seconds() / 86400

# Define time periods to analyze
time_periods = {
    'Created → Submission': 'created_to_submission_days',
    'Created → Approved': 'created_to_approved_days',
    'Submission → Approved': 'submission_to_approved_days',
    'Approved → Registration': 'approved_to_registration_days',
    'Created → Registration (Total)': 'created_to_registration_days'
}

# Print basic statistics
print("\nTime Period Statistics (in days):")
print("-"*80)
print(f"{'Period':<35} {'Count':>10} {'Mean':>10} {'Median':>10} {'Std':>10} {'Min':>10} {'Max':>10}")
print("-"*80)

for period_name, col in time_periods.items():
    valid_data = df[col].dropna()
    if len(valid_data) > 0:
        print(f"{period_name:<35} {len(valid_data):>10,} {valid_data.mean():>10.1f} "
              f"{valid_data.median():>10.1f} {valid_data.std():>10.1f} "
              f"{valid_data.min():>10.1f} {valid_data.max():>10.1f}")

# Define bins for distribution analysis
bins = [-np.inf, 0, 1, 3, 7, 14, 30, 60, 90, 180, 365, np.inf]
labels = ['Same day', '1 day', '2-3 days', '4-7 days', '1-2 weeks',
          '2-4 weeks', '1-2 months', '2-3 months', '3-6 months', '6-12 months', '1+ year']

print("\n" + "="*80)
print("TIME PERIOD DISTRIBUTION ANALYSIS")
print("="*80)

# Analyze each time period
distribution_data = {}
for period_name, col in time_periods.items():
    valid_data = df[col].dropna()
    if len(valid_data) > 0:
        df[f'{col}_bin'] = pd.cut(df[col], bins=bins, labels=labels)
        dist = df[f'{col}_bin'].value_counts().sort_index()
        distribution_data[period_name] = dist

        print(f"\n{period_name}:")
        print("-"*80)
        print(f"{'Time Period':<15} {'Count':>12} {'Percentage':>12} {'Cumulative':>12}")
        print("-"*80)

        total = len(valid_data)
        cumulative = 0
        for period, count in dist.items():
            pct = (count / total) * 100
            cumulative += pct
            print(f"{str(period):<15} {count:>12,} {pct:>11.2f}% {cumulative:>11.2f}%")

# ============================================================================
# VISUALIZATION 1: Main Distribution with Percentages
# ============================================================================
print("\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

fig = plt.figure(figsize=(24, 16))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# Plot each time period distribution
plot_configs = [
    ('Created → Submission', 'created_to_submission_days', 0, 0, 'blue'),
    ('Created → Approved', 'created_to_approved_days', 0, 1, 'green'),
    ('Submission → Approved', 'submission_to_approved_days', 1, 0, 'orange'),
    ('Approved → Registration', 'approved_to_registration_days', 1, 1, 'purple'),
    ('Created → Registration (Total)', 'created_to_registration_days', 2, 0, 'red')
]

for title, col, row, col_idx, color in plot_configs:
    ax = fig.add_subplot(gs[row, col_idx])

    valid_data = df[col].dropna()
    if len(valid_data) > 0:
        # Create histogram
        counts, bin_edges, patches = ax.hist(valid_data, bins=50, edgecolor='black',
                                             alpha=0.7, color=color)

        # Add statistics lines
        mean_val = valid_data.mean()
        median_val = valid_data.median()
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2.5,
                  label=f'Mean: {mean_val:.1f} days', zorder=5)
        ax.axvline(median_val, color='darkblue', linestyle='--', linewidth=2.5,
                  label=f'Median: {median_val:.1f} days', zorder=5)

        # Add percentile annotations
        percentiles = [50, 75, 90, 95]
        y_max = counts.max()
        for i, pct in enumerate(percentiles):
            val = np.percentile(valid_data, pct)
            ax.axvline(val, color='gray', linestyle=':', linewidth=1.5, alpha=0.5)
            ax.text(val, y_max * (0.95 - i*0.08), f'{pct}th: {val:.1f}d',
                   rotation=0, fontsize=8,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

        ax.set_title(f'{title}\n(n={len(valid_data):,})', fontweight='bold', fontsize=13)
        ax.set_xlabel('Days', fontsize=10, fontweight='bold')
        ax.set_ylabel('Number of Applications', fontsize=10, fontweight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)

        # Add statistics box
        stats_text = f'Statistics:\n' \
                    f'Mean: {mean_val:.1f} days\n' \
                    f'Median: {median_val:.1f} days\n' \
                    f'Std Dev: {valid_data.std():.1f} days\n' \
                    f'Min: {valid_data.min():.1f} days\n' \
                    f'Max: {valid_data.max():.1f} days'
        ax.text(0.97, 0.60, stats_text, transform=ax.transAxes, fontsize=8,
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

# Last subplot: Summary comparison
ax = fig.add_subplot(gs[2, 1])
ax.axis('off')

# Create summary table
summary_data = []
for period_name, col in time_periods.items():
    valid_data = df[col].dropna()
    if len(valid_data) > 0:
        summary_data.append([
            period_name,
            f"{len(valid_data):,}",
            f"{valid_data.mean():.1f}",
            f"{valid_data.median():.1f}",
            f"{valid_data.std():.1f}",
            f"{valid_data.min():.1f}",
            f"{valid_data.max():.1f}"
        ])

table = ax.table(cellText=summary_data,
                colLabels=['Period', 'Count', 'Mean', 'Median', 'Std Dev', 'Min', 'Max'],
                cellLoc='center',
                loc='center',
                bbox=[0, 0, 1, 1])
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2)

# Style header row
for i in range(7):
    table[(0, i)].set_facecolor('#4CAF50')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Alternate row colors
for i in range(1, len(summary_data) + 1):
    for j in range(7):
        if i % 2 == 0:
            table[(i, j)].set_facecolor('#f0f0f0')

fig.suptitle('Company Registration - Time Period Distribution Analysis',
             fontsize=18, fontweight='bold', y=0.995)
plt.savefig('company_registration_time_distribution.png', dpi=300, bbox_inches='tight')
print("✓ Saved: company_registration_time_distribution.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: Binned Distribution with Percentages
# ============================================================================

fig, axes = plt.subplots(3, 2, figsize=(24, 18))
fig.suptitle('Company Registration - Time Period Distribution by Bins (with Percentages)',
             fontsize=18, fontweight='bold', y=0.995)

plot_idx = 0
for period_name, col in time_periods.items():
    row = plot_idx // 2
    col_idx = plot_idx % 2
    ax = axes[row, col_idx]

    valid_data = df[col].dropna()
    if len(valid_data) > 0:
        bin_col = f'{col}_bin'
        dist = df[bin_col].value_counts().sort_index()
        total = len(valid_data)

        # Prepare data
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

        x = np.arange(len(labels))
        bars = ax.bar(x, percentages, color=plt.cm.viridis(np.linspace(0, 1, len(labels))),
                     edgecolor='black', alpha=0.8)

        # Add count and percentage labels
        for i, (bar, pct, count) in enumerate(zip(bars, percentages, counts)):
            height = bar.get_height()
            if height > 0.5:  # Only show label if bar is visible
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{pct:.1f}%\n({count:,})',
                       ha='center', va='bottom', fontsize=8, fontweight='bold')

        ax.set_xlabel('Time Period', fontsize=11, fontweight='bold')
        ax.set_ylabel('Percentage of Applications', fontsize=11, fontweight='bold')
        ax.set_title(f'{period_name}\n(Total: {total:,})', fontweight='bold', fontsize=13)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')

    plot_idx += 1

# Remove unused subplot if odd number of periods
if plot_idx < 6:
    fig.delaxes(axes[2, 1])

plt.tight_layout()
plt.savefig('company_registration_binned_distribution.png', dpi=300, bbox_inches='tight')
print("✓ Saved: company_registration_binned_distribution.png")
plt.close()

# ============================================================================
# VISUALIZATION 3: Cumulative Distribution Comparison
# ============================================================================

fig, ax = plt.subplots(1, 1, figsize=(20, 10))

colors = ['blue', 'green', 'orange', 'purple', 'red']
markers = ['o', 's', '^', 'D', 'v']

for idx, (period_name, col) in enumerate(time_periods.items()):
    valid_data = df[col].dropna()
    if len(valid_data) > 0:
        bin_col = f'{col}_bin'
        dist = df[bin_col].value_counts().sort_index()
        total = len(valid_data)

        # Calculate cumulative percentages
        cumulative = []
        cumsum = 0
        for label in labels:
            if label in dist.index:
                cumsum += dist[label]
            cumulative.append((cumsum / total) * 100)

        x = np.arange(len(labels))
        ax.plot(x, cumulative, marker=markers[idx], linewidth=2.5, markersize=8,
               label=period_name, color=colors[idx])

ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
ax.set_ylabel('Cumulative Percentage', fontsize=12, fontweight='bold')
ax.set_title('Cumulative Distribution Comparison - All Time Periods\n(What % are processed by each period)',
            fontweight='bold', fontsize=16)
ax.set_xticks(np.arange(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha='right')
ax.legend(fontsize=11, loc='lower right')
ax.grid(True, alpha=0.3)
ax.set_ylim([0, 105])

# Add reference lines
ax.axhline(50, color='gray', linestyle='--', alpha=0.5, linewidth=1, label='50%')
ax.axhline(90, color='gray', linestyle='--', alpha=0.5, linewidth=1, label='90%')

plt.tight_layout()
plt.savefig('company_registration_cumulative_distribution.png', dpi=300, bbox_inches='tight')
print("✓ Saved: company_registration_cumulative_distribution.png")
plt.close()

# ============================================================================
# VISUALIZATION 4: Company Type Analysis
# ============================================================================

if 'company_type_id' in df.columns:
    print("\nAnalyzing by company type...")

    # Get top company types
    top_types = df['company_type_id'].value_counts().head(10).index

    fig, axes = plt.subplots(2, 3, figsize=(24, 16))
    fig.suptitle('Company Registration Time Analysis by Company Type',
                fontsize=18, fontweight='bold', y=0.995)

    # For each major time period, create box plot by company type
    major_periods = [
        ('Created → Submission', 'created_to_submission_days', 0, 0),
        ('Created → Approved', 'created_to_approved_days', 0, 1),
        ('Submission → Approved', 'submission_to_approved_days', 0, 2),
        ('Approved → Registration', 'approved_to_registration_days', 1, 0),
        ('Created → Registration', 'created_to_registration_days', 1, 1)
    ]

    for period_name, col, row, col_idx in major_periods:
        ax = axes[row, col_idx]

        data_to_plot = []
        labels_to_plot = []

        for ctype in top_types:
            type_data = df[df['company_type_id'] == ctype][col].dropna()
            if len(type_data) > 10:  # Only include if sufficient data
                data_to_plot.append(type_data)
                labels_to_plot.append(f'Type {ctype}')

        if data_to_plot:
            bp = ax.boxplot(data_to_plot, labels=labels_to_plot, patch_artist=True)
            for patch in bp['boxes']:
                patch.set_facecolor('lightblue')

            ax.set_ylabel('Days', fontsize=10, fontweight='bold')
            ax.set_xlabel('Company Type', fontsize=10, fontweight='bold')
            ax.set_title(f'{period_name} by Company Type', fontweight='bold', fontsize=12)
            ax.grid(True, alpha=0.3, axis='y')
            ax.tick_params(axis='x', rotation=45)

    # Last subplot: Count by company type
    ax = axes[1, 2]
    type_counts = df['company_type_id'].value_counts().head(10)
    y_pos = np.arange(len(type_counts))

    bars = ax.barh(y_pos, type_counts.values, color='steelblue', edgecolor='black', alpha=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f'Type {t}' for t in type_counts.index])
    ax.set_xlabel('Number of Registrations', fontsize=10, fontweight='bold')
    ax.set_title('Top 10 Company Types by Count', fontweight='bold', fontsize=12)
    ax.invert_yaxis()

    # Add count labels
    for i, (bar, count) in enumerate(zip(bars, type_counts.values)):
        ax.text(count, i, f' {count:,}', va='center', fontsize=9, fontweight='bold')

    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig('company_registration_by_company_type.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: company_registration_by_company_type.png")
    plt.close()

# ============================================================================
# VISUALIZATION 5: Monthly Trends
# ============================================================================

print("\nAnalyzing monthly trends...")

if df['created_date'].notna().sum() > 0:
    df['created_year_month'] = df['created_date'].dt.to_period('M')
    df['approved_year_month'] = df['approved_date'].dt.to_period('M')

    fig, axes = plt.subplots(2, 2, figsize=(24, 14))
    fig.suptitle('Company Registration - Monthly Trends', fontsize=18, fontweight='bold', y=0.995)

    # 1. Number of registrations per month
    ax1 = axes[0, 0]
    monthly_counts = df.groupby('created_year_month').size()
    monthly_counts_recent = monthly_counts.tail(24)  # Last 24 months

    if len(monthly_counts_recent) > 0:
        monthly_counts_recent.index = monthly_counts_recent.index.to_timestamp()
        ax1.plot(monthly_counts_recent.index, monthly_counts_recent.values,
                marker='o', linewidth=2, markersize=6, color='blue')
        ax1.set_title('Monthly Registration Volume (Last 24 Months)', fontweight='bold', fontsize=13)
        ax1.set_xlabel('Month', fontsize=10, fontweight='bold')
        ax1.set_ylabel('Number of Registrations', fontsize=10, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)

        # Add simple trend line using numpy polyfit
        x_numeric = np.arange(len(monthly_counts_recent))
        z = np.polyfit(x_numeric, monthly_counts_recent.values, 1)
        p = np.poly1d(z)
        trend_line = p(x_numeric)
        ax1.plot(monthly_counts_recent.index, trend_line, 'r--', linewidth=2,
                label=f'Trend (slope={z[0]:.1f})')
        ax1.legend()

    # 2. Average processing time per month
    ax2 = axes[0, 1]
    monthly_processing = df.groupby('created_year_month')['created_to_approved_days'].mean()
    monthly_processing_recent = monthly_processing.tail(24)

    if len(monthly_processing_recent) > 0:
        monthly_processing_recent.index = monthly_processing_recent.index.to_timestamp()
        ax2.plot(monthly_processing_recent.index, monthly_processing_recent.values,
                marker='s', linewidth=2, markersize=6, color='green')
        ax2.set_title('Average Created→Approved Time per Month', fontweight='bold', fontsize=13)
        ax2.set_xlabel('Month', fontsize=10, fontweight='bold')
        ax2.set_ylabel('Average Days', fontsize=10, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)

    # 3. Approval time distribution over time (heatmap style)
    ax3 = axes[1, 0]
    df_recent = df[df['created_year_month'].notna()].copy()
    df_recent = df_recent[df_recent['created_year_month'] >= df_recent['created_year_month'].max() - 23]

    if len(df_recent) > 0:
        pivot_data = df_recent.groupby(['created_year_month', 'created_to_approved_days_bin']).size().unstack(fill_value=0)
        if not pivot_data.empty:
            pivot_pct = pivot_data.div(pivot_data.sum(axis=1), axis=0) * 100

            # Only show recent months
            pivot_pct = pivot_pct.tail(12)
            pivot_pct.index = pivot_pct.index.astype(str)

            sns.heatmap(pivot_pct.T, annot=True, fmt='.0f', cmap='YlOrRd',
                       cbar_kws={'label': 'Percentage'}, ax=ax3)
            ax3.set_title('Time Period Distribution by Month (Last 12 Months)',
                         fontweight='bold', fontsize=13)
            ax3.set_xlabel('Month', fontsize=10, fontweight='bold')
            ax3.set_ylabel('Time Period', fontsize=10, fontweight='bold')
            ax3.tick_params(axis='x', rotation=45)

    # 4. Summary statistics table
    ax4 = axes[1, 1]
    ax4.axis('off')

    # Calculate monthly statistics for recent period
    recent_stats = []
    for period_name, col in list(time_periods.items())[:3]:  # Top 3 periods
        recent_avg = df[col].tail(1000).mean()  # Last 1000 records
        overall_avg = df[col].mean()
        recent_stats.append([
            period_name,
            f"{overall_avg:.1f}",
            f"{recent_avg:.1f}",
            f"{((recent_avg - overall_avg) / overall_avg * 100):.1f}%" if overall_avg != 0 else "N/A"
        ])

    table = ax4.table(cellText=recent_stats,
                     colLabels=['Period', 'Overall Avg', 'Recent Avg\n(Last 1000)', 'Change'],
                     cellLoc='center',
                     loc='center',
                     bbox=[0, 0.2, 1, 0.6])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)

    for i in range(4):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')

    ax4.text(0.5, 0.9, 'Processing Time Trends', transform=ax4.transAxes,
            fontsize=14, fontweight='bold', ha='center')

    plt.tight_layout()
    plt.savefig('company_registration_monthly_trends.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: company_registration_monthly_trends.png")
    plt.close()

# ============================================================================
# Export detailed statistics to CSV
# ============================================================================

print("\n" + "="*80)
print("EXPORTING DETAILED STATISTICS")
print("="*80)

# Time period distribution export
export_data = []
for period_name, col in time_periods.items():
    valid_data = df[col].dropna()
    if len(valid_data) > 0:
        bin_col = f'{col}_bin'
        dist = df[bin_col].value_counts().sort_index()
        total = len(valid_data)

        for label in labels:
            if label in dist.index:
                count = dist[label]
                percentage = (count / total) * 100
            else:
                count = 0
                percentage = 0

            export_data.append({
                'Time_Period_Type': period_name,
                'Time_Bin': label,
                'Count': count,
                'Percentage': percentage,
                'Total_Records': total
            })

distribution_df = pd.DataFrame(export_data)
distribution_df.to_csv('company_registration_time_distribution.csv', index=False)
print("✓ Saved: company_registration_time_distribution.csv")

# Summary statistics by company type
if 'company_type_id' in df.columns:
    company_type_stats = []
    for ctype in top_types:
        type_df = df[df['company_type_id'] == ctype]

        stats_row = {
            'Company_Type_ID': ctype,
            'Total_Count': len(type_df)
        }

        for period_name, col in time_periods.items():
            type_data = type_df[col].dropna()
            if len(type_data) > 0:
                stats_row[f'{period_name}_Mean'] = type_data.mean()
                stats_row[f'{period_name}_Median'] = type_data.median()
                stats_row[f'{period_name}_Count'] = len(type_data)
            else:
                stats_row[f'{period_name}_Mean'] = None
                stats_row[f'{period_name}_Median'] = None
                stats_row[f'{period_name}_Count'] = 0

        company_type_stats.append(stats_row)

    company_type_df = pd.DataFrame(company_type_stats)
    company_type_df.to_csv('company_registration_by_type.csv', index=False)
    print("✓ Saved: company_registration_by_type.csv")

# Overall summary
summary_stats = []
for period_name, col in time_periods.items():
    valid_data = df[col].dropna()
    if len(valid_data) > 0:
        summary_stats.append({
            'Period': period_name,
            'Total_Count': len(valid_data),
            'Mean_Days': valid_data.mean(),
            'Median_Days': valid_data.median(),
            'Std_Dev': valid_data.std(),
            'Min_Days': valid_data.min(),
            'Max_Days': valid_data.max(),
            'Q25': valid_data.quantile(0.25),
            'Q75': valid_data.quantile(0.75),
            'Q90': valid_data.quantile(0.90),
            'Q95': valid_data.quantile(0.95)
        })

summary_df = pd.DataFrame(summary_stats)
summary_df.to_csv('company_registration_summary.csv', index=False)
print("✓ Saved: company_registration_summary.csv")

print("\n" + "="*80)
print("KEY INSIGHTS")
print("="*80)

print(f"""
COMPANY REGISTRATION TIME ANALYSIS SUMMARY

1. DATASET OVERVIEW:
   - Total Records: {len(df):,}
   - Records with approval data: {df['approved_date'].notna().sum():,}
   - Date Range: {df['created_date'].min().strftime('%Y-%m-%d') if df['created_date'].notna().sum() > 0 else 'N/A'} to {df['created_date'].max().strftime('%Y-%m-%d') if df['created_date'].notna().sum() > 0 else 'N/A'}

2. AVERAGE PROCESSING TIMES:
""")

for period_name, col in time_periods.items():
    valid_data = df[col].dropna()
    if len(valid_data) > 0:
        print(f"   - {period_name}: {valid_data.mean():.1f} days (median: {valid_data.median():.1f})")

print(f"""
3. QUICKEST PROCESSING:
   - Same-day Created→Submission: {(df['created_to_submission_days_bin'] == 'Same day').sum():,} ({(df['created_to_submission_days_bin'] == 'Same day').sum() / df['created_to_submission_days'].notna().sum() * 100:.1f}%)
   - Same-day Created→Approved: {(df['created_to_approved_days_bin'] == 'Same day').sum():,} ({(df['created_to_approved_days_bin'] == 'Same day').sum() / df['created_to_approved_days'].notna().sum() * 100:.1f}%)

4. FILES GENERATED:
   ✓ company_registration_time_distribution.png
   ✓ company_registration_binned_distribution.png
   ✓ company_registration_cumulative_distribution.png
   ✓ company_registration_by_company_type.png
   ✓ company_registration_monthly_trends.png
   ✓ company_registration_time_distribution.csv
   ✓ company_registration_by_type.csv
   ✓ company_registration_summary.csv
""")

print("="*80)
print("ANALYSIS COMPLETE!")
print("="*80)

