import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")

print("Creating corrected company registration time period chart...")

# Load data
df = pd.read_csv('companyregistrationnewsystem.csv', low_memory=False)

# Convert dates
df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
df['approved_date'] = pd.to_datetime(df['approved_date'], errors='coerce')
df['submission_date'] = pd.to_datetime(df['submission_date'], errors='coerce')

# Calculate VALID time periods only
df['created_to_submission_days'] = (df['submission_date'] - df['created_date']).dt.total_seconds() / 86400
df['submission_to_approved_days'] = (df['approved_date'] - df['submission_date']).dt.total_seconds() / 86400
df['created_to_approved_days'] = (df['approved_date'] - df['created_date']).dt.total_seconds() / 86400

# Define time periods - ONLY THE VALID ONES
valid_time_periods = {
    'Created → Submission': 'created_to_submission_days',
    'Submission → Approved': 'submission_to_approved_days',
    'Created → Approved': 'created_to_approved_days'
}

# Define time bins
bins = [-np.inf, 0, 1, 3, 7, 14, 30, 60, 90, 180, 365, np.inf]
labels = ['Same day', '1 day', '2-3 days', '4-7 days', '1-2 weeks',
          '2-4 weeks', '1-2 months', '2-3 months', '3-6 months', '6-12 months', '1+ year']

# Create figure with 3 subplots (not 5)
fig, axes = plt.subplots(1, 3, figsize=(24, 8))
fig.suptitle('Company Registration - Time Period Distribution (CORRECTED)\nOnly Valid Workflow Metrics',
             fontsize=18, fontweight='bold', y=0.98)

for idx, (period_name, col) in enumerate(valid_time_periods.items()):
    ax = axes[idx]

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
        ax.set_title(f'{period_name}\n(Total: {total:,})', fontweight='bold', fontsize=13)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')

        # Add statistics box
        mean_val = valid_data.mean()
        median_val = valid_data.median()
        stats_text = f'Mean: {mean_val:.1f}d\nMedian: {median_val:.1f}d'
        ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8),
               fontweight='bold')

# Add warning note at the bottom
warning_text = '⚠️ NOTE: "Approved → Registration" and "Created → Registration" metrics have been REMOVED because registration_date contains ' \
              'historical company founding dates (e.g., 1936-2009), NOT workflow dates from the current system.'

fig.text(0.5, 0.02, warning_text, ha='center', fontsize=11, fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.8', facecolor='#ffcccc', alpha=0.9,
                  edgecolor='#cc0000', linewidth=2), wrap=True)

plt.tight_layout(rect=[0, 0.06, 1, 0.96])
plt.savefig('company_registration_corrected_distribution.png', dpi=300, bbox_inches='tight')
print("✓ Saved: company_registration_corrected_distribution.png")
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

for period_name, col in valid_time_periods.items():
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
        all_labels.append(f'{period_name}\n(n={total:,})')
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
ax.set_title('Company Registration - Time Period Comparison (CORRECTED)\nAll Valid Metrics',
            fontweight='bold', fontsize=16, pad=20)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=11)
ax.legend(fontsize=11, loc='upper right')
ax.grid(True, alpha=0.3, axis='y')

# Add explanation
explanation = """
KEY INSIGHTS:
• Created → Submission (93.9 days avg): Time users take to prepare application - MAIN BOTTLENECK
• Submission → Approved (1.5 days avg): Fast system processing - VERY EFFICIENT!
• Created → Approved (95.4 days avg): Total time = mostly user preparation time

⚠️ registration_date field removed from analysis - contains historical company founding dates, not workflow dates
"""

ax.text(0.02, 0.98, explanation, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment='left',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#e8f4f8', alpha=0.95,
                 edgecolor='#2980b9', linewidth=2), family='monospace')

plt.tight_layout()
plt.savefig('company_registration_corrected_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: company_registration_corrected_comparison.png")
plt.close()

print("\n" + "="*80)
print("CORRECTED VISUALIZATIONS COMPLETE!")
print("="*80)
print("""
Generated Files:
  1. company_registration_corrected_distribution.png (3 separate charts)
  2. company_registration_corrected_comparison.png (combined comparison)

✅ Only showing VALID metrics:
   - Created → Submission (user preparation: 93.9 days avg)
   - Submission → Approved (system processing: 1.5 days avg)
   - Created → Approved (total time: 95.4 days avg)

❌ Removed INVALID metrics:
   - Approved → Registration (historical dates)
   - Created → Registration (historical dates)
""")

