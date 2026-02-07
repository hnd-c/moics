import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 9

print("="*80)
print("AUTHORITY LEVEL DISTRIBUTION ANALYSIS")
print("="*80)
print()

# Load workflow history data
print("Loading workflow history...")
df = pd.read_csv('Industry_workflow_history.csv')
print(f"Loaded {len(df):,} workflow records")

# Load authoritative status data
print("Loading authoritative status data...")
df_status = pd.read_csv('menuwise last date.csv.csv')
print(f"Loaded {len(df_status):,} status records")
print()

# Parse dates
print("Parsing dates...")
df['workflow_datetime'] = pd.to_datetime(df['workflow_date'], format='%d/%m/%Y %H:%M', errors='coerce')
df = df[df['workflow_datetime'].notna()].copy()

# Create status lookup dictionary
print("Creating authoritative status lookup...")
status_lookup = {}
for _, row in df_status.iterrows():
    app_id = row['table_data_id']
    auth_status = row['auth_status']
    status_lookup[app_id] = auth_status

print(f"Created lookup for {len(status_lookup):,} applications")
print()

# Define processes to analyze
processes_to_analyze = [
    'Visa Recommendation',
    'Industry Registration',
    'New Investment',
    'Industry Link',
    'Facility Request',
    'Technology Transfer Agreement',
    'Extension of Operation Period',
    'Post Registration'
]

# Status categories
status_categories = {
    'approved': {
        'name': 'Approved',
        'auth_statuses': ['Approved'],
        'color': 'seagreen'
    },
    'rejected': {
        'name': 'Rejected',
        'auth_statuses': ['Rejected'],
        'color': 'crimson'
    },
    'back_for_review': {
        'name': 'Back for Review',
        'auth_statuses': ['Back for review'],
        'color': 'orange'
    },
    'inprocess': {
        'name': 'In-Process',
        'auth_statuses': ['In Process', 'Sent for recommendation', 'Sent to external office', 'Sent for committee'],
        'color': 'darkorange'
    }
}

def analyze_authority_levels(process_name, status_category):
    """
    Analyze the distribution of maximum authority levels reached
    for applications of a given process and status.
    """
    category_info = status_categories[status_category]
    print(f"  Analyzing {process_name} - {category_info['name']}...")
    
    # Filter to this process
    process_df = df[df['menu_name'] == process_name].copy()
    
    if len(process_df) == 0:
        print(f"    No data found")
        return None
    
    # Get unique applications
    app_ids = process_df['table_data_id'].unique()
    
    # Collect max authority levels for applications matching this status
    max_levels = []
    
    for app_id in app_ids:
        # Get authoritative status
        auth_stat = status_lookup.get(app_id, None)
        
        if auth_stat is None:
            continue
        
        if auth_stat not in category_info['auth_statuses']:
            continue
        
        # Get all workflow records for this application
        app_records = process_df[process_df['table_data_id'] == app_id]
        
        # Find the maximum authority level reached
        max_level = app_records['auth_level'].max()
        
        if pd.notna(max_level):
            max_levels.append(int(max_level))
    
    if len(max_levels) == 0:
        print(f"    No applications found")
        return None
    
    print(f"    Found {len(max_levels):,} applications")
    return max_levels

def plot_authority_distribution(process_name, status_category, max_levels):
    """Create a bar chart showing distribution of maximum authority levels."""
    if max_levels is None or len(max_levels) == 0:
        return None
    
    category_info = status_categories[status_category]
    
    # Count occurrences
    level_counts = Counter(max_levels)
    
    # Create sorted list of levels
    all_levels = sorted(level_counts.keys())
    counts = [level_counts[level] for level in all_levels]
    
    # Calculate percentages
    total = len(max_levels)
    percentages = [(count / total) * 100 for count in counts]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 6))
    
    x_pos = np.arange(len(all_levels))
    bars = ax.bar(x_pos, counts, color=category_info['color'], 
                   edgecolor='black', alpha=0.7, linewidth=1.5)
    
    # Add labels on bars
    for i, (bar, count, pct) in enumerate(zip(bars, counts, percentages)):
        if count > 0:
            label = f'{count}\n({pct:.1f}%)'
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts)*0.01,
                   label, ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # Calculate statistics
    median_level = np.median(max_levels)
    mean_level = np.mean(max_levels)
    mode_level = level_counts.most_common(1)[0][0]
    mode_count = level_counts.most_common(1)[0][1]
    
    # Format axis
    ax.set_xlabel('Maximum Authority Level Reached', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Applications', fontsize=12, fontweight='bold')
    
    title_text = f'{process_name} - {category_info["name"]} Applications\nDistribution of Maximum Authority Level Reached'
    ax.set_title(title_text, fontsize=14, fontweight='bold', pad=20)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'L{level}' for level in all_levels], fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Stats box
    stats_text = (f'Total Applications: {total:,}\n'
                 f'Mean Level: {mean_level:.1f}\n'
                 f'Median Level: {median_level:.1f}\n'
                 f'Most Common: L{mode_level} ({mode_count} apps, {mode_count/total*100:.1f}%)')
    
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5, 
                     edgecolor='black', linewidth=1.5))
    
    # Add cumulative percentage line
    ax2 = ax.twinx()
    cumulative_pct = np.cumsum(percentages)
    ax2.plot(x_pos, cumulative_pct, color='red', marker='o', linewidth=2, 
             markersize=6, label='Cumulative %', linestyle='--')
    ax2.set_ylabel('Cumulative Percentage (%)', fontsize=12, fontweight='bold', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim(0, 105)
    ax2.grid(False)
    
    # Add cumulative percentage labels
    for i, (x, y) in enumerate(zip(x_pos, cumulative_pct)):
        if i % max(1, len(x_pos) // 10) == 0 or i == len(x_pos) - 1:  # Show every nth label
            ax2.text(x, y + 2, f'{y:.0f}%', ha='center', fontsize=7, 
                    color='red', fontweight='bold')
    
    fig.tight_layout()
    
    return fig

# ==================== MAIN ANALYSIS ====================

print("Starting authority level distribution analysis...")
print()

total_files_generated = 0

for process_name in processes_to_analyze:
    print(f"Analyzing: {process_name}")
    print("-" * 80)
    
    for status_category in ['approved', 'rejected', 'back_for_review', 'inprocess']:
        category_info = status_categories[status_category]
        
        # Analyze authority levels
        max_levels = analyze_authority_levels(process_name, status_category)
        
        if max_levels is None or len(max_levels) == 0:
            continue
        
        # Create visualization
        fig = plot_authority_distribution(process_name, status_category, max_levels)
        
        if fig is not None:
            # Save figure
            base_name = process_name.lower().replace(' ', '_')
            filename = f"{base_name}_{status_category}_authority_levels.png"
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"  ✓ Saved: {filename}")
            plt.close(fig)
            total_files_generated += 1
    
    print()

print("="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print()
print(f"Total files generated: {total_files_generated}")
print()
print("="*80)
print("WHAT THESE CHARTS SHOW")
print("="*80)
print()
print("Each chart displays:")
print("  • The distribution of the MAXIMUM authority level reached")
print("  • How many applications reached L1, L2, L3, etc. as their highest level")
print("  • Bars: Absolute count of applications at each level")
print("  • Red line: Cumulative percentage")
print()
print("Interpretation:")
print("  • Higher levels = More complex approval process")
print("  • L1-L3 = Basic/simple applications (low complexity)")
print("  • L4-L6 = Standard applications (medium complexity)")
print("  • L7+ = Complex applications requiring senior approval")
print()
print("Example insights:")
print("  • If most approved apps reach L5+ → Process requires senior sign-off")
print("  • If rejected apps stop at L2-L3 → Early rejection (fast fail)")
print("  • If back-for-review apps reach L4+ → Issues found late in process")
print()
print("File naming: {process}_{status}_authority_levels.png")
print()
print("Examples:")
print("  - industry_registration_approved_authority_levels.png")
print("  - visa_recommendation_rejected_authority_levels.png")
print("  - new_investment_back_for_review_authority_levels.png")
