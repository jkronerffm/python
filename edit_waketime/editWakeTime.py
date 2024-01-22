import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import (UIButton,
    UIWindow, UISelectionList, UILabel, UIDropDownMenu, UIVerticalScrollBar,
    UIPanel, UITextEntryLine, )
import json
import sys
from dictToObj import obj, objToDict, objToJson
import logging

class UIEditWakeTime:
    def __init__(self, wakeTime):
        self._wakeTime = wakeTime
        
        pygame.display.set_caption('Wake Time')
        self._window_surface = pygame.display.set_mode((800, 600))

        self._background = pygame.Surface((800, 600))
        self._background.fill(pygame.Color('#ffffff'))

        logging.debug('load themes')
        self._manager = pygame_gui.UIManager((800, 600), 'themes/button1.json')
        self._manager.get_theme().load_theme('themes/selectionList.json')
        self._initUI()

    def _initUISelectionPanel(self):
        self._listPanel = UIPanel(pygame.Rect((10, 0), (200,300)), 1, self._manager, container=self._mainPanel,
                                  anchors={
                                      'left': 'left',
                                      'top': 'top',
                                      'top_target': self._label
                                  })
        self._selectionList = UISelectionList(pygame.Rect((0,0), (176, 296)), [],
                                              manager = self._manager,
                                              container = self._listPanel,
                                              object_id=ObjectID(class_id="selection_list.@selection_list_item"),
                                              anchors={
                                                  'left': 'left',
                                                  'top': 'top',
                                                  'right': 'right',
                                                  'bottom':'bottom'
                                              })
        self._uiScrollbar = UIVerticalScrollBar(pygame.Rect((-20,0), (20,296)),
                                                100.0,
                                                self._manager,
                                                container=self._listPanel,
                                                anchors=
                                                {
                                                    'right': 'right',
                                                    'top': 'top'
                                                })
        jobs = [job.name[len("start_"):] for job in self._wakeTime.scheduler.job]
        self._selectionList.add_items(jobs)
        
    def _initUIEditPanel(self):
        self._editPanel = UIPanel(pygame.Rect((10, 0), (400, 300)), 1,
                                  self._manager,
                                  container = self._mainPanel,
                                  anchors= {
                                      'left': 'left',
                                      'top': 'top',
                                      'left_target': self._listPanel,
                                      'top_target': self._label
                                  })
        self._labelName = UILabel(pygame.Rect((10, 10, 100, 24)), "Name:", self._manager, container= self._editPanel)
        self._editName = UITextEntryLine(pygame.Rect((10, 2, 250, 28)), self._manager, container = self._editPanel,
                                     anchors = {
                                         'left': 'left',
                                         'top': 'top',
                                         'top_target': self._labelName
                                     })
        self._labelType = UILabel(pygame.Rect((10, 10, 100, 24)), "Type:", self._manager, container=self._editPanel,
                                  anchors= {
                                      'left': 'left',
                                      'top': 'top',
                                      'top_target': self._editName
                                  })
        self._dropBoxType = UIDropDownMenu(["date", "cron"], "date",pygame.Rect((10, 2, 100, 28)), self._manager, container= self._editPanel,
                                                       anchors= {
                                                           'left': 'left',
                                                           'top': 'top',
                                                           'top_target': self._labelType
                                                       })
        self._cronPanel = UIPanel(pygame.Rect((10, 2, 380, 
        
    def _initUI(self):
        logging.debug('build UIElements')
        self._mainPanel = UIPanel(pygame.Rect((5, 5), (790, 590)), 1, self._manager)
        self._label = UILabel(relative_rect=pygame.Rect((10, 2), (100, 24)), text='Jobs:', manager=self._manager, container=self._mainPanel)
        self._initUISelectionPanel()
        self._initUIEditPanel()

    def onQuit():
        self._isRunning = False
        
    def onSelectionListClick(self, event):
        logging.debug(f"selectionList clicked on {event.text}")
        job = getWakeTime(self._wakeTime, event.text)
        logging.debug(f"job={job}")
        self._editName.set_text(job.name)
        
    def handleEvent(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    self._isRunning = False
            elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                    if event.ui_element == self._selectionList:
                        self.onSelectionListClick(event)

            self._manager.process_events(event)
        
    def run(self):
        self._isRunning = True
        clock = pygame.time.Clock()

        while self._isRunning:
            try:
                time_delta = clock.tick(60) / 1000.0
                self.handleEvent()
                self._manager.update(time_delta)
                self._window_surface.blit(self._background, (0, 0))
                self._manager.draw_ui(self._window_surface)

                pygame.display.update()
            except KeyboardInterrupt:
                self._isRunning = False
        
        
def loadWakeTime(filepath):
    with open(filepath) as f:
        wakeTime = json.load(f)

    return obj(wakeTime)

def getWakeTime(wakeTime, name):
    if not name.startswith('start_'):
        name = "start_" + name

    return next(x for x in wakeTime.scheduler.job if x.name == name)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    wakeTime = loadWakeTime(r"../radio/waketime.json")
    pygame.init()
          
    uiEditWakeTime = UIEditWakeTime(wakeTime)
    uiEditWakeTime.run()

    pygame.quit()
    sys.exit()
