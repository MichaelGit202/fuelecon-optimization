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

balls = list_tables()
print(balls)
fetch_all_data(balls[8][0])
#for ball in balls:
#    fetch_all_data(ball[0])