Swift Logistics Warehouse Bottleneck Assessment

📌 Overview

This collection has a data engineering and analytics process that is designed to evaluate middle-mile logistics network performance. By processing very nested JSON shipment tracking logs the process finds and marks "choked" courier warehouses that need immediate action.

Of depending on averages that can be easily wrong this solution uses 90th Percentile (P90) Dwell Times and Active Live Backlog volume to find real structural problems.

🛠️ Tech Stack & Architecture

SQL Engine: DuckDB. Chosen for its performance when querying local JSON files in memory and for handling complex array structures without needing a separate database server.

Orchestration: Python 3

Data Formatting: Pandas (for showing results on the terminal and for exporting to CSV)

📂 Repository Structure

warehouse_analysis.sql: The DuckDB SQL script. Handles enforcing the structure, cleaning strings parsing timestamps, using window functions (LEAD()). Deciding what to classify.

run_pipeline.py: The Python script that connects to DuckDB runs the SQL query shows the analysis on the terminal and creates the CSV file.

Approach_Document.md: A detailed explanation of the math used, why the thresholds were chosen and what actions to take.

warehouse_priority_list.csv: The final result that has the list of warehouses that need attention (created when the script runs).

.gitignore: Makes sure the big raw dataset (dataset.json) is not added to version control.

🚀. Execution

1. Prerequisites

Make sure you have Python 3.8 or newer installed. You need to install the needed libraries:

pip install duckdb pandas

2. Add the Dataset

Since the original dataset is large it is not included. Put the dataset.json file in the folder of this project before starting the process.

3. Run the Pipeline

Start the process from your terminal:

python run_pipeline.py

4. Output

After running the script will:

Show a clean table on the terminal with the worst warehouses.

Create a file called warehouse_priority_list.csv in the folder.

🧠 Core Methodology

The classification process marks a warehouse as Prioritize for Clearing if any of these conditions are met compared to the evaluation date (2023-10-07 23:59:59):

Critical Backlog: Has 5 or more parcels stuck with no movement for than 48 hours.

Inefficiency: The past 90th Percentile dwell time of the place is more than 48 hours.

Severe SLA Breach: Has 2 or more parcels that have not moved for an average of, than 72 hours.

All other places are marked as Ignore.

Author: Anand Raj