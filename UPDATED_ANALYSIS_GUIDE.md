# Updated Workflow Time Distribution Analysis - Quick Guide

**Date:** January 28, 2026  
**Script:** `workflow_time_bin_charts.py` (Version 2.0)

---

## What Changed

Based on your feedback, I've implemented the following improvements:

### 1. ✅ More Detailed Time Bins (Especially First Week)

**Previous bins:**
- 0-7d, 8-14d, 15-30d, 31-60d, 61-90d, 91-180d, 181-365d, 365+d

**New bins (16 bins total):**
- **Day-by-day for first week:** 1d, 2d, 3d, 4d, 5d, 6d, 7d
- **Weekly progression:** 2wk (8-14d), 3wk (15-21d), 4wk (22-28d), 5wk (29-35d)
- **Monthly progression:** 2mo (36-60d), 3mo (61-90d), 6mo (91-180d)
- **Yearly:** 1yr (181-365d), 1yr+ (365+d)

**Why this matters:**
- Can now see day-to-day patterns in the critical first week
- Identify if applications stall at specific early days
- More granular view of fast-track vs delayed applications

### 2. ✅ Removed Review Cycles (Transitions Only)

**Previous approach:**
- Tracked both transitions (1→2) AND review cycles (1→1, 2→2)
- Review cycles shown as separate orange segments

**New approach:**
- **Only track actual transitions** (when auth level changes)
- Review time is automatically captured in the transition time
- Cleaner, simpler visualization

**Example:**
- If an application is at Level 2 from Day 5 to Day 12 (with multiple reviews), then moves to Level 3 on Day 12
- Old: Would show "L2_review: 7 days" separately
- New: The L2→L3 transition captures all 7 days automatically

**Why this is better:**
- More intuitive - you see the actual progression
- The time between levels already includes all review/processing time
- Cleaner visualizations with fewer segments

### 3. ✅ Split Figures into Separate Files

**Previous:** One combined PNG with 2 panels (top: histogram, bottom: transitions)

**New:** Two separate PNG files per process:
- `{process}_distribution.png` - Time distribution histogram only
- `{process}_transitions.png` - Transition breakdown only

**Benefits:**
- Easier to view each chart at full size
- Can share one without the other if needed
- Better for presentations and reports
- Cleaner, more focused visualizations

### 4. ✅ Added Labels on Transition Bars

**Previous:** Color-coded segments with legend only

**New:** Each segment shows:
- **Transition name** (e.g., "L1→L2")
- **Percentage** (e.g., "25.3%")
- Directly on the bar (if segment is >3% width)

**Example label:**
```
┌─────────────────┐
│   L2→L3         │
│   28.5%         │
└─────────────────┘
```

**Benefits:**
- No need to cross-reference with legend constantly
- Exact percentages visible at a glance
- Much faster to interpret the data

---

## Generated Files (12 total - 2 per process)

### Visa Recommendation (Largest - 7,257 applications)
- `visa_recommendation_distribution.png` (~227 KB)
- `visa_recommendation_transitions.png` (~863 KB)

### Industry Registration (2,101 applications)
- `industry_registration_distribution.png` (~213 KB)
- `industry_registration_transitions.png` (~743 KB)

### New Investment (1,395 applications)
- `new_investment_distribution.png` (~218 KB)
- `new_investment_transitions.png` (~748 KB)

### Industry Link (1,678 applications)
- `industry_link_distribution.png` (~206 KB)
- `industry_link_transitions.png` (~301 KB)

### Facility Request (336 applications)
- `facility_request_distribution.png` (~207 KB)
- `facility_request_transitions.png` (~420 KB)

### Technology Transfer Agreement (222 applications)
- `technology_transfer_agreement_distribution.png` (~215 KB)
- `technology_transfer_agreement_transitions.png` (~514 KB)

---

## How to Read the New Visualizations

### Distribution Chart (*_distribution.png)

**What it shows:**
- X-axis: 16 time bins (1d, 2d, 3d... up to 1yr+)
- Y-axis: Number of applications
- Bars: Count of applications in each bin
- Statistics box: Total, median, mean, 95th percentile

**Key questions to ask:**
1. **Where are most applications concentrated?**
   - If most are in 1d-7d bins → Very efficient process
   - If spread across 1mo-3mo → Slower, more variable process

2. **Is there a sharp drop-off?**
   - Drop after day 7 → Many fast-track applications
   - Gradual decline → Consistent processing across timeframes

3. **Are there outliers?**
   - Applications in 6mo+ bins → Problem cases needing investigation

4. **What's the shape?**
   - Left-skewed (concentrated early) → Good!
   - Right-skewed (long tail) → Some applications delayed
   - Bimodal (two peaks) → Two distinct processing patterns

### Transition Chart (*_transitions.png)

**What it shows:**
- Y-axis: Same 16 time bins as distribution chart
- X-axis: Percentage (0-100%)
- Stacked bars: Each segment is one transition
- Labels: Transition name and percentage directly on bars

**Key questions to ask:**
1. **Do patterns differ by time bin?**
   - Compare 1d applications vs 3mo applications
   - Different segments dominate in different bins

2. **Which transitions take the most time?**
   - Look for large segments (>30%)
   - These are your bottlenecks

3. **Are there transitions that only appear in slow bins?**
   - May indicate escalation to higher authority levels
   - Only problematic applications reach these levels

4. **How do fast applications differ from slow ones?**
   - Fast bins (1-7d): Fewer transitions, complete at lower levels
   - Slow bins (3mo+): More transitions, higher auth levels

**Reading the labels:**
- "L1→L2: 35.2%" means 35.2% of total time spent moving from Level 1 to Level 2
- "L3→L4: 18.7%" means 18.7% of total time for that transition
- Blue shades = forward progression (good)
- Orange/red shades = backward movement (indicates problems)

---

## Example Analysis Workflow

### Step 1: Start with Distribution Chart

Open `visa_recommendation_distribution.png`:

**Observe:**
- "Median: 45 days" - typical processing time
- Peak at 3wk bin - most applications complete around 3 weeks
- Long tail to 6mo+ - some delayed applications

**Insight:** Most applications are processed within 3-4 weeks, but there's a problematic subset taking 3+ months

### Step 2: Investigate with Transition Chart

Open `visa_recommendation_transitions.png`:

**Compare bins:**

**3wk bin (typical):**
- L1→L2: 20%
- L2→L3: 25%
- L3→L4: 30%
- L4→L5: 25%
- Pattern: Smooth progression through levels

**3mo bin (delayed):**
- L1→L2: 10%
- L2→L3: 15%
- L3→L4: 15%
- L4→L5: 12%
- L5→L6: 18%
- L6→L7: 20%
- L7→L8: 10%
- Pattern: Progresses to much higher auth levels

**Insight:** Delayed applications reach levels 7-8, while typical applications complete at level 5. The issue isn't that specific transitions are slow - it's that certain applications require more approvals.

**Action:** Investigate why some applications require level 7-8 approval. Can some be pre-screened to complete at lower levels?

---

## Key Patterns to Identify

### Pattern 1: Fast-Track Applications

**Distribution:** Concentrated in 1d-7d bins

**Transitions:**
- Few segments (2-3 transitions)
- Large percentages per segment
- Complete at levels 2-3
- No backward movements

**Interpretation:** These applications are straightforward, don't require high-level review

**Action:** Document criteria for fast-track. Try to route more applications this way.

### Pattern 2: Standard Processing

**Distribution:** Peak at 2wk-4wk bins

**Transitions:**
- 4-6 transition segments
- Relatively balanced percentages (15-25% each)
- Progress through levels 1-5
- Smooth forward progression

**Interpretation:** Normal workflow, no major bottlenecks

**Action:** This is your baseline. Keep monitoring to ensure it doesn't degrade.

### Pattern 3: Delayed Applications

**Distribution:** Spread across 2mo-6mo bins

**Transitions:**
- Many segments (7+ transitions)
- One or two segments >30% (bottlenecks)
- Reach levels 6+
- May show backward movements (orange segments)

**Interpretation:** Complex cases requiring high-level approval or with issues

**Action:** 
- Identify the specific bottleneck transitions (>30% segments)
- Check if backward movements (L5←L1) are common
- Consider early intervention or additional documentation requirements

### Pattern 4: Problem Cases

**Distribution:** In 6mo+ or 1yr+ bins

**Transitions:**
- Very fragmented (many small segments)
- Multiple backward movements
- Progress to highest auth levels (8+)

**Interpretation:** Exceptional cases, possibly contentious or complex

**Action:**
- Manual review of these specific applications
- May need policy changes or special handling procedures
- Track root causes (missing docs, legal issues, etc.)

---

## Quick Reference: What Each File Shows

| File Pattern | Shows | Use For |
|-------------|--------|---------|
| `*_distribution.png` | How many applications in each time bin | Overall process speed, variability, outliers |
| `*_transitions.png` | Where time is spent in each bin | Identifying bottlenecks, comparing fast vs slow |

---

## Comparison Across Processes

After reviewing individual processes, compare them:

### Speed Comparison
- Which process has lowest median days?
- Which has most applications in 1d-7d bins?
- Which has longest tail (most 3mo+ applications)?

### Complexity Comparison
- Which process has most transitions?
- Which reaches highest auth levels?
- Which shows most backward movements?

### Consistency Comparison
- Which has tightest distribution (small std deviation)?
- Which has most outliers?
- Which is most predictable?

---

## Technical Details

### Time Bin Boundaries

| Label | Days Range | Typical Use |
|-------|-----------|-------------|
| 1d | 0-1 days | Same-day processing |
| 2d | >1-2 days | Next-day processing |
| 3d | >2-3 days | Quick turnaround |
| 4d | >3-4 days | Fast processing |
| 5d | >4-5 days | Business week |
| 6d | >5-6 days | Including weekend |
| 7d | >6-7 days | One week mark |
| 2wk | >7-14 days | Two weeks |
| 3wk | >14-21 days | Three weeks |
| 4wk | >21-28 days | Four weeks/1 month |
| 5wk | >28-35 days | Five weeks |
| 2mo | >35-60 days | Two months |
| 3mo | >60-90 days | Three months/quarter |
| 6mo | >90-180 days | Half year |
| 1yr | >180-365 days | One year |
| 1yr+ | >365 days | Over one year |

### Transition Naming Convention

- **Forward:** `L1→L2` = Level 1 to Level 2
- **Backward:** `L5←L1` = Sent back from Level 5 to Level 1
- **Color scheme:**
  - Blue shades (lighter to darker) = Forward progression through levels
  - Orange/red shades = Backward movements (problems/rejections)

### Percentage Calculation

For each application:
1. Calculate total processing time: `last_timestamp - first_timestamp`
2. For each transition: `transition_time = next_timestamp - current_timestamp`
3. Calculate percentage: `(transition_time / total_time) * 100`
4. Aggregate by bin: Average percentages for all applications in same bin
5. Normalize: Ensure percentages sum to 100% per bin

---

## Next Steps

### Immediate Actions

1. **Open and review all 12 files**
   - Start with largest process (Visa Recommendation)
   - Look at distribution first, then transitions
   - Take notes on patterns you see

2. **Identify top 3 issues**
   - Which process is slowest?
   - Which transitions are bottlenecks (>30% in slow bins)?
   - Are there backward movements indicating problems?

3. **Deep dive on one process**
   - Pick the highest-priority process
   - Extract list of applications in slowest bin (3mo+)
   - Review their actual records and comments
   - Identify common factors

### Analysis Extensions

The script can be easily modified for:

1. **Temporal analysis:** Compare 2023 vs 2024 vs 2025
2. **Industry segmentation:** Tourism vs Service vs ICT applications
3. **Role analysis:** Which roles/teams cause delays
4. **Status analysis:** Approved vs rejected vs sent-back patterns

---

## Summary of Improvements

| Aspect | Before | After | Benefit |
|--------|--------|-------|---------|
| **Time bins** | 8 bins, weekly | 16 bins, daily for week 1 | More detail on early processing |
| **Transitions** | Included review cycles | Transitions only | Cleaner, more intuitive |
| **Format** | 1 combined file | 2 separate files | Easier viewing, better for presentations |
| **Labels** | Legend only | On-bar labels with % | Faster interpretation, exact values visible |

---

**Your visualizations are now more detailed, cleaner, and easier to interpret!**

Review the files and let me know if you need:
- Additional processes analyzed
- Different time bin boundaries
- Specific segmentation (by year, industry, etc.)
- Interactive dashboard version
- Statistical analysis of specific bottlenecks
