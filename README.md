# Swift Logistics Warehouse Bottleneck Assessment

**Author:** Anand Raj  
**Project Type:** Data Engineering & Analytics Pipeline  
**Primary Focus:** Middle-mile logistics network performance evaluation  

---

## 📌 Overview

This repository contains a complete data engineering and analytics pipeline designed to evaluate middle-mile logistics network performance.  

By processing raw, heavily nested JSON shipment tracking logs, the pipeline systematically identifies and flags **"choked"** courier warehouses that require immediate operational intervention.

### Why This Approach?

Traditional logistics monitoring often relies on average dwell times, which can be heavily skewed by outliers or small sample sizes.  

This solution instead leverages two more robust signals:

- **90th Percentile (P90) Dwell Times** — captures structural inefficiency rather than being distorted by a few extreme cases.
- **Active Live Backlog Volume** — measures real-time operational pressure (parcels currently stuck).

Together, these metrics isolate true structural bottlenecks that demand prioritization.

---

## 🛠️ Tech Stack & Architecture

| Component              | Technology     | Rationale                                                                 |
|------------------------|----------------|---------------------------------------------------------------------------|
| **SQL Engine**         | DuckDB         | Exceptional speed when querying local JSON files in-memory. Native support for unnesting complex nested arrays without requiring a dedicated database server. |
| **Orchestration**      | Python 3       | Lightweight, flexible orchestration layer. Handles connection to DuckDB, execution, terminal rendering, and CSV export. |
| **Data Formatting**    | Pandas         | Used for clean terminal output rendering and generation of the final CSV artifact. |

### High-Level Flow

1. Raw nested JSON (`dataset.json`) is read by DuckDB.
2. Complex array structures are unnested and cleaned.
3. Timestamp parsing, dwell time calculations, and window functions (`LEAD()`) are applied.
4. Classification logic flags warehouses based on backlog and P90 thresholds.
5. Results are printed to the terminal and exported as `warehouse_priority_list.csv`.

---

## 📂 Repository Structure

```
.
├── warehouse_analysis.sql      # Core DuckDB SQL script
├── run_pipeline.py             # Python orchestrator
├── Approach_Document.md        # Mathematical framework & recommendations
├── warehouse_priority_list.csv # Generated output (priority list)
├── dataset.json                # Raw input (gitignored due to size)
├── .gitignore
└── README.md                   # This file
```

### File Descriptions

| File                         | Purpose |
|-----------------------------|---------|
| `warehouse_analysis.sql`    | Core analytical logic. Handles schema enforcement, string sanitization, timestamp parsing, window functions (`LEAD()`), dwell-time calculations, and final classification. |
| `run_pipeline.py`           | Python execution script. Connects to an in-memory DuckDB instance, executes the SQL, formats terminal output via Pandas, and exports the final CSV. |
| `Approach_Document.md`      | Detailed breakdown of the mathematical framework, threshold justifications, and operational recommendations. |
| `warehouse_priority_list.csv` | Final generated artifact containing the prioritized list of flagged hubs. |
| `.gitignore`                | Excludes the large raw dataset (`dataset.json`) from version control. |

---

## 🚀 Setup and Execution

### 1. Prerequisites

- Python **3.8+**
- Required packages:

```bash
pip install duckdb pandas
```

### 2. Add the Dataset

The raw dataset is large and therefore excluded via `.gitignore`.

Place the file `dataset.json` in the **root directory** of this project before running the pipeline.

### 3. Run the Pipeline

From the project root, execute:

```bash
python run_pipeline.py
```

### 4. Expected Output

Upon successful execution the script will:

1. Print a cleanly formatted summary table to the terminal showing the worst-offending hubs.
2. Generate `warehouse_priority_list.csv` in the project root.

---

## 🧠 Core Methodology

All classifications are performed relative to a fixed **evaluation anchor date**:

```
2023-10-07 23:59:59
```

A warehouse is flagged as **Prioritize for Clearing** if it meets **any** of the following conditions:

| Condition                    | Threshold                                      | Interpretation |
|-----------------------------|------------------------------------------------|----------------|
| **Critical Backlog**        | ≥ 5 parcels stuck without movement for > 48 hours | Immediate operational pressure |
| **Structural Inefficiency** | Historical P90 dwell time > 48 hours           | Systemic process or capacity problem |
| **Severe SLA Breach**       | ≥ 2 parcels stationary for an average of > 72 hours | High-risk service level failures |

Warehouses that do **not** meet any of the above criteria are tagged as **Ignore**.

### Design Philosophy

- Prefer **percentile-based** metrics over means to reduce the impact of outliers.
- Combine **historical structural signals** (P90) with **current live backlog** for a more complete picture.
- Keep thresholds deliberately conservative so that only warehouses with clear, actionable problems are surfaced.

---

## 📊 Output Artifact

The primary deliverable is:

```
warehouse_priority_list.csv
```

This file contains the prioritized list of warehouses that require operational attention, ranked according to the severity of the signals described above.

---

## 📝 Notes & Recommendations

- Always verify that `dataset.json` is present and correctly named before running the pipeline.
- The SQL script is designed to be self-contained and can be inspected independently of the Python orchestrator.
- For production use, consider parameterizing the anchor date and thresholds so they can be adjusted without modifying the core SQL.

---

**Author:** Anand Raj  
**Last Updated:** August 2026
