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
#!/usr/bin/env python3

import time
import os
import netifaces
import RPi.GPIO as GPIO
from rpi_lcd import LCD
import psutil
import shutil
import platform
import subprocess

# GPIO Pins
BTN_MENU = 23   # Change menu option
MENU_BTN_EN = True
LONG_THRESHOLD_MENU = 0.2  # seconds
BTN_ACTION = 24 # Perform selected action
ACTION_BTN_EN = True
LONG_THRESHOLD = 1  # seconds
press_time = None
# Menu options
MENU_OPTIONS = ["Show IP", "Shutdown", "Reboot","Status"]
break_status = False

# Setup
lcd = LCD()
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(BTN_MENU, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_ACTION, GPIO.IN, pull_up_down=GPIO.PUD_UP)

current_option = 0


def get_ip_address():
    """Get the first non-loopback IPv4 address."""
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
    """Display current menu option."""
    lcd.clear()
    lcd.text("Option:", 1)
    lcd.text(MENU_OPTIONS[current_option], 2)


def perform_action():
    global break_status
    #Perform the action based on current menu option.
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
    elif MENU_OPTIONS[current_option] == "Status" and not break_status:
        break_status = True
        while break_status:    # Use break_status to control the loop
            cpu_usage, memory_usage = get_metrics()
            lcd.text("CPU: " + cpu_usage, 1)
            lcd.text("Mem: " + memory_usage, 2)
            if GPIO.input(BTN_ACTION) == GPIO.LOW:  # Check if the action button is pressed
                break_status = False
                display_menu()
            #time.sleep(1)
    elif MENU_OPTIONS[current_option] == "Status" and break_status:
        display_menu()
        break_status = False
def bytes2human(n):
    # Convert bytes to human-readable
    symbols = ('B','KB','MB','GB','TB','PB')
    i = 0
    while n >= 1024 and i < len(symbols)-1:
        n /= 1024.0
        i += 1
    return f"{n:.1f}{symbols[i]}"

def get_cpu_usage():
    # Measured over 1 second
    return psutil.cpu_percent(interval=1)  # percent
    # psutil docs recommend interval>0 for a measured reading[2]

def get_cpu_core_temps():
    # Try psutil sensors (Linux/FreeBSD commonly)
    temps = []
    if hasattr(psutil, "sensors_temperatures"):
        data = psutil.sensors_temperatures(fahrenheit=False) or {}
        # Common keys include 'coretemp', 'cpu_thermal', 'acpitz' etc.[2][1][3][14]
        for chip, entries in data.items():
            for ent in entries:
                # ent.current is the temperature in °C[2][1][3][14]
                temps.append((chip, ent.label or chip, ent.current))
    return temps
def get_memory_usage():
    vm = psutil.virtual_memory()
    # vm.percent is RAM usage percentage; vm.available is free-like bytes[2][3]
    return {
        "percent_used": vm.percent,
        "available_bytes": vm.available,
        "available_human": bytes2human(vm.available),
        "total_bytes": vm.total,
        "total_human": bytes2human(vm.total)
    }
def get_metrics():
    metrics = {
        "cpu_usage": str(get_cpu_usage()) + "%",
        "cpu_core_temps": str(int(get_cpu_core_temps()[0][2])) + "C",
        "memory_usage": str(int(get_memory_usage()["percent_used"])) + "%",
        "memory_available": str(get_memory_usage()["available_human"]),
    }
    return metrics["cpu_usage"]+" "+metrics["cpu_core_temps"], metrics["memory_usage"]+" "+metrics["memory_available"]

def menu_button_callback(channel):
    global press_time
    global current_option
    global MENU_BTN_EN
    global ACTION_BTN_EN
    print("mbp")
    if MENU_BTN_EN:
        if GPIO.input(BTN_MENU) == GPIO.LOW:
            ACTION_BTN_EN = False
            press_time = time.monotonic()
        else:
            duration = time.monotonic() - press_time
            if duration >= LONG_THRESHOLD_MENU:
                current_option = (current_option + 1) % len(MENU_OPTIONS)
                display_menu()
            press_time = None
            ACTION_BTN_EN = True


def action_button_callback(channel):
    global press_time
    global current_option
    global MENU_BTN_EN
    global ACTION_BTN_EN
    # Button pressed when input goes LOW with pull-up wiring
    print("abp")
    if ACTION_BTN_EN:
        MENU_BTN_EN = False
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
                    lcd.text("Action not done", 1)
                    lcd.text("Press longer", 2)
                    time.sleep(1)
                    display_menu()
            press_time = None
            MENU_BTN_EN = True


def main():
    display_menu()
    GPIO.add_event_detect(BTN_MENU, GPIO.BOTH, callback=menu_button_callback, bouncetime=300)
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


