import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")

print("Creating discounted deregistration three-phase time distribution charts...")

# Today's date for pending calculations
today = pd.Timestamp('2026-01-25')

# Define time bins
bins = [-np.inf, 0, 1, 3, 7, 14, 30, 60, 90, 180, 365, np.inf]
labels = ['Same day', '1 day', '2-3 days', '4-7 days', '1-2 weeks',
          '2-4 weeks', '1-2 months', '2-3 months', '3-6 months', '6-12 months', '1+ year']

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

# ============================================================================
# PHASE 1: Initial Discount Application (Bargaining & Discount Calculation)
# ============================================================================
print("\nProcessing Phase 1: Initial Discount Application...")

df1 = pd.read_csv('discountedderegistration.csv', low_memory=False)
df1['created_date'] = pd.to_datetime(df1['created_date'], errors='coerce')
df1['submission_date'] = pd.to_datetime(df1['submission_date'], errors='coerce')
df1['approved_date'] = pd.to_datetime(df1['approved_date'], errors='coerce')

# Approved records in Phase 1
df1_approved = df1[(df1['application_status'] == 'APPROVED') &
                   (df1['submission_date'].notna()) &
                   (df1['approved_date'].notna())].copy()
df1_approved['time_days'] = (df1_approved['approved_date'] - df1_approved['submission_date']).dt.total_seconds() / 86400

# Pending records in Phase 1 (not approved or no approved_date)
df1_pending = df1[(df1['submission_date'].notna()) &
                  ((df1['application_status'] != 'APPROVED') | (df1['approved_date'].isna()))].copy()
df1_pending['time_days'] = (today - df1_pending['submission_date']).dt.total_seconds() / 86400

counts1_approved, pct1_approved = calculate_distribution(df1_approved, bins, labels)
counts1_pending, pct1_pending = calculate_distribution(df1_pending, bins, labels)

print(f"  Phase 1 Approved: {len(df1_approved):,} records")
print(f"  Phase 1 Pending: {len(df1_pending):,} records")

# ============================================================================
# PHASE 2: Payment Processing
# ============================================================================
print("\nProcessing Phase 2: Payment Processing...")

df2 = pd.read_csv('discounteddiregistrationpahse2.csv', low_memory=False)
df2['created_date'] = pd.to_datetime(df2['created_date'], errors='coerce')
df2['submission_date'] = pd.to_datetime(df2['submission_date'], errors='coerce')
df2['approved_date'] = pd.to_datetime(df2['approved_date'], errors='coerce')

# Approved records in Phase 2
df2_approved = df2[(df2['application_status'] == 'APPROVED') &
                   (df2['submission_date'].notna()) &
                   (df2['approved_date'].notna())].copy()
df2_approved['time_days'] = (df2_approved['approved_date'] - df2_approved['submission_date']).dt.total_seconds() / 86400

# Pending records in Phase 2
df2_pending = df2[(df2['submission_date'].notna()) &
                  ((df2['application_status'] != 'APPROVED') | (df2['approved_date'].isna()))].copy()
df2_pending['time_days'] = (today - df2_pending['submission_date']).dt.total_seconds() / 86400

counts2_approved, pct2_approved = calculate_distribution(df2_approved, bins, labels)
counts2_pending, pct2_pending = calculate_distribution(df2_pending, bins, labels)

print(f"  Phase 2 Approved: {len(df2_approved):,} records")
print(f"  Phase 2 Pending: {len(df2_pending):,} records")

# ============================================================================
# PHASE 3: Final Verification & Closure
# ============================================================================
print("\nProcessing Phase 3: Final Verification & Closure...")

df3 = pd.read_csv('discounteddiregistrationpahse3.csv', low_memory=False)
df3['created_date'] = pd.to_datetime(df3['created_date'], errors='coerce')
df3['submission_date'] = pd.to_datetime(df3['submission_date'], errors='coerce')
df3['approved_date'] = pd.to_datetime(df3['approved_date'], errors='coerce')

# Approved records in Phase 3
df3_approved = df3[(df3['application_status'] == 'APPROVED') &
                   (df3['submission_date'].notna()) &
                   (df3['approved_date'].notna())].copy()
df3_approved['time_days'] = (df3_approved['approved_date'] - df3_approved['submission_date']).dt.total_seconds() / 86400

# Pending records in Phase 3
df3_pending = df3[(df3['submission_date'].notna()) &
                  ((df3['application_status'] != 'APPROVED') | (df3['approved_date'].isna()))].copy()
df3_pending['time_days'] = (today - df3_pending['submission_date']).dt.total_seconds() / 86400

counts3_approved, pct3_approved = calculate_distribution(df3_approved, bins, labels)
counts3_pending, pct3_pending = calculate_distribution(df3_pending, bins, labels)

print(f"  Phase 3 Approved: {len(df3_approved):,} records")
print(f"  Phase 3 Pending: {len(df3_pending):,} records")

# ============================================================================
# Create three separate figures
# ============================================================================

phases_data = [
    {
        'phase_num': 1,
        'title': 'Phase 1: Initial Discount Application & Eligibility Assessment',
        'subtitle': 'Discount calculation, annual report review, and eligibility verification',
        'approved_counts': counts1_approved,
        'approved_pct': pct1_approved,
        'approved_total': len(df1_approved),
        'pending_counts': counts1_pending,
        'pending_pct': pct1_pending,
        'pending_total': len(df1_pending),
        'color_approved': '#2ecc71',  # Green
        'color_pending': '#e67e22'    # Orange
    },
    {
        'phase_num': 2,
        'title': 'Phase 2: Payment Processing & Documentation',
        'subtitle': 'Discounted fee payment, receipt verification, and payment confirmation',
        'approved_counts': counts2_approved,
        'approved_pct': pct2_approved,
        'approved_total': len(df2_approved),
        'pending_counts': counts2_pending,
        'pending_pct': pct2_pending,
        'pending_total': len(df2_pending),
        'color_approved': '#3498db',  # Blue
        'color_pending': '#9b59b6'    # Purple
    },
    {
        'phase_num': 3,
        'title': 'Phase 3: Final Verification & Deregistration Completion',
        'subtitle': 'Final document review, clearance issuance, and official company closure',
        'approved_counts': counts3_approved,
        'approved_pct': pct3_approved,
        'approved_total': len(df3_approved),
        'pending_counts': counts3_pending,
        'pending_pct': pct3_pending,
        'pending_total': len(df3_pending),
        'color_approved': '#1abc9c',  # Teal
        'color_pending': '#e74c3c'    # Red
    }
]

for phase_data in phases_data:
    fig, ax = plt.subplots(1, 1, figsize=(16, 9))

    # Add annotation in top-right corner
    fig.text(0.98, 0.98, f'{phase_data["phase_num"]} of 3',
             fontsize=16, fontweight='bold',
             ha='right', va='top',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))

    x = np.arange(len(labels))
    width = 0.35

    # Plot approved and pending bars
    bars_approved = ax.bar(x - width/2, phase_data['approved_pct'], width,
                          label=f"Approved (n={phase_data['approved_total']:,})",
                          color=phase_data['color_approved'], alpha=0.8,
                          edgecolor='black', linewidth=1.5)

    bars_pending = ax.bar(x + width/2, phase_data['pending_pct'], width,
                         label=f"Pending - In Process (n={phase_data['pending_total']:,})",
                         color=phase_data['color_pending'], alpha=0.8,
                         edgecolor='black', linewidth=1.5)

    # Add labels on bars
    for bar, pct, count in zip(bars_approved, phase_data['approved_pct'], phase_data['approved_counts']):
        height = bar.get_height()
        if height > 1:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{pct:.1f}%\n({count:,})',
                   ha='center', va='bottom', fontsize=8, fontweight='bold')

    for bar, pct, count in zip(bars_pending, phase_data['pending_pct'], phase_data['pending_counts']):
        height = bar.get_height()
        if height > 1:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{pct:.1f}%\n({count:,})',
                   ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax.set_xlabel('Time Period', fontsize=13, fontweight='bold')
    ax.set_ylabel('Percentage of Applications', fontsize=13, fontweight='bold')
    ax.set_title(f'Discounted Deregistration: {phase_data["title"]}\n{phase_data["subtitle"]}',
                fontweight='bold', fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=11)
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    filename = f'discounted_deregistration_phase{phase_data["phase_num"]}_time_distribution.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {filename}")
    plt.close()

# ============================================================================
# Summary Statistics
# ============================================================================
print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

print("\nPHASE 1: INITIAL DISCOUNT APPLICATION")
print(f"  Approved: {len(df1_approved):,} | Mean: {df1_approved['time_days'].mean():.1f} days | Median: {df1_approved['time_days'].median():.1f} days")
print(f"  Pending:  {len(df1_pending):,} | Mean: {df1_pending['time_days'].mean():.1f} days | Median: {df1_pending['time_days'].median():.1f} days")

print("\nPHASE 2: PAYMENT PROCESSING")
print(f"  Approved: {len(df2_approved):,} | Mean: {df2_approved['time_days'].mean():.1f} days | Median: {df2_approved['time_days'].median():.1f} days")
if len(df2_pending) > 0:
    print(f"  Pending:  {len(df2_pending):,} | Mean: {df2_pending['time_days'].mean():.1f} days | Median: {df2_pending['time_days'].median():.1f} days")

print("\nPHASE 3: FINAL VERIFICATION & CLOSURE")
print(f"  Approved: {len(df3_approved):,} | Mean: {df3_approved['time_days'].mean():.1f} days | Median: {df3_approved['time_days'].median():.1f} days")
if len(df3_pending) > 0:
    print(f"  Pending:  {len(df3_pending):,} | Mean: {df3_pending['time_days'].mean():.1f} days | Median: {df3_pending['time_days'].median():.1f} days")

print("\n" + "="*80)
print("DISCOUNTED DEREGISTRATION CHARTS COMPLETE!")
print("="*80)
print("""
Generated Files:
  1. discounted_deregistration_phase1_time_distribution.png (Phase 1: Discount Application)
  2. discounted_deregistration_phase2_time_distribution.png (Phase 2: Payment Processing)
  3. discounted_deregistration_phase3_time_distribution.png (Phase 3: Final Closure)

Process Overview:
  Phase 1: Companies apply for discount, authorities calculate reduced penalties
  Phase 2: Approved companies make discounted payments and verify receipts
  Phase 3: Final documentation review and official deregistration completion

Timeline:
  - Approved: submission_date to approved_date
  - Pending: submission_date to Jan 25, 2026 (still in process)
""")
