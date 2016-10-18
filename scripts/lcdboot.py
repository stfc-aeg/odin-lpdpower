from usblcd import UsbLcd
import sys

lcd = UsbLcd("/dev/ttyACM0", 57600, rows=4, cols=20)
lcd.set_backlight_colour((0xFF, 0x30, 0x00))

lcd.clear()
lcd.write(sys.argv[1])
