'''
1. This is the minimal code to display the IP address of a raspberry pi on an LCD using the rpi_lcd library.
2. configure your according to your setup.
3. This code is tested for a 16x2 LCD and a Raspberry Pi 4 Model B.

by Akash K
'''


from time import sleep
import netifaces
from rpi_lcd import LCD

# configure refresh rate
refresh_rate = 5  # seconds

# Initialize LCD
lcd = LCD()

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

def main():
    while True:
        lcd.clear()
        ip = get_ip_address()
        if ip:
            lcd.text("IP Address:", 1)
            lcd.text(ip, 2)
        else:
            lcd.text("IP not found", 1)
        sleep(refresh_rate)

if __name__ == "__main__":
    main()  