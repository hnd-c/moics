import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import os
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 9

print("="*80)
print("BANIJYA WORKFLOW - TRANSITION BREAKDOWN ANALYSIS")
print("="*80)
print()

# Define time bins
bins = [0, 1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 35, 60, 90, 180, 365, np.inf]
bin_labels = ['1d', '2d', '3d', '4d', '5d', '6d', '7d', '2wk', '3wk', '4wk', '5wk', '2mo', '3mo', '6mo', '1yr', '1yr+']

# Get all Excel files
files = [f for f in os.listdir('.') if f.endswith('.xlsx')]

# Color schemes
forward_colors = plt.cm.Blues(np.linspace(0.4, 0.9, 20))
review_colors = plt.cm.Oranges(np.linspace(0.4, 0.8, 20))

# Status categories
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
    
    parts = filename.replace('.xlsx', '').split('_')
    entity_type = parts[0]
    app_type = parts[1] if len(parts) > 1 else 'Unknown'
    
    applications = []
    
    for track_code in df['TrackCode'].unique():
        app_records = df[df['TrackCode'] == track_code].sort_values('ActionDate')
        
        if len(app_records) == 0:
            continue
        
        final_status = app_records.iloc[-1]['Working_Status']
        
        start_time = pd.to_datetime(app_records['ActionDate'].min())
        end_time = pd.to_datetime(app_records['ActionDate'].max())
        total_days = (end_time - start_time).total_seconds() / 86400
        
        # Calculate transitions with percentages
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
            'bin': bin_labels[bin_idx],
            'transitions': transitions,
            'entity_type': entity_type,
            'app_type': app_type
        })
    
    return applications

def aggregate_transitions_by_bin(app_df):
    """Aggregate transition percentages by time bin."""
    bin_aggregates = {}
    
    for bin_label in bin_labels:
        apps_in_bin = app_df[app_df['bin'] == bin_label]
        
        if len(apps_in_bin) == 0:
            bin_aggregates[bin_label] = {'transitions': {}, 'count': 0}
            continue
        
        transition_lists = defaultdict(list)
        for _, app in apps_in_bin.iterrows():
            for trans_key, pct in app['transitions'].items():
                transition_lists[trans_key].append(pct)
        
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

def plot_transition_breakdown(entity_type, app_type, status_category, app_df, bin_aggregates):
    """Plot transition breakdown by time bin."""
    if app_df is None or len(app_df) == 0:
        return None
    
    category_info = status_categories[status_category]
    
    bins_with_data = [(bl, bin_aggregates[bl]) for bl in bin_labels 
                      if bin_aggregates[bl]['count'] > 0]
    
    if len(bins_with_data) == 0:
        return None
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Get all unique transitions
    all_transitions = set()
    for _, bin_data in bins_with_data:
        all_transitions.update(bin_data['transitions'].keys())
    
    all_transitions = sorted(all_transitions)
    
    # Assign colors
    transition_colors = {}
    for trans in all_transitions:
        if '→' in trans:
            from_order = int(trans.split('→')[0][1:])
            color_idx = min(from_order - 1, len(forward_colors) - 1)
            transition_colors[trans] = forward_colors[color_idx]
        elif '←' in trans:
            from_order = int(trans.split('←')[0][1:])
            color_idx = min(from_order - 1, len(review_colors) - 1)
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
        
        bars = ax.barh(y_pos, widths, left=left_positions, 
                       color=transition_colors[trans], label=trans, 
                       edgecolor='white', linewidth=1.5)
        
        # Add labels
        for bin_idx, (bar, width, left) in enumerate(zip(bars, widths, left_positions)):
            if width > 3:
                x_pos_label = left + width / 2
                y_pos_label = bin_idx
                label_text = f'{trans}\n{width:.1f}%'
                ax.text(x_pos_label, y_pos_label, label_text,
                        ha='center', va='center', fontsize=7, fontweight='bold',
                        color='white', bbox=dict(boxstyle='round,pad=0.3', 
                                                facecolor='black', alpha=0.6, edgecolor='none'))
    
    # Format axis
    bin_labels_with_counts = [f"{bl}\n(n={bd['count']})" 
                              for bl, bd in bins_with_data]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(bin_labels_with_counts, fontsize=10)
    ax.set_xlabel('Percentage of Total Time (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Time Bin', fontsize=12, fontweight='bold')
    
    title_text = f'{entity_type} - {app_type}\n{category_info["name"]} - Transition Breakdown by Time Bin'
    ax.set_title(title_text, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(0, 100)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
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
    
    ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1.02, 0.5),
              fontsize=9, frameon=True, title='Transitions', title_fontsize=10,
              edgecolor='black', fancybox=False)
    
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

df_all = pd.DataFrame(all_applications)

entity_types = df_all['entity_type'].unique()
app_types = df_all['app_type'].unique()

print("="*80)
print("GENERATING TRANSITION BREAKDOWN CHARTS")
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
            
            status_subset = subset[subset['final_status'].isin(category_info['final_statuses'])]
            
            if len(status_subset) == 0:
                continue
            
            print(f"  {category_info['name']}: {len(status_subset):,} applications")
            
            # Aggregate transitions by bin
            bin_aggregates = aggregate_transitions_by_bin(status_subset)
            
            # Generate transition breakdown chart
            fig_trans = plot_transition_breakdown(entity_type, app_type, status_category, 
                                                 status_subset, bin_aggregates)
            if fig_trans:
                filename_trans = f"banijya_{entity_type}_{app_type}_{status_category}_transitions.png"
                fig_trans.savefig(filename_trans, dpi=300, bbox_inches='tight')
                plt.close(fig_trans)
                total_files_generated += 1

print()
print("="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print()
print(f"Total transition charts generated: {total_files_generated}")
print()
print("File naming: banijya_{EntityType}_{AppType}_{Status}_transitions.png")
print()
print("Now you have all 3 chart types for each combination:")
print("  1. *_time.png - Time distribution")
print("  2. *_authority.png - Authority level distribution")
print("  3. *_transitions.png - Transition breakdown by time bin")
