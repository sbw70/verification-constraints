from machine import Pin, time_pulse_us
import time

SIGNAL_PIN = 5
TIMEOUT_US = 30000
BURST_END_MS = 150
HEARTBEAT_MS = 5000

pin = Pin(SIGNAL_PIN, Pin.IN, Pin.PULL_DOWN)

print("FLEET015_WITNESS_READY pin=GPIO5")
print("mode=servo_pwm_observer expected_hz=50")

in_burst = False
pulse_count = 0
burst_start = 0
last_pulse = 0
width_min = None
width_max = None
last_heartbeat = time.ticks_ms()

while True:
    now = time.ticks_ms()
    width = time_pulse_us(pin, 1, TIMEOUT_US)

    if width > 0:
        now = time.ticks_ms()

        if not in_burst:
            in_burst = True
            pulse_count = 0
            burst_start = now
            width_min = width
            width_max = width
            print("WITNESS_BURST_START ticks_ms={}".format(now))

        pulse_count += 1
        last_pulse = now

        if width < width_min:
            width_min = width
        if width > width_max:
            width_max = width

    elif in_burst and time.ticks_diff(now, last_pulse) >= BURST_END_MS:
        duration = time.ticks_diff(last_pulse, burst_start)
        print(
            "WITNESS_BURST_END ticks_ms={} pulses={} duration_ms={} pulse_min_us={} pulse_max_us={}".format(
                now, pulse_count, duration, width_min, width_max
            )
        )
        in_burst = False

    if time.ticks_diff(now, last_heartbeat) >= HEARTBEAT_MS:
        print("WITNESS_HEARTBEAT ticks_ms={} state={}".format(
            now, "ACTIVE" if in_burst else "IDLE"
        ))
        last_heartbeat = now
