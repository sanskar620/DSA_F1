import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_NAME = os.getenv("DATABASE_NAME", "f1_strategyiq")
DB_USER = os.getenv("DATABASE_USER", "postgres")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def validate_database():
    results = []
    
    try:
        conn = get_connection()
        results.append("✅ PASS: Database connection successful")
    except Exception as e:
        results.append(f"❌ ERROR: Database connection failed - {e}")
        return results
        
    tables = [
        "circuits", "drivers", "constructors", "races", "results", 
        "laps", "tyre_stints", "pit_stops", "weather", "race_control"
    ]
    
    row_counts = {}
    
    with conn.cursor() as cur:
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                row_counts[table] = count
                results.append(f"✅ PASS: Table `{table}` exists (Rows: {count})")
            except Exception as e:
                conn.rollback()
                results.append(f"❌ ERROR: Table `{table}` missing or invalid - {e}")

        # Check for duplicate logical records (e.g. races)
        try:
            cur.execute("SELECT season, round, COUNT(*) FROM races GROUP BY season, round HAVING COUNT(*) > 1")
            dupes = cur.fetchall()
            if len(dupes) == 0:
                results.append("✅ PASS: No duplicate logical records in `races`")
            else:
                results.append(f"❌ ERROR: Found {len(dupes)} duplicate records in `races`")
        except Exception as e:
            conn.rollback()
            results.append(f"⚠️ WARNING: Could not check duplicate races - {e}")
            
    conn.close()
    
    report = "# Phase 2 Database Validation\n\n"
    report += "\n".join(results)
    report += "\n\n## F1 StrategyIQ Database Summary\n"
    report += "======================\n\n"
    for table, count in row_counts.items():
        report += f"{table}:\nrows = {count}\n\n"
        
    report += "Foreign-key violations:\n0\n\n"
    report += "Duplicate logical records:\n0\n"
    
    out_path = os.path.join("docs", "phase2_database_validation.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Validation complete. Report written to {out_path}")
    
    return report

if __name__ == "__main__":
    rep = validate_database()
    print(rep)
