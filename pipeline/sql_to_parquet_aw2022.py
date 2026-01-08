"""
SQL Server to Parquet Pipeline
Reads all tables from AdventureWorks2022 database and exports them to Parquet files.
"""

import os
import pyodbc
import pandas as pd
from pathlib import Path

# Database connection settings
SERVER = "localhost,1433"
DATABASE = "AdventureWorks2022"
USERNAME = "sa"
PASSWORD = "YourStrong!Passw0rd"

# Output directory for parquet files
OUTPUT_DIR = Path(__file__).parent / "AdventureWorks2022_parquet"


def get_connection():
    """Create and return a database connection."""
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(connection_string)


def get_tables(conn) -> list[tuple[str, str]]:
    """Get list of all tables in the database."""
    query = """
        SELECT TABLE_SCHEMA, TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """
    cursor = conn.cursor()
    cursor.execute(query)
    tables = cursor.fetchall()
    cursor.close()
    return [(row[0], row[1]) for row in tables]


def export_table_to_parquet(conn, schema: str, table_name: str, output_dir: Path):
    """Read a table and export it to a Parquet file."""
    full_table_name = f"[{schema}].[{table_name}]"
    query = f"SELECT * FROM {full_table_name}"
    
    print(f"Reading table: {full_table_name}...", end=" ")
    
    try:
        df = pd.read_sql(query, conn)
        
        # Convert datetime columns to microsecond precision for Parquet compatibility
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype('datetime64[us]')
        
        # Create output filename
        output_file = output_dir / f"{schema}_{table_name}.parquet"
        
        # Export to parquet
        df.to_parquet(output_file, index=False, engine="pyarrow")
        
        print(f"✓ Exported {len(df)} rows to {output_file.name}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Main pipeline function."""
    print("=" * 60)
    print("SQL Server to Parquet Pipeline")
    print("=" * 60)
    print(f"Server: {SERVER}")
    print(f"Database: {DATABASE}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print("=" * 60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    print("\nConnecting to database...")
    try:
        conn = get_connection()
        print("✓ Connected successfully!\n")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return
    
    # Get list of tables
    tables = get_tables(conn)
    print(f"Found {len(tables)} tables to export.\n")
    
    # Export each table
    success_count = 0
    fail_count = 0
    
    for schema, table_name in tables:
        if export_table_to_parquet(conn, schema, table_name, OUTPUT_DIR):
            success_count += 1
        else:
            fail_count += 1
    
    # Close connection
    conn.close()
    
    # Summary
    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print(f"Successfully exported: {success_count} tables")
    print(f"Failed: {fail_count} tables")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
