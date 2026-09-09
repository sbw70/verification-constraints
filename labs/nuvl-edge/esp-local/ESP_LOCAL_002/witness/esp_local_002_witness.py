import time
from machine import Pin

WITNESS_PIN = 5

rise_us = None
burst_start_ms = None
last_pulse_ms = None
pulse_count = 0
pulse_min_us = None
pulse_max_us = None

def edge(pin):
    global rise_us
    global burst_start_ms
    global last_pulse_ms
    global pulse_count
    global pulse_min_us
    global pulse_max_us

    now_us = time.ticks_us()
    now_ms = time.ticks_ms()

    if pin.value():
        rise_us = now_us
        return

    if rise_us is None:
        return

    width_us = time.ticks_diff(now_us, rise_us)
    rise_us = None

    if width_us < 300 or width_us > 3000:
        return

    if pulse_count == 0:
        burst_start_ms = now_ms
        print(
            "ESP_LOCAL_001_WITNESS_BURST_START ticks_ms={}".format(
                burst_start_ms
            )
        )

    pulse_count += 1
    last_pulse_ms = now_ms

    if pulse_min_us is None or width_us < pulse_min_us:
        pulse_min_us = width_us

    if pulse_max_us is None or width_us > pulse_max_us:
        pulse_max_us = width_us


pin = Pin(WITNESS_PIN, Pin.IN)
pin.irq(
    trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
    handler=edge,
)

print(
    "ESP_LOCAL_001_WITNESS_READY pin=GPIO{} expected_hz=50".format(
        WITNESS_PIN
    )
)

last_heartbeat = time.ticks_ms()

while True:
    now = time.ticks_ms()

    if (
        pulse_count > 0
        and last_pulse_ms is not None
        and time.ticks_diff(now, last_pulse_ms) > 150
    ):
        duration_ms = time.ticks_diff(
            last_pulse_ms,
            burst_start_ms,
        )

        print(
            "ESP_LOCAL_001_WITNESS_BURST_END "
            "pulses={} duration_ms={} "
            "pulse_min_us={} pulse_max_us={}".format(
                pulse_count,
                duration_ms,
                pulse_min_us,
                pulse_max_us,
            )
        )

        burst_start_ms = None
        last_pulse_ms = None
        pulse_count = 0
        pulse_min_us = None
        pulse_max_us = None

    if time.ticks_diff(now, last_heartbeat) >= 5000:
        print(
            "ESP_LOCAL_001_WITNESS_HEARTBEAT "
            "ticks_ms={} state={}".format(
                now,
                "ACTIVE" if pulse_count else "IDLE",
            )
        )
        last_heartbeat = now

    time.sleep_ms(10)

