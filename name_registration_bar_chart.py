import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")

print("Loading data...")

# Load company registration to get date range
df_company = pd.read_csv('companyregistrationnewsystem.csv', low_memory=False)
df_company['created_date'] = pd.to_datetime(df_company['created_date'], errors='coerce')
earliest_company_date = df_company['created_date'].min()

# Load and filter name registration data
df_name = pd.read_csv('nameregisvation.csv', low_memory=False)
df_name['created_date'] = pd.to_datetime(df_name['created_date'], errors='coerce')
df_name['approved_date'] = pd.to_datetime(df_name['approved_date'], errors='coerce')

# Filter to aligned date range
df_name_filtered = df_name[df_name['created_date'] >= earliest_company_date].copy()

# Calculate processing time
df_name_filtered['processing_days'] = (df_name_filtered['approved_date'] - df_name_filtered['created_date']).dt.total_seconds() / 86400

# Separate approved and rejected
approved = df_name_filtered[(df_name_filtered['status'] == 'APPROVED') &
                            (df_name_filtered['processing_days'].notna())].copy()
rejected = df_name_filtered[(df_name_filtered['status'] == 'REJECTED') &
                            (df_name_filtered['processing_days'].notna())].copy()

print(f"Approved records: {len(approved):,}")
print(f"Rejected records: {len(rejected):,}")

# Define time bins
bins = [-np.inf, 0, 1, 3, 7, 14, 30, 60, 90, 180, 365, np.inf]
labels = ['Same day', '1 day', '2-3 days', '4-7 days', '1-2 weeks',
          '2-4 weeks', '1-2 months', '2-3 months', '3-6 months', '6-12 months', '1+ year']

approved['time_bin'] = pd.cut(approved['processing_days'], bins=bins, labels=labels)
rejected['time_bin'] = pd.cut(rejected['processing_days'], bins=bins, labels=labels)

approved_total = len(approved)
rejected_total = len(rejected)

# ============================================================================
# VISUALIZATION: Time Period Distribution Bar Chart
# ============================================================================

fig, ax = plt.subplots(1, 1, figsize=(16, 10))

x = np.arange(len(labels))
width = 0.35

# Calculate counts and percentages
approved_counts = []
rejected_counts = []
for label in labels:
    approved_counts.append((approved['time_bin'] == label).sum())
    rejected_counts.append((rejected['time_bin'] == label).sum())

approved_pcts = [(c / approved_total) * 100 for c in approved_counts]
rejected_pcts = [(c / rejected_total) * 100 for c in rejected_counts]

# Create bars
bars1 = ax.bar(x - width/2, approved_pcts, width, label='Approved',
                color='#27ae60', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax.bar(x + width/2, rejected_pcts, width, label='Rejected',
                color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)

# Add percentage and count labels on bars
for bar, pct, count in zip(bars1, approved_pcts, approved_counts):
    height = bar.get_height()
    if height > 0.3:  # Only show label if bar is visible enough
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{pct:.1f}%\n({count:,})',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

for bar, pct, count in zip(bars2, rejected_pcts, rejected_counts):
    height = bar.get_height()
    if height > 0.3:  # Only show label if bar is visible enough
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{pct:.1f}%\n({count:,})',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

# Styling
ax.set_xlabel('Time Period', fontsize=13, fontweight='bold')
ax.set_ylabel('Percentage of Applications', fontsize=13, fontweight='bold')
ax.set_title('Name Registration - Time Period Distribution Comparison\n(Percentage with Counts)',
              fontweight='bold', fontsize=16, pad=20)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=11)
ax.legend(fontsize=12, loc='upper right')
ax.grid(True, alpha=0.3, axis='y', linewidth=1)

# Set y-axis limit to accommodate labels
ax.set_ylim([0, max(max(approved_pcts), max(rejected_pcts)) * 1.15])

# Add comparison text at the bottom
comparison_text = f'From {earliest_company_date.strftime("%Y-%m-%d")} onwards  |  ' \
                 f'Approved: {len(approved):,} records  |  Rejected: {len(rejected):,} records  |  ' \
                 f'Approval Rate: {(len(approved)/(len(approved)+len(rejected))*100):.1f}%'

fig.text(0.5, 0.02, comparison_text, ha='center', fontsize=11, fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.8', facecolor='#ecf0f1', alpha=0.9,
                  edgecolor='#34495e', linewidth=2))

plt.tight_layout(rect=[0, 0.04, 1, 0.96])
plt.savefig('name_registration_time_period_bar_chart.png', dpi=300, bbox_inches='tight')
print("✓ Saved: name_registration_time_period_bar_chart.png")
plt.close()

print("\n" + "="*80)
print("BAR CHART VISUALIZATION COMPLETE!")
print("="*80)
print(f"""
Generated: name_registration_time_period_bar_chart.png

Key Statistics:
  • Approved: {len(approved):,} records
  • Rejected: {len(rejected):,} records
  • Approval Rate: {(len(approved)/(len(approved)+len(rejected))*100):.1f}%

Top Time Periods:
  Approved:
    - Same day: {approved_pcts[0]:.1f}% ({approved_counts[0]:,})
    - Within 1 week: {sum(approved_pcts[:4]):.1f}%

  Rejected:
    - 4-7 days: {rejected_pcts[3]:.1f}% ({rejected_counts[3]:,})
    - Within 1 week: {sum(rejected_pcts[:4]):.1f}%
""")
