from random import *
from math import *
import pygame
pygame.init()

class Room:
    def __init__(self,room_types=[
        "Enemy","Elite","Miniboss","Shop"
    ],room_weights=None):
        if room_weights==None:
            room_weights=[1 for i in room_types]
        
        self.type=choices(room_types,room_weights)[0]
        print(self.type)

class Map:
    def __init__(self,floors=10,density=0.7,staircase=0.5):
        self.floors=floors
        self.rooms=[]
        self.density=density
        for i in range(self.floors):
            new_room_line=[]
            if random()<staircase:
                self.density=self.density**(0.9+random()*0.1)
            else:
                self.density=self.density**(1+random()/9)
            for ii in range(1+int(6*self.density)):
                new_room=Room(room_weights=[2,1,0.2,1])
        
            print()
new_map=Map(34)