import ubinascii
import ujson
import utime
import machine
import network

from umqtt.robust import MQTTClient
from usched import Sched

import config

_PIN_PUSHBUTTON = const(0)
_PIN_RELAY = const(12)
_PIN_LED = const(13)

_DELAY_MS = 20
_CLIENT_ID = None
_ACTUATOR_TOPIC = None

led = machine.Pin(_PIN_LED, machine.Pin.OUT)
relay = machine.Pin(_PIN_RELAY, machine.Pin.OUT)
button = machine.Pin(_PIN_PUSHBUTTON, machine.Pin.IN)

demanded_relay_state = None

def handle_subscription(topic, payload):
    global demanded_relay_state
    try:
        payload = ujson.loads(payload.decode('utf-8'))
    except ValueError:
        payload = {}
    if 'state' in payload.keys():
        demanded_relay_state = not payload['state']

def poll_mqtt():
    yield
    while True:
        client.check_msg()
        yield

def loose_some_time(delay):
    yield
    while True:
        utime.sleep_ms(delay)
        yield

def relay_control(relay):
    global demanded_relay_state
    yield
    while True:
        if relay.value() != demanded_relay_state:
            relay.value(demanded_relay_state)
            yield 1.5
        else:
            yield

def led_copies_relay_state(led, relay):
    yield
    while True:
        if relay.value() != led.value():
            led.value(relay.value())
        yield 0.1

print('Connecting to WLAN...')
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
cstart_ms = utime.ticks_ms()
if not wlan.isconnected():
    wlan.connect(config.WLAN_SSID, config.WLAN_PSK)
    while not wlan.isconnected():
        utime.sleep_ms(100)
        if utime.ticks_diff(cstart_ms, utime.ticks_ms()) > 10000:
            print('Connecting to WLAN timed out. Resetting!')
            machine.reset()

print('Connecting to MQTT broker')
mac_address = ubinascii.hexlify(wlan.config('mac')).decode('utf-8')
client = MQTTClient(config.CLIENT_ID_PREFIX + mac_address, config.BROKER)
client.set_callback(handle_subscription)
client.set_last_will(config.LOG_TOPIC_PREFIX, config.LAST_WILL)
try:
    client.connect()
except KeyboardInterrupt:
    raise
except Exception:
    print('Failed to connect to MQTT broker. Resetting!')
    machine.reset()
_ACTUATOR_TOPIC = config.ACTUATOR_BASE_TOPIC + mac_address
try:
    client.subscribe(_ACTUATOR_TOPIC)
except KeyboardInterrupt:
    raise
except Exception:
    print('Failed to subscribe to actuator topic. Resetting!')
    machine.reset()

print("Initializing Scheduler...")
scheduler = Sched()
scheduler.add_thread(poll_mqtt())
scheduler.add_thread(loose_some_time(_DELAY_MS))
scheduler.add_thread(relay_control(relay))
if config.LED_DISPLAY_RELAY_STATE:
    scheduler.add_thread(led_copies_relay_state(led, relay))
print("Starting Scheduler...")
scheduler.run()

print("Disconnecting from MQTT-Broker")
client.disconnect()
