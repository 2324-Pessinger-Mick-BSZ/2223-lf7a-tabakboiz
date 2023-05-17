import sys
sys.path.insert(0, "..")
from opcua import Client
import time
from datetime import datetime
import sqlite3

database = "schalter_db.sqlite3"
ip_address_pi = "192.168.2.59"

#Verbindungsaufbau mit SQLLite
try:
    conn = sqlite3.connect(database)
except sqlite3.Error as e:
    print(e) 

cursor = conn.cursor()

#Tabelle: pktime | temperature | gas | humidity | pressure | altitude 
cursor.execute("""CREATE TABLE IF NOT EXISTS zustaende (pktime DATETIME UNIQUE NOT NULL, temperature DECIMAL(15, 10) NOT NULL, gas DECIMAL(15, 10) NOT NULL, humidity DECIMAL(15, 10) NOT NULL, 
pressure DECIMAL(15, 10) NOT NULL, altitude DECIMAL(15, 10) NOT NULL, CONSTRAINT PK_pktime PRIMARY KEY(pktime));""")

#Verbindung zum OPCUA Server
client = Client("opc.tcp://" + ip_address_pi + ":4840")
client.connect()


#Datenaktualisierung
while True:

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")


    #Werte aus dem OPCUA Server auslesen
    Changed = client.get_node('ns=2;i=8').get_value()
    var_pressure = client.get_node('ns=2;i=6').get_value()
    var_humidity = client.get_node('ns=2;i=5').get_value()
    var_gas = client.get_node('ns=2;i=4').get_value()
    var_altitude = client.get_node('ns=2;i=7').get_value()
    var_temp = client.get_node('ns=2;i=3').get_value()
    var_time = client.get_node('ns=2;i=9').get_value()

    #Einfügen der ausgelesenen Werte in SQLLite
    count = cursor.execute("""
    INSERT INTO zustaende (pktime, temperature, gas, humidity, pressure, altitude) 
    VALUES (?,?,?,?,?, ?);""",
    (current_time, var_temp, var_gas, var_humidity, var_pressure, var_altitude)).rowcount
    conn.commit()

    #1.1 um sicher zu gehen dass die Zeit als Primary Key gegeben werden kann
    time.sleep(1.1)