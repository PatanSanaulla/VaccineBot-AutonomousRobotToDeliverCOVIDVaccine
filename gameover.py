import RPi.GPIO as gpio
import numpy as np
import time

def init():
    gpio.setmode(gpio.BOARD)
    gpio.setup(31, gpio.OUT)
    gpio.setup(33, gpio.OUT)
    gpio.setup(35, gpio.OUT)
    gpio.setup(37, gpio.OUT)
    
    gpio.setup(36, gpio.OUT)
    
    gpio.setup(12, gpio.IN, pull_up_down = gpio.PUD_UP)
    
def gameover():
    gpio.output(31, False)
    gpio.output(33, False)
    gpio.output(35, False)
    gpio.output(37, False)
    gpio.output(36, False)
    gpio.cleanup()
    
init()

gameover()