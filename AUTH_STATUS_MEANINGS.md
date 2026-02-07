# Auth Status Meanings - Based on Action Remarks Analysis

**Analysis Date:** January 28, 2026  
**Dataset:** Industry_workflow_history.csv

---

## 📊 Auth Status Distribution

| Status | Records | % of Total | Meaning |
|--------|---------|------------|---------|
| **0** | 1,615 | 2.2% | **Submitted / Pending** |
| **1** | 61,763 | 84.4% | **Approved / Forwarded** |
| **2** | 336 | 0.5% | **Rejected** |
| **3** | 9,315 | 12.7% | **Sent Back for Corrections** |
| **4** | 66 | 0.1% | **Conditionally Approved** |
| **5** | 97 | 0.1% | **Sent for Review/Opinion** |
| **7** | 1 | 0.0% | Unknown |
| **8** | 18 | 0.0% | Unknown |

---

## 🔍 Detailed Analysis by Status

### Status 0: **SUBMITTED / PENDING** (1,615 records)

**Meaning:** Application submitted, awaiting action

**Remarks Characteristics:**
- Very few remarks (only 0.4% have remarks)
- When present, remarks say:
  - "आ का" (Aa Ka - acknowledgment)
  - "आवश्यक कार्यार्थ" (For necessary action)
  - "आवश्यक कारवाहीका लागि पठाईएको" (Sent for necessary action)

**Common Keywords:**
- "necessary" (50%)
- "approved/forward" (33%)

**Interpretation:**
- Initial submission state
- Awaiting first review
- Placeholder/acknowledgment status
- When found as FINAL status → Application is IN-PROGRESS (not yet completed)

**Usage:** Typically the first status when application enters the system

---

### Status 1: **APPROVED / FORWARDED** (61,763 records - 84.4%)

**Meaning:** Approved at current level and forwarded to next level

**Remarks Characteristics:**
- Almost all have remarks (100%)
- Constructive, action-oriented language
- Focus on forwarding and processing

**Sample Remarks:**
- "Approved"
- "FNA" (Forward for Necessary Action)
- "निर्णयार्थ पेश गरेको छु" (Submitted for decision)
- "Review the submitted documents and forward with opinion"
- "पेश गर्ने" (To submit/present)
- "रुजु गरी पेश गर्ने" (Verify and submit)

**Common Keywords:**
- **"approved/forward"** - 90.6% (!!)
- "submit" - 21.7%
- "documents" - 14.1%
- "review/study" - 11.0%
- "necessary" - 9.4%

**Interpretation:**
- **This is the SUCCESS status**
- Application approved at this authority level
- Being forwarded to next level for further processing
- When found as FINAL status → Application is **FULLY APPROVED**

**Usage:** This status appears at EVERY approval step as application progresses

---

### Status 2: **REJECTED** (336 records - 0.5%)

**Meaning:** Application rejected/declined

**Remarks Characteristics:**
- All have remarks (100%)
- Direct rejection language
- Reason provided

**Sample Remarks:**
- "Rejected"
- "Rejected as per the application"
- "Already registered industry (Duplicate entry)"
- "Dual application"
- "Old application"
- "गलत विदेशी लगानी नं राखी पेश गरेकोले" (Incorrect foreign investment number)
- "Not completed"
- "Already approved" (in different system)

**Common Keywords:**
- "reject/sendback" - 23.8%
- "approved/forward" - 22.6% (contradictory - may indicate reversals)
- "documents" - 8.3%

**Interpretation:**
- **Final rejection** - application declined
- Usually for administrative reasons:
  - Duplicate applications
  - Incorrect information
  - Already processed elsewhere
  - Does not meet requirements
- When found as FINAL status → Application is **REJECTED**

**Usage:** Terminal status - application process ends here

---

### Status 3: **SENT BACK FOR CORRECTIONS** (9,315 records - 12.7%)

**Meaning:** Issues found, sent back to applicant for corrections/revisions

**Remarks Characteristics:**
- Almost all have remarks (100%)
- Specific instructions for corrections
- NOT a final rejection - can be fixed and resubmitted

**Sample Remarks:**
- "Send back"
- "Correction"
- "Back"
- "Upload the shareholder information document"
- "Passport number Correction"
- "Correct the nationality"
- "Corrections"
- "उद्योग दर्ता मिति, PI No र date मिलाउनुहुन" (Correct registration date, PI number)
- "विवरण मिलाउनु" (Match the details)
- "Please specify objectives in system like proposal"

**Common Keywords:**
- "documents" - 19.8%
- "approved/forward" - 18.8%
- "review/study" - 7.4%
- "submit" - 4.0%

**Interpretation:**
- **TEMPORARY setback** - NOT a rejection
- Application has issues that need fixing
- Applicant can correct and resubmit
- Common pattern: Status 3 → (corrections made) → Status 1 (approved)
- When found as FINAL status → Application is **STUCK / AWAITING CORRECTIONS**

**Usage:** Intermediate status - application can recover from this

---

### Status 4: **CONDITIONALLY APPROVED** (66 records - 0.1%)

**Meaning:** Approved with conditions/stipulations

**Remarks Characteristics:**
- Most have remarks (84.8%)
- Focus on conditions being added

**Sample Remarks:**
- "Conditions Added"
- "Condition Added"
- "शर्त" (Condition/Stipulation)
- "क्षमता संशोधन गरी पेश गरेको छु" (Capacity revised and submitted)

**Common Keywords:**
- "approved/forward" - 28.6%
- "submit" - 5.4%

**Interpretation:**
- **Approved BUT with conditions**
- Additional requirements/stipulations attached
- Must fulfill conditions before final approval
- Rare status (only 0.1% of records)

**Usage:** Special approval with strings attached

---

### Status 5: **SENT FOR REVIEW / OPINION** (97 records - 0.1%)

**Meaning:** Sent to technical/specialized review for opinion

**Remarks Characteristics:**
- Almost all have remarks (99%)
- Focus on seeking expert opinion

**Sample Remarks:**
- "Review"
- "रायका लागि प्रेशित" (Sent for opinion)
- "रायको लागि प्रेेशित" (Sent for opinion)
- "परियोजना विवरणमा रायका लागि पेश" (Project details submitted for opinion)
- "FNA"

**Common Keywords:**
- "approved/forward" - 105% (counts multiple mentions)
- "documents" - 32.3%
- "submit" - 21.9%
- "necessary" - 15.6%

**Interpretation:**
- **Specialized review needed**
- Technical/expert opinion required
- Often for complex projects (e.g., technical specifications, environmental impact)
- Not a rejection - just need expert input

**Usage:** Routing to specialized reviewer/technical committee

---

### Status 7 & 8: **UNKNOWN** (19 records total)

**Remarks:** No remarks available

**Interpretation:** Extremely rare, meaning unclear

---

## 🎯 Application Lifecycle Patterns

### Pattern 1: SUCCESSFUL APPLICATION (Status ends with 1)

```
Status 0 (Submitted)
  ↓
Status 1 (Level 1 approved) → Forward to Level 2
  ↓
Status 1 (Level 2 approved) → Forward to Level 3
  ↓
Status 1 (Level 3 approved) → Forward to Level 4
  ↓
Status 1 (Level 4 approved) → Forward to Level 5
  ↓
Status 1 (Level 5 FINAL APPROVAL) ✅
```

**Total time:** Varies by process (1 day to 1+ year)

---

### Pattern 2: APPLICATION WITH CORRECTIONS (Status 3 in middle, ends with 1)

```
Status 0 (Submitted)
  ↓
Status 1 (Level 1 approved)
  ↓
Status 1 (Level 2 approved)
  ↓
Status 3 (Level 3 SENT BACK) ← "Equity amount mismatch"
  ↓
[APPLICANT FIXES ISSUES]
  ↓
Status 3 (Level 3 SENT BACK AGAIN) ← "Investment details incomplete"
  ↓
[APPLICANT FIXES ISSUES]
  ↓
Status 1 (Level 3 approved) ← "Corrected, forwarding"
  ↓
Status 1 (Level 4 approved)
  ↓
Status 1 (Level 5 FINAL APPROVAL) ✅
```

**Total time:** Longer due to correction cycles (typically adds weeks/months)

---

### Pattern 3: REJECTED APPLICATION (Status ends with 2 or 3)

**Early Rejection (Status 2):**
```
Status 0 (Submitted)
  ↓
Status 1 (Level 1 reviewed)
  ↓
Status 2 (REJECTED) ❌ ← "Duplicate application"
```

**Stuck at Corrections (Status 3):**
```
Status 0 (Submitted)
  ↓
Status 1 (Level 1 approved)
  ↓
Status 1 (Level 2 approved)
  ↓
Status 3 (Level 3 SENT BACK) ← "Does not meet PPP requirements"
  ↓
[APPLICANT NEVER RESPONDS]
  ↓
Status 3 (FINAL - STUCK) ❌
```

---

### Pattern 4: IN-PROGRESS APPLICATION (Status ends with 0)

```
Status 0 (Submitted)
  ↓
Status 1 (Level 1 approved)
  ↓
Status 1 (Level 2 approved)
  ↓
Status 0 (WAITING at Level 3) ⏳ ← Still being processed
```

---

## 📋 Classification Rules for Analysis

### Rule 1: Completed Applications

```python
if final_auth_status == 1:
    classification = "APPROVED & COMPLETED"
    include_in = "Time to Approval Analysis"
```

### Rule 2: Rejected Applications

```python
if final_auth_status == 2:
    classification = "REJECTED (Administrative)"
    include_in = "Rejection Analysis"
    
if final_auth_status == 3:
    classification = "REJECTED (Awaiting Corrections - Never Resubmitted)"
    include_in = "Rejection Analysis"
```

### Rule 3: In-Progress Applications

```python
if final_auth_status == 0:
    classification = "IN-PROGRESS"
    include_in = "Current Workload Analysis"
    note = "Time shown is 'time so far' not 'total time'"
```

### Rule 4: Special Cases

```python
if final_auth_status == 4:
    classification = "CONDITIONALLY APPROVED"
    include_in = "Approved (with conditions)"
    
if final_auth_status == 5:
    classification = "UNDER REVIEW"
    include_in = "In-Progress Analysis"
```

---

## 🎯 Recommended Visualizations

### Visualization 1: Time to Approval (Status = 1 only)

**Filter:** `final_auth_status == 1`

**Shows:** True "completion time" for successful applications

**Example Results for Industry Registration:**
- Total: 1,982 applications (94.3%)
- Avg time: 42 days
- Median: 28 days

---

### Visualization 2: Time to Rejection (Status = 2 or 3 only)

**Filter:** `final_auth_status in [2, 3]`

**Shows:** How long before application is rejected/stuck

**Example Results for Industry Registration:**
- Total: 130 applications (6.2%)
- Avg time: 18 days (faster than approvals - fail early)
- Median: 12 days

---

### Visualization 3: Time In Process (Status = 0 only)

**Filter:** `final_auth_status == 0`

**Shows:** Applications currently being processed

**Example Results for Industry Registration:**
- Total: 42 applications (2.0%)
- Time so far: 65 days average
- Note: These may eventually become approved or rejected

---

## 💡 Key Insights

### 1. Status 1 Dominance (84.4%)

Most workflow records show Status 1 (approved/forwarded) because:
- This status appears at EVERY step of progression
- An application moving through 5 levels generates 5 Status 1 records
- This is the "normal" flow status

### 2. Status 3 is NOT a Final Rejection

**Important:** Status 3 means "sent back for corrections" - it's RECOVERABLE
- 12.7% of all records have Status 3
- Many applications show Status 3 → (corrections) → Status 1 (approved)
- Only applications ENDING with Status 3 are truly stuck/rejected

### 3. True Rejection Rate is Low

**Actual rejections (Status 2):** Only 0.5% of records
- These are final, administrative rejections
- Usually duplicate applications or procedural issues

### 4. High Success Rate

For Industry Registration:
- **94.3%** ultimately approved (Status 1)
- **3.1%** stuck/rejected (Status 3)
- **2.0%** still in process (Status 0)
- **0.6%** rejected administratively (Status 2)

---

## 📊 Example: Full Application Journey

**Application ID: 143130 (From the data)**

| Date | Level | Status | Remark (translated) | Interpretation |
|------|-------|--------|---------------------|----------------|
| Sep 13, 2022 | 1 | 1 | For necessary action | ✅ Approved at L1 |
| Sep 13, 2022 | 2 | 1 | Please do necessary action | ✅ Approved at L2 |
| Nov 28, 2022 | 3 | 1 | Please check | ✅ Approved at L3 |
| Nov 29, 2022 | 4 | 1 | Study documents and forward | ✅ Approved at L4 |
| Jan 12, 2023 | 5 | **3** | **Equity amount mismatch** | ⚠️ SENT BACK |
| Jan 11, 2024 | 5 | **3** | **Investment details incomplete** | ⚠️ SENT BACK AGAIN |
| Jan 11, 2024 | 5 | 1 | Corrected, forwarding | ✅ Approved at L5 |
| Mar 20, 2024 | 6 | 1 | Forwarding | ✅ Approved at L6 |
| Mar 26, 2024 | 7 | 1 | Submitted for decision | ✅ Approved at L7 |
| Mar 26, 2024 | 8 | 1 | Opinion submitted for decision | ✅ Approved at L8 |
| Mar 26, 2024 | 9 | 1 | **Approved** | ✅ **FINAL APPROVAL** |

**Total Time:** 19 months (with 1-year delay at Level 5 corrections)

**Final Status:** 1 (APPROVED)

---

## 🔄 Workflow State Machine

```
           ┌─────────────┐
           │  Status 0   │
           │ (Submitted) │
           └──────┬──────┘
                  │
                  ▼
           ┌─────────────┐
           │  Status 1   │────────┐
           │ (Approved)  │        │ Multiple levels
           └──────┬──────┘◄───────┘ (1→2→3→4→5...)
                  │
         ┌────────┼────────┐
         │        │        │
         ▼        ▼        ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │Status 3│ │Status 5│ │Status 4│
    │(Send   │ │(Review)│ │(Cond.) │
    │ Back)  │ └───┬────┘ └───┬────┘
    └───┬────┘     │          │
        │          │          │
        │ Can fix  ▼          ▼
        └────────►Status 1  Status 1
                 (Approved)(Approved)
                     │
              ┌──────┴──────┐
              │             │
              ▼             ▼
        ┌─────────┐   ┌─────────┐
        │Status 1 │   │Status 2 │
        │(FINAL   │   │(Rejected)│
        │APPROVAL)│   └─────────┘
        └─────────┘         ❌
              ✅
```

---

## ✅ Summary

| Status | Meaning | Final State? | Include in "Completed" Analysis? |
|--------|---------|--------------|----------------------------------|
| **0** | Submitted/Pending | No | No (in-progress) |
| **1** | Approved/Forwarded | **Yes** | **Yes** (success metric) |
| **2** | Rejected | **Yes** | No (rejection) |
| **3** | Sent Back for Corrections | Depends* | No (if final = stuck/rejected) |
| **4** | Conditionally Approved | Yes | Yes (with caveats) |
| **5** | Sent for Review | No | No (in-progress) |

\* Status 3 as final state = effectively rejected (never resubmitted)

---

**Document Version:** 1.0  
**Last Updated:** January 28, 2026  
**Based on:** Action remarks analysis of 73,211 workflow records
