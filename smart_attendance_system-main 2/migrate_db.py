import sqlite3

def migrate():
    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE attendance ADD COLUMN latitude REAL")
        cursor.execute("ALTER TABLE attendance ADD COLUMN longitude REAL")
        conn.commit()
        print("✅ Database migration successful: Added latitude and longitude to attendance table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✅ Columns already exist. No migration needed.")
        else:
            print(f"❌ Error during migration: {e}")
            
    conn.close()

if __name__ == "__main__":
    migrate()
