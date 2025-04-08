import os
import pygame
from useful_stuff import *
cardSideImages={}
def loadCardImages(path="./Resources/images/cards/"): # must have slash at the end
    for name in os.listdir(path):
        if name.endswith(".png"):
            with open(os.path.join(path, name)) as f:
                cardSideImages[''.join(name.split(".")[:-1])] = pygame.transform.scale(pygame.image.load(path + name), (210, 320))
loadCardImages()