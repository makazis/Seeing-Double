import Engine.board
from Engine.button import *
from Engine.spell import spell_data
import pygame
import json
from random import *
import math


import useful_stuff

def combat(surface,parent,save_data):
    lost=False
    #This is used whenever the code is in debug mode
    debugMode=False
    debug_menu_shows_card_library=False #A debug mode, will be added later.
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
    for i,_i in enumerate(parent.room.enemies):
        new_enemy_card=_board.add_card_to_game(_i,"Creature",team=1)
        _board.locations["OnTable"].append({
        "Card":new_enemy_card,
        "Position":[800+i%4*300,300+350*i//4],
        "Side":2
    })
    _board.shuffle_card_pile("Deck")
    #for i in range(5):
    #    _board.draw_a_card()
    #_board.turn_start()
    clock=pygame.time.Clock()
    if is_debugging:         
        dm_1_y=0
        debug_menu_1_library=[_board.add_card_to_game(i,"Spell") for i in spell_data]
        for i in debug_menu_1_library:
            i.iflip("0")
            i.draw()
    while combat_menu_is_running:
        clock.tick()
        dt=clock.get_fps()
        if dt==0:
            dt=1
        dt=60/dt
        dt=min(dt,4) #limits at 15 fps, then breaks if game runs slower. This is a feature, not a bug, trust
        for event in _board.update(dt):
            if event.type == pygame.KEYDOWN and is_debugging:
                if event.key == pygame.K_F7:
                    debugMode = not debugMode
                if event.key == pygame.K_F1:
                    debug_menu_shows_card_library = not debug_menu_shows_card_library
                    dm_1_y=0 
        
        response=_board.draw(dt,surface)
        if response=="Game Over":
            combat_menu_is_running=False
            lost=True
        elif response=="Victory":
            combat_menu_is_running=False
            lost=False
        if debug_menu_shows_card_library:
            for I,i in enumerate(debug_menu_1_library):
                x_pos=I%7*220+960-660
                y_pos=I//7*330-dm_1_y+180
                center(i.sprite,_board.surface,x_pos,y_pos)
                if abs(_board.mouse_pos[0]-x_pos)<105 and abs(_board.mouse_pos[1]-y_pos)<160:
                    pygame.draw.rect(_board.surface,(255,255,0),(x_pos-105,y_pos-160,210,320),3,15)
                    if _board.click[0]:
                        _board.hand.cards.append(i)
                        debug_menu_shows_card_library=False
            if _board.mouse_scroll>0:
                dm_1_y-=100
                dm_1_y=max(0,dm_1_y)
            elif _board.mouse_scroll<0:
                dm_1_y+=100

        surface.blit(pygame.transform.scale(_board.surface,(screen_width,screen_height)),(0,0))

        if debugMode:
            useful_stuff.draw_fps_counter(surface, clock)
            if _board.keys[pygame.K_1]:
                combat_menu_is_running=False
            surface.blit(useful_stuff.render_text(f"dt:  {round(dt,2)}",30,(255,255,0),"comicsansms"),(0,30))
        
        pygame.display.flip()
    parent.player_hp=pcard_1.parent.hp
    #for i in _board.locations["OnTable"]:
    #    if i["Side"]==2:
    #        parent.enemy_effects.append((i["Card"].parent.data["Animations"][0]["Sprite Path"],i["Card"].parent.data["Gift"],i["Card"].parent.data["Gift Chance"]))
    return lost
#combat(screen)
