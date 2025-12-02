import time

import hardware
import config
import display_ui
import game_core

FIRST_BOOT = True

def main_game_loop():
    """Main loop for difficulty/level selection and running the game."""
    global FIRST_BOOT

    # --- Startup ---
    if FIRST_BOOT:
        display_ui.startup_pixels()
        display_ui.startup_loading_bar()
        FIRST_BOOT = False

    display_ui.show_lines(["Shift Quest", "", "Rotate to choose", "Press to confirm"])
    time.sleep(1)

    # --- Game Flow ---
    while True:
        difficulty = display_ui.select_difficulty(list(config.DIFFICULTY_CONFIG.keys()))
        display_ui.show_lines([f"Selected: {difficulty}", ""])
        time.sleep(0.4)

        level = display_ui.select_level()
        display_ui.show_lines([f"Start {difficulty} L{level}", "", "(auto start)"])
        time.sleep(0.4)

        game_core.run_level(difficulty, level)

# Initialization and Execution
if __name__ == "__main__":
    hw_components = hardware.init_hardware()

    display_ui.setup_ui(hw_components)
    game_core.setup_core(hw_components)

    main_game_loop()
