import machine

pin = machine.Pin(0, machine.Pin.IN)
if pin.value():
    print('Starting Sonoff Switch Work Scheduler...')
    import sonoff_switch
else:
    print('Button held down during boot. Entering REPL...')
