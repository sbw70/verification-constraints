import time
from machine import Pin

p = Pin(4, Pin.IN)
rise = None
start = None
last = None
count = 0
mn = None
mx = None

def edge(pin):
    global rise,start,last,count,mn,mx
    us = time.ticks_us()
    ms = time.ticks_ms()

    if pin.value():
        rise = us
        return

    if rise is None:
        return

    w = time.ticks_diff(us, rise)
    rise = None

    if w < 300 or w > 3000:
        return

    if count == 0:
        start = ms
        print("005_WITNESS_BURST_START ticks_ms={}".format(ms))

    count += 1
    last = ms
    mn = w if mn is None or w < mn else mn
    mx = w if mx is None or w > mx else mx

p.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=edge)

print("005_WITNESS_READY GPIO4 SERVO2_COM15")

hb = time.ticks_ms()

while True:
    now = time.ticks_ms()

    if count and last is not None and time.ticks_diff(now,last) > 150:
        print("005_WITNESS_BURST_END pulses={} duration_ms={} pulse_min_us={} pulse_max_us={}".format(
            count, time.ticks_diff(last,start), mn, mx))
        start = None
        last = None
        count = 0
        mn = None
        mx = None

    if time.ticks_diff(now,hb) >= 5000:
        print("005_WITNESS_HEARTBEAT state={}".format("ACTIVE" if count else "IDLE"))
        hb = now

    time.sleep_ms(10)
