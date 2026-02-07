import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 9

print("="*80)
print("WORKFLOW TIME DISTRIBUTION - INTEGRATED WITH AUTHORITATIVE STATUS")
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
valid_dates = df['workflow_datetime'].notna().sum()
print(f"Successfully parsed {valid_dates:,} dates ({valid_dates/len(df)*100:.1f}%)")
print()

# Filter to records with valid dates
df = df[df['workflow_datetime'].notna()].copy()

# Create status lookup dictionary from authoritative source
print("Creating authoritative status lookup...")
status_lookup = {}
for _, row in df_status.iterrows():
    app_id = row['table_data_id']
    auth_status = row['auth_status']
    status_lookup[app_id] = auth_status

print(f"Created lookup for {len(status_lookup):,} applications")
print()

# Display status distribution from authoritative source
print("="*80)
print("AUTHORITATIVE STATUS DISTRIBUTION")
print("="*80)
print()
status_counts = df_status['auth_status'].value_counts()
for status, count in status_counts.items():
    pct = count/len(df_status)*100
    print(f"  {status:30s}: {count:6,} ({pct:5.1f}%)")
print()

# Define time bins
bins = [0, 1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 35, 60, 90, 180, 365, np.inf]
bin_labels = ['1d', '2d', '3d', '4d', '5d', '6d', '7d', '2wk', '3wk', '4wk', '5wk', '2mo', '3mo', '6mo', '1yr', '1yr+']

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

# Color schemes
forward_colors = plt.cm.Blues(np.linspace(0.4, 0.9, 10))
review_colors = plt.cm.Oranges(np.linspace(0.4, 0.8, 10))

# Today's date for calculating days since last activity
today = pd.Timestamp('2026-01-28')

# Status categories mapping from authoritative status
# User decision needed: Should "Back for review" be IN-PROCESS or treated separately?
status_categories = {
    'approved_all': {
        'name': 'Approved (All)',
        'auth_statuses': ['Approved'],
        'filter_func': lambda auth_stat, final_level, days_dormant: auth_stat == 'Approved',
        'color': 'seagreen',
        'description': 'All applications with authoritative status = Approved',
        'confidence': 'Mixed - includes potential intermediate approvals'
    },
    'approved_l4plus': {
        'name': 'Approved (L4+)',
        'auth_statuses': ['Approved'],
        'filter_func': lambda auth_stat, final_level, days_dormant: auth_stat == 'Approved' and final_level >= 4,
        'color': 'darkgreen',
        'description': 'Approved applications that reached Level 4 or higher',
        'confidence': 'HIGH - Reached senior approval levels'
    },
    'approved_l4plus_or_dormant': {
        'name': 'Approved (L4+ or Dormant)',
        'auth_statuses': ['Approved'],
        'filter_func': lambda auth_stat, final_level, days_dormant: auth_stat == 'Approved' and (final_level >= 4 or days_dormant > 180),
        'color': 'mediumseagreen',
        'description': 'Approved at L4+ OR no activity for 180+ days',
        'confidence': 'HIGH - Best balance of completeness and confidence'
    },
    'approved_l6plus': {
        'name': 'Approved (L6+)',
        'auth_statuses': ['Approved'],
        'filter_func': lambda auth_stat, final_level, days_dormant: auth_stat == 'Approved' and final_level >= 6,
        'color': 'forestgreen',
        'description': 'Approved applications at Level 6 or higher only',
        'confidence': 'VERY HIGH - Ultra-confident final approvals'
    },
    'rejected': {
        'name': 'Rejected',
        'auth_statuses': ['Rejected'],
        'filter_func': lambda auth_stat, final_level, days_dormant: auth_stat == 'Rejected',
        'color': 'crimson',
        'description': 'Applications with authoritative status = Rejected',
        'confidence': 'N/A'
    },
    'back_for_review': {
        'name': 'Back for Review',
        'auth_statuses': ['Back for review'],
        'filter_func': lambda auth_stat, final_level, days_dormant: auth_stat == 'Back for review',
        'color': 'orange',
        'description': 'Applications sent back for review (still active but needs revision)',
        'confidence': 'N/A'
    },
    'inprocess': {
        'name': 'In-Process',
        'auth_statuses': ['In Process', 'Sent for recommendation', 'Sent to external office', 'Sent for committee'],
        'filter_func': lambda auth_stat, final_level, days_dormant: auth_stat in ['In Process', 'Sent for recommendation', 'Sent to external office', 'Sent for committee'],
        'color': 'darkorange',
        'description': 'Applications currently being processed',
        'confidence': 'N/A'
    }
}

def calculate_application_data_by_status(process_name, status_category):
    """
    Calculate time distribution and transition data for applications of a given process,
    filtered by authoritative status from menuwise last date file.
    """
    category_info = status_categories[status_category]
    print(f"  Processing {process_name} - {category_info['name']}...")
    
    # Filter to this process
    process_df = df[df['menu_name'] == process_name].copy()
    
    if len(process_df) == 0:
        print(f"    No data found for {process_name}")
        return None
    
    # Get unique applications
    app_ids = process_df['table_data_id'].unique()
    
    # Filter applications by authoritative status with additional criteria
    filtered_app_ids = []
    for app_id in app_ids:
        # Get authoritative status
        auth_stat = status_lookup.get(app_id, None)
        
        if auth_stat is None:
            continue  # Skip if no authoritative status
        
        app_records = process_df[process_df['table_data_id'] == app_id].sort_values('workflow_datetime')
        
        final_level = app_records.iloc[-1]['auth_level']
        last_activity = app_records['workflow_datetime'].max()
        days_dormant = (today - last_activity).days
        
        if category_info['filter_func'](auth_stat, final_level, days_dormant):
            filtered_app_ids.append(app_id)
    
    if len(filtered_app_ids) == 0:
        print(f"    No {category_info['name']} applications found")
        return None
    
    print(f"    Found {len(filtered_app_ids):,} {category_info['name'].lower()} applications")
    
    application_data = []
    
    for app_id in filtered_app_ids:
        app_records = process_df[process_df['table_data_id'] == app_id].sort_values('workflow_datetime')
        
        if len(app_records) < 1:
            continue
        
        # Calculate total processing time
        start_time = app_records['workflow_datetime'].min()
        end_time = app_records['workflow_datetime'].max()
        total_days = (end_time - start_time).total_seconds() / 86400
        
        # Calculate transitions
        transitions = {}
        
        for i in range(len(app_records) - 1):
            from_level = app_records.iloc[i]['auth_level']
            to_level = app_records.iloc[i+1]['auth_level']
            transition_time = (app_records.iloc[i+1]['workflow_datetime'] - 
                             app_records.iloc[i]['workflow_datetime']).total_seconds() / 86400
            
            # Only track actual transitions (skip same-level)
            if from_level == to_level:
                continue
            
            # Create transition key
            if to_level > from_level:
                trans_key = f"L{int(from_level)}→L{int(to_level)}"
            else:
                trans_key = f"L{int(from_level)}←L{int(to_level)}"
            
            # Calculate percentage
            if total_days > 0:
                trans_pct = (transition_time / total_days) * 100
            else:
                trans_pct = 0
            
            # Accumulate
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
        
        application_data.append({
            'app_id': app_id,
            'total_days': total_days,
            'bin': bin_labels[bin_idx],
            'transitions': transitions,
            'num_steps': len(app_records)
        })
    
    print(f"    Processed {len(application_data):,} applications successfully")
    return pd.DataFrame(application_data)

def aggregate_transitions_by_bin(app_df):
    """Aggregate transition percentages by time bin."""
    bin_aggregates = {}
    
    for bin_label in bin_labels:
        apps_in_bin = app_df[app_df['bin'] == bin_label]
        
        if len(apps_in_bin) == 0:
            bin_aggregates[bin_label] = {'transitions': {}, 'count': 0}
            continue
        
        # Collect all transition percentages
        transition_lists = defaultdict(list)
        for _, app in apps_in_bin.iterrows():
            for trans_key, pct in app['transitions'].items():
                transition_lists[trans_key].append(pct)
        
        # Calculate mean percentage
        transition_means = {}
        for trans_key, pct_list in transition_lists.items():
            transition_means[trans_key] = np.mean(pct_list)
        
        # Normalize to 100%
        total = sum(transition_means.values())
        if total > 0:
            transition_means = {k: (v/total)*100 for k, v in transition_means.items()}
        
        bin_aggregates[bin_label] = {
            'transitions': transition_means,
            'count': len(apps_in_bin)
        }
    
    return bin_aggregates

def plot_status_analysis(process_name, status_category, app_df, bin_aggregates):
    """Create distribution and transition charts for a specific status category."""
    if app_df is None or len(app_df) == 0:
        return None, None
    
    category_info = status_categories[status_category]
    
    # Create two separate figures
    fig1 = plt.figure(figsize=(14, 6))
    ax1 = fig1.add_subplot(111)
    
    fig2 = plt.figure(figsize=(14, 8))
    ax2 = fig2.add_subplot(111)
    
    # ==================== FIGURE 1: Distribution ====================
    
    bin_counts = app_df['bin'].value_counts().reindex(bin_labels, fill_value=0)
    
    x_pos = np.arange(len(bin_labels))
    bars = ax1.bar(x_pos, bin_counts.values, color=category_info['color'], 
                   edgecolor='black', alpha=0.7, linewidth=1.5)
    
    # Add labels
    total_apps = len(app_df)
    for i, (bar, count) in enumerate(zip(bars, bin_counts.values)):
        if count > 0:
            percentage = (count / total_apps) * 100
            label = f'{int(count)}\n({percentage:.1f}%)'
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(bin_counts)*0.01,
                    label, ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # Statistics
    median_days = app_df['total_days'].median()
    mean_days = app_df['total_days'].mean()
    p95_days = app_df['total_days'].quantile(0.95)
    
    # Format axis
    ax1.set_xlabel('Time Period', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Number of Applications', fontsize=12, fontweight='bold')
    
    # Enhanced title with confidence info for approved categories
    if 'approved' in status_category:
        title_text = f'{process_name}\n{category_info["name"]} - Time Distribution [AUTHORITATIVE]\n[{category_info["confidence"]}]'
    else:
        title_text = f'{process_name}\n{category_info["name"]} Applications - Time Distribution [AUTHORITATIVE]'
    
    ax1.set_title(title_text, fontsize=14, fontweight='bold', pad=20)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(bin_labels, rotation=45, ha='right', fontsize=10)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Stats box
    stats_text = (f'Total: {len(app_df):,} applications\n'
                 f'Median: {median_days:.1f} days\n'
                 f'Mean: {mean_days:.1f} days\n'
                 f'95th percentile: {p95_days:.1f} days')
    ax1.text(0.98, 0.97, stats_text, transform=ax1.transAxes,
            fontsize=10, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5, edgecolor='black', linewidth=1.5))
    
    fig1.tight_layout()
    
    # ==================== FIGURE 2: Transitions ====================
    
    bins_with_data = [(bl, bin_aggregates[bl]) for bl in bin_labels 
                      if bin_aggregates[bl]['count'] > 0]
    
    if len(bins_with_data) == 0:
        ax2.text(0.5, 0.5, 'No transition data available', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)
        fig2.tight_layout()
        return fig1, fig2
    
    # Get all unique transitions
    all_transitions = set()
    for _, bin_data in bins_with_data:
        all_transitions.update(bin_data['transitions'].keys())
    
    all_transitions = sorted(all_transitions)
    
    # Assign colors
    transition_colors = {}
    for trans in all_transitions:
        if '→' in trans:
            from_level = int(trans.split('→')[0][1:])
            color_idx = min(from_level - 1, len(forward_colors) - 1)
            transition_colors[trans] = forward_colors[color_idx]
        elif '←' in trans:
            from_level = int(trans.split('←')[0][1:])
            color_idx = min(from_level - 1, len(review_colors) - 1)
            transition_colors[trans] = review_colors[color_idx]
        else:
            transition_colors[trans] = 'gray'
    
    # Create stacked bars
    y_pos = np.arange(len(bins_with_data))
    
    for trans_idx, trans in enumerate(all_transitions):
        left_positions = np.zeros(len(bins_with_data))
        widths = []
        
        for bin_idx, (bin_label, bin_data) in enumerate(bins_with_data):
            if trans_idx > 0:
                for prev_trans in all_transitions[:trans_idx]:
                    left_positions[bin_idx] += bin_data['transitions'].get(prev_trans, 0)
            
            width = bin_data['transitions'].get(trans, 0)
            widths.append(width)
        
        bars = ax2.barh(y_pos, widths, left=left_positions, 
                       color=transition_colors[trans], label=trans, 
                       edgecolor='white', linewidth=1.5)
        
        # Add labels
        for bin_idx, (bar, width, left) in enumerate(zip(bars, widths, left_positions)):
            if width > 3:
                x_pos_label = left + width / 2
                y_pos_label = bin_idx
                label_text = f'{trans}\n{width:.1f}%'
                ax2.text(x_pos_label, y_pos_label, label_text,
                        ha='center', va='center', fontsize=7, fontweight='bold',
                        color='white', bbox=dict(boxstyle='round,pad=0.3', 
                                                facecolor='black', alpha=0.6, edgecolor='none'))
    
    # Format axis
    bin_labels_with_counts = [f"{bl}\n(n={bd['count']})" 
                              for bl, bd in bins_with_data]
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(bin_labels_with_counts, fontsize=10)
    ax2.set_xlabel('Percentage of Total Time (%)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Time Bin', fontsize=12, fontweight='bold')
    
    if 'approved' in status_category:
        title_text = f'{process_name}\n{category_info["name"]} - Transition Breakdown [AUTHORITATIVE]\n[{category_info["confidence"]}]'
    else:
        title_text = f'{process_name}\n{category_info["name"]} Applications - Transition Breakdown [AUTHORITATIVE]'
    
    ax2.set_title(title_text, fontsize=14, fontweight='bold', pad=20)
    ax2.set_xlim(0, 100)
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Legend
    forward_trans = [t for t in all_transitions if '→' in t]
    backward_trans = [t for t in all_transitions if '←' in t]
    
    handles = []
    labels = []
    
    if forward_trans:
        labels.append('Forward Transitions:')
        handles.append(plt.Rectangle((0,0),1,1, fc="w", fill=False, edgecolor='none', linewidth=0))
        for t in forward_trans[:15]:
            handles.append(plt.Rectangle((0,0),1,1, fc=transition_colors[t], edgecolor='black', linewidth=0.5))
            labels.append(t)
    
    if backward_trans:
        labels.append('\nBackward Movements:')
        handles.append(plt.Rectangle((0,0),1,1, fc="w", fill=False, edgecolor='none', linewidth=0))
        for t in backward_trans[:10]:
            handles.append(plt.Rectangle((0,0),1,1, fc=transition_colors[t], edgecolor='black', linewidth=0.5))
            labels.append(t)
    
    ax2.legend(handles, labels, loc='center left', bbox_to_anchor=(1.02, 0.5),
              fontsize=9, frameon=True, title='Transitions', title_fontsize=10,
              edgecolor='black', fancybox=False)
    
    fig2.tight_layout()
    
    return fig1, fig2

# ==================== MAIN ANALYSIS ====================

print("Starting analysis with AUTHORITATIVE status integration...")
print()

total_files_generated = 0

for process_name in processes_to_analyze:
    print(f"Analyzing: {process_name}")
    print("-" * 80)
    
    # Process all status categories
    for status_category in ['approved_all', 'approved_l4plus', 'approved_l4plus_or_dormant', 
                            'approved_l6plus', 'rejected', 'back_for_review', 'inprocess']:
        category_info = status_categories[status_category]
        
        # Calculate application-level data
        app_df = calculate_application_data_by_status(process_name, status_category)
        
        if app_df is None or len(app_df) == 0:
            continue
        
        # Aggregate transitions
        print(f"  Aggregating transition data...")
        bin_aggregates = aggregate_transitions_by_bin(app_df)
        
        # Create visualizations
        print(f"  Creating visualizations...")
        fig1, fig2 = plot_status_analysis(process_name, status_category, app_df, bin_aggregates)
        
        if fig1 is not None and fig2 is not None:
            # Save figures with "v2" suffix to distinguish from old analysis
            base_name = process_name.lower().replace(' ', '_')
            
            filename1 = f"{base_name}_{status_category}_distribution_v2.png"
            fig1.savefig(filename1, dpi=300, bbox_inches='tight')
            print(f"  ✓ Saved: {filename1}")
            plt.close(fig1)
            total_files_generated += 1
            
            filename2 = f"{base_name}_{status_category}_transitions_v2.png"
            fig2.savefig(filename2, dpi=300, bbox_inches='tight')
            print(f"  ✓ Saved: {filename2}")
            plt.close(fig2)
            total_files_generated += 1
    
    print()

print("="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print()
print(f"Total files generated: {total_files_generated}")
print()
print("Files saved with '_v2' suffix to distinguish from previous analysis")
print()
print("Status categories analyzed:")
print("  • approved_all - All approved applications")
print("  • approved_l4plus - High confidence (L4+ only)")
print("  • approved_l4plus_or_dormant - Recommended (L4+ or dormant 180d)")
print("  • approved_l6plus - Ultra-high confidence (L6+ only)")
print("  • rejected - Rejected applications")
print("  • back_for_review - Applications sent back for review (NEW)")
print("  • inprocess - In-process, sent for recommendation, external office, committee")
print()
print("="*80)
print("KEY IMPROVEMENT")
print("="*80)
print()
print("This analysis uses AUTHORITATIVE status from 'menuwise last date.csv.csv'")
print("instead of inferring status from the last workflow record.")
print()
print("Benefits:")
print("  ✓ More accurate categorization of approved/rejected/in-process")
print("  ✓ Captures 'Back for review' as separate category")
print("  ✓ Includes intermediate states like 'Sent for committee'")
print("  ✓ Based on official system status, not inferred from workflow")
