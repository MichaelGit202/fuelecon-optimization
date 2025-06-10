import sqlite3

con = sqlite3.connect('obd_data.db')


def list_tables():
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    heads = cursor.fetchall()
    #print(heads)
    #print(type(heads[0][0]))
    return heads


def fetch_all_data(table):
    cursor = con.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    data = cursor.fetchall()
    print(data)

def fetch_tables_and_top_rows(limit=10):
    tables = list_tables()
    cursor = con.cursor()
    result = {}
    for (table_name,) in tables:
        try:
            # Try ordering by `id` column (assumed to be the primary key)
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            result[table_name] = rows
        except sqlite3.OperationalError as e:
            print(f"Skipping table '{table_name}': {e}")
            result[table_name] = []
    return result

balls = list_tables()
print(balls)
#fetch_all_data(balls[8][0])
#for ball in balls:
#    fetch_all_data(ball[0])

tables = fetch_tables_and_top_rows()
#print(tables)
for table in tables:
    print("\n")
    print(f"{table} : {tables[table]}")
    with open("sample.json", "a") as file:  
        file.write(f"{table} : {tables[table]}")
    file.close()

