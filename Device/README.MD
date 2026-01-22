# Bluetooth Server:
We will run the server through bluetooth, computer connects to microcontroller through bluetooth and microcontroller turns the servos through its pins.

# Technology explanation:
Helping explanation Video: 
https://youtu.be/0Q_4q1zU6Zc

To summerize concepts to our project:
## Terms:
    Classic bluetooth: 
        Inneficient battery wise.
        Meant to send a lot of data continously like for video/audio streams.
        Low latency for fast applications.
    Bluetooth Low Energy(BLE):
        Low power requirements.
        Short data burst, send info once in a while.
        Our chip only supports BLE natively so we don't need another module.
    
    We will use BLE for our server.

    Peripheral - Device that advertizes itself(Server).
    Central - Device that scans Peripheral and connects to them(Client).
    

### Protocol: 
## Genetic Access Profile(GAP):
- Controls advertising and connections.
- Controls Security.
- And is in charge of "Network Topology".

Topology is kind of connection type.

Connection Orianted: Central and Peripheral connect and can exchange data both ways. e.g: Servo server sends their rotation and can get command to rotate them.

Connectionless: One device acts as a broadcast and puts data to any device around. e.g: Sensor server sends device rotation but doesn't have any commands.

## Generic ATTribute Profile (GATT):
- Controls data transfer itself.
- Has one or more Services(clarified later).

### Service(Group of data):
A collection of "Characteristics." Each service has its own UUID.

### Characteristics(Piece of data).
- Value: The actual information we want to send. Number/String/Bytes.
- Properties:
    - Handle: 16bit used to access the Characteristic.
    - The Characteristic's UUID.
    - Permissions: What can other devices do with this data, Read/Write/Notify
- Descriptor: Additional information for the Characteristic such as what is it and what's it used for.

Example for GATT profile:

Robot with two services, one for sound one for moving.

Sound Service has 2 Characteristic
- noise Characteristic that can be written with a number 1-5 that plays a musical note.
- Voice Characteristic read only that gives what words it manages to understand around it.

Moving service has 5 Characteristic one for each movement and one for rotation if the robot is flipped.

## Peripheral device(Server)'s job:
    - Peripheral device needs to be able to broadcasts(Advertises) to show other devices it can be connected to -and shows its services.
    - Needs to define a Service with at least one Characteristic.
    - Needs to define for its' Characteristics how the client uses them.(Read/Write/Notify)
        
# Our project's Server:
pass