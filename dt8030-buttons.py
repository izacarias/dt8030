###
 # Copyright 2017, Google, Inc.
 # Licensed under the Apache License, Version 2.0 (the `License`);
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at
 # 
 #    http://www.apache.org/licenses/LICENSE-2.0
 # 
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an `AS IS` BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.
### 

#!/usr/bin/python

from sense_hat import SenseHat
import datetime
import time
import jwt
import paho.mqtt.client as mqtt


########################################################################
# Define project-based variables. 
# You need to edit this block of variables to run your script
#    Description:
#    
#  - ssl_private_key_filepath:
#      The path to the 
#  - ssl_algorithm = 'RS256' # Either RS256 or ES256
#  - root_cert_filepath = '/home/pi/roots.pem'
#  - project_id = 'dt8030-iulzac'
#  - gcp_location = 'europe-west1'
#  - registry_id = 'raspberry-pi'
#  - device_id = 'resp1'

ssl_private_key_filepath = '/home/pi/demo_private.pem'
ssl_algorithm = 'RS256' # Either RS256 or ES256
root_cert_filepath = '/home/pi/roots.pem'
project_id = 'dt8030-iulzac'
gcp_location = 'europe-west1'
registry_id = 'raspberry-pi'
device_id = 'resp1'
########################################################################

########################################################################
# This code is used to create a connection to the Google Cloud

# Get the current time (UTC)
cur_time = datetime.datetime.utcnow()

# Create the authentication token
def create_jwt():
  token = {
      'iat': cur_time,
      'exp': cur_time + datetime.timedelta(minutes=60),
      'aud': project_id
  }
  # Read the private certificate file
  with open(ssl_private_key_filepath, 'r') as f:
    private_key = f.read()
  # Encrypt the data for authentication
  return jwt.encode(token, private_key, ssl_algorithm)

# These variables are used to store the location of the corresponding
# device and topic (URL)
_CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(project_id, gcp_location, registry_id, device_id)
_MQTT_TOPIC = '/devices/{}/events'.format(device_id)

## Create a MQTT Client to connect to the cloud
client = mqtt.Client(client_id=_CLIENT_ID)
## Set the authentication details
client.username_pw_set(
    username='unused',
    password=create_jwt())

## These functions are used by the MQTT Client to show messages
## - On error
## - When connecting to the cloud
## - When sending data to the cloud
def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_connect(unusued_client, unused_userdata, unused_flags, rc):
    print('on_connect', error_str(rc))

def on_publish(unused_client, unused_userdata, unused_mid):
    print('on_publish')

client.on_connect = on_connect
client.on_publish = on_publish
client.tls_set(ca_certs=root_cert_filepath)
client.connect('mqtt.googleapis.com', 8883)
client.loop_start()

## Create an object to interact with the SenseHat
sense = SenseHat()

## Repeat this code until user press CTRL+C
while True:
  try:
    btn_pressed = ""
    for event in sense.stick.get_events():
      ## Check if the joystick was pressed
      if event.action == "pressed":
        if event.direction == "up":
          btn_pressed = "u"
        elif event.direction == "down":
          btn_pressed = "d"
        elif event.direction == "left":
          btn_pressed = "l"
        elif event.direction == "right":
          btn_pressed = "r"
        elif event.direction == "middle":
          btn_pressed = "m"
          
        ## create the message (JSON format)
        payload = '{{ "ts": {}, "button": {} }}'.format(int(time.time()), btn_pressed)
        ## send the data to the Cloud
        client.publish(_MQTT_TOPIC, payload, qos=1)
        
        ## Print the event (just for debugging)
        print("{}\n".format(payload))
        
        time.sleep(1)
        sense.clear()
        
  except KeyboardInterrupt:
    ## Stop the Googgle Cloud Client when CTRL+C was pressed
    client.loop_stop()
