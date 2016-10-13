MicroPython MQTT Sonoff Switch
==============================
This project uses MicroPython to implement a MQTT controllable relay switch
on the ITead Sonoff Switch.

Dependencies
------------
The following modules need to be imported as frozen and pre-compiled modules:
 * The MicroPython MQTT client libraries from the MicroPythin Library repository https://github.com/micropython/micropython-lib
  * umqtt.simple
  * umqtt.robust
 * Following modules from the excellent micro-threadding library from https://github.com/peterhinch/Micropython-scheduler
  * usched
  * pushbutton
  * delay
