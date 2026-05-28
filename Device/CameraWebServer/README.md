# Camera

---

## WebServer

Example code for a camera web server was given for the esp32-cam we're using, and as it isn't a big focus.
I decided to use the example code without looking into understanding how it works too much so I'll note the important
parts down below:

### Configurations for the camera.

The base site(http://RubikCamera) has many configuration options.
If the quality of the video is bad or hard to analyze the picture, try to change the settings.
I've found that the first option of MegaHertz influences the upload speed, so if you put the camera speed too high the
quality will be better but the upload time will be worse.
The settings seem to reset when uploading code or pressing the restart button the esp-cam, so I recommend to write down
any settings changed to set them in following attempts.

### Getting images from the camera.

Adding /capture to the url returns a single live frame from the camera.
We used the requests library to get the image

```python
import requests
import numpy as np
import cv2
answer = requests.get("http://RubikCamera/Capture") # make an http get reqeust to the site 
if answer.status_code != 200: # if we didn't get an "Okay"
    raise requests.HTTPError
img_np = np.asarray(bytearray(answer.content), dtype=np.uint8) ## the content is in answer.content.
# we make it into a byte array then make it into a numpy array, I'm not completely sure why this works.
# but since it's not in focus I decided to go with it.
img = cv2.imdecode(img_np, -1) # then we transform the numpy array of the image into a cv2 image.
```

There is also a camera stream in :81/stream, which we can use with cv2 VideoStream directly, but I decided against it.
Mainly because I wasn't entirely sure how much control I get compared to getting a live capture. 
And the documentation is lacking.

### *WI-FI CREDENTIALS*

Since we're using tcp/http we need to be in a shared network with the client.
I've decided to join the local network, which can be a hotspot or another network.
The settings to the network options are in wifi_credentials.h, which I decided to add to git ignore to not show any
passwords in the repository.
There is an example in the repository, remove the .example from the name and put in the details of the network.
---