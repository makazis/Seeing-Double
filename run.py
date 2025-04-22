from random import *
from math import *
import json
import pygame
pygame.init()
from Engine.board import Board
from Engine.map import Map
from combat import combat
from not_combat import not_combat
from useful_stuff import *
with open("./Resources/other/decks.json","r") as read_file:
    default_deck_1=json.loads(read_file.read())["Warrior"]
class Run:
    def __init__(self,surface,save_data):
        self.act=1
        self.rarity_weights=[150,40,10,0]
        self.deck=default_deck_1.copy()
        self.surface=surface
        self.victory=False #No winning
        self.player_hp=90
        self.money=99
        self.floor=0
        self.early_picked_cards=[]
        self.middle_picked_cards=[]
        self.late_picked_cards=[]
        self.camera_map_y=0
        self.room=0
        with open("Resources/other/map_pools.json","r") as f:
            room_distrib=json.loads(f.read())["Basic"]
        self.map=Map(25,0.9,0.02,room_distrib)
        self.choose_map_path(first=True)
        self.player_hp_healed=0
        #not_combat(surface,self,save_data)
        while self.player_hp>0:
            self.floor+=1
            if self.room.type=="Enemy":
                combat(surface,self,save_data)
                if self.player_hp>0:
                    self.player_hp_healed=min(90-self.player_hp,10)
                    not_combat(surface,self,save_data)
            if self.player_hp>0:
                self.choose_map_path()
        print(self.early_picked_cards,self.middle_picked_cards,self.late_picked_cards)
    def choose_map_path(self,first=False):
        if first:
            possible_rooms=self.map.rooms[0]
        else:
            possible_rooms=self.room.p_connections
            print(possible_rooms)
        choosing_map_room=True
        map_board=Board(self.surface.get_size())
        animations=[]
        chosen_room=None
        if first:
            animations.append({
                "Type":"Wait",
                "Timer":0.5
            })
            animations.append({
                "Type":"Scroll",
                "End Y":self.map.surface.get_height()-1080,
                "Starting Y":0,
                "Timer":1.5,
                "Max Timer":1.5
            })
        while choosing_map_room:
            calculate_dt()
            #for event in pygame.event.get():
            #    if event.type==pygame.QUIT:
            #        exit()
            if len(animations)>0:
                current_animation=animations[0]
                current_animation["Timer"]-=dt/60
                current_animation["Timer"]=max(current_animation["Timer"],0)
                if current_animation["Timer"]==0:
                    animations.pop(0)
                if current_animation["Type"]=="Scroll":
                    q=current_animation["Timer"]/current_animation["Max Timer"]
                    self.camera_map_y=current_animation["Starting Y"]*q+current_animation["End Y"]*(1-q)
            else:
                if map_board.mouse_scroll<0:
                        animations.append({
                    "Type":"Scroll",
                    "End Y":min(self.map.surface.get_height()-1080,self.camera_map_y+300),
                    "Starting Y":self.camera_map_y,
                    "Timer":0.1,
                    "Max Timer":0.1
                })
                elif map_board.mouse_scroll>0:
                        animations.append({
                    "Type":"Scroll",
                    "End Y":max(0,self.camera_map_y-307), #TroLOLOLOLOLOL
                    "Starting Y":self.camera_map_y,
                    "Timer":0.1,
                    "Max Timer":0.1
                })
            map_board.update(dt)
            map_board.surface.blit(self.map.surface,(0,-self.camera_map_y))
            for I,i in enumerate(possible_rooms):
                cq=(1+sin(I*tau/5+map_board.time_passed/20))/2*70+30
                
                if dist(map_board.mouse_pos,(i.pos[0],i.pos[1]-self.camera_map_y))<=43:
                    pygame.draw.circle(map_board.surface,(cq,cq/2+50,100),(i.pos[0],i.pos[1]-self.camera_map_y),43,5)
                    if map_board.click[0]:
                        pygame.draw.circle(self.map.surface,(55,55,55),(i.pos[0],i.pos[1]),47,5)
                        self.room=i
                        choosing_map_room=False
                else:
                    pygame.draw.circle(map_board.surface,(100,cq/2+50,cq),(i.pos[0],i.pos[1]-self.camera_map_y),43,5)
            map_board.display_mouse_cursor()
            self.surface.blit(pygame.transform.scale(map_board.surface,self.surface.get_size()),(0,0))
            pygame.display.update()