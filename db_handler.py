import sqlite3




def list_tables():
    con = sqlite3.connect('obd_data.db')
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    heads = cursor.fetchall()
    #print(heads)
    #print(type(heads[0][0]))
    con.close()
    return heads


def fetch_all_data(table):
    con = sqlite3.connect('obd_data.db')
    cursor = con.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    data = cursor.fetchall()
    print(data)
    con.close()

def fetch_tables_and_top_rows(limit=10):
    con = sqlite3.connect('obd_data.db')
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
    con.close()
    return result



def fetch_table_preview_data(limit=5):
    return _fetch_tables(limit)

def fetch_graph_data(limit=5000):
    return _fetch_tables(limit)

def _fetch_tables(limit):
    conn = sqlite3.connect("your.db")
    cursor = conn.cursor()

    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    table_data = {}

    for (table_name,) in tables:
        rows = cursor.execute(
            f"SELECT timestamp, value FROM {table_name} ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        ).fetchall()
        table_data[table_name] = rows

    conn.close()
    return table_data

#balls = list_tables()
#print(balls)
#fetch_all_data(balls[8][0])
#for ball in balls:
#    fetch_all_data(ball[0])

tables = fetch_tables_and_top_rows(10)
#print(tables)
for table in tables:
    print("\n")
    print(f"{table} : {tables[table]}")
    with open("sample.json", "a") as file:  
        file.write(f"{table} : {tables[table]}")
    file.close()

