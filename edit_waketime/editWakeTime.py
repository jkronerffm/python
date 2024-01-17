import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIButton, UIWindow
import json
import sys
from dictToObj import dictToObj

def loadWakeTime(filepath):
    with open(filepath) as f:
        wakeTime = json.load(f)

    return dictToObj(wakeTime)

if __name__ == "__main__":
    wakeTime = loadWakeTime(r"../radio/waketime.json")
    for job in wakeTime.scheduler.job:
        print(str(job))
        
    pygame.init()

    pygame.display.set_caption('Wake Time')
    window_surface = pygame.display.set_mode((800, 600))

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager((800, 600), 'themes/button1.json')
    manager.get_theme().load_theme('themes/uiWindow.json')

    is_running = True
    hello_button = UIButton(relative_rect=pygame.Rect((350, 280), (-1,-1)),
                                               text='Say Hello',
                                               manager = manager,
                                               object_id=ObjectID(class_id='@friendly_buttons',
                                                                  object_id='#hello_button'))
    uiWindow = UIWindow(rect=pygame.Rect((400, 300), (200, 50)), manager=manager, window_display_title = "Hello World",
                                         object_id=ObjectID(class_id='window'))
    uiWindow.hide()
    clock = pygame.time.Clock()

    while is_running:
        try:
            time_delta = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == hello_button:
                        print("Hello World!")
                        uiWindow.show()
                manager.process_events(event)

            manager.update(time_delta)
            window_surface.blit(background, (0, 0))
            manager.draw_ui(window_surface)

            pygame.display.update()
        except KeyboardInterrupt:
            is_running = False

    pygame.quit()
    sys.exit()
