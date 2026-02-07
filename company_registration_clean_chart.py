import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")

print("Creating clean company registration time period charts...")

# Load data
df = pd.read_csv('companyregistrationnewsystem.csv', low_memory=False)

# Convert dates
df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
df['approved_date'] = pd.to_datetime(df['approved_date'], errors='coerce')
df['submission_date'] = pd.to_datetime(df['submission_date'], errors='coerce')

# Calculate time periods
df['created_to_submission_days'] = (df['submission_date'] - df['created_date']).dt.total_seconds() / 86400
df['submission_to_approved_days'] = (df['approved_date'] - df['submission_date']).dt.total_seconds() / 86400
df['created_to_approved_days'] = (df['approved_date'] - df['created_date']).dt.total_seconds() / 86400

# Define time periods
time_periods = {
    'Created → Submission': 'created_to_submission_days',
    'Submission → Approved': 'submission_to_approved_days',
    'Created → Approved': 'created_to_approved_days'
}

# Define time bins
bins = [-np.inf, 0, 1, 3, 7, 14, 30, 60, 90, 180, 365, np.inf]
labels = ['Same day', '1 day', '2-3 days', '4-7 days', '1-2 weeks',
          '2-4 weeks', '1-2 months', '2-3 months', '3-6 months', '6-12 months', '1+ year']

# Create 3 separate figures, each with annotation "1 of 3", "2 of 3", "3 of 3"
for idx, (period_name, col) in enumerate(time_periods.items()):
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))

    # Add annotation in top-right corner
    fig.text(0.98, 0.98, f'{idx + 1} of 3',
             fontsize=16, fontweight='bold',
             ha='right', va='top',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))

    valid_data = df[col].dropna()
    if len(valid_data) > 0:
        # Create bins
        df[f'{col}_bin'] = pd.cut(df[col], bins=bins, labels=labels)
        dist = df[f'{col}_bin'].value_counts().sort_index()
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
                     edgecolor='black', alpha=0.8, linewidth=1.5)

        # Add count and percentage labels
        for i, (bar, pct, count) in enumerate(zip(bars, percentages, counts)):
            height = bar.get_height()
            if height > 0.5:  # Only show label if bar is visible
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{pct:.1f}%\n({count:,})',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')

        ax.set_xlabel('Time Period', fontsize=11, fontweight='bold')
        ax.set_ylabel('Percentage of Applications', fontsize=11, fontweight='bold')
        ax.set_title(f'Company Registration - Time Period Distribution by Bins\n{period_name} (Total: {total:,})',
                    fontweight='bold', fontsize=13)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    filename = f'company_registration_time_distribution_clean_{idx + 1}_of_3.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {filename}")
    plt.close()

# Also create a single comparison bar chart
fig, ax = plt.subplots(1, 1, figsize=(18, 10))

# Prepare data for all 3 periods in one chart
all_data = []
all_labels = []
all_colors = []

color_map = {
    'Created → Submission': '#3498db',
    'Submission → Approved': '#2ecc71',
    'Created → Approved': '#e67e22'
}

for period_name, col in time_periods.items():
    valid_data = df[col].dropna()
    if len(valid_data) > 0:
        df[f'{col}_bin'] = pd.cut(df[col], bins=bins, labels=labels)
        dist = df[f'{col}_bin'].value_counts().sort_index()
        total = len(valid_data)

        counts = []
        for label in labels:
            if label in dist.index:
                counts.append(dist[label])
            else:
                counts.append(0)

        percentages = [(c / total) * 100 for c in counts]
        all_data.append(percentages)
        all_labels.append(f'{period_name} (n={total:,})')
        all_colors.append(color_map[period_name])

# Create grouped bar chart
x = np.arange(len(labels))
width = 0.25

bars1 = ax.bar(x - width, all_data[0], width, label=all_labels[0],
               color=all_colors[0], alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax.bar(x, all_data[1], width, label=all_labels[1],
               color=all_colors[1], alpha=0.8, edgecolor='black', linewidth=1.5)
bars3 = ax.bar(x + width, all_data[2], width, label=all_labels[2],
               color=all_colors[2], alpha=0.8, edgecolor='black', linewidth=1.5)

# Add labels on bars
for bars, data in zip([bars1, bars2, bars3], all_data):
    for bar, pct in zip(bars, data):
        height = bar.get_height()
        if height > 1:  # Only show if visible
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{pct:.1f}%',
                   ha='center', va='bottom', fontsize=8, fontweight='bold')

ax.set_xlabel('Time Period', fontsize=13, fontweight='bold')
ax.set_ylabel('Percentage of Applications', fontsize=13, fontweight='bold')
ax.set_title('Company Registration - Time Period Comparison',
            fontweight='bold', fontsize=16, pad=20)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=11)
ax.legend(fontsize=12, loc='upper right')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('company_registration_time_comparison_clean.png', dpi=300, bbox_inches='tight')
print("✓ Saved: company_registration_time_comparison_clean.png")
plt.close()

print("\n" + "="*80)
print("CLEAN VISUALIZATIONS COMPLETE!")
print("="*80)
print("""
Generated Files:
  1. company_registration_time_distribution_clean_1_of_3.png
  2. company_registration_time_distribution_clean_2_of_3.png
  3. company_registration_time_distribution_clean_3_of_3.png
  4. company_registration_time_comparison_clean.png (combined comparison)

No commentary, warnings, or notes included.
""")

