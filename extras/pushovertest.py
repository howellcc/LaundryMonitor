import http.client, urllib

apitoken = "pushover api token"
userkey = "pushover user key"

conn = http.client.HTTPSConnection("api.pushover.net:443")
conn.request("POST", "/1/messages.json",
  urllib.parse.urlencode({
    "token": apitoken,
    "user": userkey,
    "message": "hello world",
  }), { "Content-type": "application/x-www-form-urlencoded" })
conn.getresponse()
conn.close()


