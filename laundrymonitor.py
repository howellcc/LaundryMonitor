#import what we need
import time
import datetime
import json
import smbus
import http.client, urllib
import inspect, os
import RPi.GPIO as GPIO

#GLOBALS
SECONDSBETWEENCHECKS = 10
LIGHTSENSORTHRESHOLD = 50
PUSHOVERAPITOKEN = ""
PUSHOVERUSERKEY = ""
PREVIOUSLIGHTSTATE = False
LIGHTFIRSTNOTICED = datetime.MINYEAR
LASTNOTIFICATIONSENT = datetime.datetime.now()
REMINDERSSENT = 0
DRYER_ISVIBRATING = False
DRYER_VIBRATION_STARTTIME = datetime.datetime(2000,1,1,0,0,0)
DRYER_LAST_VIBRATION_TIME = datetime.datetime(9999,1,1,0,0,0)
DRYER_STOP_TIME_THRESHOLD_SEC = 60
DRYER_MIN_RUNTIME_THRESHOLD_SEC = 60 * 5
DRYER_SENSOR_PIN = 14


def Main():
    "This is the main execution of the Laundry Monitor. Its an infinite loop."
    global PUSHOVERAPITOKEN
    global PUSHOVERUSERKEY
    global SECONDSBETWEENCHECKS
    
    settingsFile = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/laundrymonitorconfig.json"
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
        poCredsFile.write("{\r\n    \"PUSHOVERUSERKEY\":\"\",\r\n")
        poCredsFile.write("    \"PUSHOVERAPITOKEN\": \"\",\r\n")
        poCredsFile.write("    \"QUIETHOURSSTART\": \"22:00\",\r\n")
        poCredsFile.write("    \"QUIETHOURSEND\": \"7:00\",\r\n")
        poCredsFile.write("    \"MINUTESBETWEENREMINDERS\": \"15\",\r\n")
        poCredsFile.write("    \"MAXNUMBEROFREMINDERS\": \"10\"\r\n")
        poCredsFile.write("}")
        poCredsFile.close()
        print("Pushover credentials file didn't exist, please fill in.")
        return;
    
    #Our credentials file might exits, but it might not be populated. 
    if(len(PUSHOVERAPITOKEN) == 0 or len(PUSHOVERUSERKEY) == 0):
        print("Pushover credentials are empty")
        return
    
    SetupDryer()

    #Time to get down to business
    while(1):
        MonitorTheWashingMachine()
        MonitorTheDryer()
        time.sleep(SECONDSBETWEENCHECKS)
    return;

def SetupDryer():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DRYER_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(DRYER_SENSOR_PIN, GPIO.RISING)
    GPIO.add_event_callback(DRYER_SENSOR_PIN, DryerSensorCallback)

def DryerSensorCallback(x):
    global DRYER_ISVIBRATING
    global DRYER_LAST_VIBRATION_TIME
    global DRYER_VIBRATION_STARTTIME

    if(not DRYER_ISVIBRATING):
        DRYER_VIBRATION_STARTTIME = datetime.datetime.now()
    DRYER_LAST_VIBRATION_TIME = datetime.datetime.now()
    DRYER_ISVIBRATING = True

def MonitorTheDryer():
    "This function monitors the dryer."
    global DRYER_ISVIBRATING
    global DRYER_LAST_VIBRATION_TIME
    global DRYER_VIBRATION_STARTTIME
    global DRYER_STOP_TIME_THRESHOLD_SEC
    global DRYER_MIN_RUNTIME_THRESHOLD_SEC
    
    current_time = datetime.datetime.now()
    howLongSinceIStopped = (current_time - DRYER_LAST_VIBRATION_TIME).total_seconds()
    howLongWasIRunning = (DRYER_LAST_VIBRATION_TIME - DRYER_VIBRATION_STARTTIME).total_seconds()
    if(DRYER_ISVIBRATING and howLongSinceIStopped > DRYER_STOP_TIME_THRESHOLD_SEC): #has it stopped vibrating for threshold. 
        DRYER_ISVIBRATING = False
        if(howLongWasIRunning > DRYER_MIN_RUNTIME_THRESHOLD_SEC):
            SendNofitication("Dryer is Done!!!")
    return

def MonitorTheWashingMachine():
    "This function monitors the washing machine."
    #print("Monitor the Washing Machine")
    global LIGHTFIRSTNOTICED
    global PREVIOUSLIGHTSTATE

    currentLightState = IsWasherDone()
    if(PREVIOUSLIGHTSTATE == False and currentLightState):
        SendNofitication("Washer is Done!!!")
        LIGHTFIRSTNOTICED = datetime.datetime.now
    PREVIOUSLIGHTSTATE = currentLightState
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

    global LIGHTSENSORTHRESHOLD
    currentLightState = False
    if(ch0 > LIGHTSENSORTHRESHOLD):
        currentLightState = True
    return currentLightState;

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
        conn.close()
    return;
        

# excution
Main()
