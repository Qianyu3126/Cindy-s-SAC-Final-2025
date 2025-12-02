import time
import displayio
from adafruit_display_text import label
from rotary_encoder import RotaryEncoder 

import config

display = None
main_group = None
FONT = None
pixels = None
encoder = None
button = None
OLED_WIDTH = config.OLED_WIDTH
OLED_HEIGHT = config.OLED_HEIGHT

def setup_ui(hw):
    global display, main_group, FONT, pixels, encoder, button
    display = hw["display"]
    main_group = hw["main_group"]
    FONT = hw["FONT"]
    pixels = hw["pixels"]
    encoder = hw["encoder"]
    button = hw["button"]

def clear_group():
    """Removes all objects from the main display group."""
    while len(main_group) > 0:
        main_group.pop()

def display_refresh():
    """Forces the display to update."""
    display.refresh()

def text_width(text, scale=1):
    """Calculates the pixel width of a text string (based on terminalio.FONT)."""
    return len(text) * 6 * scale

def show_center_text(text, scale=1, top_left_tag=None):
    """Displays text centered on the screen, optionally with a tag in the top-left corner."""
    clear_group()
    if top_left_tag:
        lbl_tag = label.Label(FONT, text=top_left_tag, x=2, y=8)
        main_group.append(lbl_tag)

    w = text_width(text, scale)
    x = max(0, (OLED_WIDTH - w)//2)
    y = OLED_HEIGHT//2 - (6 * scale)

    lbl = label.Label(FONT, text=text, x=x, y=y, scale=scale)
    main_group.append(lbl)
    display_refresh()

def show_lines(lines):
    """Displays a list of text lines, vertically spaced."""
    clear_group()
    y = 8
    for ln in lines:
        lbl = label.Label(FONT, text=ln, x=4, y=y)
        main_group.append(lbl)
        y += 12
    display_refresh()

def show_command_with_header(command_text, difficulty_short, level):
    """Displays the game command with a level/difficulty header."""
    tag = f"{difficulty_short}_L{level}"
    show_center_text(command_text, scale=1, top_left_tag=tag)


def startup_pixels():
    """Six NeoPixels turn on one-by-one."""
    pixels.fill((0, 0, 0))
    for i in range(config.NEOPIXEL_COUNT):
        pixels[i] = config.PIXEL_COLORS[i]
        time.sleep(0.15)
    time.sleep(0.2)

def startup_loading_bar():
    clear_group()
    bar_width = 100
    bar_height = 10
    bar_x = (OLED_WIDTH - bar_width) // 2
    bar_y = (OLED_HEIGHT - bar_height) // 2

    bar_bitmap = displayio.Bitmap(bar_width, bar_height, 2)
    palette = displayio.Palette(2)
    palette[0] = 0x000000
    palette[1] = 0xFFFFFF

    bar_tile = displayio.TileGrid(bar_bitmap, pixel_shader=palette, x=bar_x, y=bar_y)
    main_group.append(bar_tile)

    display_refresh()

    for w in range(bar_width):
        for h in range(bar_height):
            bar_bitmap[w, h] = 1
        display_refresh()
        time.sleep(0.01)

    time.sleep(0.3)

# Onboarding
def select_difficulty(options):
    current_index = 1

    def refresh():
        clear_group()
        main_group.append(label.Label(FONT, text="Select Difficulty", x=8, y=6))

        spacing = 12
        x = 0
        total_w = sum(text_width(word, 2 if i == current_index else 1) for i, word in enumerate(options)) + spacing * (len(options) - 1)
        start_x = (OLED_WIDTH - total_w)//2
        x = start_x

        for i, word in enumerate(options):
            scale = 2 if i == current_index else 1
            lbl = label.Label(FONT, text=word, x=x, y=36, scale=scale)
            main_group.append(lbl)
            x += text_width(word, scale) + spacing
        
        display_refresh()

    refresh()
    pulse_buffer = 0

    while True:
        diff = encoder.update()
        if diff != 0:
            pulse_buffer += diff
            if abs(pulse_buffer) >= config.PULSES_PER_DETENT:
                detents = int(pulse_buffer / config.PULSES_PER_DETENT)
                new_index = (current_index - detents) % len(options)
                if new_index != current_index:
                    current_index = new_index
                    refresh()
                pulse_buffer -= detents * config.PULSES_PER_DETENT

        if not button.value:
            time.sleep(0.15)
            while not button.value: time.sleep(0.01)
            return options[current_index]

        time.sleep(0.004)

def select_level():
    ENCODER_DIRECTION = 1
    current_level = 1

    def refresh():
        clear_group()
        main_group.append(label.Label(FONT, text="Select Level", x=8, y=6))
        main_group.append(label.Label(FONT, text=f"Level {current_level}", x=20, y=30, scale=2))
        display_refresh()

    refresh()
    pulse_buffer = 0

    while True:
        diff = encoder.update()

        if diff:  
            pulse_buffer += diff
        
            if pulse_buffer >= config.PULSES_PER_DETENT:
                current_level += 1
                current_level = min(current_level, 10)   
                pulse_buffer -= config.PULSES_PER_DETENT
                refresh()

            elif pulse_buffer <= -config.PULSES_PER_DETENT:
                current_level -= 1
                current_level = max(current_level, 1)    
                pulse_buffer += config.PULSES_PER_DETENT
                refresh()

        if not button.value:
            time.sleep(0.15)
            while not button.value:
                time.sleep(0.01)
            return current_level

        time.sleep(0.004)

