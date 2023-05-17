import time
from datetime import datetime
import board
import adafruit_bme680
from opcua import ua, Server
import netifaces as ni
import paho.mqtt.client as paho
import json


a = [0,0,0,0,0]
b = a.copy()
Flag = 0

#Temperatur kalibrieren
temperature_offset = -5

#Verbindung zum Server für Dashboard
hostname = 'localhost'
port = 1883
topic_name = "home/air"

mqttc = paho.Client()
mqttc.connect(hostname, port)


#Server für OPC
server=Server()

IPV4_Address = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
url="opc.tcp://"+IPV4_Address+":4840"
server.set_endpoint(url)

server.set_security_policy(
    [
        ua.SecurityPolicyType.NoSecurity
    ])


#Aufsetzen der hierachischen Abbildung der Werte in OPCUA
name = "Luft_Server"
addspace = server.register_namespace(name)
node = server.get_objects_node()

Raspi=node.add_object(addspace,"Raspi")

myfolder = Raspi.add_folder(addspace, "Messung")

var_temp = myfolder.add_variable(addspace,"Temperatur",6.1)
var_gas = myfolder.add_variable(addspace,"Gas",6.2)
var_humidity = myfolder.add_variable(addspace,"Feuchtigkeit",6.3)
var_pressure = myfolder.add_variable(addspace,"Druck",6.4)
var_altitude = myfolder.add_variable(addspace,"Höhe",6.5)

Changed = myfolder.add_variable(addspace,"Changed",6.6)
Time = myfolder.add_variable(addspace,"Time",0)

var_temp.set_writable()
var_gas.set_writable()
var_humidity.set_writable()
var_pressure.set_writable()
var_altitude.set_writable()

Changed.set_writable()
Time.set_writable()

#Sensor Objekt erstellen über I2C BOard
i2c = board.I2C()
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)


#OPC Server wird gestarten
server.start()
print("Server startet auf {}".format(url))


while True:
    
    TIME = datetime.now()

    b = a.copy()
    
    #Werte vom Sensor in einem Array speichern
    a[0] = bme680.temperature + temperature_offset
    a[1] = bme680.gas
    a[2] = bme680.relative_humidity
    a[3] = bme680.pressure
    a[4] = bme680.altitude

    #Änderung regestrieren
    if a == b:
        Flag = 0
    else: 
        Flag = 1
        
        
    #Werte vom Sensor in OPCUA eintragen
    var_temp.set_value(a[0])
    var_gas.set_value(a[1])
    var_humidity.set_value(a[2])
    var_pressure.set_value(a[3])
    var_altitude.set_value(a[4])
    
    Changed.set_value(Flag)
    Time.set_value(TIME)
    
    
    #Daten über mqttc publizieren
    data_dict = {'Temperatur': a[0], 'Gas': a[1], 'Humidity': a[2], 'Pressure': a[3], 'Altitude': a[4]}
    mqttc.publish(topic_name, json.dumps(data_dict))
    

    time.sleep(1)



