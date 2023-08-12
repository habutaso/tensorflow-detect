# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)

p1 = GPIO.PWM(17, 50)
p2 = GPIO.PWM(18, 50)


p1.start(0)
p2.start(0)

dr1 = [0, 10, 25, 50, 75, 50, 25, 10, 0, 0, 0, 0, 0, 0, 0, 0]
dr2 = [0, 0, 0, 0, 0, 0, 0, 0, 10, 25, 50, 75, 50, 25, 10, 0]

try:
    for i in range(8):
        p1.ChangeDutyCycle(dr1[i])
        p2.ChangeDutyCycle(dr2[i])
        GPIO.output(23, GPIO.HIGH)  # LED点灯
        sleep(2)
        GPIO.output(23, GPIO.LOW)
        sleep(2)

except KeyboardInterrupt:
    pass

p1.stop()
p2.stop()

GPIO.cleanup()
