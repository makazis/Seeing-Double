import os
import json
import pygame
import Engine.card_manager as cardman
from useful_stuff import *
from Engine.buff_tips import textify
spell_data={}
for root, dirs, files in os.walk(r"Resources/spells/"):
    for file in files:
        if file.endswith(".json"):
            with open(os.path.join(root,file),"r") as f:
                spell_data[file[:-5]]=json.loads(f.read())
overlays={}
for root, dirs, files in os.walk(r"Resources/overlays/"):
    for file in files:
        if file.endswith(".json"):
            with open(os.path.join(root,file),"r") as f:
                overlays[file[:-5]]=json.loads(f.read())
for i in overlays:
    overlays[i]["Sprite"]=pygame.image.load(overlays[i]["Path"])
    overlays[i]["Sprite"].set_colorkey(cardman.card_transparency_color)
#inv_card_overlay=pygame.image.load("Resources/images/cards/inv_p.png")
#inv_card_overlay.set_colorkey(cardman.card_transparency_color)

spell_sprite_cache={}
class Spell:
    def __init__(self,id):
        self.id=id #Will use this later, just needed for board things rn
        self.data=spell_data[self.id].copy()
        if not "Overlay" in self.data:
            self.data["Overlay"]="Standart"
        self.type="Spell"
        self.inv=False
        self.exhausted=False
        if "Image Path" in self.data:
            if not self.data["Image Path"] in spell_sprite_cache:
                spell_sprite_cache[self.data["Image Path"]]=pygame.transform.scale(pygame.image.load(self.data["Image Path"]),(170,100))
    def draw(self,side_on,inv=False):
        self.card.side_from_surface(cardman.cardSideImages["default-back"], "Back")
        self.card.side_from_surface(pygame.Surface((210,320)),side_on)
        self.card.sides[side_on].fill(card_transparency_color) #Replace this with image handling when the time comes
        if "Image Path" in self.data:
            self.card.sides[side_on].blit(spell_sprite_cache[self.data["Image Path"]],(20,20))
        self.card.sides[side_on].blit(overlays[self.data["Overlay"]]["Sprite"],(0,0))
        center(render_text(self.data["Card Data"]["Name"],14,overlays[i]["Title Color"],"Consolas"),self.card.sides[side_on],105,135)
        card_desc=self.data["Card Data"]["Description"]
        self.card.sides[side_on].blit(textify(card_desc,180,overlays[i]["Body Color"]),(0,165))
        #for I,i in enumerate(card_desc):
        #    y_pos=I-(len(card_desc)-1)/2
        #    center(render_text(i,14,(253,255,255),"Consolas"),self.card.sides[side_on],105,226+y_pos*20)
        if "Rarity" in self.data:
            if self.data["Rarity"]=="Uncommon":
                pygame.draw.rect(self.card.sides[side_on],(0,255,255),(0,0,210,320),2,15)
            if self.data["Rarity"]=="Rare":
                pygame.draw.rect(self.card.sides[side_on],(255,255,0),(0,0,210,320),2,15)
            if self.data["Rarity"]=="Cursed":
                pygame.draw.rect(self.card.sides[side_on],(125,0,195),(0,0,210,320),2,15)
            
        self.card.sides[side_on].blit(card_transparency_overlay,(0,0))
        
            #pygame.image.save(self.card.sides[side_on],"t.png")
        for I in range(self.data["Energy Cost"]):
            center(mid_energy_icon,self.card.sides[side_on],15+I*40,15)
"""
    new_object_manager.
        new_object_manager.card.side_from_surface(pygame.Surface((210,320)),side_on)
            new_object_manager.card.sides[side_on].fill((0,0,0)) #Replace this with image handling when the time comes
    else:
            new_object_manager.card.side_from_surface(cardSideImages["default-back"], "Back")"""