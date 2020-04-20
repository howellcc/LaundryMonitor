import datetime, time
import RPi.GPIO as GPIO

#GLOBALS
ISVIBRATING = False
LAST_VIBRATION_TIME = datetime.datetime.now()
START_VIBRATION_TIME = datetime.datetime.now()
SENSOR_PIN = 14



def VibrationCallback(x):
    global ISVIBRATING
    global LAST_VIBRATION_TIME
    global START_VIBRATION_TIME
    
    LAST_VIBRATION_TIME = datetime.datetime.now()
    if not ISVIBRATING:
        START_VIBRATION_TIME = LAST_VIBRATION_TIME
        ISVIBRATING = True

def MonitorTheDryer():
    "This function monitors the dryer."

    current_time = time.time()
    global ISVIBRATING
    global LAST_VIBRATION_TIME
    global START_VIBRATION_TIME
    
    ISVIBRATING = current_time - LAST_VIBRATION_TIME < 2


    #global ISVIBRATING
    #if(ISVIBRATING):
        #figure out if we should actually send a notification
        #Have we already notified
        #Do we need to notify again
        #Are we outside of quiet hours?
        #SendNofitication("The Dryer is Done!!!")
        #print("its vibrating")
    return

def Main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(SENSOR_PIN, GPIO.RISING)
    GPIO.add_event_callback(SENSOR_PIN, VibrationCallback(x))

    #Time to get down to business
    while(1):
        MonitorTheDryer()
        time.sleep(10)
    return;
    

Main()
