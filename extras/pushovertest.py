import requests, http.client, urllib, os, inspect, time, datetime, json

#GLOBALS
PUSHOVERAPITOKEN = ""
PUSHOVERUSERKEY = ""


def Main():
    global PUSHOVERAPITOKEN
    global PUSHOVERUSERKEY

    #settingsFile = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "../laundrymonitorconfig.json"
    settingsFile = os.path.abspath("../laundrymonitorconfig.json")
    #import pushover credentials from outside file.
    try:
        #read json file and load credentials
        with open(settingsFile) as f:
            d = json.load(f)
            PUSHOVERUSERKEY = d["PUSHOVERUSERKEY"]
            PUSHOVERAPITOKEN = d["PUSHOVERAPITOKEN"]
    except:
        #load failed, likely because the file didn't exist. Create it so it can be filled.
        print("Pushover credentials file didn't exist, please fill in.")
        return

    #Our credentials file might exits, but it might not be populated.
    if(len(PUSHOVERAPITOKEN) == 0 or len(PUSHOVERUSERKEY) == 0):
        print("Pushover credentials are empty")
        return

#    conn = http.client.HTTPSConnection("api.pushover.net:443")
#    conn.request("POST", "/1/messages.json",
#        urllib.parse.urlencode({
#            "token": PUSHOVERAPITOKEN,
#            "user": PUSHOVERUSERKEY,
#            "message": "hello world"},
#            files = {
#                "attachment": ("image.jpg", open("washingicon.jpg", "rb"), "image/jpeg")
#            })) #, { "Content-type": "application/x-www-form-urlencoded" })
#    conn.getresponse()
#    conn.close()

    r = requests.post("https://api.pushover.net/1/messages.json", data = {
        "token": PUSHOVERAPITOKEN,
        "user": PUSHOVERUSERKEY,
        "message": "hello world"
        }) #,
        #files = {
        #    "attachment": ("image.jpg", open("washingicon.jpg", "rb"), "image/jpeg")
        #})
    print(r.text)
    return

Main()


