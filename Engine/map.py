from random import *
from math import *
import pygame
from useful_stuff import *
pygame.init()
non_repeatables=["","Elite","Miniboss","Shop","Rest",""]
encounter_types=["Enemy","Elite","Miniboss","Shop","Rest","Unknown"]
import os
import json
enemy_pools={}
for root,dirs,files in os.walk("Resources/enemy pools/"):
    for file in files:
        if file.endswith(".json"):
            with open(os.path.join(root,file),"r") as f:
                enemy_pools[file[:-5]]=json.loads(f.read())


class Room:
    def __init__(self,pos=(0,0)):
        self.pos=pos
        self.connections=[]
        self.p_connections=[]
        self.enemy_pool_name="Enemy_Pool_1"
    def choose_type(self,room_types=encounter_types,room_weights=None):
        if room_weights==None:
            room_weights=[1 for i in room_types]
        self.type=choices(room_types,room_weights)[0]
        if self.type=="Enemy":
            self.enemy_pool=choices(enemy_pools[self.enemy_pool_name]["Pool"],[i["Weight"] for i in enemy_pools[self.enemy_pool_name]["Pool"]])[0]
            self.enemies=[]
            for i in self.enemy_pool["Creatures"]:
                if i["Type"]=="Random Creature":
                    self.enemies.append(choices(i["Creature Choices"],[ii["weight"] for ii in i["Creature Choices"]])[0]["id"])
            

def draw_invis_line(surface,color,point_a,point_b,fragments=4,width=3,fragment_density=0.5):
    langle=atan2(point_a[1]-point_b[1],point_a[0]-point_b[0])
    for i in range(fragments):
        q=(2*i+1)/(2*fragments)
        wq=1/(2*fragments)*fragment_density
        start_x=point_a[0]*(q-wq)+point_b[0]*(1-q+wq)
        start_y=point_a[1]*(q-wq)+point_b[1]*(1-q+wq)

        end_x=point_a[0]*(q+wq)+point_b[0]*(1-q-wq)
        end_y=point_a[1]*(q+wq)+point_b[1]*(1-q-wq)
        
        pygame.draw.polygon(surface,color,(
            (
                start_x+sin(langle)*width,
                start_y-cos(langle)*width
            ),
            (
                start_x-sin(langle)*width,
                start_y+cos(langle)*width
            ),
            (
                end_x-sin(langle)*width,
                end_y+cos(langle)*width
            ),
            (
                end_x+sin(langle)*width,
                end_y-cos(langle)*width
            )
        ))
class Map:
    def __init__(self,floors=10,density=0.7,staircase=0.5,room_weight_distrib=None):
        self.floors=floors
        self.rooms=[]
        self.density=density
        self.room_weight_distrib=room_weight_distrib
        #1800 x ? y
        #160 y per floor
        self.surface=pygame.Surface((1920,floors*160+160+320))
        self.surface.fill((82,82,82))
        distrib_iterator=0
        for i in range(self.floors):
            if i>self.room_weight_distrib[distrib_iterator]["Max"]:
                distrib_iterator+=1
            new_room_line=[]
            if random()<staircase:
                self.density=self.density**(0.9+random()*0.1)
            else:
                self.density=self.density**(1+random()/9)
            if i>0:
                p_room_count=room_count
            room_count=1+int(6*self.density)
            for ii in range(room_count):
                new_room_pos_x=(4+ii-(room_count-1)/2)/(8)*1920+randint(-64,64)
                new_room_pos_y=(floors*160+320)-(i*160+80+randint(-52,52))
                new_room=Room(pos=(new_room_pos_x,new_room_pos_y))
                new_room_weights=self.room_weight_distrib[distrib_iterator]["Weights"].copy()
                if "Enemy Pool" in self.room_weight_distrib[distrib_iterator]: new_room.enemy_pool_name=self.room_weight_distrib[distrib_iterator]["Enemy Pool"];print(i)
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
                                        if self.rooms[i-1][ii+iii-1].type in non_repeatables:
                                            new_room_weights[non_repeatables.index(self.rooms[i-1][ii+iii-1].type)]=0.00001
                                        #draw_invis_line(self.surface,(55,55,55),new_room.pos,new_room.connections[-1].pos,10,6,0.6)
                                        #pygame.draw.line(self.surface,(55,55,55),new_room.pos,new_room.connections[-1].pos,4)
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
                                            if self.rooms[i-1][ii+iii-1].type in non_repeatables:
                                                new_room_weights[non_repeatables.index(self.rooms[i-1][ii+iii-1].type)]=0.00001
                                            #pygame.draw.line(self.surface,(55,55,55),new_room.pos,new_room.connections[-1].pos,4)
                                    except: #if error occurs, fuck it, we ball
                                        pass
                            else:
                                for iii in connections:
                                    try:
                                        if room_count>ii+iii>-1:
                                            new_room.connections.append(self.rooms[i-1][ii+iii])
                                            self.rooms[i-1][ii+iii].p_connections.append(new_room)
                                            if self.rooms[i-1][ii+iii].type in non_repeatables:
                                                new_room_weights[non_repeatables.index(self.rooms[i-1][ii+iii].type)]=0.000001
                                            #pygame.draw.line(self.surface,(55,55,55),new_room.pos,new_room.connections[-1].pos,4)
                                    except: #if error occurs, fuck it, we ball
                                        pass
                new_room.choose_type(encounter_types,new_room_weights)
            self.rooms.append(new_room_line)
        boss_room=Room((900,240))
        for i in self.rooms[-1]:
            i.p_connections.append(boss_room)
        boss_room.p_connections=[None]
        boss_room.choose_type(["Boss1"],[1])
        self.rooms.append([boss_room])
        
        for I,i in enumerate(self.rooms[::-1]): #iterate in reverse, in order to delete the rooms with no ways to go on from
            removed_rooms=[]
            for new_room in i:
                if len(new_room.p_connections)==0:
                    removed_rooms.append(new_room)
            if I<floors-1:
                for ii in removed_rooms:
                    for iii in self.rooms[::-1][I+1]:
                        if ii in iii.p_connections:
                            #print([iv.type for iv in iii.p_connections],ii.type)
                            iii.p_connections.remove(ii)
                    i.remove(ii)
                
        for i in self.rooms:
            for new_room in i:
                for ii in new_room.p_connections:
                    if ii!=None:
                        draw_invis_line(self.surface,(55,55,55),new_room.pos,ii.pos,8,6,0.4)
        for i in self.rooms:
            for new_room in i:
                if new_room.type in encounter_types:
                    center(map_icons[new_room.type],self.surface,new_room.pos[0],new_room.pos[1])
                else:
                    pygame.draw.circle(self.surface,(255,255,255),new_room.pos,10)
                
        #pygame.image.save(self.surface,"a.png")