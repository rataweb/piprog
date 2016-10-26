import RPi.GPIO as GPIO
import subprocess
import sys
import os
import time

### Settings ###

# Path to binary eeprom.epp file to write to eeprom.
# Use the eepmake command from https://github.com/raspberrypi/hats/eepromutils to create this file
# based on the information from eeprom_settings.txt
EEPROM_FILE = "/path/to/eeprom.eep"

# Type of EEPROM. Supported types are "24c32", "24c64", "24c128", "24c512", "24c1024".
EEPROM_TYPE = "24c32"





### main code ##

PIN_LED_GREEN = 33
PIN_LED_RED = 35
PIN_BUTTON = 37

I2C_DEV_PATH = "/sys/class/i2c-adapter/i2c-3"
I2C_DEV_NAME = "3-0050"
I2C_USE_BITBANG = True

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(PIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_LED_GREEN, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(PIN_LED_RED, GPIO.OUT, initial=GPIO.LOW)


def main():
    print("eeprom writer running - press button to write eeprom!")
    setup_i2c()
    while True:
        GPIO.output(PIN_LED_GREEN, GPIO.HIGH)
        if GPIO.input(PIN_BUTTON) == GPIO.LOW:
            print("writing eeprom... ")
            GPIO.output(PIN_LED_GREEN, GPIO.LOW)
            write_eeprom()
            print("   DONE!")
    GPIO.cleanup()


def setup_i2c():
    if not subprocess.call(["modprobe", "i2c_dev"]) == 0:
        print("error loading i2c_dev kernel module")
        exit(1)
    if I2C_USE_BITBANG:
        if not subprocess.call(["dtoverlay", "i2c-gpio","i2c_gpio_sda=2","i2c_gpio_scl=3"]) == 0:
            print("error loading i2c-gpio dtoverlay. If the dtoverlay command is not found, please update to latest raspian")
            exit(1)
    if not subprocess.call(["modprobe","at24"]) == 0:
        print("error loading at24 kernel module")
        exit(1)
    if not os.path.exists(I2C_DEV_PATH+"/"+I2C_DEV_NAME):
        new_device = open(I2C_DEV_PATH+"/new_device", "w")
        new_device.write(EEPROM_TYPE+" 0x50\n")
        new_device.close()
    if not os.path.exists(I2C_DEV_PATH+"/"+I2C_DEV_NAME+"/eeprom"):
        print("eeprom does not exist on i2c device " + I2C_DEV_PATH+"/"+I2C_DEV_NAME)
        exit(1)


def blink_led(pin, times=1, delay=0.5):
    for i in range(times):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(delay)


def write_eeprom():
    GPIO.output(PIN_LED_RED, GPIO.HIGH)

    if not os.path.exists(EEPROM_FILE):
        print("eeprom file "+EEPROM_FILE+" does not exist!")
        blink_led(PIN_LED_RED, 3, 0.6)
    else:
        FNULL = open(os.devnull, 'w')
        result = subprocess.call(["dd", "if="+EEPROM_FILE, "of="+I2C_DEV_PATH+"/"+I2C_DEV_NAME+"/eeprom"], stdout=FNULL, stderr=subprocess.STDOUT)

        GPIO.output(PIN_LED_GREEN, GPIO.LOW)
        GPIO.output(PIN_LED_RED, GPIO.LOW)

        if result == 0:
            print("eeprom write successful")
            blink_led(PIN_LED_GREEN, 3, 0.2)
        else:
            print("error writing eeprom")
            blink_led(PIN_LED_RED, 3, 0.5)



if __name__ == '__main__':
    sys.exit(main())
