import os
import pygame
from useful_stuff import *
from Engine.card_manager import *
import json
creature_data={}
for root, dirs, files in os.walk(r"Resources/creatures/"):
    for file in files:
        if file.endswith(".json"):
            with open(os.path.join(root,file),"r") as f:
                creature_data[file[:-5]]=json.loads(f.read())
cached_sprite_pictures={}
block_icon=pygame.image.load("Resources/images/icons/defence.png")
class Creature:
    def __init__(self,_id,**kwargs):
        self.id=_id
        self.data=creature_data[self.id].copy()
        self.max_hp=self.data["Health"]
        self.hp=self.max_hp
        self.secondary_hp=self.hp
        self.block=0
        self.card=None
        self.sprite=[]
        for i in self.data["Animations"]:
            if not i["Sprite Path"] in cached_sprite_pictures:
                cached_sprite_pictures[i["Sprite Path"]]=pygame.image.load(i["Sprite Path"])
                #cached_sprite_pictures[i["Sprite Path"]+"-"]=cached_sprite_pictures[i["Sprite Path"]].copy()
                #cached_sprite_pictures[i["Sprite Path"]+"-"].fill((242,188,204),special_flags=pygame.BLEND_MULT)
                
            self.sprite.append(i.copy())
        self.type="Creature"
        self.b_timer=0
        self.team=1
        self.alive=True
        self.o_alive=True
        self.powers=[]
        self.buffs={}
        self.action=None
        self.poison_color=(93,208,94)
        self.antivenom_color=(65,156,65)
        self.variables={}
        self.board=None
        self.turns=0
        self.deck=None
        if "team" in kwargs:
            self.team=kwargs["team"]
        if self.team==0:
            self.hp_color=(255,0,0)
            self.block_color=(125,125,125)
            self.sec_hp_color=(255,125,0)
        else:
            self.hp_color=(255,0,125)
            self.sec_hp_color=(125,0,255)
            self.attacks=self.data["Attack Pattern"]
            self.enemy=None
            if self.attacks["Type"]=="Card Based":
                self.max_energy=self.attacks["Energy"]
                self.deck=[]
                self.discard=[]
    def draw(self,delta=1):
        if self.card!=None:
            self.b_timer+=delta
            if self.team==0:
                self.card.sides[self.card.data["Side On Top"]].blit(cardSideImages["default-back"],(0,0))
            elif self.team==1:
                if self.alive:
                    self.card.sides[self.card.data["Side On Top"]].blit(cardSideImages["default-back"],(0,0))
                else:
                    self.card.sides[self.card.data["Side On Top"]].blit(cardSideImages["dead"],(0,0))
            
            if self.hp>round(self.secondary_hp,1):
                self.secondary_hp+=delta/6
            if self.hp<round(self.secondary_hp,1):
                self.secondary_hp-=delta/6
            for i in self.sprite:
                x_position=i["X Center"]+105
                y_position=i["Y Center"]+160
                if self.card.data["Side On Top"]==i["Side"]:
                    if self.alive:
                        center(cached_sprite_pictures[i["Sprite Path"]],self.card.sides[i["Side"]],x_position,y_position)
                        
                else:
                    pass
            if self.alive:
                pygame.draw.rect(self.card.sides[self.card.data["Side On Top"]],(5,5,5),(5,300,200,20),0,10)
                if self.block>0:
                    pygame.draw.rect(self.card.sides[self.card.data["Side On Top"]],(155,155,155),(5,300,200*self.hp/self.max_hp,20),0,10)
                else:
                    pygame.draw.rect(self.card.sides[self.card.data["Side On Top"]],self.sec_hp_color,(5,300,200*self.secondary_hp/self.max_hp,20),0,10)
                    pygame.draw.rect(self.card.sides[self.card.data["Side On Top"]],self.hp_color,(5,300,200*self.hp/self.max_hp,20),0,10)
                if "Poison" in self.buffs:
                    if "Antivenom" in self.buffs:
                        pygame.draw.rect(self.card.sides[self.card.data["Side On Top"]],self.antivenom_color,(5+200*(self.hp-min(self.hp,self.buffs["Poison"]))/self.max_hp,300,200*(min(self.hp,self.buffs["Poison"]))/self.max_hp,20),0,10)
                    else:
                        pygame.draw.rect(self.card.sides[self.card.data["Side On Top"]],self.poison_color,(5+200*(self.hp-min(self.hp,self.buffs["Poison"]))/self.max_hp,300,200*(min(self.hp,self.buffs["Poison"]))/self.max_hp,20),0,10)
                if self.block>0:
                    center(block_icon,self.card.sides[self.card.data["Side On Top"]],15,310)
                    center(render_text(f"{self.block}",20,(255,255,255),"Conosolas"),self.card.sides[self.card.data["Side On Top"]],15,310)
                center(render_text(f"{self.hp}/{self.max_hp}",20,(255,255,255),"Conosolas"),self.card.sides[self.card.data["Side On Top"]],105,310)
                self.card.sides[self.card.data["Side On Top"]].blit(card_transparency_overlay,(0,0))
            #center()
    def take_damage(self,damage):
        was_unblocked=False
        if damage>0:
            
            print(self.id,damage,self.block)
            #if "Vulnerable" in self.buffs:
            #    damage=int(damage*1.5)
            if self.block>0:
                self.block-=damage
                if self.block<=0:
                    self.board.check_for_powers("Lose All Block")
            else:
                
                if not "Immune" in self.buffs:
                    self.hp-=damage
                    was_unblocked=True
            if self.block<0:
                if not "Immune" in self.buffs:
                    was_unblocked=True
                    self.hp+=self.block

            if self.hp<=0:
                self.alive=False
            self.update_action()
            self.draw()
            return was_unblocked,
        return was_unblocked,
    def turn_start(self):
        self.turns+=1
        if self.team==1:
            if self.turns==1:
                if "Start Of Game Effect" in self.data:
                    self.board.targets=[self]
                    self.board.prime_caster=self
                    self.board.run_effect(self.data["Start Of Game Effect"])
            if self.attacks["Type"]=="Random":
                self.prime_action=choices(self.attacks["Attacks"],[i["Weight"] for i in self.attacks["Attacks"]])[0]
            elif self.attacks["Type"]=="Card Based":
                self.energy=self.max_energy
                self.cards_played=[]
                while self.energy>0:
                    if len(self.deck)==0:
                        self.deck=self.discard.copy()
                        self.discard=[]
                    new_card=choice(self.deck)
                    self.deck.remove(new_card)
                    self.discard.append(new_card)
                    if new_card.test_play_availability(self.energy,self):
                        self.energy-=new_card.data["Energy Cost"]
                        if "Buff Cost" in new_card.data:
                            for i in new_card.data["Buff Cost"]:
                                self.buffs[i]-=new_card.data["Buff Cost"][i]
                                if self.buffs[i]==0:
                                    del self.buffs[i]
            self.update_action()
        else:
            pass
            #for i in self.powers:

            #self.block_2=0
            #self.block_1=0
            if "Poison" in self.buffs:
                if not "Antivenom" in self.buffs:
                    self.hp-=self.buffs["Poison"]
                    if self.hp<=0:
                        self.alive=False
                    self.update_action()

        removed_buffs=[]
        for i in self.buffs:
            if i in temporal_buffs:
                self.buffs[i]-=1
                if self.buffs[i]<=0:
                    removed_buffs.append(i)
        for i in removed_buffs:
            del self.buffs[i]
        
    def update_action(self):

        if self.team==1:
            if self.attacks["Type"] in ["Random"]:
                self.action=self.prime_action.copy()
                if self.action["Type"] in ["Deal Damage","Deal Damage And Block","Multi Attack"]:
                    self.action["Damage Displayed"]=self.action["Damage"]
                    if "Strength" in self.buffs:
                        self.action["Damage Displayed"]+=self.buffs["Strength"]
                    if "Vulnerable" in self.enemy.buffs:
                        self.action["Damage Displayed"]=int(self.action["Damage Displayed"]*1.5)
                    if "Weak" in self.buffs:
                        self.action["Damage Displayed"]=int(self.action["Damage Displayed"]*0.75)
                if self.action["Type"]=="Deal Damage And Block":
                    self.action["Block Displayed"]=self.action["Block"]
                    if "Dexterity" in self.buffs:
                        self.action["Block Displayed"]+=self.buffs["Dexterity"]

                if not self.alive:
                    self.action={
                        "Type":"None"
                    }
        
    def complete_action(self,board):
        #turn starts
        
        self.block=0
        if self.action["Type"]=="Deal Damage":
            board.player.parent.take_damage(self.action["Damage Displayed"])

        if self.action["Type"]=="Buff Self":
            for buff_applied in self.action["Buffs"]:
                if not buff_applied["Type"] in self.buffs:
                    self.buffs[buff_applied["Type"]]=0
                if "Conduit" in self.buffs and buff_applied["Type"] in conduit_buffs:
                    if buff_applied["Value"]<0:
                        self.buffs[buff_applied["Type"]]+=-self.buffs["Conduit"]
                    else:
                        self.buffs[buff_applied["Type"]]+=self.buffs["Conduit"]
                self.buffs[buff_applied["Type"]]+=buff_applied["Value"]
    
        
        if self.action["Type"]=="Deal Damage And Block":
            board.player.parent.take_damage(self.action["Damage Displayed"])
            self.block+=self.action["Block Displayed"]
    

        if self.action["Type"]=="Multi Attack":
            for i in range(self.action["Hits"]):
                board.player.parent.take_damage(self.action["Damage Displayed"])
    def turn_end(self):
        if self.team==1:
            if "Poison" in self.buffs:
                if not "Antivenom" in self.buffs:
                    self.hp-=self.buffs["Poison"]
                    if self.hp<=0:
                        self.alive=False
                    self.update_action()