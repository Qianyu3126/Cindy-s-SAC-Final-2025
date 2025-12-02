# game_core.py -- Game Parameters and Gesture Detection

import time
import random

import config

# Global variables for hardware access (will be set by setup_core)
accelerometer = None
encoder = None
button = None
pixels = None

def setup_core(hw):
    """Initializes core-related global variables using hardware objects."""
    global accelerometer, encoder, button, pixels
    accelerometer = hw["accelerometer"]
    encoder = hw["encoder"]
    button = hw["button"]
    pixels = hw["pixels"]

# ----------------- Game Parameters -----------------
def params_for(difficulty, level):
    """Calculates game parameters based on difficulty and level."""
    cfg = config.DIFFICULTY_CONFIG[difficulty]
    level = max(1, min(10, level))
    reaction = max(0.8, cfg["base_reaction"] - (level - 1) * 0.12)

    base_t = cfg["base_shift_threshold"]
    if difficulty == "EASY":
        tilt_threshold = max(0.8, base_t - (level - 1) * 0.06)
    elif difficulty == "MEDIUM":
        tilt_threshold = max(1.0, base_t - (level - 1) * 0.08)
    else:
        tilt_threshold = base_t + (level - 1) * 0.05

    return {
        "moves": cfg["moves"],
        "reaction_time": reaction,
        "shift_threshold": tilt_threshold,
        "noise_threshold": 0.12,
        "mistakes_allowed": cfg["mistakes_allowed"],
        "twist_detents_needed": cfg["twist_detents_needed"],
        "score_to_win": 6
    }

# ----------------- Gesture Detection -----------------
def wait_for_gesture(timeout, target, params):
    """Waits for the player to perform the target gesture within the timeout."""
    start = time.monotonic()

    def back_to_neutral(t=1.2):
        """Waits for the accelerometer to return to a relatively neutral state."""
        t0 = time.monotonic()
        while time.monotonic() - t0 < t:
            ax, ay, az = accelerometer.acceleration
            if abs(ax) < params["noise_threshold"] and abs(ay) < params["noise_threshold"]:
                return True
            time.sleep(0.03)
        return False

    twist_count = 0
    local_buf = 0

    while time.monotonic() - start < timeout:
        # Twist
        if target == "Twist":
            diff = encoder.update()
            if diff:
                local_buf += diff
                if abs(local_buf) >= config.PULSES_PER_DETENT:
                    det = int(local_buf / config.PULSES_PER_DETENT)
                    twist_count += abs(det)
                    local_buf -= det * config.PULSES_PER_DETENT

            needed = params["twist_detents_needed"]
            if needed and twist_count >= needed:
                back_to_neutral(0.6)
                return "Twist"

            time.sleep(0.02)
            continue

        # Tilt
        x, y, z = accelerometer.acceleration
        x = 0 if abs(x) < params["noise_threshold"] else x
        y = 0 if abs(y) < params["noise_threshold"] else y

        if x > params["shift_threshold"]:
            back_to_neutral()
            return "Shift Right"
        if x < -params["shift_threshold"]:
            back_to_neutral()
            return "Shift Left"
        if y > params["shift_threshold"]:
            back_to_neutral()
            return "Shift Forward"
        if y < -params["shift_threshold"]:
            back_to_neutral()
            return "Shift Backward"

        time.sleep(0.03)

    return None

# ----------------- Game Engine -----------------
# We put the run_level here too, as it is the main execution loop for the game.
import display_ui

def run_level(difficulty, level):
    """Runs a single level of the game."""
    p = params_for(difficulty, level)

    MOVES = p["moves"]
    REACTION = p["reaction_time"]
    MISTAKES_ALLOWED = p["mistakes_allowed"]
    SCORE_TO_WIN = p["score_to_win"]

    display_ui.show_lines([f"{difficulty} Level {level}", "", "Press button to start"])
    
    # Wait for button press to start
    while button.value: time.sleep(0.01)
    time.sleep(0.2)
    while not button.value: time.sleep(0.01)

    pixels.fill(config.BLUE)
    score = 0
    mistakes = 0

    while True:
        # Game over check
        if mistakes >= MISTAKES_ALLOWED:
            pixels.fill(config.RED)
            display_ui.show_lines(["GAME OVER", f"Score: {score}", "", "Press button"])
            while button.value: time.sleep(0.02)
            while not button.value: time.sleep(0.02)
            return False

        # Win check
        if score >= SCORE_TO_WIN:
            pixels.fill(config.GREEN)
            display_ui.show_lines(["YOU WIN!!", f"Score: {score}", "", "Press button"])
            while button.value: time.sleep(0.02)
            while not button.value: time.sleep(0.02)
            return True

        # Next move
        target = random.choice(MOVES)
        short = difficulty[0]
        display_ui.show_command_with_header(target, short, level)

        act = wait_for_gesture(REACTION, target, p)

        # Process result
        if act is None:
            pixels.fill(config.RED)
            display_ui.show_command_with_header("Too Slow", short, level)
            mistakes += 1
            time.sleep(0.6)
        elif act == target:
            pixels.fill(config.GREEN)
            display_ui.show_command_with_header("Good!", short, level)
            score += 1
            time.sleep(0.5)
        else:
            pixels.fill(config.RED)
            display_ui.show_command_with_header("Wrong", short, level)
            mistakes += 1
            time.sleep(0.6)

        pixels.fill(config.BLUE)