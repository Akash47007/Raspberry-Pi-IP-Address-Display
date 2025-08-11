#!/usr/bin/env python3
'''
1. This code is designed to display the IP address of a Raspberry Pi on an LCD using the rpi_lcd library and provide functionaloity like shutdown and reboot.
2. configure your LCD according to your setup.
3. This code is tested for a 16x2 LCD and a Raspberry Pi 4 Model B with two pushbuttons.
4. The display ip option will works on a single press whereas the shutdown and reboot options will work on a long press.
5. The duration of the long press is configurable by changing the LONG_THRESHOLD variable.
6. the buttons are connected to GPIO pins 23 and 24.

by Akash K
'''
import time
import os
import netifaces
import RPi.GPIO as GPIO
from rpi_lcd import LCD

# GPIO Pins
BTN_MENU = 23   # Change menu option
BTN_ACTION = 24 # Perform selected action
LONG_THRESHOLD = 0.5  # Change this for long press duration in seconds
press_time = None
# Menu options
MENU_OPTIONS = ["Show IP", "Shutdown", "Reboot"]

# Setup
lcd = LCD()
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(BTN_MENU, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_ACTION, GPIO.IN, pull_up_down=GPIO.PUD_UP)

current_option = 0


def get_ip_address():
    #Get the first non-loopback IPv4 address.
    for iface in netifaces.interfaces():
        if iface == "lo":
            continue
        try:
            addrs = netifaces.ifaddresses(iface)
            ipv4_info = addrs.get(netifaces.AF_INET)
            if ipv4_info:
                return ipv4_info[0]["addr"]
        except Exception:
            pass
    return None


def display_menu():
    lcd.clear()
    lcd.text("Option:", 1)
    lcd.text(MENU_OPTIONS[current_option], 2)


def perform_action():
    lcd.clear()
    if MENU_OPTIONS[current_option] == "Show IP":
        ip = get_ip_address()
        if ip:
            lcd.text("IP Address:", 1)
            lcd.text(ip, 2)
        else:
            lcd.text("IP not found", 1)
    elif MENU_OPTIONS[current_option] == "Shutdown":
        lcd.text("Shutting down...", 1)
        time.sleep(2)
        os.system("sudo shutdown now")
    elif MENU_OPTIONS[current_option] == "Reboot":
        lcd.text("Rebooting...", 1)
        time.sleep(2)
        os.system("sudo reboot")


def menu_button_callback(channel):
    global current_option
    current_option = (current_option + 1) % len(MENU_OPTIONS)
    display_menu()


def action_button_callback(channel):
    global press_time
    global current_option
    if GPIO.input(BTN_ACTION) == GPIO.LOW:
        if current_option == 0:
            perform_action()
        else:
            press_time = time.monotonic()
    else:
        if press_time is not None:
            duration = time.monotonic() - press_time
            press_time = None
            if duration >= LONG_THRESHOLD:
                perform_action()
            else:
                lcd.clear()
                lcd.text("Short press", 1)
                lcd.text("ignored", 2)
                time.sleep(1)
                display_menu()


def main():
    display_menu()
    GPIO.add_event_detect(BTN_MENU, GPIO.FALLING, callback=menu_button_callback, bouncetime=300)
    GPIO.add_event_detect(BTN_ACTION, GPIO.BOTH, callback=action_button_callback, bouncetime=300)

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
