import board
import busio
import digitalio
import neopixel
import displayio
import i2cdisplaybus
import adafruit_displayio_ssd1306
import adafruit_adxl34x
import terminalio
from rotary_encoder import RotaryEncoder

import config

def init_hardware():
    """Initializes all hardware components and returns them in a dictionary."""
 
    i2c = busio.I2C(board.SCL, board.SDA)

    accelerometer = adafruit_adxl34x.ADXL345(i2c)

    displayio.release_displays()
    display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
    display = adafruit_displayio_ssd1306.SSD1306(
        display_bus, 
        width=config.OLED_WIDTH, 
        height=config.OLED_HEIGHT
    )
    main_group = displayio.Group()
    display.root_group = main_group
    FONT = terminalio.FONT

    encoder = RotaryEncoder(
        board.D9, 
        board.D8, 
        debounce_ms=3, 
        pulses_per_detent=config.PULSES_PER_DETENT
    )

    button = digitalio.DigitalInOut(board.D7)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP

    pixels = neopixel.NeoPixel(
        board.D6, 
        config.NEOPIXEL_COUNT, 
        brightness=config.NEOPIXEL_BRIGHTNESS, 
        auto_write=True
    )
    
    return {
        "accelerometer": accelerometer,
        "display": display,
        "main_group": main_group,
        "FONT": FONT,
        "encoder": encoder,
        "button": button,
        "pixels": pixels,
    }
