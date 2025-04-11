from random import *
from math import *
import pygame
pygame.init()

class Room:
    def __init__(self,room_types=[
        "Enemy","Elite","Miniboss","Shop"
    ],room_weights=None,pos=(0,0)):
        if room_weights==None:
            room_weights=[1 for i in room_types]
        
        self.type=choices(room_types,room_weights)[0]
        self.pos=pos
        self.connections=[]
        self.p_connections=[]
class Map:
    def __init__(self,floors=10,density=0.7,staircase=0.5):
        self.floors=floors
        self.rooms=[]
        self.density=density
        #1800 x ? y
        #80 y per floor
        self.surface=pygame.Surface((1800,floors*160+80))
        for i in range(self.floors):
            new_room_line=[]
            if random()<staircase:
                self.density=self.density**(0.9+random()*0.1)
            else:
                self.density=self.density**(1+random()/9)
            if i>0:
                p_room_count=room_count
            room_count=1+int(6*self.density)
            for ii in range(room_count):
                new_room_pos_x=(1+ii)/(room_count+1)*1800+randint(-64,64)
                new_room_pos_y=(floors*160+80)-(i*160+40+randint(-52,52))
                new_room=Room(room_weights=[2,1,0.2,1],pos=(new_room_pos_x,new_room_pos_y))
                
                pygame.draw.circle(self.surface,(255,255,255),(new_room_pos_x,new_room_pos_y),10)
                new_room_line.append(new_room)
                if i>0:
                    while len(new_room.connections)==0:
                        if (room_count+p_room_count)%2==0:
                            connections=[iii for iii in range(3)]
                            shuffle(connections)
                            for iii in range(randint(randint(0,1),2)):
                                connections.pop(0)
                            for iii in connections:
                                try:
                                    if room_count>ii+iii-1>-1:
                                        new_room.connections.append(self.rooms[i-1][ii+iii-1])
                                        self.rooms[i-1][ii+iii-1].p_connections.append(new_room)
                                        pygame.draw.line(self.surface,(255,255,255),new_room.pos,new_room.connections[-1].pos)
                                except: #if error occurs, fuck it, we ball
                                    pass
                            #print(connections)
                        else:
                            connections=[iii for iii in range(2)]
                            shuffle(connections)
                            for iii in range(randint(randint(0,1),1)):
                                connections.pop(0)
                            if room_count>p_room_count: #more rooms now, than there were
                                for iii in connections:
                                    try:
                                        if room_count>ii+iii-1>-1:
                                            new_room.connections.append(self.rooms[i-1][ii+iii-1])
                                            self.rooms[i-1][ii+iii-1].p_connections.append(new_room)
                                            pygame.draw.line(self.surface,(255,255,255),new_room.pos,new_room.connections[-1].pos)
                                    except: #if error occurs, fuck it, we ball
                                        pass
                            else:
                                for iii in connections:
                                    try:
                                        if room_count>ii+iii>-1:
                                            new_room.connections.append(self.rooms[i-1][ii+iii])
                                            self.rooms[i-1][ii+iii].p_connections.append(new_room)
                                            pygame.draw.line(self.surface,(255,255,255),new_room.pos,new_room.connections[-1].pos)
                                    except: #if error occurs, fuck it, we ball
                                        pass
            self.rooms.append(new_room_line)
        pygame.image.save(self.surface,"a.png")
new_map=Map(16,1)