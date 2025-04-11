from random import *
from math import *
import json
from combat import combat
from not_combat import not_combat
with open("./Resources/decks.json","r") as read_file:
    default_deck_1=json.loads(read_file.read())["Warrior"]
class Run:
    def __init__(self,surface,save_data):
        self.rarity_weights=[150,40,10,0]
        self.deck=default_deck_1.copy()
        self.surface=surface
        self.victory=False #No winning
        self.player_hp=90
        self.money=99
        self.floor=0
        self.enemy_effects=[]
        self.player_hp_healed=0
        #not_combat(surface,self,save_data)
        while self.player_hp>0:
            self.floor+=1

            combat(surface,self,save_data)
            if self.player_hp>0:
                self.player_hp_healed=min(90-self.player_hp,10)
                not_combat(surface,self,save_data)