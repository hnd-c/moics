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

# ============================================================================
# VISUALIZATION: Histogram-based Time Period Distribution
# ============================================================================

fig, axes = plt.subplots(1, 2, figsize=(24, 10))
fig.suptitle(f'Name Registration - Time Period Distribution (Aligned Date Range)\nFrom {earliest_company_date.strftime("%Y-%m-%d")} onwards',
             fontsize=20, fontweight='bold', y=0.98)

# 1. APPROVED Histogram
ax1 = axes[0]
counts, bin_edges, patches = ax1.hist(approved['processing_days'], bins=50,
                                       edgecolor='black', alpha=0.75, color='#2ecc71', linewidth=1.5)

# Calculate statistics
mean_val = approved['processing_days'].mean()
median_val = approved['processing_days'].median()

# Add mean and median lines
ax1.axvline(mean_val, color='#e74c3c', linestyle='--', linewidth=3,
            label=f'Mean: {mean_val:.1f} days', zorder=5)
ax1.axvline(median_val, color='#3498db', linestyle='--', linewidth=3,
            label=f'Median: {median_val:.1f} days', zorder=5)

# Add percentile annotations
percentiles = [50, 75, 90, 95, 99]
y_max = counts.max()
colors_percentile = ['#3498db', '#9b59b6', '#f39c12', '#e67e22', '#c0392b']

for i, (pct, color) in enumerate(zip(percentiles, colors_percentile)):
    val = np.percentile(approved['processing_days'], pct)
    ax1.axvline(val, color=color, linestyle=':', linewidth=2, alpha=0.6)

    # Position labels to avoid overlap
    y_pos = y_max * (0.92 - (i % 3) * 0.12)
    x_offset = 5 if i >= 3 else 0

    ax1.text(val + x_offset, y_pos, f'{pct}th: {val:.1f}d',
             rotation=0, fontsize=10, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.7, edgecolor='black'),
             color='white')

# Styling
ax1.set_title(f'APPROVED Applications (n={len(approved):,})',
              fontweight='bold', fontsize=16, pad=20, color='#27ae60')
ax1.set_xlabel('Days from Creation to Approval', fontsize=13, fontweight='bold')
ax1.set_ylabel('Number of Applications', fontsize=13, fontweight='bold')
ax1.legend(loc='upper right', fontsize=12, framealpha=0.9)
ax1.grid(True, alpha=0.3, linewidth=1)

# Add statistics box
stats_text = f'STATISTICS\n' + '─'*25 + '\n' \
             f'Mean:        {mean_val:>8.1f} days\n' \
             f'Median:      {median_val:>8.1f} days\n' \
             f'Std Dev:     {approved["processing_days"].std():>8.1f} days\n' \
             f'Min:         {approved["processing_days"].min():>8.1f} days\n' \
             f'Max:         {approved["processing_days"].max():>8.1f} days\n' \
             f'─'*25 + '\n' \
             f'Same Day:    {(approved["processing_days"] < 0.5).sum():>8,} ({(approved["processing_days"] < 0.5).sum()/len(approved)*100:>5.1f}%)\n' \
             f'≤ 1 week:    {(approved["processing_days"] <= 7).sum():>8,} ({(approved["processing_days"] <= 7).sum()/len(approved)*100:>5.1f}%)\n' \
             f'≤ 1 month:   {(approved["processing_days"] <= 30).sum():>8,} ({(approved["processing_days"] <= 30).sum()/len(approved)*100:>5.1f}%)'

ax1.text(0.98, 0.58, stats_text, transform=ax1.transAxes, fontsize=10,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round,pad=1', facecolor='#d5f4e6', alpha=0.9, edgecolor='#27ae60', linewidth=2),
         family='monospace', fontweight='bold')

# 2. REJECTED Histogram
ax2 = axes[1]
counts, bin_edges, patches = ax2.hist(rejected['processing_days'], bins=50,
                                       edgecolor='black', alpha=0.75, color='#e74c3c', linewidth=1.5)

# Calculate statistics
mean_val = rejected['processing_days'].mean()
median_val = rejected['processing_days'].median()

# Add mean and median lines
ax2.axvline(mean_val, color='#c0392b', linestyle='--', linewidth=3,
            label=f'Mean: {mean_val:.1f} days', zorder=5)
ax2.axvline(median_val, color='#3498db', linestyle='--', linewidth=3,
            label=f'Median: {median_val:.1f} days', zorder=5)

# Add percentile annotations
y_max = counts.max()
for i, (pct, color) in enumerate(zip(percentiles, colors_percentile)):
    val = np.percentile(rejected['processing_days'], pct)
    ax2.axvline(val, color=color, linestyle=':', linewidth=2, alpha=0.6)

    # Position labels to avoid overlap
    y_pos = y_max * (0.92 - (i % 3) * 0.12)
    x_offset = 5 if i >= 3 else 0

    ax2.text(val + x_offset, y_pos, f'{pct}th: {val:.1f}d',
             rotation=0, fontsize=10, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.7, edgecolor='black'),
             color='white')

# Styling
ax2.set_title(f'REJECTED Applications (n={len(rejected):,})',
              fontweight='bold', fontsize=16, pad=20, color='#c0392b')
ax2.set_xlabel('Days from Creation to Rejection', fontsize=13, fontweight='bold')
ax2.set_ylabel('Number of Applications', fontsize=13, fontweight='bold')
ax2.legend(loc='upper right', fontsize=12, framealpha=0.9)
ax2.grid(True, alpha=0.3, linewidth=1)

# Add statistics box
stats_text = f'STATISTICS\n' + '─'*25 + '\n' \
             f'Mean:        {mean_val:>8.1f} days\n' \
             f'Median:      {median_val:>8.1f} days\n' \
             f'Std Dev:     {rejected["processing_days"].std():>8.1f} days\n' \
             f'Min:         {rejected["processing_days"].min():>8.1f} days\n' \
             f'Max:         {rejected["processing_days"].max():>8.1f} days\n' \
             f'─'*25 + '\n' \
             f'Same Day:    {(rejected["processing_days"] < 0.5).sum():>8,} ({(rejected["processing_days"] < 0.5).sum()/len(rejected)*100:>5.1f}%)\n' \
             f'≤ 1 week:    {(rejected["processing_days"] <= 7).sum():>8,} ({(rejected["processing_days"] <= 7).sum()/len(rejected)*100:>5.1f}%)\n' \
             f'≤ 1 month:   {(rejected["processing_days"] <= 30).sum():>8,} ({(rejected["processing_days"] <= 30).sum()/len(rejected)*100:>5.1f}%)'

ax2.text(0.98, 0.58, stats_text, transform=ax2.transAxes, fontsize=10,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round,pad=1', facecolor='#fadbd8', alpha=0.9, edgecolor='#c0392b', linewidth=2),
         family='monospace', fontweight='bold')

# Add overall comparison text at the bottom
comparison_text = f'KEY COMPARISON:  Approved mean: {approved["processing_days"].mean():.1f} days  |  Rejected mean: {rejected["processing_days"].mean():.1f} days  |  ' \
                 f'Difference: {abs(rejected["processing_days"].mean() - approved["processing_days"].mean()):.1f} days ({rejected["processing_days"].mean() / approved["processing_days"].mean():.1f}x slower)'

fig.text(0.5, 0.02, comparison_text, ha='center', fontsize=12, fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.8', facecolor='#ecf0f1', alpha=0.9, edgecolor='#34495e', linewidth=2))

plt.tight_layout(rect=[0, 0.04, 1, 0.96])
plt.savefig('name_registration_histograms_only.png', dpi=300, bbox_inches='tight')
print("✓ Saved: name_registration_histograms_only.png")
plt.close()

# ============================================================================
# Also create a single large histogram comparison overlay
# ============================================================================

fig, ax = plt.subplots(1, 1, figsize=(20, 12))

# Plot both distributions with transparency
ax.hist(approved['processing_days'], bins=60, alpha=0.6, color='#2ecc71',
        edgecolor='black', linewidth=1, label=f'Approved (n={len(approved):,})')
ax.hist(rejected['processing_days'], bins=60, alpha=0.6, color='#e74c3c',
        edgecolor='black', linewidth=1, label=f'Rejected (n={len(rejected):,})')

# Add mean lines for both
approved_mean = approved['processing_days'].mean()
rejected_mean = rejected['processing_days'].mean()

ax.axvline(approved_mean, color='#27ae60', linestyle='--', linewidth=3,
          label=f'Approved Mean: {approved_mean:.1f} days')
ax.axvline(rejected_mean, color='#c0392b', linestyle='--', linewidth=3,
          label=f'Rejected Mean: {rejected_mean:.1f} days')

# Styling
ax.set_title(f'Name Registration - Approved vs Rejected Time Distribution (Overlay)\nFrom {earliest_company_date.strftime("%Y-%m-%d")} onwards',
            fontweight='bold', fontsize=18, pad=20)
ax.set_xlabel('Days from Creation to Decision', fontsize=14, fontweight='bold')
ax.set_ylabel('Number of Applications', fontsize=14, fontweight='bold')
ax.legend(loc='upper right', fontsize=13, framealpha=0.95)
ax.grid(True, alpha=0.3, linewidth=1)

# Add statistics comparison box
comparison_stats = f'PROCESSING TIME COMPARISON\n' + '='*40 + '\n\n' \
                  f'APPROVED:\n' \
                  f'  Mean:      {approved["processing_days"].mean():>8.1f} days\n' \
                  f'  Median:    {approved["processing_days"].median():>8.1f} days\n' \
                  f'  Same Day:  {(approved["processing_days"] < 0.5).sum():>8,} ({(approved["processing_days"] < 0.5).sum()/len(approved)*100:>5.1f}%)\n' \
                  f'  ≤ 1 week:  {(approved["processing_days"] <= 7).sum():>8,} ({(approved["processing_days"] <= 7).sum()/len(approved)*100:>5.1f}%)\n\n' \
                  f'REJECTED:\n' \
                  f'  Mean:      {rejected["processing_days"].mean():>8.1f} days\n' \
                  f'  Median:    {rejected["processing_days"].median():>8.1f} days\n' \
                  f'  Same Day:  {(rejected["processing_days"] < 0.5).sum():>8,} ({(rejected["processing_days"] < 0.5).sum()/len(rejected)*100:>5.1f}%)\n' \
                  f'  ≤ 1 week:  {(rejected["processing_days"] <= 7).sum():>8,} ({(rejected["processing_days"] <= 7).sum()/len(rejected)*100:>5.1f}%)\n\n' \
                  f'DIFFERENCE:\n' \
                  f'  Rejected takes {rejected["processing_days"].mean() - approved["processing_days"].mean():>5.1f} days longer\n' \
                  f'  Rejected is {rejected["processing_days"].mean() / approved["processing_days"].mean():>5.1f}x slower than Approved'

ax.text(0.98, 0.97, comparison_stats, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round,pad=1', facecolor='#ecf0f1', alpha=0.95, edgecolor='#34495e', linewidth=2),
        family='monospace', fontweight='bold')

plt.tight_layout()
plt.savefig('name_registration_histogram_overlay.png', dpi=300, bbox_inches='tight')
print("✓ Saved: name_registration_histogram_overlay.png")
plt.close()

print("\n" + "="*80)
print("HISTOGRAM VISUALIZATIONS COMPLETE!")
print("="*80)
print("""
Generated Files:
  1. name_registration_histograms_only.png (side-by-side histograms)
  2. name_registration_histogram_overlay.png (overlaid comparison)

Both visualizations show the time period distributions with:
  ✓ Detailed statistics boxes
  ✓ Percentile annotations (50th, 75th, 90th, 95th, 99th)
  ✓ Mean and median lines
  ✓ Processing time breakdowns
""")

