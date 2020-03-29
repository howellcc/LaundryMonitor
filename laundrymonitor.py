#import what we need
import time
import datetime
import json
import smbus
import http.client, urllib
import inspect, os

#GLOBALS
SECONDSBETWEENCHECKS = 10
PUSHOVERAPITOKEN = ""
PUSHOVERUSERKEY = ""
PREVIOUSLIGHTSTATE = False
LIGHTFIRSTNOTICED = datetime.MINYEAR


def Main():
    "This is the main execution of the Laundry Monitor. Its an infinite loop."
    global PUSHOVERAPITOKEN
    global PUSHOVERUSERKEY
    global SECONDSBETWEENCHECKS
    
    settingsFile = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/pushovercredentials.json"
    #import pushover credentials from outside file. 
    try:
        #read json file and load credentials
        with open(settingsFile) as f:
            d = json.load(f)
            PUSHOVERUSERKEY = d["PUSHOVERUSERKEY"]
            PUSHOVERAPITOKEN = d["PUSHOVERAPITOKEN"]
    except:
        #load failed, likely because the file didn't exist. Create it so it can be filled.
        poCredsFile = open(settingsFile,"w+")
        poCredsFile.write("{\r\n    \"PUSHOVERUSERKEY\":\"\",\r\n    \"PUSHOVERAPITOKEN\": \"\"\r\n}")
        poCredsFile.close()
        print("Pushover credentials file didn't exist, please fill in.")
        return;
    
    #Our credentials file might exits, but it might not be populated. 
    if(len(PUSHOVERAPITOKEN) == 0 or len(PUSHOVERUSERKEY) == 0):
        print("Pushover credentials are empty")
        return

    #Time to get down to business
    while(1):
        MonitorTheWashingMachine()
        MonitorTheDryer()
        time.sleep(SECONDSBETWEENCHECKS)
    return;


def MonitorTheWashingMachine():
    "This function monitors the washing machine."
    #print("Monitor the Washing Machine")
    global LIGHTFIRSTNOTICED
    global PREVIOUSLIGHTSTATE

    currentLightState = IsWasherDone()
    #print("previous light state: ",PREVIOUSLIGHTSTATE)
    #print("current light state: ",currentLightState)
    if(PREVIOUSLIGHTSTATE == False and currentLightState):
        #print("I should notify")
        SendNofitication("Washer is Done!!!")
        LIGHTFIRSTNOTICED = datetime.datetime.now
    #else if()
    #TODO HERE
    PREVIOUSLIGHTSTATE = currentLightState
    return;

def MonitorTheDryer():
    "This function monitors the dryer."
    if(IsDryerDone()):
        #figure out if we should actually send a notification
        #Have we already notified
        #Do we need to notify again
        #Are we outside of quiet hours?
        SendNofitication("The Dryer is Done!!!")
    return;

def IsWasherDone():
    "Checks the light"
    #check the light

    # Get I2C bus
    bus = smbus.SMBus(1)

    # TSL2561 address, 0x39(57)
    # Select control register, 0x00(00) with command register, 0x80(128)
    #		0x03(03)	Power ON mode
    bus.write_byte_data(0x39, 0x00 | 0x80, 0x03)
    # TSL2561 address, 0x39(57)
    # Select timing register, 0x01(01) with command register, 0x80(128)
    #		0x02(02)	Nominal integration time = 402ms
    bus.write_byte_data(0x39, 0x01 | 0x80, 0x02)

    time.sleep(0.5)

    # Read data back from 0x0C(12) with command register, 0x80(128), 2 bytes
    # ch0 LSB, ch0 MSB
    data = bus.read_i2c_block_data(0x39, 0x0C | 0x80, 2)

    # Read data back from 0x0E(14) with command register, 0x80(128), 2 bytes
    # ch1 LSB, ch1 MSB
    data1 = bus.read_i2c_block_data(0x39, 0x0E | 0x80, 2)

    # close the bus
    bus.close()

    # Convert the data
    ch0 = data[1] * 256 + data[0]
    ch1 = data1[1] * 256 + data1[0]

    # Output data to screen
    #print("Full Spectrum(IR + Visible) :%d lux", ch0)
    #print("Infrared Value :%d lux", ch1)
    #print("Visible Value :%d lux", (ch0 - ch1))

    currentLightState = False
    if(ch0 > 2):
        currentLightState = True
    return currentLightState;

def IsDryerDone():
    "Check the vibration sensor. Return true if vibration has stopped"
    #TODO check the vibration sensor
    return False;

def SendNofitication( message ):
    "Sends the Pushover notification"
    if(len(PUSHOVERAPITOKEN) > 0 and len(PUSHOVERUSERKEY) > 0):
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": PUSHOVERAPITOKEN,
            "user": PUSHOVERUSERKEY,
            "message": message,
        }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
        #print("notification sent")
    return;
        

# excution
Main()
