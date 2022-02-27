from sys import exit

import pygame
from pygame.locals import *

CDROM = pygame.cdrom  # Accesses and controls CD drives
CURSOR = pygame.cursors  # Loads cursor images
DISPLAY = pygame.display  # Accesses the display
DRAW = pygame.draw  # Draws shapes, lines, and points
EVENT = pygame.event  # Manages external events
FONT = pygame.font  # Uses system fonts
IMAGE = pygame.image  # Loads and saves an image
JOYSTICK = pygame.joystick  # Uses joysticks and similar devices
KEYS = pygame.key  # Reads key presses from the keyboard
MIXER = pygame.mixer  # Loads and plays sounds
MOUSE = pygame.mouse  # Manages the mouse
MOVIE = pygame.movie  # Plays movie files
MUSIC = pygame.mixer_music  # Works with music and streaming audio
OVERLAY =pygame.overlay  # Accesses advanced video overlays
PYGAME = pygame  # Contains high-level Pygame functions
RECT = pygame.rect  # Manages rectangular areas
SOUNDARRAY = pygame.sndarray  # Manipulates sound data
SPRITE = pygame.sprite  # Manages moving images
SURFACE = pygame.surface  # Manages images and the screen
SURFARRAY = pygame.surfarray  # Manipulates image pixel data
TIME = pygame.time  # Manages timing and frame rate
TRANSFORM = pygame.transform  # Resizes and moves images

LIST_OF_MODULES = [CDROM, CURSOR, DISPLAY, DRAW, EVENT, FONT, IMAGE, JOYSTICK, KEYS, MIXER, MOUSE, MOVIE, MUSIC,
                   OVERLAY, RECT, SOUNDARRAY, SPRITE, SURFACE, SURFARRAY, TIME, TRANSFORM]

for module in LIST_OF_MODULES:
    if module is not None:
        print(module, " : is present")
    else:
        print(module, " : is not present")

background_image_file = "./images/luxury_hotel-wallpaper-1680x1260.jpg"
cursor_image_file = "./images/gv.png"

pygame.init()

screen = DISPLAY.set_mode((640, 480), 0, 32)  # Tamanho do ecra, flag e depth, 8bit, 15bits, 16bits, 32bits, etc.
DISPLAY.set_caption("NTXUVA")

background = IMAGE.load(background_image_file).convert()
mouse_cursor = IMAGE.load(cursor_image_file).convert_alpha()
icon = IMAGE.load(cursor_image_file).convert()
DISPLAY.set_icon(icon)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            print("saindo: ", event.type)
            exit()

        screen.blit(background, (0, 0))

        x, y = MOUSE.get_pos()
        print("Evento: ", event.type, "Posicao: ", x, y)
        x -= mouse_cursor.get_width() / 2
        y -= mouse_cursor.get_height()/2

        screen.blit(mouse_cursor, (x, y))

        DISPLAY.update()