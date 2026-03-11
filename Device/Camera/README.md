# Camera

---

## WebServer
Example code for a camera web server was given for the esp32-cam we're using, and as it isn't a big focus.
I decided to use the example code without looking into understanding how it works too much so I'll note the important parts down below:

### The camera stream is in **ip:81/stream**, an example to read from it using python is given.

### Camera configuration is in port **ip:80**, many settings for the camera, which change the output for the stream.
If the quality of the camera is bad you can try to mess with the settings to see if it will help.
I believe that when restarting the camera it resets the settings so if you find a good set try to request them all on root/first connection.

### *WI-FI CREDENTIALS*
Since we're using tcp/http we need to be in a shared network with the client.
For that we join via Wi-Fi the network, the details to join are in wifi_credentials.h.
Take the wifi_credentials.h.example rename remove the .example and replace the *** to your network's settings.

---

## Camera client:
For now an example code later will have simplified class/functions to interact with the camera easily.

Details on the simplified code will be here later.
