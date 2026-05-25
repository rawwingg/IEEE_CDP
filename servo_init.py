import lgpio
import time


#isolated servo adjustment code
s1 = 18
PWM_FREQ = 50

h1 = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h1, s1)  # <-- this is the key line

def set_servo_angle(angle, SERVO_GPIO, h):
    angle    = max(0, min(180, angle))
    pulse_us = int(500 + (angle / 180.0) * 2000)
    lgpio.tx_servo(h, SERVO_GPIO, pulse_us, PWM_FREQ)
    print(f"Servo: {angle} deg (pulse: {pulse_us}us)")

set_servo_angle(0, s1, h1)
time.sleep(1)

set_servo_angle(0, s2, h2)
time.sleep(1)

set_servo_angle(90, s1, h1)
time.sleep(1)

set_servo_angle(90, s2, h2)
time.sleep(1)

lgpio.gpiochip_close(h1)
lgpio.gpiochip_close(h2)