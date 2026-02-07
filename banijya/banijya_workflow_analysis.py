import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import os
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 9

print("="*80)
print("BANIJYA WORKFLOW ANALYSIS - TIME & AUTHORITY DISTRIBUTION")
print("="*80)
print()

# Define time bins
bins = [0, 1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 35, 60, 90, 180, 365, np.inf]
bin_labels = ['1d', '2d', '3d', '4d', '5d', '6d', '7d', '2wk', '3wk', '4wk', '5wk', '2mo', '3mo', '6mo', '1yr', '1yr+']

# Get all Excel files
files = [f for f in os.listdir('.') if f.endswith('.xlsx')]

# Color schemes
forward_colors = plt.cm.Blues(np.linspace(0.4, 0.9, 10))
review_colors = plt.cm.Oranges(np.linspace(0.4, 0.8, 10))

# Status categories for banijya
status_categories = {
    'approved': {
        'name': 'Approved',
        'final_statuses': ['Accept'],
        'color': 'seagreen'
    },
    'pending_payment': {
        'name': 'Pending Payment',
        'final_statuses': ['AcceptNotPaid'],
        'color': 'mediumseagreen'
    },
    'rejected': {
        'name': 'Rejected',
        'final_statuses': ['Reject'],
        'color': 'crimson'
    },
    'sent_back': {
        'name': 'Sent Back',
        'final_statuses': ['SendBack'],
        'color': 'orange'
    },
    'in_process': {
        'name': 'In Process',
        'final_statuses': ['Request', 'Forward'],
        'color': 'darkorange'
    }
}

def analyze_file(filename):
    """Analyze a single file and return application-level data."""
    print(f"  Loading {filename}...")
    
    df = pd.read_excel(filename)
    
    # Parse entity and application type from filename
    parts = filename.replace('.xlsx', '').split('_')
    entity_type = parts[0]
    app_type = parts[1] if len(parts) > 1 else 'Unknown'
    
    print(f"    Records: {len(df):,}, Applications: {df['TrackCode'].nunique():,}")
    
    # Process each application
    applications = []
    
    for track_code in df['TrackCode'].unique():
        app_records = df[df['TrackCode'] == track_code].sort_values('ActionDate')
        
        if len(app_records) == 0:
            continue
        
        # Get final status
        final_status = app_records.iloc[-1]['Working_Status']
        
        # Calculate time
        start_time = pd.to_datetime(app_records['ActionDate'].min())
        end_time = pd.to_datetime(app_records['ActionDate'].max())
        total_days = (end_time - start_time).total_seconds() / 86400
        
        # Get max authority level
        max_order = app_records['Working_Order'].max()
        
        # Calculate transitions
        transitions = {}
        for i in range(len(app_records) - 1):
            from_order = app_records.iloc[i]['Working_Order']
            to_order = app_records.iloc[i+1]['Working_Order']
            transition_time = (pd.to_datetime(app_records.iloc[i+1]['ActionDate']) - 
                             pd.to_datetime(app_records.iloc[i]['ActionDate'])).total_seconds() / 86400
            
            if from_order == to_order:
                continue
            
            if to_order > from_order:
                trans_key = f"O{int(from_order)}→O{int(to_order)}"
            else:
                trans_key = f"O{int(from_order)}←O{int(to_order)}"
            
            if total_days > 0:
                trans_pct = (transition_time / total_days) * 100
            else:
                trans_pct = 0
            
            if trans_key in transitions:
                transitions[trans_key] += trans_pct
            else:
                transitions[trans_key] = trans_pct
        
        # Assign to bin
        bin_idx = np.digitize([total_days], bins)[0] - 1
        if bin_idx < 0:
            bin_idx = 0
        if bin_idx >= len(bin_labels):
            bin_idx = len(bin_labels) - 1
        
        applications.append({
            'track_code': track_code,
            'final_status': final_status,
            'total_days': total_days,
            'max_order': int(max_order) if pd.notna(max_order) else 0,
            'num_steps': len(app_records),
            'bin': bin_labels[bin_idx],
            'transitions': transitions,
            'entity_type': entity_type,
            'app_type': app_type
        })
    
    print(f"    Processed {len(applications):,} applications")
    return applications

def plot_time_distribution(entity_type, app_type, status_category, app_df):
    """Plot time distribution for a specific combination."""
    if app_df is None or len(app_df) == 0:
        return None
    
    category_info = status_categories[status_category]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    bin_counts = app_df['bin'].value_counts().reindex(bin_labels, fill_value=0)
    
    x_pos = np.arange(len(bin_labels))
    bars = ax.bar(x_pos, bin_counts.values, color=category_info['color'], 
                   edgecolor='black', alpha=0.7, linewidth=1.5)
    
    total_apps = len(app_df)
    for i, (bar, count) in enumerate(zip(bars, bin_counts.values)):
        if count > 0:
            percentage = (count / total_apps) * 100
            label = f'{int(count)}\n({percentage:.1f}%)'
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(bin_counts)*0.01,
                   label, ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    median_days = app_df['total_days'].median()
    mean_days = app_df['total_days'].mean()
    p95_days = app_df['total_days'].quantile(0.95)
    
    ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Applications', fontsize=12, fontweight='bold')
    
    title_text = f'{entity_type} - {app_type}\n{category_info["name"]} Applications - Time Distribution'
    ax.set_title(title_text, fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(bin_labels, rotation=45, ha='right', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    stats_text = (f'Total: {len(app_df):,} applications\n'
                 f'Median: {median_days:.1f} days\n'
                 f'Mean: {mean_days:.1f} days\n'
                 f'95th percentile: {p95_days:.1f} days')
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5, edgecolor='black', linewidth=1.5))
    
    fig.tight_layout()
    return fig

def plot_authority_distribution(entity_type, app_type, status_category, max_levels):
    """Plot authority level distribution."""
    if max_levels is None or len(max_levels) == 0:
        return None
    
    category_info = status_categories[status_category]
    
    level_counts = Counter(max_levels)
    all_levels = sorted(level_counts.keys())
    counts = [level_counts[level] for level in all_levels]
    
    total = len(max_levels)
    percentages = [(count / total) * 100 for count in counts]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    x_pos = np.arange(len(all_levels))
    bars = ax.bar(x_pos, counts, color=category_info['color'], 
                   edgecolor='black', alpha=0.7, linewidth=1.5)
    
    for i, (bar, count, pct) in enumerate(zip(bars, counts, percentages)):
        if count > 0:
            label = f'{count}\n({pct:.1f}%)'
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts)*0.01,
                   label, ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    median_level = np.median(max_levels)
    mean_level = np.mean(max_levels)
    mode_level = level_counts.most_common(1)[0][0]
    mode_count = level_counts.most_common(1)[0][1]
    
    ax.set_xlabel('Maximum Working Order Reached', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Applications', fontsize=12, fontweight='bold')
    
    title_text = f'{entity_type} - {app_type}\n{category_info["name"]} - Authority Level Distribution'
    ax.set_title(title_text, fontsize=14, fontweight='bold', pad=20)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'O{level}' for level in all_levels], fontsize=10, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    stats_text = (f'Total Applications: {total:,}\n'
                 f'Mean Order: {mean_level:.1f}\n'
                 f'Median Order: {median_level:.1f}\n'
                 f'Most Common: O{mode_level} ({mode_count} apps, {mode_count/total*100:.1f}%)')
    
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5, 
                     edgecolor='black', linewidth=1.5))
    
    # Cumulative percentage
    ax2 = ax.twinx()
    cumulative_pct = np.cumsum(percentages)
    ax2.plot(x_pos, cumulative_pct, color='red', marker='o', linewidth=2, 
             markersize=6, label='Cumulative %', linestyle='--')
    ax2.set_ylabel('Cumulative Percentage (%)', fontsize=12, fontweight='bold', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim(0, 105)
    ax2.grid(False)
    
    fig.tight_layout()
    return fig

# ==================== MAIN ANALYSIS ====================

print("Loading all banijya data...")
print()

all_applications = []

for filename in sorted(files):
    apps = analyze_file(filename)
    all_applications.extend(apps)

print()
print(f"Total applications processed: {len(all_applications):,}")
print()

# Convert to DataFrame
df_all = pd.DataFrame(all_applications)

# Get unique combinations
entity_types = df_all['entity_type'].unique()
app_types = df_all['app_type'].unique()

print("="*80)
print("GENERATING VISUALIZATIONS")
print("="*80)
print()

total_files_generated = 0

for entity_type in sorted(entity_types):
    for app_type in sorted(app_types):
        
        subset = df_all[(df_all['entity_type'] == entity_type) & 
                       (df_all['app_type'] == app_type)]
        
        if len(subset) == 0:
            continue
        
        print(f"\n{entity_type} - {app_type}")
        print("-" * 80)
        
        for status_category in ['approved', 'pending_payment', 'rejected', 'sent_back', 'in_process']:
            category_info = status_categories[status_category]
            
            # Filter by final status
            status_subset = subset[subset['final_status'].isin(category_info['final_statuses'])]
            
            if len(status_subset) == 0:
                continue
            
            print(f"  {category_info['name']}: {len(status_subset):,} applications")
            
            # Generate time distribution chart
            fig_time = plot_time_distribution(entity_type, app_type, status_category, status_subset)
            if fig_time:
                filename_time = f"banijya_{entity_type}_{app_type}_{status_category}_time.png"
                fig_time.savefig(filename_time, dpi=300, bbox_inches='tight')
                plt.close(fig_time)
                total_files_generated += 1
            
            # Generate authority level distribution chart
            max_levels = status_subset['max_order'].tolist()
            fig_auth = plot_authority_distribution(entity_type, app_type, status_category, max_levels)
            if fig_auth:
                filename_auth = f"banijya_{entity_type}_{app_type}_{status_category}_authority.png"
                fig_auth.savefig(filename_auth, dpi=300, bbox_inches='tight')
                plt.close(fig_auth)
                total_files_generated += 1

print()
print("="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print()
print(f"Total files generated: {total_files_generated}")
print()
print("File naming convention:")
print("  banijya_{EntityType}_{AppType}_{Status}_time.png")
print("  banijya_{EntityType}_{AppType}_{Status}_authority.png")
print()
print("Where:")
print("  EntityType: Company, Private, Sajhedari")
print("  AppType: New, Navikaran, Khareji, Samsodhan")
print("  Status: approved, pending_payment, rejected, sent_back, in_process")
print()
print("Examples:")
print("  banijya_Company_New_approved_time.png")
print("  banijya_Private_Navikaran_approved_authority.png")
print("  banijya_Sajhedari_Khareji_sent_back_time.png")
