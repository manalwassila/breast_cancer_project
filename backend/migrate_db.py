import sqlite3

def migrate():
    conn = sqlite3.connect('mammoscan.db')
    cur = conn.cursor()
    
    # List of columns to check/add for Analysis table
    columns_to_add = [
        ('doctor_result', 'VARCHAR'),
    ]
    
    cur.execute('PRAGMA table_info(analyses)')
    existing_columns = [col[1] for col in cur.fetchall()]
    
    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            print(f"Adding column {col_name} to analyses table...")
            cur.execute(f"ALTER TABLE analyses ADD COLUMN {col_name} {col_type}")
        else:
            print(f"Column {col_name} already exists.")
            
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
