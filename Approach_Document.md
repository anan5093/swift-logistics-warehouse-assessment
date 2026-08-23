# SWIFT Assignment - Choked Hubs Prioritization

**Candidate:** Anand Raj 

**Date:**  August 24, 2026

**Role:** Data Analyst/Business Analyst

---

## 1. Executive Summary

The goal of this assessment is to process raw, nested tracking logs to identify "choked" courier warehouses across the middle-mile logistics network. A choked warehouse is one that is currently failing to clear its active inventory or has a historical track record of severe sorting delays.

Instead of relying on simple averages, which are often skewed by fast-moving parcels, I designed an analytical pipeline that isolates structural tail-end delays and active, stagnant inventory. This document outlines the engineering architecture, data sanitization steps, and the mathematical logic used to flag hubs for immediate operational intervention.

---

## 2. Technical Architecture & Tooling

To process the newline-delimited JSON dataset, I opted for a hybrid DuckDB + Python architecture.

- **DuckDB (SQL Engine):** Chosen for its exceptional speed in processing local files in-memory and its native support for parsing complex JSON arrays. It allows for the execution of advanced window functions without the overhead of spinning up a traditional relational database (like PostgreSQL).

- **Python (Pandas):** Used purely as an orchestration layer to execute the SQL logic, format the console output for easy reading, and export the final compiled dataset to a `.csv` artifact.

---

## 3. Data Engineering & Sanitization

Real-world logistics data is notoriously messy. The raw dataset contained missing keys, inconsistent capitalization, and variable timestamp formats. Before applying any business logic, I built a robust sanitization layer in SQL:

- **Dynamic Schema Inference:** Instead of enforcing a rigid struct that causes crashes when the location key is missing, I ingested the `deduped_track_details` as a raw `JSON[]` array. By using the `->>` operator, missing keys safely default to `NULL` rather than breaking the pipeline.

- **String Normalization:** Warehouse names were standardized using `UPPER()`, `TRIM()`, and `REGEXP_REPLACE()` to strip irregular whitespaces, ensuring that `"Mumbai, MAHARASHTRA"` and `"MUMBAI,  MAHARASHTRA"` resolve to the exact same physical hub.

- **Timestamp Parsing:** Timezone tags (`UTC`) were stripped, and `strptime()` was configured to handle timestamps both with and without fractional seconds.

---

## 4. Mathematical Framework & Business Logic

To mathematically define a "choked" warehouse, I split the evaluation into two distinct dimensions: **Historical Turnaround Inefficiency** and **Active Live Backlog**.

### Dimension A: Historical Dwell Time ($D_h$)

Dwell time represents the transit delay within a specific hub. For any given parcel ($s$) arriving at hub ($h$), the dwell duration is the difference between its arrival scan ($T_{in}$) and its departure scan ($T_{out}$). This was calculated using the SQL `LEAD()` window function to look ahead to the next chronological event.

$$
D_{s, h} = \frac{\text{Epoch}(T_{out}) - \text{Epoch}(T_{in})}{3600}
$$

Instead of using the mean ($\mu$) dwell time, I calculated the **90th Percentile ($P90$)** for each hub. Logistics networks naturally have high volumes of "pass-through" parcels that drag the average down. The $P90$ metric specifically isolates the slowest 10% of shipments, revealing true structural bottlenecks.

### Dimension B: Active Live Backlog ($B_h$)

To find parcels actively choking the system right now, I measured latency relative to the assignment's cutoff date ($T_{cutoff}$ = 2023-10-07 23:59:59).

Let $T_{last}$ be the last known scan of a parcel that has not reached a terminal state (Delivered/Cancelled). The active age ($A_{s,h}$) of a stuck parcel is:

$$
A_{s, h} = \frac{\text{Epoch}(T_{cutoff}) - \text{Epoch}(T_{last})}{3600}
$$

I defined the backlog volume ($B_h$) as the count of all parcels sitting untouched for over 48 hours.

---

## 5. Classification Thresholds

A warehouse ($h$) is flagged as **Prioritize for Clearing** if it satisfies any condition in the following boolean logic gate:

$$
C_h = \begin{cases}
1, & \text{if } (B_h \ge 5) \lor (P90_h > 48) \lor (B_h \ge 2 \land \bar{A}_h > 72) \\
0, & \text{otherwise}
\end{cases}
$$

**Threshold Justifications:**

- **$B_h \ge 5$ (Critical Backlog Volume):** The hub has 5 or more parcels actively stuck for over 2 days.
- **$P90_h > 48$ (Structural Inefficiency):** Historically, 10% of all volume passing through this hub experiences delays of over 48 hours.
- **$B_h \ge 2 \land \bar{A}_h > 72$ (Severe Aging):** Even if the absolute volume of stuck parcels is low (2 or more), they have been decaying on the floor for an average of over 3 days, indicating a severe Service Level Agreement (SLA) breach.

All other facilities operating within normal parameters are tagged as **Ignore**.

---

## 6. Conclusion

By treating tracking events as a time-series dataset and leveraging window functions, this pipeline successfully processed over 8,000 unique hubs. The resulting CSV output provides on-ground operations managers with an immediate, mathematically sound priority list for dispatching clearance teams and re-routing upstream line-haul trucks.
