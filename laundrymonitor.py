#import what we need
import datetime
import importlib

#constants
SecondsBetweenChecks = 60
PUSHOVERAPITOKEN = ""
PUSHOVERUSERKEY = ""

#globals
previousLightState = True
lightFirstNoticed = datetime.MINYEAR


def Main():
    "This is the main execution of the Laundry Monitor. Its an infinite loop."
    #TODO import pushover credentials from outside file. 
    try:
        importlib.import_module("pushovercredentials")
    except:
        poCredsFile= open("pushovercredentials.py","w+")
        poCredsFile.write("global PUSHOVERAPITOKEN\r\n")
        poCredsFile.write("global PUSHOVERUSERKEY\r\n")
        poCredsFile.write("PUSHOVERAPITOKEN = \"\"\r\n")
        poCredsFile.write("PUSHOVERUSERKEY = \"\"\r\n")
        poCredsFile.close()
        print("Pushover credentials file didn't exist, please fill in.")
        return;
    
    #Our credentials file might exits, but it might not be populated. 
    if(len(PUSHOVERAPITOKEN) == 0 or len(PUSHOVERUSERKEY) == 0):
        print("Pushover credentials are empty")
        return

    while(1):
        MonitorTheWashingMachine()
        MonitorTheDryer()
        time.sleep(SecondsBetweenChecks)
    return;


def MonitorTheWashingMachine():
    "This function monitors the washing machine."
    if(previousLightState == False and IsWasherDone()):
        SendNofitication("Washer is Done!!!")
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
    #TODO check the light
    currentLightState = True
    previousLightState = currentLightState
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
    return;
        

# excution
Main()
