import TetrisNumpyGame
import os
from pynput import keyboard

# the pynput module is used as keylistener. It differenciates between special keys like "space" and 
# normal charackter keys

def clear():
	os.system("clear")
    
possible_controls = { keyboard.Key.left , keyboard.Key.right, keyboard.Key.space, keyboard.Key.up, keyboard.Key.down, "z", "c", "a"}
    
control_mapping = {keyboard.Key.up: "up", 
                   keyboard.Key.down:"down", 
                   keyboard.Key.left : "left",
                   keyboard.Key.right : "right", 
                   keyboard.Key.space : "space"}

tetris = TetrisNumpyGame.Tetris()
tetris.get_state()
clear()
print(tetris.screen)

def game():
    score = 0
    restart_required = False
    while not restart_required:
        with keyboard.Events() as events:
            event = events.get(1.0)
            if event != None and type(event) == keyboard.Events.Press and type(event.key) != keyboard.KeyCode and event.key in possible_controls:
                action = control_mapping[event.key]
            elif event != None and type(event) == keyboard.Events.Press and type(event.key) == keyboard.KeyCode and event.key.char in possible_controls:
                action = event.key.char
            else:
                action = "nothing"
            action_reward = tetris.take_action(action)
            cleared_lines_reward = tetris.clear_lines()
            _, restart_required = tetris.check_for_restart()
            if restart_required:
                print("Game over. Final score: ", score)
                break
            tetris.get_state()
            score += action_reward + cleared_lines_reward
            clear()
            print(tetris.screen)
            print("Score: ", score)
        

if __name__ == "__main__":
    game()