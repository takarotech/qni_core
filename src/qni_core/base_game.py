import os
import pygame
import tkinter
import logging
import platform

from . import logger, config, electrodes


class BaseGame(object):
    FPS = 30
    _logger = logging.getLogger('base_game')

    def __init__(self):
        logger.config_logger()
        self.root = tkinter.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        self.root.bind_all('<Escape>', self.__exit__) # works only on windows because of overrideredirect
        self.root.bind_all('<Button-1>', self.__exit__) # exit on window click - cross platform
        self.root.geometry('{}x{}+{}+{}'.format(*(config.TILE_SIZE + config.SCREEN_POSITION)))
        os.environ['SDL_WINDOWID'] = str(self.root.winfo_id())
        if platform.system == 'Windows':
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        self.root.update()

        pygame.init()
        self.window_surface = pygame.display.set_mode(config.TILE_SIZE)
        self.electrodes = electrodes.EvElectrodesGrid(
            config.ELECTRODES_SIZE, config.TILE_SIZE, False)
        self.fps_clock = pygame.time.Clock()
        self.running = True
        self._logger.info('Window opened!')

    def __loop__(self, pygame_events):
        pass

    def _handle_events(self, pygame_events):
        for i in pygame_events:
            if i.type == pygame.KEYDOWN:
                if i.key == pygame.K_ESCAPE:
                    self.__exit__()
            elif i.type == pygame.QUIT:
                self.__exit__()

    def mainloop(self):
        while self.running:
            # limit framerate
            time_diff = self.fps_clock.tick(self.FPS)
            # update electrodes touch events
            self.electrodes.update()
            # handle pygame events
            pygame_events = pygame.event.get()
            self._handle_events(pygame_events)
            # game loop iteration
            self.__loop__(pygame_events, time_diff)
            # update surface
            pygame.display.update()
            self.root.update()

    def __exit__(self, *_, **__):
        if hasattr(self, '_exit'):
            return
        setattr(self, '_exit', True)
        self._logger.warning('Window closed!')
        self.running = False
        self.root.quit()
        # self.root.destroy()
