import duckdb
import pandas as pd

def main():
    # Configure Pandas to print a clean, wide table in the terminal
    pd.set_option('display.max_rows', 20)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.colheader_justify', 'left')

    con = duckdb.connect()
    
    # Read the SQL file we just created
    with open('warehouse_analysis.sql', 'r') as f:
        query = f.read()

    # Execute and dump to dataframe
    df = con.sql(query).df()
    
    # Save the required 3rd deliverable
    output_file = 'warehouse_priority_list.csv'
    df.to_csv(output_file, index=False)
    
    # Print the summary stats
    print("\n" + "=" * 90)
    print(" LOGISTICS WAREHOUSE BOTTLENECK ANALYSIS ".center(90))
    print("=" * 90)
    print(f"Total Warehouses Evaluated: {len(df)}")
    print(f"Prioritize for Clearing:    {(df['priority_category'] == 'Prioritize for Clearing').sum()}")
    print(f"Ignore (Normal Flow):       {(df['priority_category'] == 'Ignore').sum()}")
    print(f"Exported to:                {output_file}")
    
    # Print the actual table preview
    print("\n" + "-" * 90)
    print(" PRIORITY WAREHOUSES PREVIEW (TOP 15) ".center(90))
    print("-" * 90)
    print(df.head(15).to_string(index=False))
    print("=" * 90 + "\n")

if __name__ == '__main__':
    main()