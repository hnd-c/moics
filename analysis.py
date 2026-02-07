import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)

# Load the data
print("Loading data...")
df_name = pd.read_csv('nameregisvation.csv', low_memory=False)

print(f"Dataset shape: {df_name.shape}")
print(f"\nColumns: {df_name.columns.tolist()}\n")

# Convert date columns to datetime
date_columns = ['created_date', 'updated_date', 'approved_date', 'expire_date', 'submission_date']
for col in date_columns:
    if col in df_name.columns:
        df_name[col] = pd.to_datetime(df_name[col], errors='coerce')
        print(f"{col} - Non-null values: {df_name[col].notna().sum()}")

print("\n" + "="*80)
print("CALCULATING TIME PERIODS")
print("="*80 + "\n")

# Calculate time differences (in days)
df_name['created_to_updated_days'] = (df_name['updated_date'] - df_name['created_date']).dt.total_seconds() / 86400
df_name['updated_to_approved_days'] = (df_name['approved_date'] - df_name['updated_date']).dt.total_seconds() / 86400
df_name['created_to_approved_days'] = (df_name['approved_date'] - df_name['created_date']).dt.total_seconds() / 86400

# Basic statistics
print("Time Period Statistics (in days):")
print("-" * 80)
periods = {
    'Created to Updated': 'created_to_updated_days',
    'Updated to Approved': 'updated_to_approved_days',
    'Created to Approved': 'created_to_approved_days'
}

for period_name, col in periods.items():
    valid_data = df_name[col].dropna()
    if len(valid_data) > 0:
        print(f"\n{period_name}:")
        print(f"  Count: {len(valid_data)}")
        print(f"  Mean: {valid_data.mean():.2f} days")
        print(f"  Median: {valid_data.median():.2f} days")
        print(f"  Std Dev: {valid_data.std():.2f} days")
        print(f"  Min: {valid_data.min():.2f} days")
        print(f"  Max: {valid_data.max():.2f} days")
        print(f"  25th percentile: {valid_data.quantile(0.25):.2f} days")
        print(f"  75th percentile: {valid_data.quantile(0.75):.2f} days")

# ============================================================================
# VISUALIZATION 1: Overall Time Period Distributions
# ============================================================================
print("\n" + "="*80)
print("Creating visualizations...")
print("="*80 + "\n")

fig, axes = plt.subplots(3, 2, figsize=(18, 15))
fig.suptitle('Time Period Analysis - Overall Distributions', fontsize=16, fontweight='bold')

for idx, (period_name, col) in enumerate(periods.items()):
    valid_data = df_name[col].dropna()

    if len(valid_data) > 0:
        # Histogram
        axes[idx, 0].hist(valid_data, bins=50, edgecolor='black', alpha=0.7)
        axes[idx, 0].set_title(f'{period_name} - Distribution', fontweight='bold')
        axes[idx, 0].set_xlabel('Days')
        axes[idx, 0].set_ylabel('Frequency')
        axes[idx, 0].axvline(valid_data.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {valid_data.mean():.1f}')
        axes[idx, 0].axvline(valid_data.median(), color='green', linestyle='--', linewidth=2, label=f'Median: {valid_data.median():.1f}')
        axes[idx, 0].legend()

        # Box plot
        axes[idx, 1].boxplot(valid_data, vert=True)
        axes[idx, 1].set_title(f'{period_name} - Box Plot', fontweight='bold')
        axes[idx, 1].set_ylabel('Days')
        axes[idx, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('time_period_overall_distribution.png', dpi=300, bbox_inches='tight')
print("✓ Saved: time_period_overall_distribution.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: Analysis by is_group_company
# ============================================================================
print("Analyzing by is_group_company...")

if 'is_group_company' in df_name.columns:
    fig, axes = plt.subplots(3, 2, figsize=(18, 15))
    fig.suptitle('Time Period Analysis by Group Company Status', fontsize=16, fontweight='bold')

    for idx, (period_name, col) in enumerate(periods.items()):
        # Box plot comparison
        data_to_plot = []
        labels = []
        for group_status in df_name['is_group_company'].dropna().unique():
            group_data = df_name[df_name['is_group_company'] == group_status][col].dropna()
            if len(group_data) > 0:
                data_to_plot.append(group_data)
                labels.append(str(group_status))

        if data_to_plot:
            axes[idx, 0].boxplot(data_to_plot, labels=labels)
            axes[idx, 0].set_title(f'{period_name} by Group Company', fontweight='bold')
            axes[idx, 0].set_xlabel('Is Group Company')
            axes[idx, 0].set_ylabel('Days')
            axes[idx, 0].grid(True, alpha=0.3)

            # Violin plot
            plot_df = df_name[['is_group_company', col]].dropna()
            if len(plot_df) > 0:
                sns.violinplot(data=plot_df, x='is_group_company', y=col, ax=axes[idx, 1])
                axes[idx, 1].set_title(f'{period_name} - Distribution by Group Company', fontweight='bold')
                axes[idx, 1].set_xlabel('Is Group Company')
                axes[idx, 1].set_ylabel('Days')

    plt.tight_layout()
    plt.savefig('time_period_by_group_company.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: time_period_by_group_company.png")
    plt.close()

    # Statistical summary by group company
    print("\nStatistics by Group Company:")
    print("-" * 80)
    for period_name, col in periods.items():
        print(f"\n{period_name}:")
        summary = df_name.groupby('is_group_company')[col].agg(['count', 'mean', 'median', 'std'])
        print(summary)

# ============================================================================
# VISUALIZATION 3: Analysis by master_company_category
# ============================================================================
print("\nAnalyzing by master_company_category...")

if 'master_company_category' in df_name.columns:
    # Get top categories by count
    top_categories = df_name['master_company_category'].value_counts().head(10).index
    df_filtered = df_name[df_name['master_company_category'].isin(top_categories)]

    fig, axes = plt.subplots(3, 1, figsize=(20, 15))
    fig.suptitle('Time Period Analysis by Master Company Category (Top 10)', fontsize=16, fontweight='bold')

    for idx, (period_name, col) in enumerate(periods.items()):
        plot_df = df_filtered[['master_company_category', col]].dropna()
        if len(plot_df) > 0:
            # Calculate mean for each category and sort
            category_means = plot_df.groupby('master_company_category')[col].mean().sort_values()
            sorted_categories = category_means.index.tolist()

            sns.boxplot(data=plot_df, x='master_company_category', y=col,
                       order=sorted_categories, ax=axes[idx])
            axes[idx].set_title(f'{period_name} by Company Category', fontweight='bold')
            axes[idx].set_xlabel('Master Company Category')
            axes[idx].set_ylabel('Days')
            axes[idx].tick_params(axis='x', rotation=45)

            # Add mean line for each category
            for i, cat in enumerate(sorted_categories):
                mean_val = category_means[cat]
                axes[idx].plot([i-0.4, i+0.4], [mean_val, mean_val], 'r-', linewidth=2)

    plt.tight_layout()
    plt.savefig('time_period_by_company_category.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: time_period_by_company_category.png")
    plt.close()

    # Statistical summary by category
    print("\nStatistics by Master Company Category (Top 10):")
    print("-" * 80)
    for period_name, col in periods.items():
        print(f"\n{period_name}:")
        summary = df_filtered.groupby('master_company_category')[col].agg(['count', 'mean', 'median', 'std']).sort_values('mean')
        print(summary)

# ============================================================================
# VISUALIZATION 4: Analysis by company_type_id
# ============================================================================
print("\nAnalyzing by company_type_id...")

if 'company_type_id' in df_name.columns:
    # Get top company types by count
    top_types = df_name['company_type_id'].value_counts().head(10).index
    df_filtered = df_name[df_name['company_type_id'].isin(top_types)]

    fig, axes = plt.subplots(3, 1, figsize=(20, 15))
    fig.suptitle('Time Period Analysis by Company Type ID (Top 10)', fontsize=16, fontweight='bold')

    for idx, (period_name, col) in enumerate(periods.items()):
        plot_df = df_filtered[['company_type_id', col]].dropna()
        if len(plot_df) > 0:
            # Calculate mean for each type and sort
            type_means = plot_df.groupby('company_type_id')[col].mean().sort_values()
            sorted_types = type_means.index.tolist()

            sns.boxplot(data=plot_df, x='company_type_id', y=col,
                       order=sorted_types, ax=axes[idx])
            axes[idx].set_title(f'{period_name} by Company Type', fontweight='bold')
            axes[idx].set_xlabel('Company Type ID')
            axes[idx].set_ylabel('Days')

            # Add mean line for each type
            for i, typ in enumerate(sorted_types):
                mean_val = type_means[typ]
                axes[idx].plot([i-0.4, i+0.4], [mean_val, mean_val], 'r-', linewidth=2)

    plt.tight_layout()
    plt.savefig('time_period_by_company_type.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: time_period_by_company_type.png")
    plt.close()

    # Statistical summary by company type
    print("\nStatistics by Company Type ID (Top 10):")
    print("-" * 80)
    for period_name, col in periods.items():
        print(f"\n{period_name}:")
        summary = df_filtered.groupby('company_type_id')[col].agg(['count', 'mean', 'median', 'std']).sort_values('mean')
        print(summary)

# ============================================================================
# VISUALIZATION 5: Heatmap of correlations and combined analysis
# ============================================================================
print("\nCreating combined analysis visualization...")

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Correlation heatmap
ax1 = fig.add_subplot(gs[0, :])
correlation_cols = ['created_to_updated_days', 'updated_to_approved_days', 'created_to_approved_days']
numeric_cols = correlation_cols.copy()
if 'company_type_id' in df_name.columns:
    numeric_cols.append('company_type_id')
if 'is_group_company' in df_name.columns:
    numeric_cols.append('is_group_company')

corr_matrix = df_name[numeric_cols].corr()
sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0, ax=ax1)
ax1.set_title('Correlation Matrix of Time Periods and Categories', fontweight='bold', fontsize=14)

# Time series trends (if we can extract year/month)
if df_name['created_date'].notna().sum() > 0:
    ax2 = fig.add_subplot(gs[1, :])
    df_name['year_month'] = df_name['created_date'].dt.to_period('M')
    monthly_stats = df_name.groupby('year_month')['created_to_approved_days'].agg(['mean', 'count'])
    monthly_stats = monthly_stats[monthly_stats['count'] >= 10]  # Filter months with at least 10 records

    if len(monthly_stats) > 0:
        monthly_stats.index = monthly_stats.index.to_timestamp()
        ax2.plot(monthly_stats.index, monthly_stats['mean'], marker='o', linewidth=2)
        ax2.set_title('Average Created-to-Approved Time Trend Over Time', fontweight='bold', fontsize=14)
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Average Days')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)

# Summary statistics table
ax3 = fig.add_subplot(gs[2, :])
ax3.axis('tight')
ax3.axis('off')

summary_data = []
for period_name, col in periods.items():
    valid_data = df_name[col].dropna()
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

table = ax3.table(cellText=summary_data,
                 colLabels=['Period', 'Count', 'Mean (days)', 'Median (days)', 'Std Dev', 'Min', 'Max'],
                 cellLoc='center',
                 loc='center',
                 bbox=[0, 0, 1, 1])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)

# Style header row
for i in range(7):
    table[(0, i)].set_facecolor('#4CAF50')
    table[(0, i)].set_text_props(weight='bold', color='white')

fig.suptitle('Combined Time Period Analysis Summary', fontsize=16, fontweight='bold', y=0.995)
plt.savefig('time_period_combined_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: time_period_combined_analysis.png")
plt.close()

# ============================================================================
# EXPORT SUMMARY TO CSV
# ============================================================================
print("\nExporting summary statistics to CSV...")

summary_list = []
for period_name, col in periods.items():
    # Overall statistics
    valid_data = df_name[col].dropna()
    if len(valid_data) > 0:
        summary_list.append({
            'Analysis_Type': 'Overall',
            'Category': 'All',
            'Time_Period': period_name,
            'Count': len(valid_data),
            'Mean_Days': valid_data.mean(),
            'Median_Days': valid_data.median(),
            'Std_Dev': valid_data.std(),
            'Min_Days': valid_data.min(),
            'Max_Days': valid_data.max()
        })

    # By is_group_company
    if 'is_group_company' in df_name.columns:
        for group_status in df_name['is_group_company'].dropna().unique():
            group_data = df_name[df_name['is_group_company'] == group_status][col].dropna()
            if len(group_data) > 0:
                summary_list.append({
                    'Analysis_Type': 'is_group_company',
                    'Category': str(group_status),
                    'Time_Period': period_name,
                    'Count': len(group_data),
                    'Mean_Days': group_data.mean(),
                    'Median_Days': group_data.median(),
                    'Std_Dev': group_data.std(),
                    'Min_Days': group_data.min(),
                    'Max_Days': group_data.max()
                })

    # By master_company_category (top 10)
    if 'master_company_category' in df_name.columns:
        top_categories = df_name['master_company_category'].value_counts().head(10).index
        for category in top_categories:
            cat_data = df_name[df_name['master_company_category'] == category][col].dropna()
            if len(cat_data) > 0:
                summary_list.append({
                    'Analysis_Type': 'master_company_category',
                    'Category': str(category),
                    'Time_Period': period_name,
                    'Count': len(cat_data),
                    'Mean_Days': cat_data.mean(),
                    'Median_Days': cat_data.median(),
                    'Std_Dev': cat_data.std(),
                    'Min_Days': cat_data.min(),
                    'Max_Days': cat_data.max()
                })

    # By company_type_id (top 10)
    if 'company_type_id' in df_name.columns:
        top_types = df_name['company_type_id'].value_counts().head(10).index
        for company_type in top_types:
            type_data = df_name[df_name['company_type_id'] == company_type][col].dropna()
            if len(type_data) > 0:
                summary_list.append({
                    'Analysis_Type': 'company_type_id',
                    'Category': str(company_type),
                    'Time_Period': period_name,
                    'Count': len(type_data),
                    'Mean_Days': type_data.mean(),
                    'Median_Days': type_data.median(),
                    'Std_Dev': type_data.std(),
                    'Min_Days': type_data.min(),
                    'Max_Days': type_data.max()
                })

summary_df = pd.DataFrame(summary_list)
summary_df.to_csv('time_period_analysis_summary.csv', index=False)
print("✓ Saved: time_period_analysis_summary.csv")

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print("\nGenerated files:")
print("  1. time_period_overall_distribution.png")
print("  2. time_period_by_group_company.png")
print("  3. time_period_by_company_category.png")
print("  4. time_period_by_company_type.png")
print("  5. time_period_combined_analysis.png")
print("  6. time_period_analysis_summary.csv")
print("\nAll visualizations and summary statistics have been saved!")


