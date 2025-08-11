# Raspberry-Pi-IP-Address-Display
This project focusses on displaying the IP address and providing basic functionality through a LCD display.

# Full version:
This version provides functionality like **shutdown** and **reboot** along with the IP display functionality. It uses two pushbuttons in addition to perform tis action, one is change option button connected to gpio 23 by default and the other is the action button, connected to gpio 24 by default. The gpio pins corresponding to these buttons can be changes in the code.

# Minimal version:
This version provides a periodically updating ip address display on a LCD usin i2c interface.

# Setup Process 
**Make sure the required libraries mensioned are installed before proceeding**
1. copy the chosen python file to ***/usr/local/bin*** and save it as displayip.py
2. copy the service file to ***/etc/systemd/system*** and save it as displayip.service
3. run the following commands from the ***/usr/local/bin*** directory:
```bash
    sudo chmod +x displayip.py
    sudo systemctl daemon-reload
    sudo systemctl enable displayiplcd.service
    sudo systemctl start displayiplcd.service
```
# requirements
1. netinterfaces
2. rpi_lcd
3. rpi-lgpio - for full version only

# NOTE
The code might show errors if **rpi-gpio** library is used. Uninstall the **rpi-gpio** and install **rpi-lgpio** for the code to work(for full version only).

Make sure that the lcd is configured properly according to rpi_lcd library. Visit the library's repository for more info.

Both versions have the same service file and software setup process.

You can also create a virtual environment and update the service file accordingly if you know what you are doing. This by default uses a system wide interpreter.
