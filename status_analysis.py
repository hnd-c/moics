import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
print("Loading data...")
df_name = pd.read_csv('nameregisvation.csv', low_memory=False)

# Convert date columns to datetime
df_name['created_date'] = pd.to_datetime(df_name['created_date'], errors='coerce')
df_name['updated_date'] = pd.to_datetime(df_name['updated_date'], errors='coerce')
df_name['approved_date'] = pd.to_datetime(df_name['approved_date'], errors='coerce')
df_name['submission_date'] = pd.to_datetime(df_name['submission_date'], errors='coerce')

print("\n" + "="*80)
print("STATUS FIELD ANALYSIS")
print("="*80)

# Get status distribution
print("\n1. STATUS DISTRIBUTION:")
print("-"*80)
status_counts = df_name['status'].value_counts()
print(status_counts)
print(f"\nTotal records: {len(df_name):,}")

# Calculate percentages
print("\nPercentages:")
for status, count in status_counts.items():
    percentage = (count / len(df_name)) * 100
    print(f"  {status:15s}: {count:>8,} ({percentage:>5.1f}%)")

# Check which statuses have approved_date
print("\n" + "="*80)
print("2. APPROVED_DATE PRESENCE BY STATUS")
print("="*80)
print("\nWhich statuses have an 'approved_date' populated:")
print("-"*80)

for status in status_counts.index:
    status_df = df_name[df_name['status'] == status]
    has_approved = status_df['approved_date'].notna().sum()
    percentage = (has_approved / len(status_df)) * 100
    print(f"  {status:15s}: {has_approved:>8,} / {len(status_df):>8,} ({percentage:>5.1f}%)")

# Check submission_date patterns
print("\n" + "="*80)
print("3. SUBMISSION_DATE PRESENCE BY STATUS")
print("="*80)
print("\nWhich statuses have a 'submission_date' populated:")
print("-"*80)

for status in status_counts.index:
    status_df = df_name[df_name['status'] == status]
    has_submitted = status_df['submission_date'].notna().sum()
    percentage = (has_submitted / len(status_df)) * 100
    print(f"  {status:15s}: {has_submitted:>8,} / {len(status_df):>8,} ({percentage:>5.1f}%)")

# Analyze workflow timing by status
print("\n" + "="*80)
print("4. TIMING ANALYSIS BY STATUS")
print("="*80)

# Calculate days from creation to approval for each status
df_name['created_to_approved_days'] = (df_name['approved_date'] - df_name['created_date']).dt.total_seconds() / 86400
df_name['created_to_submission_days'] = (df_name['submission_date'] - df_name['created_date']).dt.total_seconds() / 86400

print("\nTime from Creation to Approval (in days):")
print("-"*80)
print(f"{'Status':<15} {'Count':>10} {'Mean':>10} {'Median':>10} {'Std Dev':>10} {'Min':>10} {'Max':>10}")
print("-"*80)

for status in ['APPROVED', 'REJECTED', 'VERIFIED', 'DRAFT']:
    if status in status_counts.index:
        status_df = df_name[df_name['status'] == status]
        timing_data = status_df['created_to_approved_days'].dropna()

        if len(timing_data) > 0:
            print(f"{status:<15} {len(timing_data):>10,} {timing_data.mean():>10.1f} "
                  f"{timing_data.median():>10.1f} {timing_data.std():>10.1f} "
                  f"{timing_data.min():>10.1f} {timing_data.max():>10.1f}")
        else:
            print(f"{status:<15} {0:>10,} {'N/A':>10} {'N/A':>10} {'N/A':>10} {'N/A':>10} {'N/A':>10}")

print("\nTime from Creation to Submission (in days):")
print("-"*80)
print(f"{'Status':<15} {'Count':>10} {'Mean':>10} {'Median':>10} {'Std Dev':>10} {'Min':>10} {'Max':>10}")
print("-"*80)

for status in ['APPROVED', 'REJECTED', 'VERIFIED', 'DRAFT']:
    if status in status_counts.index:
        status_df = df_name[df_name['status'] == status]
        timing_data = status_df['created_to_submission_days'].dropna()

        if len(timing_data) > 0:
            print(f"{status:<15} {len(timing_data):>10,} {timing_data.mean():>10.1f} "
                  f"{timing_data.median():>10.1f} {timing_data.std():>10.1f} "
                  f"{timing_data.min():>10.1f} {timing_data.max():>10.1f}")
        else:
            print(f"{status:<15} {0:>10,} {'N/A':>10} {'N/A':>10} {'N/A':>10} {'N/A':>10} {'N/A':>10}")

# Analyze VERIFIED vs APPROVED relationship
print("\n" + "="*80)
print("5. WORKFLOW STATE ANALYSIS")
print("="*80)

print("\nUnderstanding the workflow:")
print("-"*80)

# DRAFT: Has approved_date?
draft_df = df_name[df_name['status'] == 'DRAFT']
draft_with_approval = draft_df['approved_date'].notna().sum()
print(f"\nDRAFT:")
print(f"  - Total: {len(draft_df):,}")
print(f"  - With approved_date: {draft_with_approval:,}")
print(f"  - Interpretation: {'Work in progress, not submitted' if draft_with_approval == 0 else 'Some drafts have been approved before (status not updated)'}")

# VERIFIED: Has approved_date?
verified_df = df_name[df_name['status'] == 'VERIFIED']
verified_with_approval = verified_df['approved_date'].notna().sum()
print(f"\nVERIFIED:")
print(f"  - Total: {len(verified_df):,}")
print(f"  - With approved_date: {verified_with_approval:,}")
print(f"  - Interpretation: {'Submitted and verified, pending final approval' if verified_with_approval < len(verified_df) * 0.1 else 'Verification step in workflow'}")

# APPROVED: Should all have approved_date
approved_df = df_name[df_name['status'] == 'APPROVED']
approved_with_date = approved_df['approved_date'].notna().sum()
print(f"\nAPPROVED:")
print(f"  - Total: {len(approved_df):,}")
print(f"  - With approved_date: {approved_with_date:,}")
print(f"  - Missing approved_date: {len(approved_df) - approved_with_date:,}")
print(f"  - Interpretation: Final approval granted")

# REJECTED: Has approved_date?
rejected_df = df_name[df_name['status'] == 'REJECTED']
rejected_with_approval = rejected_df['approved_date'].notna().sum()
print(f"\nREJECTED:")
print(f"  - Total: {len(rejected_df):,}")
print(f"  - With approved_date: {rejected_with_approval:,}")
print(f"  - Interpretation: Application denied")

# Create visualization
print("\n" + "="*80)
print("6. CREATING VISUALIZATIONS")
print("="*80)

fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Status Analysis and Workflow Patterns', fontsize=16, fontweight='bold')

# 1. Status distribution pie chart
ax1 = axes[0, 0]
status_counts.plot(kind='pie', ax=ax1, autopct='%1.1f%%', startangle=90)
ax1.set_title('Status Distribution', fontweight='bold')
ax1.set_ylabel('')

# 2. Approved_date presence by status
ax2 = axes[0, 1]
approved_presence = []
labels_list = []
for status in ['APPROVED', 'REJECTED', 'VERIFIED', 'DRAFT']:
    if status in status_counts.index:
        status_df = df_name[df_name['status'] == status]
        has_approved = status_df['approved_date'].notna().sum()
        approved_presence.append(has_approved)
        labels_list.append(status)

ax2.bar(labels_list, approved_presence, color=['green', 'red', 'orange', 'gray'])
ax2.set_title('Records with Approved_Date by Status', fontweight='bold')
ax2.set_ylabel('Count')
ax2.set_xlabel('Status')
for i, v in enumerate(approved_presence):
    ax2.text(i, v + max(approved_presence)*0.01, f'{v:,}', ha='center', va='bottom', fontweight='bold')

# 3. Processing time comparison
ax3 = axes[1, 0]
processing_times = []
status_labels = []
for status in ['APPROVED', 'REJECTED', 'VERIFIED']:
    if status in status_counts.index:
        status_df = df_name[df_name['status'] == status]
        timing_data = status_df['created_to_approved_days'].dropna()
        if len(timing_data) > 0:
            processing_times.append(timing_data)
            status_labels.append(f"{status}\n(n={len(timing_data):,})")

if processing_times:
    bp = ax3.boxplot(processing_times, labels=status_labels, patch_artist=True)
    colors = ['lightgreen', 'lightcoral', 'lightyellow']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    ax3.set_title('Created → Approved Time by Status', fontweight='bold')
    ax3.set_ylabel('Days')
    ax3.set_xlabel('Status')
    ax3.grid(True, alpha=0.3)

# 4. Status counts bar chart with numbers
ax4 = axes[1, 1]
status_counts_sorted = status_counts.sort_values(ascending=True)
bars = ax4.barh(range(len(status_counts_sorted)), status_counts_sorted.values)
ax4.set_yticks(range(len(status_counts_sorted)))
ax4.set_yticklabels(status_counts_sorted.index)
ax4.set_title('Status Counts (sorted)', fontweight='bold')
ax4.set_xlabel('Count')

# Add value labels on bars
for i, (idx, val) in enumerate(status_counts_sorted.items()):
    ax4.text(val, i, f' {val:,}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('status_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: status_analysis.png")
plt.close()

# Create a detailed comparison for APPROVED vs REJECTED
print("\n" + "="*80)
print("7. APPROVED vs REJECTED COMPARISON")
print("="*80)

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('Detailed Comparison: APPROVED vs REJECTED Applications', fontsize=16, fontweight='bold')

# Get approved and rejected data
approved = df_name[df_name['status'] == 'APPROVED'].copy()
rejected = df_name[df_name['status'] == 'REJECTED'].copy()

# Add timing calculations
for df_subset in [approved, rejected]:
    df_subset['processing_days'] = (df_subset['approved_date'] - df_subset['created_date']).dt.total_seconds() / 86400

# Row 1: Processing time distributions
ax = axes[0, 0]
approved_times = approved['processing_days'].dropna()
if len(approved_times) > 0:
    ax.hist(approved_times, bins=50, edgecolor='black', alpha=0.7, color='green')
    ax.set_title(f'APPROVED - Processing Time\n(n={len(approved_times):,})', fontweight='bold')
    ax.set_xlabel('Days from Creation to Approval')
    ax.set_ylabel('Frequency')
    ax.axvline(approved_times.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {approved_times.mean():.1f}d')
    ax.axvline(approved_times.median(), color='blue', linestyle='--', linewidth=2, label=f'Median: {approved_times.median():.1f}d')
    ax.legend()

ax = axes[0, 1]
rejected_times = rejected['processing_days'].dropna()
if len(rejected_times) > 0:
    ax.hist(rejected_times, bins=50, edgecolor='black', alpha=0.7, color='red')
    ax.set_title(f'REJECTED - Processing Time\n(n={len(rejected_times):,})', fontweight='bold')
    ax.set_xlabel('Days from Creation to Rejection')
    ax.set_ylabel('Frequency')
    ax.axvline(rejected_times.mean(), color='darkred', linestyle='--', linewidth=2, label=f'Mean: {rejected_times.mean():.1f}d')
    ax.axvline(rejected_times.median(), color='blue', linestyle='--', linewidth=2, label=f'Median: {rejected_times.median():.1f}d')
    ax.legend()

# Box plot comparison
ax = axes[0, 2]
data_to_plot = [approved_times, rejected_times]
labels = ['APPROVED', 'REJECTED']
bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
bp['boxes'][0].set_facecolor('lightgreen')
bp['boxes'][1].set_facecolor('lightcoral')
ax.set_title('Processing Time Comparison', fontweight='bold')
ax.set_ylabel('Days')
ax.grid(True, alpha=0.3)

# Row 2: By company type
ax = axes[1, 0]
if 'company_type_id' in df_name.columns:
    approved_by_type = approved['company_type_id'].value_counts().head(10)
    ax.barh(range(len(approved_by_type)), approved_by_type.values, color='green', alpha=0.7)
    ax.set_yticks(range(len(approved_by_type)))
    ax.set_yticklabels([f"Type {x}" for x in approved_by_type.index])
    ax.set_title('APPROVED - Top 10 Company Types', fontweight='bold')
    ax.set_xlabel('Count')
    for i, val in enumerate(approved_by_type.values):
        ax.text(val, i, f' {val:,}', va='center')

ax = axes[1, 1]
if 'company_type_id' in df_name.columns:
    rejected_by_type = rejected['company_type_id'].value_counts().head(10)
    ax.barh(range(len(rejected_by_type)), rejected_by_type.values, color='red', alpha=0.7)
    ax.set_yticks(range(len(rejected_by_type)))
    ax.set_yticklabels([f"Type {x}" for x in rejected_by_type.index])
    ax.set_title('REJECTED - Top 10 Company Types', fontweight='bold')
    ax.set_xlabel('Count')
    for i, val in enumerate(rejected_by_type.values):
        ax.text(val, i, f' {val:,}', va='center')

# Success rate by company type
ax = axes[1, 2]
if 'company_type_id' in df_name.columns:
    # Get top company types overall
    top_types = df_name['company_type_id'].value_counts().head(10).index

    success_rates = []
    type_labels = []
    for ctype in top_types:
        total = len(df_name[df_name['company_type_id'] == ctype])
        approved_count = len(approved[approved['company_type_id'] == ctype])
        if total > 0:
            success_rate = (approved_count / total) * 100
            success_rates.append(success_rate)
            type_labels.append(f"Type {ctype}")

    bars = ax.barh(range(len(success_rates)), success_rates)
    ax.set_yticks(range(len(success_rates)))
    ax.set_yticklabels(type_labels)
    ax.set_title('Approval Rate by Company Type', fontweight='bold')
    ax.set_xlabel('Approval Rate (%)')
    ax.set_xlim([0, 100])

    # Color bars based on success rate
    for i, (bar, rate) in enumerate(zip(bars, success_rates)):
        if rate >= 90:
            bar.set_color('green')
        elif rate >= 70:
            bar.set_color('yellow')
        else:
            bar.set_color('red')
        ax.text(rate, i, f' {rate:.1f}%', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('approved_vs_rejected_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: approved_vs_rejected_comparison.png")
plt.close()

# Summary statistics
print("\n" + "="*80)
print("RECOMMENDATIONS")
print("="*80)

print("""
Based on the analysis, here's what you should focus on:

1. **PRIMARY FOCUS - APPROVED Applications:**
   - These are successfully processed applications
   - Analyze: Created → Approved timeline
   - Key metric: How long does approval take?
   - Break down by: company_type_id, office_id, time period

2. **SECONDARY FOCUS - REJECTED Applications:**
   - These show where applications fail
   - Analyze: Created → Rejection timeline
   - Key questions:
     * Are rejections faster/slower than approvals?
     * Which company types get rejected more?
     * What are common rejection reasons (latest_remarks)?

3. **IGNORE for Main Analysis:**
   - DRAFT: Work in progress, not finalized
   - VERIFIED: Intermediate state (if it exists in your workflow)

4. **WORKFLOW UNDERSTANDING:**
""")

# Determine likely workflow
if len(verified_df) > 0 and verified_with_approval < len(verified_df) * 0.5:
    print("   Likely workflow: DRAFT → VERIFIED → APPROVED/REJECTED")
    print("   - DRAFT: Application being prepared")
    print("   - VERIFIED: Submitted and under review")
    print("   - APPROVED/REJECTED: Final decision")
else:
    print("   Likely workflow: DRAFT → APPROVED/REJECTED")
    print("   - DRAFT: Application being prepared/submitted")
    print("   - APPROVED/REJECTED: Final decision")

print(f"""
5. **KEY METRICS TO TRACK:**
   - Approval rate: {(len(approved) / (len(approved) + len(rejected)) * 100):.1f}%
   - Average approval time: {approved_times.mean():.1f} days
   - Average rejection time: {rejected_times.mean():.1f} days
   - Total processed: {len(approved) + len(rejected):,}
   - Pending (DRAFT/VERIFIED): {len(draft_df) + len(verified_df):,}
""")

# Export summary
summary_data = {
    'Status': [],
    'Count': [],
    'Percentage': [],
    'Has_Approved_Date': [],
    'Avg_Processing_Days': [],
    'Median_Processing_Days': []
}

for status in status_counts.index:
    status_df = df_name[df_name['status'] == status]
    has_approved = status_df['approved_date'].notna().sum()
    timing_data = status_df['created_to_approved_days'].dropna()

    summary_data['Status'].append(status)
    summary_data['Count'].append(len(status_df))
    summary_data['Percentage'].append((len(status_df) / len(df_name)) * 100)
    summary_data['Has_Approved_Date'].append(has_approved)
    summary_data['Avg_Processing_Days'].append(timing_data.mean() if len(timing_data) > 0 else None)
    summary_data['Median_Processing_Days'].append(timing_data.median() if len(timing_data) > 0 else None)

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv('status_summary.csv', index=False)
print("\n✓ Saved: status_summary.csv")

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)


