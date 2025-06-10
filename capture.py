from datetime import datetime
import obd
import time
import pandas as pd
import sqlite3

# This will store all the data rows
data_tables = {}
conn = sqlite3.connect("obd_data.db")
# a callback that prints every new value to the console
def new_rpm(r):
    print (r.value)

def load_obd_pids():
    df = pd.read_csv("pids.csv")
    print(df.head())

#checks if a command exists
def commands_exist():
    obd.commands.has_command(obd.commands.RPM) # True

def list_all_commands():
    for cmd in obd.commands:
        print(cmd)

def supported_commands():
    connection = obd.OBD()  # or obd.Async("COMx") if you're using async
    # This returns a set of supported commands
    supported = connection.supported_commands
    # Print them out
    for cmd in supported:
        print(cmd.name)
    return supported

def handle_data(rsp):
    val = rsp.value

    if hasattr(val, '__dict__'):  # structured object like Status
       val = str(vars(object_to_dict(val))) # or json.dumps() if you want a stringified dict
    elif hasattr(val, 'magnitude'):
        val = val.magnitude
    else:
        val = str(val)  # fallback to string for BitArray etc.

    data_tables[rsp.command.name].append({
        "timestamp": datetime.now(),
        "value": val,
        "response": None  # optional: remove or serialize if needed
    })

    print(f"RECORDED : {rsp.command.name} = {val}")
    #print(rsp)

def object_to_dict(obj):
    if isinstance(obj, dict):
        return {k: object_to_dict(v) for k, v in obj.items()}
    elif hasattr(obj, '__dict__'):
        return {k: object_to_dict(v) for k, v in vars(obj).items()}
    elif hasattr(obj, 'supported') and hasattr(obj, 'completed'):
        return {
            "supported": obj.supported,
            "completed": obj.completed
        }
    elif hasattr(obj, 'magnitude'):
        return obj.magnitude
    else:
        return str(obj)  # fallback
    
def save_info_old():
    for cmd_name, rows in data_tables.items():
        if not rows:
            continue
        # Remove or convert unserializable fields like `response`
        df = pd.DataFrame([
            {
                "timestamp": row["timestamp"],
                "value": row["value"]
            }
            for row in rows
        ])
        df.set_index("timestamp", inplace=True)
        safe_name = cmd_name.replace(" ", "_").replace("/", "_")
        df.to_csv(f"{safe_name}.csv")
        print(f"Saved: {safe_name}.csv")

def save_info():
    conn = sqlite3.connect("obd_data.db")
    for cmd_name, rows in data_tables.items():
        if not rows:
            continue
        table_name = cmd_name.replace(" ", "_").replace("/", "_")
        df = pd.DataFrame([{
            "timestamp": row["timestamp"],
            "value": row["value"]
        } for row in rows])
        df.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()

    #print table names to a text file, will include empty tables
   
    with open("table-heads.txt", "a") as file:  # open for writing
        for cmd_name, rows in data_tables.items():
            has_rows = "T" if rows else "F"
            file.write(f"{cmd_name} {has_rows}\n")

def regular_query(code):
    ports = obd.scan_serial()
    connection = obd.OBD('COM4')
    print("Ports:")
    print(connection)
    r = connection.query(code)
    print(vars(r))



def main():
    connection = obd.Async(portstr="COM4")
    for cmd in connection.supported_commands:
        print(cmd)
        if cmd.mode == 1 and cmd.header is not None:  # Mode 1 = live data
            try:
                connection.watch(cmd, callback=handle_data)
                data_tables[cmd.name] = []
            except Exception as e:
                print(f"Could not watch {cmd.name}: {e}")
    connection.start()
    
    # the callback will now be fired upon receipt of new values
    time.sleep(10)
    connection.stop()
    save_info()

if __name__ == "__main__":
    main()
    #regular_query(obd.commands.STATUS) #STATUS_DRIVE_CYCLE

    
#for cmd in connection.supported_commands:
#    if cmd.mode == 1 and cmd.header is not None:  # Mode 1 = live data
#        try:
#            connection.watch(cmd, callback=handle_data)
#        except Exception as e:
#            print(f"Could not watch {cmd.name}: {e}")





    #connection = obd.Async(portstr="COM4")
    #connection.watch(obd.commands.RPM, callback=new_rpm)
    #connection.start()
    #
    ## the callback will now be fired upon receipt of new values
    #time.sleep(60)
    #connection.stop()




    # Connect to the OBD-II adapter
    #connection = obd.OBD()  # Auto-connects to USB/Bluetooth if available
    #
    ## Get list of supported commands (Mode 01 PIDs)
    #supported_cmds = connection.supported_commands
    #
    ## Print supported commands
    #for cmd in supported_cmds:
    #    print(cmd.name)





    #ports = obd.scan_serial()
    #print (ports)
    #
    #connection = obd.OBD('COM4')
    #
    #print("works")
    #print(connection)
    #
    #
    #r = connection.query(obd.commands.RPM)
    #print(r