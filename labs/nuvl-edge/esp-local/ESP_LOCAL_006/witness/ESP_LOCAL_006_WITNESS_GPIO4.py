from machine import Pin, time_pulse_us
import time

PIN = 4
p = Pin(PIN, Pin.IN)

print("ESP_LOCAL_006_WITNESS_READY GPIO4")

while True:
    width = time_pulse_us(p, 1, 2000000)

    if width > 0:
        print("PWM_HIGH_US", width)

    time.sleep_ms(5)
