from Engine.card import *
import Engine.creature as creature
import Engine.spell as spell
import Engine.button as button
from Engine.buff_tips import buff_tips
import sys
import logging
import os
import Engine.pile
import pygame
from math import cos, sin, pi

class Board:
    def __init__(self,inherited_screen_size=(1920,1080)):
        self.locations={  #Contains all the data about where cards can exist
            "Board":[],
            "OnTable":[]
        }
        self.card_piles={} #Stored as a dict so that you can get a card pile by its name
        self.surface=pygame.Surface((1920,1080))
        self.camera_x=0
        self.camera_y=0 #Puts the camera about right

        self.mouse_pos=[0,0] #Set to this for now, as it causes a crash if unset
        self.r_mouse_pos=[0,0]
        self.mouse_pos_multiplier=[[1920,1080][i]/inherited_screen_size[i] for i in range(2)] #Adjusts the mouse correctly
        self.drag_screen_allowed=True #Sets whether or not if you drag something, it will be dragged across the screen
        self.mouse_down=[False for i in range(3)]
        self.ctimer=[0,0,0]
        self.mcctimer=0
        self.click=[False,False,False] #Can accurately detect the first frame when the mouse button is clicked
        self.mouse_scroll=0
        self.game_over=False
        self.open_GUIs={}

        

        self.time_passed=0
        self.tech={} #Current Effects happening on board
    
        self.hand=None
        self.player=None

        self.droplets=[] #The array for the particles on the black side of the screen
        self.ba_frames={}
        self.energy=3
        self.npc_cache=[]
        self.p_turn=False
        self.game_speed=2

        self.data={
            "Cards Drawn Per Turn":5,
            "Energy Per Turn":3,
        }
        self.powers=[]
        self.bad_apple=True #trolololol

        self.inventory_y=0
    def setup_hand(self,max_cards=10):
        self.hand=Engine.pile.Hand((0,500),max_cards)
    def setup_card_pile(self,card_pile_name="Deck",pos=(900,0),custom_size=(210,320)):
        self.card_piles[card_pile_name]=Engine.pile.Pile(card_pile_name,pos,custom_size=custom_size)
        #self.card_piles.append(card_pile_name)
    def draw(self,delta=1,screen=None):
        if len(self.npc_cache)==0 and not self.p_turn:
            
            self.turn_start() #has to be up here so that some stuff down the line doesn't get sad/
            
        if not self.player.parent.alive:
            return "Game Over"
        #self.t_surface.fill((12,34,56))
        self.drag_screen_allowed=False
        self.surface.fill((15,15,15)) #Fills the board with a nice color to draw on
        if len(self.droplets)<6:
            self.droplets.append({
                "max time":randint(10,40),
                "max radius":randint(50,200),
                "time":0,
                "center":[randint(0,1920),randint(0,1080)]
            })
        self.removed_droplets=[]
        for i in self.droplets:
            cq=240*(1-i["time"]/i["max time"])**1.6+15
            other_cq=205-(1-i["time"]/i["max time"])**1.6*205
            corner_pos=[ii-(i["time"]/i["max time"])*i["max radius"] for ii in i["center"]]
            pygame.draw.rect(self.surface,(cq,cq,cq),(corner_pos[0],corner_pos[1],(i["time"]/i["max time"])*i["max radius"]*2,(i["time"]/i["max time"])*i["max radius"]*2),3,15)
            i["time"]+=delta/10
            if i["time"]>i["max time"]:
                self.removed_droplets.append(i)
        for i in self.removed_droplets:
            self.droplets.remove(i)
        #self.dead_characters=[]
        current_animation=None
        if len(self.npc_cache)>0:
            current_animation=self.npc_cache[0]
            if current_animation["Type"]=="Action Animation":
                self.npc_cache[0]["Time Elapsed"]+=delta/60
                if self.npc_cache[0]["Time Elapsed"]>1/self.game_speed and not self.npc_cache[0]["Action Completed"]:
                    current_animation["Target"]["Card"].parent.complete_action(self)
                    self.npc_cache[0]["Action Completed"]=True
                if self.npc_cache[0]["Time Elapsed"]>2/self.game_speed:
                    self.npc_cache.pop(0)
                    
            if current_animation["Type"]=="Wait":
                self.npc_cache[0]["Time Left"]-=delta/60*self.game_speed
                if self.npc_cache[0]["Time Left"]<=0:
                    self.npc_cache.pop(0)
            if current_animation["Type"]=="Butterfly Blessing":
                self.targets=[current_animation["Target"].parent]
                self.run_effect(current_animation["Effect"])
                self.npc_cache.pop(0)
        enemies_alive=len(self.locations["OnTable"])-1
        if self.click[2]:
            if "Inspecting Creature" in self.open_GUIs:
                del self.open_GUIs["Inspecting Creature"]
        for i in self.locations["OnTable"]:
            xmod=0
            if current_animation!=None:
                if current_animation["Type"]=="Action Animation":
                    if current_animation["Target"]==i:
                        xmod=-(abs(sin(current_animation["Time Elapsed"]*pi*self.game_speed/2))**2.2)*100
            i["Card"].draw(delta=delta)
            
            if i["Side"]==0:
                center(i["Card"].sprite,self.surface,i["Position"][0]+xmod,i["Position"][1])
            else:
                center(i["Card"].sprite,self.surface,i["Position"][0]+xmod*i["Card"].parent.alive,i["Position"][1])
                action=i["Card"].parent.action
                if action!=None:
                    if action["Type"]=="Deal Damage":
                        center(sword_icon,self.surface,i["Position"][0],i["Position"][1]-184)
                        center(render_text(action["Damage Displayed"],20,(205,205,205)),self.surface,i["Position"][0]+24,i["Position"][1]-184)
                    elif action["Type"]=="Buff Self":
                        center(buff_icon,self.surface,i["Position"][0],i["Position"][1]-184)
                    if action["Type"]=="Multi Attack":
                        center(sword_icon,self.surface,i["Position"][0],i["Position"][1]-184)
                        center(render_text(f"{action['Damage Displayed']}x{action['Hits']}",20,(205,205,205)),self.surface,i["Position"][0]+24,i["Position"][1]-184)
                    if action["Type"]=="Deal Damage And Block":
                        center(sword_icon,self.surface,i["Position"][0],i["Position"][1]-184)
                        center(shield_icon,self.surface,i["Position"][0]+40,i["Position"][1]-184)
                        center(render_text(action["Damage Displayed"],20,(205,205,205)),self.surface,i["Position"][0]+24,i["Position"][1]-184)
                        center(render_text(action["Block Displayed"],20,(205,205,205)),self.surface,i["Position"][0]+64,i["Position"][1]-184)
                if not i["Card"].parent.alive:
                    enemies_alive-=1
            if i["Card"].parent.alive:
                for II,ii in enumerate(i["Card"].parent.buffs):
                    center(dis_buff_icons[ii],self.surface,i["Position"][0]-100+II%11*33,i["Position"][1]+II//11*33+180)
                    center(render_text(str(i["Card"].parent.buffs[ii]),15,(255,0,0)),self.surface,i["Position"][0]-100+II%11*33+17,i["Position"][1]+II//11*37+10+180)
            
                if abs(self.mouse_pos[0]-i["Position"][0])<105 and abs(self.mouse_pos[1]-i["Position"][1])<160:
                    pygame.draw.rect(self.surface,(0,255,0),(i["Position"][0]-105,i["Position"][1]-160,210,320),3,15)
                    if self.click[2]:
                        self.open_GUIs["Inspecting Creature"]={
                            "Creature":i["Card"].parent,
                            "Timer":0,
                            "Space":i
                        }
        for GUI_type in self.open_GUIs:
            GUI=self.open_GUIs[GUI_type]
            if GUI_type=="Inspecting Creature":
                GUI["Timer"]+=delta/60 #should count seconds that have passed since it has started
                pygame.draw.rect(self.surface,(125,255,0),(GUI["Space"]["Position"][0]-105,GUI["Space"]["Position"][1]-160,210,320),3,15)
                tooltip_y=-200
                for ii in GUI["Creature"].buffs:
                    pygame.draw.rect(self.surface,(55,55,55),(GUI["Space"]["Position"][0]+105,GUI["Space"]["Position"][1]+tooltip_y,210,buff_tips[ii].get_height()+20),0,15)
                    pygame.draw.rect(self.surface,(105,105,105),(GUI["Space"]["Position"][0]+105,GUI["Space"]["Position"][1]+tooltip_y,210,buff_tips[ii].get_height()+20),3,15)
                    self.surface.blit(buff_tips[ii],(GUI["Space"]["Position"][0]+105,GUI["Space"]["Position"][1]+tooltip_y))
                    tooltip_y+= buff_tips[ii].get_height()+20                        
        if enemies_alive==0:
            return "Victory"
                #if i["Card"].parent.hp<0:
                #    self.dead_characters.append(i)
        #for i in self.dead_characters:
        #    self.locations["OnTable"].remove(i)
        
        for iterated_card_pile in self.card_piles: #Draws the top card of every card pile
            self.card_piles[iterated_card_pile].draw(self.surface)
        if self.hand!=None:
            self.hand.draw(self,delta=delta)
        
        #cooler cursor
        
        #pygame.draw.circle(self.surface,(255,255,255),self.mouse_pos,mc_size+3,2)

        #pygame.draw.rect(self.surface,(91,40,22),(90,860-self.energy*20,20,self.energy*20),3,10)
        if self.p_turn:
            for i in range(self.energy):
                center(large_energy_icon,self.surface,50+i*50,850)
            if button.display_button("end turn",bpc=(91,40,22),click=self.click,surface=self.surface,mouse_pos=self.mouse_pos,x=100,y=800) or self.keys[pygame.K_e]:
                self.end_turn()
        if button.display_button("Deck",bpc=(244,144,224),click=self.click,surface=self.surface,mouse_pos=self.mouse_pos,x=30,y=50) or self.keys[pygame.K_c]:
            self.display_deck(self.deck,screen)
        self.display_mouse_cursor()
    def display_mouse_cursor(self,surface=None):
        if surface==None:
            surface=self.surface
        mc_size=10-(min(self.mcctimer/6,1)/1)**2*8 #adding a smooth easing motion for more fun
        for i in range(6):
            r = abs(cos(self.time_passed / 40 + pi / 3 * i)) * 255
            g = abs(cos(self.time_passed / 40 + pi / 3 * i)) * 255
            b = abs(cos(self.time_passed / 40 + pi / 3 * i)) * 255
            pygame.draw.polygon(surface, (r, g, b), [
                (
                    self.mouse_pos[0] + cos(self.time_passed / 40 + 2 * pi / 6 * i) * mc_size,
                    self.mouse_pos[1] + sin(self.time_passed / 40 + 2 * pi / 6 * i) * mc_size,
                ),
                (
                    self.mouse_pos[0] + cos(self.time_passed / 40 + 2 * pi / 6 * i + pi / 20) * (mc_size + 5),
                    self.mouse_pos[1] + sin(self.time_passed / 40 + 2 * pi / 6 * i + pi / 20) * (mc_size + 5),
                ),
                (
                    self.mouse_pos[0] + cos(self.time_passed / 40 + 2 * pi / 6 * i) * (mc_size + 10),
                    self.mouse_pos[1] + sin(self.time_passed / 40 + 2 * pi / 6 * i) * (mc_size + 10),
                ),
                (
                    self.mouse_pos[0] + cos(self.time_passed / 40 + 2 * pi / 6 * i - pi / 20) * (mc_size + 5),
                    self.mouse_pos[1] + sin(self.time_passed / 40 + 2 * pi / 6 * i - pi / 20) * (mc_size + 5),
                )
            ])
    def update(self,delta): #Updates the board so that 
        self.time_passed+=delta
        self.mouse_rel=pygame.mouse.get_rel()
        self.mouse_down=pygame.mouse.get_pressed()
        self.mouse_pos=pygame.mouse.get_pos()
        self.r_mouse_pos=[self.mouse_pos[i]*self.mouse_pos_multiplier[i] for i in range(2)] #adjusts to the change in resolution
        self.mouse_pos=[self.r_mouse_pos[0]+self.camera_x,self.r_mouse_pos[1]+self.camera_y] #adds the position of camera to the mouse, allowing simple access. 
        if self.mouse_down[0] and self.drag_screen_allowed:
            self.camera_x-=self.mouse_rel[0]
            self.camera_y-=self.mouse_rel[1]
        self.ctimer=[(self.ctimer[i]+1)*self.mouse_down[i] for i in range(3)]
        self.click=[self.ctimer[i]==1 for i in range(3)]
        if self.mouse_down[0]:
            self.mcctimer=min(6,self.mcctimer+delta)
        else:
            if self.mcctimer>0:
                self.mcctimer-=delta
            else:
                self.mcctimer=0
        self.keys=pygame.key.get_pressed()
        self.mouse_scroll=0
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                exit()
            if event.type==pygame.MOUSEWHEEL:
                self.mouse_scroll=event.y
                #print(self.mouse_scroll)
    def add_card_to_game(self,plain_card_id,plain_card_type="Creature",prime=True,**kwargs): #Adds a new card to the game, returns the created card
        new_card=Card() 

        if plain_card_type=="Spell":
            new_object_manager=spell.Spell(plain_card_id)
            new_object_manager.card=new_card
            
            new_object_manager.draw("0") #Draws the new card at the start, so it is visible at all
            new_card.parent=new_object_manager #Also attributes the parent to whatever is locked inside the card
            new_card.spells["0"]=new_object_manager
            if "Extra Sides" in new_object_manager.data:
                for I,i in enumerate(new_object_manager.data["Extra Sides"]):
                    new_card.spells[str(I+1)]=spell.Spell(i)
                    new_card.spells[str(I+1)].card=new_card
                    new_card.spells[str(I+1)].draw(str(I+1))
                new_card.switch_trigger=new_object_manager.data["Switch Trigger"]
        elif plain_card_type=="Creature":
            new_object_manager=creature.Creature(plain_card_id,**kwargs)
            new_object_manager.board=self
            if new_object_manager.team==1:
                new_object_manager.enemy=self.player.parent
            new_object_manager.card=new_card
            new_object_manager.draw() #Draws the new card at the start, so it is visible at all
            new_card.parent=new_object_manager #Also attributes the parent to whatever is locked inside the card
        
        
        return new_object_manager.card
        

    def draw_a_card(self,from_pile="Deck"): #Takes a card from a deck, adds it to the hand, the animation engine itself figures out how to animate that
        if from_pile=="Deck":
            if len(self.card_piles[from_pile].cards)==0:
                if len(self.card_piles["Graveyard"].cards)>0:
                    for i in self.card_piles["Graveyard"].cards:
                        self.card_piles["Deck"].cards.append(i)
                    self.card_piles["Graveyard"].cards=[] 
                    self.shuffle_card_pile("Deck")
        if len(self.card_piles[from_pile].cards)>0:
            drawn_card=self.card_piles[from_pile].cards.pop(0)
            if len(self.hand.cards)<self.hand.max_cards:
                self.hand.cards.append(drawn_card)
                drawn_card.vector_space_element=Vector_Element()
                drawn_card.vector_space_element.setup(self.card_piles[from_pile].pos[0],self.card_piles[from_pile].pos[1])
                drawn_card.previous_leon=drawn_card.data["Side On Top"]
                if drawn_card.previous_leon=="Back":
                    drawn_card.previous_leon="0"
                drawn_card.iflip("Back")
                drawn_card.clear_animations()
                drawn_card.flip(40,drawn_card.previous_leon)
                drawn_card.draw()
            else:
                return "Full Hand"
        else:
            return "Empty Pile"
    def import_deck(self,json_deck_list=[],to_card_pile="Deck"): #Imports deck from a decklist
        self.deck=json_deck_list
        # Ideal decklist should be a list consisting of cards in the following format
        # {"Name":"CARD NAME","Type":"CARD TYPE"}
        # This doesn't shuffle the deck, so it has to be done manually
        if not to_card_pile in self.card_piles:
            self.setup_card_pile(to_card_pile)
        for iterated_card_packed in json_deck_list:
            new_card=self.add_card_to_game(iterated_card_packed["ID"],iterated_card_packed["Type"])
            self.card_piles[to_card_pile].cards.append(new_card)
            new_card.iflip("Back")
    def shuffle_card_pile(self,card_pile="Deck"):
        shuffle(self.card_piles[card_pile].cards)
    def check_for_target(self,locations=[]):
        #Currently this is somehow pretty fucking useless, i'll fix it once we add proper effect building
        possible_cards=[]
        #First finds all the cards, then removes all the ones that don't count.
        for iterated_card_pile in self.card_piles:
            possible_cards.extend(self.card_piles[iterated_card_pile].cards) 
        for i in self.locations:
            if not i in ["Board"]: #Custom Card Location
                if len(locations)>0:
                    if i in locations:
                        #print(i,locations)
                        for card in self.locations[i]["Cards"]:
                            possible_cards.append(card)
                    else:
                        continue
                else:
                    for card in i["Cards"]:
                        possible_cards.append(card)
            else:
                if len(locations)>0:
                    if "Board" in locations:
                        for space in self.locations[i]:
                            if space["Space"].card!=None:
                                possible_cards.append(space["Space"].card)

        #print(possible_cards)
        return possible_cards
    

       #Effect Building Starts Here
    #Warning: No Return after this

    #You are now entering the wastelands
    #Population: 5 of my braincells (currently)


    def play_a_card(self,card,target=None,prime=True):
        self.targets=target
        self.prime_caster=self.player.parent
        if "Target" in card.data:
            if card.data["Target"]=="Self":
                self.targets=[self.player.parent]
            if card.data["Target"]=="Single":
                self.targets=target
            if card.data["Target"]=="All Enemies":
                self.targets=[]
                for i in self.locations["OnTable"]:
                    if i["Side"]==2:
                        self.targets.append(i["Card"].parent)
                #print(self.targets[0].id)
        self.card_played=card
        
        if card.type=="Spell":
            self.caster=card
            if "Effects" in card.data:
                if "On Play" in card.data["Effects"]:
                    for effect in card.data["Effects"]["On Play"]:
                        self.run_effect(effect)
        if card.data["Type"]=="Power":
            self.prime_caster.powers.append(card)
            card.exhausted=True
        if "Attributes" in card.data:
            if "Exhaust" in card.data["Attributes"]:
                card.exhausted=True 

        
        
    def run_effect(self,effect):
        print(self.targets[0].id,effect)
        #print(effect)
        #Basic card effects
        if effect["Type"]=="Draw Cards":
            for i in range(effect["Cards Drawn"]):
                self.draw_a_card()
        if effect["Type"]=="Gain Block":
            o_block=effect["Block"]
            if type(o_block)==dict:
                if "Variable" in o_block:
                    new_o_block=self.prime_caster.variables[o_block["Variable"]]
                o_block=new_o_block
            
            if "Dexterity" in self.prime_caster.buffs:
                o_block+=self.prime_caster.buffs["Dexterity"]
            print(o_block)
            for i in self.targets:
                i.block+=o_block
                i.draw()
        if effect["Type"]=="Deal Damage":
            o_damage=effect["Damage"]
            if type(o_damage)==dict:
                if "Variable" in o_damage:
                    new_o_damage=self.prime_caster.variables[o_damage["Variable"]]
                o_damage=new_o_damage
            if "Strength" in self.prime_caster.buffs:
                o_damage+=self.prime_caster.buffs["Strength"]
            for i in self.targets:
                s_damage=o_damage
                if "Vulnerable" in i.buffs:
                    s_damage=int(s_damage*1.5)
                data=i.take_damage(s_damage)
                if data[0]: #damage was unblocked
                    self.p_targets=self.targets.copy()
                    self.targets=[i]
                    self.check_for_powers("Deal Unblocked Damage")
                    self.targets=self.p_targets.copy()
        if effect["Type"]=="Apply Buff":
            for ii in self.targets:
                for i in effect["Buffs"]:
                    if not i["Type"] in ii.buffs:
                        ii.buffs[i["Type"]]=0
                    
                    if type(i["Value"])==dict:
                        added_value=self.prime_caster.variables[i["Value"]["Variable"]]
                    else:
                        added_value=i["Value"]
                    
                    if "Conduit" in ii.buffs and i["Type"] in conduit_buffs:
                        if added_value<0:
                            added_value+=-ii.buffs["Conduit"]
                        else:
                            added_value+=ii.buffs["Conduit"]
                    if i["Type"]=="Hot" and "Cold" in ii.buffs:
                        ii.buffs["Cold"]-=added_value
                        if ii.buffs["Cold"]<0:
                            ii.buffs["Hot"]=-ii.buffs["Cold"]
                        elif ii.buffs["Cold"]==0:
                            del ii.buffs["Hot"]
                        if ii.buffs["Cold"]<=0:
                            del ii.buffs["Cold"]
                    elif i["Type"]=="Cold" and "Hot" in ii.buffs:
                        ii.buffs["Hot"]-=added_value
                        if ii.buffs["Hot"]<0:
                            print(ii.buffs["Hot"],ii.buffs["Cold"])
                            ii.buffs["Cold"]=-ii.buffs["Hot"]
                        elif ii.buffs["Hot"]==0:
                            del ii.buffs["Cold"]
                        if ii.buffs["Hot"]<=0:
                            del ii.buffs["Hot"]
                    
                    else:
                        ii.buffs[i["Type"]]+=added_value
        if effect["Type"]=="Gain Energy":
            self.energy+=effect["Energy"]
        
        if effect["Type"]=="Give HP":
            
            for target in self.targets:
                target.max_hp+=effect["HP"]
                target.hp+=effect["HP"]


        #Logic Elements
        if effect["Type"]=="Multiple Effects":
            for i in effect["Effects"]:
                self.run_effect(i)
        
        if effect["Type"]=="Modify Global Variable":
            if not effect["Name"] in self.data:
                self.data[effect["Name"]]=0
            if effect["Operation"]=="+":
                self.data[effect["Name"]]+=effect["Value"]
            if effect["Operation"]=="-":
                self.data[effect["Name"]]-=effect["Value"]
            if effect["Operation"]=="*":
                self.data[effect["Name"]]*=effect["Value"]
                self.data[effect["Name"]]=round(self.data[effect["Name"]],2)
            if effect["Operation"]=="/":
                self.data[effect["Name"]]/=effect["Value"]
                self.data[effect["Name"]]=round(self.data[effect["Name"]],2)
        
        if effect["Type"]=="Set Target":
            self.targets=[]
            if effect["Target"]=="Self":
                self.targets=[self.player.parent]
            if effect["Target"]=="All Enemies":
                for i in self.locations["OnTable"]:
                    if i["Side"]==2:
                        self.targets.append(i["Card"].parent)
        
        if effect["Type"]=="Assign Variable": #TODO: Make this better, more accessible, and usable. 
            if effect["Select"]=="Property":
                if "Target" in effect:
                    target=self.get_targets(effect["Target"])[0]
                else:
                    target=self.targets[0]
                if effect["Property"]=="Block":
                    self.prime_caster.variables[effect["Variable"]]=target.block
                elif effect["Property"]=="Buff":
                    if effect["Buff"] in target.buffs:
                        self.prime_caster.variables[effect["Variable"]]=target.buffs[effect["Buff"]]
                    else:
                        self.prime_caster.variables[effect["Variable"]]=0
        
        if effect["Type"]=="If":
            if effect["Property 1"]=="Variable":
                challenger=self.prime_caster.variables[effect["Variable 1"]]
            if effect["Against"]=="Int":
                is_valid=False
                if effect["Sign"]==">":
                    if challenger>effect["Int"]: is_valid=True
                if effect["Sign"]==">=":
                    if challenger>=effect["Int"]: is_valid=True
                if effect["Sign"]=="=":
                    if challenger==effect["Int"]: is_valid=True
                if effect["Sign"]=="<":
                    if challenger<effect["Int"]: is_valid=True
                if effect["Sign"]=="<=":
                    if challenger<=effect["Int"]: is_valid=True
                
                if is_valid:
                    for new_effect in effect["Then"]:
                        self.run_effect(new_effect)
        
        #Card Elements
        if effect["Type"]=="Flip Self":
            self.card_played.card.flip_action("Exhaust")
        if effect["Type"]=="Flip To Side":
            self.card_played.card.flip_action("Forced",effect["Side"])
        
    def get_targets(self,targeting="Self"):
        if type(targeting)==str:
            if targeting=="Self":
                return [self.prime_caster]
    def turn_start(self):
        self.energy=self.data["Energy Per Turn"]
        self.p_turn=True
        
        self.player.parent.minus_block=self.player.parent.block
        for i in self.locations["OnTable"]:
            i["Card"].parent.turn_start()
        for i in range(self.data["Cards Drawn Per Turn"]):
            self.draw_a_card()
        
        #handles adaptations
        for i in self.player.parent.powers:
            if "Start Of Turn" in i.data["Effects"]:
                self.targets=[self.player.parent]
                for effect in i.data["Effects"]["Start Of Turn"]:
                    
                    self.run_effect(effect)
                self.npc_cache.append({
                    "Type":"Wait",
                    "Time Left":0.1
                })
            elif "Permanent" in i.data["Effects"]:
                if i.data["Effects"]["Permanent"]=="barricade":
                    self.player.parent.minus_block-=self.player.parent.block
        self.player.parent.block-=self.player.parent.minus_block
        self.player.parent.draw()
    def check_for_powers(self,which_type):
        for i in self.player.parent.powers:
            if which_type in i.data["Effects"]:
                if which_type not in ["Deal Unblocked Damage"]:
                    self.targets=[self.player.parent]
                for effect in i.data["Effects"][which_type]:
                    self.run_effect(effect)
                self.npc_cache.append({
                    "Type":"Wait",
                    "Time Left":0.1
                })

    def end_turn(self):
        self.p_turn=False
        for i in self.hand.cards:
            if "Attributes" in i.parent.data:
                if "Forced" in i.parent.data["Attributes"]:
                    self.targets=[i.parent]
                    self.play_a_card(i.parent)
            self.card_piles["Graveyard"].cards.append(i)
        self.hand.cards=[]
        self.check_for_powers("End Of Turn")
        for i in self.locations["OnTable"]:
            i["Card"].parent.turn_end()
            if i["Side"]==2:
                self.npc_cache.append({
                    "Type":"Wait",
                    "Time Left":0.4
                })
                self.npc_cache.append({
                    "Type":"Action Animation",
                    "Action Completed":False,
                    "Target":i,
                    "Time Elapsed":0
                })
    def update_enemy_actions(self):
        for i in self.locations["OnTable"]:
            if i["Side"]==2:
                i["Card"].parent.update_action()
    def display_deck(self,deck,surface):
        cards_in_deck=[self.add_card_to_game(i["ID"],"Spell") for i in deck]
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    exit()
            self.update(1)
            self.surface.fill((15,15,15))
            for I,i in enumerate(cards_in_deck):
                x_pos=I%6*220+(1920-1100)/2
                y_pos=I//6*330+10
                i.draw()
                self.surface.blit(i.sprite,(x_pos,y_pos))
            if button.display_button("Back",bpc=(244,44,24),click=self.click,surface=self.surface,mouse_pos=self.mouse_pos,x=30,y=50):
                return None
            mc_size=10-(min(self.mcctimer/6,1)/1)**2*8 #adding a smooth easing motion for more fun
            for i in range(6):
                r = abs(cos(self.time_passed / 40 + pi / 3 * i)) * 255
                g = abs(cos(self.time_passed / 40 + pi / 3 * i)) * 255
                b = abs(cos(self.time_passed / 40 + pi / 3 * i)) * 255
                pygame.draw.polygon(self.surface, (r, g, b), [
                    (
                        self.mouse_pos[0] + cos(self.time_passed / 40 + 2 * pi / 6 * i) * mc_size,
                        self.mouse_pos[1] + sin(self.time_passed / 40 + 2 * pi / 6 * i) * mc_size,
                    ),
                    (
                        self.mouse_pos[0] + cos(self.time_passed / 40 + 2 * pi / 6 * i + pi / 20) * (mc_size + 5),
                        self.mouse_pos[1] + sin(self.time_passed / 40 + 2 * pi / 6 * i + pi / 20) * (mc_size + 5),
                    ),
                    (
                        self.mouse_pos[0] + cos(self.time_passed / 40 + 2 * pi / 6 * i) * (mc_size + 10),
                        self.mouse_pos[1] + sin(self.time_passed / 40 + 2 * pi / 6 * i) * (mc_size + 10),
                    ),
                    (
                        self.mouse_pos[0] + cos(self.time_passed / 40 + 2 * pi / 6 * i - pi / 20) * (mc_size + 5),
                        self.mouse_pos[1] + sin(self.time_passed / 40 + 2 * pi / 6 * i - pi / 20) * (mc_size + 5),
                    )
                ])
            surface.blit(pygame.transform.scale(self.surface,surface.get_size()),(0,0))

            pygame.display.update()