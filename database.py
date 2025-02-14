import sqlite3

def init_db():
    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        age TEXT,
        gender TEXT,
        phone_no TEXT,
        symptoms TEXT
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

def save_booking(full_name, age, gender, phone_no, symptoms):
    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO bookings (full_name, age, gender, phone_no, symptoms)
    VALUES (?, ?, ?, ?, ?);
    """
    cursor.execute(insert_query, (full_name, age, gender, phone_no, symptoms))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
