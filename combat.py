import Engine.board
from Engine.button import *
import pygame
import json
from random import *
import math


import useful_stuff

def combat(surface,parent,save_data):
    lost=False
    debugMode=False
    screen_width = surface.get_width()
    screen_height = surface.get_height()
    combat_menu_is_running=True
    
    _board=Engine.board.Board((screen_width,screen_height))
    _board.game_speed=speeds[save_data["Settings Prefferences"]['Game Speed']]
    _board.bad_apple=save_data["Settings Prefferences"]['Bad Apple']
    
    _board.setup_card_pile("Deck",(1867,1000),(105,160))
    _board.setup_card_pile("Graveyard",(53,1000),(105,160))
    _board.setup_hand()
    
    _board.hand.pos=[960,900]
    _board.import_deck(parent.deck)
    pcard_1=_board.add_card_to_game("Warrior","Creature",team=0)
    pcard_1.parent.hp=parent.player_hp
    _board.locations["OnTable"].append({
        "Card":pcard_1,
        "Position":[200,300],
        "Side":0
    })
    _board.player=pcard_1
    for i in range(min(8,int(parent.floor**0.35))):
        new_enemy_card=_board.add_card_to_game("butterfly_"+str(randint(1,6)),"Creature",team=1)
        _board.locations["OnTable"].append({
        "Card":new_enemy_card,
        "Position":[800+i%4*300,300+350*i//4],
        "Side":2
    })
        for ii in parent.enemy_effects:
            if random()<0.5: #the effect activates
                _board.npc_cache.append({
                    "Type":"Wait",
                    "Time Left":0.4
                })
                _board.npc_cache.append({
                    "Type":"Butterfly Blessing",
                    "Effect":ii[1],
                    "Target":new_enemy_card
                })
    _board.shuffle_card_pile("Deck")
    #for i in range(5):
    #    _board.draw_a_card()
    #_board.turn_start()
    clock=pygame.time.Clock()
    while combat_menu_is_running:
        clock.tick()
        dt=clock.get_fps()
        if dt==0:
            dt=1
        dt=60/dt
        dt=min(dt,4) #limits at 15 fps, then breaks if game runs slower. This is a feature, not a bug, trust
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                exit()
            #if event.type==pygame.MOUSEBUTTONDOWN:
            #    if event.button==3:
            #        if _board.locations["Hand"]["Card Rendered On Top"]:
            #            _board.locations["Hand"]["Card Rendered On Top"].flip(50)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F7:
                    debugMode = not debugMode
                
        _board.update(dt)
        response=_board.draw(dt,surface)
        if response=="Game Over":
            combat_menu_is_running=False
            lost=True
        elif response=="Victory":
            combat_menu_is_running=False
            lost=False
        surface.blit(pygame.transform.scale(_board.surface,(screen_width,screen_height)),(0,0))

        if debugMode:
            useful_stuff.draw_fps_counter(surface, clock)
            surface.blit(useful_stuff.render_text(f"dt:  {round(dt,2)}",30,(255,255,0),"comicsansms"),(0,30))
        pygame.display.flip()
    parent.player_hp=pcard_1.parent.hp
    for i in _board.locations["OnTable"]:
        if i["Side"]==2:
            parent.enemy_effects.append((i["Card"].parent.data["Animations"][0]["Sprite Path"],i["Card"].parent.data["Gift"],i["Card"].parent.data["Gift Chance"]))
    return lost
#combat(screen)
