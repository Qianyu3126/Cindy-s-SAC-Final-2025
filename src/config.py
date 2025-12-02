PULSES_PER_DETENT = 3
OLED_WIDTH = 128
OLED_HEIGHT = 64

NEOPIXEL_PIN = 6  # board.D6
NEOPIXEL_COUNT = 6
NEOPIXEL_BRIGHTNESS = 0.25

PIXEL_COLORS = [
    (255, 0, 0),    # Red
    (255, 128, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (128, 0, 255)   # Purple
]
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

DIFFICULTY_CONFIG = {
    "EASY": {
        "moves": ["Shift Left", "Shift Right", "Shift Forward", "Shift Backward"],
        "base_reaction": 4.0,
        "base_shift_threshold": 1.5,
        "mistakes_allowed": 4,
        "twist_detents_needed": None,
    },
    "MEDIUM": {
        "moves": ["Shift Left", "Shift Right", "Shift Forward", "Shift Backward", "Twist"],
        "base_reaction": 3.0,
        "base_shift_threshold": 2.0,
        "mistakes_allowed": 3,
        "twist_detents_needed": 1,
    },
    "HARD": {
        "moves": ["Shift Left", "Shift Right", "Shift Forward", "Shift Backward", "Twist"],
        "base_reaction": 2.0,
        "base_shift_threshold": 2.6,
        "mistakes_allowed": 1,
        "twist_detents_needed": 2,
    }
}
