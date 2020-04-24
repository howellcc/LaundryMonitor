import datetime, time
import RPi.GPIO as GPIO

#GLOBALS
ISVIBRATING = False
LAST_VIBRATION_TIME = datetime.datetime(9999,1,1,0,0,0)
VIBRATION_STOP_TIME_THRESHOLD_SEC = 30
DRYER_SENSOR_PIN = 14

def VibrationCallback(x):
    global ISVIBRATING
    global LAST_VIBRATION_TIME
    
    LAST_VIBRATION_TIME = datetime.datetime.now()
    ISVIBRATING = True

def MonitorTheDryer():
    "This function monitors the dryer."

    global ISVIBRATING
    global LAST_VIBRATION_TIME
    global VIBRATION_STOP_TIME_THRESHOLD_SEC
    
    current_time = datetime.datetime.now()
    timeDelta = current_time - LAST_VIBRATION_TIME
    if(timeDelta.total_seconds() > VIBRATION_STOP_TIME_THRESHOLD_SEC): #has it stopped vibrating for threshold. 
        ISVIBRATING = False

    if(ISVIBRATING):
        print("its vibrating")
    else:
        print("it stopped")
    return

def Main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DRYER_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(DRYER_SENSOR_PIN, GPIO.RISING)
    GPIO.add_event_callback(DRYER_SENSOR_PIN, VibrationCallback)

    #Time to get down to business
    while(1):
        MonitorTheDryer()
        time.sleep(10)
    return;
    

Main()
