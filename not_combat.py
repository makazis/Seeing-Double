from Engine.board import *
from Engine.card import *
from Engine.button import *
from Engine.spell import *
import pygame

card_pools=[
    [] for i in range(3) #By Rarity
]
for i in spell_data:
    th=spell_data[i]
    if not "Not In Pool" in th:
        card_pools[rarities.index(th["Rarity"])].append(i)
def not_combat(surface,parent,save_data):
    win=pygame.Surface((1920,1080))
    nc_menu_is_running=True
    screen_width = surface.get_width()
    screen_height = surface.get_height()
    menu_board=Board((screen_width,screen_height))
    clock=pygame.time.Clock()
    menu="Main"
    card_selection=CardReward(3,parent)
    card_is_selected=False
    while nc_menu_is_running:
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
        win.fill((15,15,15))
        menu_board.update(dt)

        if menu=="Main":
            center(render_text(f"HP:{parent.player_hp} + {parent.player_hp_healed}",30,(255,125,0),font="Consolas"),win,260,50)
            center(render_text(f"Floor:{parent.floor}",30,(255,125,0),font="Consolas"),win,260,80)


            if display_button(surface=win,mouse_pos=menu_board.mouse_pos,click=menu_board.click,
                          x=1800,y=1000,text="Leave",size=20,bpc=(255,55,55)):
                nc_menu_is_running=False
            if not card_is_selected:
                if display_button(surface=win,mouse_pos=menu_board.mouse_pos,click=menu_board.click,
                            x=1750,y=100,text="Choose A Card",size=20,bpc=(255,255,55)):
                    menu="Card Selection"
        if menu=="Card Selection":
            center(render_text("Choose 1 of these cards",30,font="Consolas"),win,960,50)
            for I,i in enumerate(card_selection.cards):
                I-=1
                i["DC"].draw()
                center(i["DC"].sprite,win,960+I*480,250)
                if abs(960+I*480-menu_board.mouse_pos[0])<105:
                    if abs(250-menu_board.mouse_pos[1])<160:
                        pygame.draw.rect(win,(255,255,0),(960+I*480-110,250-165,220,330),3,15)
                        
                        if menu_board.click[0]:
                            card_is_selected=True
                            parent.deck.append(i)
                            if parent.floor<7:
                                parent.early_picked_cards.append(i["ID"])
                            elif parent.floor<17:
                                parent.middle_picked_cards.append(i["ID"])
                            else:
                                parent.late_picked_cards.append(i["ID"])
                            menu="Main"
                        if menu_board.click[2]:
                            i["DC"].flip_action()
            if display_button(surface=win,mouse_pos=menu_board.mouse_pos,click=menu_board.click,
                          x=960,y=500,text="Skip",size=20,bpc=(255,55,55)):
                menu="Main"
        mc_size=10-(min(menu_board.mcctimer/6,1)/1)**2*8
        for i in range(6):
                r = abs(cos(menu_board.time_passed / 40 + pi / 3 * i)) * 255
                g = abs(cos(menu_board.time_passed / 40 + pi / 3 * i)) * 255
                b = abs(cos(menu_board.time_passed / 40 + pi / 3 * i)) * 255
                pygame.draw.polygon(win, (r, g, b), [
                    (
                        menu_board.mouse_pos[0] + cos(menu_board.time_passed / 40 + 2 * pi / 6 * i) * mc_size,
                        menu_board.mouse_pos[1] + sin(menu_board.time_passed / 40 + 2 * pi / 6 * i) * mc_size,
                    ),
                    (
                        menu_board.mouse_pos[0] + cos(menu_board.time_passed / 40 + 2 * pi / 6 * i + pi / 20) * (mc_size + 5),
                        menu_board.mouse_pos[1] + sin(menu_board.time_passed / 40 + 2 * pi / 6 * i + pi / 20) * (mc_size + 5),
                    ),
                    (
                        menu_board.mouse_pos[0] + cos(menu_board.time_passed / 40 + 2 * pi / 6 * i) * (mc_size + 10),
                        menu_board.mouse_pos[1] + sin(menu_board.time_passed / 40 + 2 * pi / 6 * i) * (mc_size + 10),
                    ),
                    (
                        menu_board.mouse_pos[0] + cos(menu_board.time_passed / 40 + 2 * pi / 6 * i - pi / 20) * (mc_size + 5),
                        menu_board.mouse_pos[1] + sin(menu_board.time_passed / 40 + 2 * pi / 6 * i - pi / 20) * (mc_size + 5),
                    )
                ])
        surface.blit(pygame.transform.scale(win,surface.get_size()),(0,0))
        pygame.display.update()
    parent.player_hp+=parent.player_hp_healed
class CardReward:
    def __init__(self,cards=3,parent=None):
        self.cards=[]
        for i in range(cards):
            card_isnt_selected=True
            while card_isnt_selected:
                rarity_1=choices([i for i in range(len(rarities))],parent.rarity_weights)[0]
                if len(card_pools[rarity_1])>0:
                    card_1=choice(card_pools[rarity_1])
                    card_isnt_selected=False
            p_card_1=card_1
            card_1_manager=Spell(card_1)
            card_1=Card()
            card_1.spells["0"]=card_1_manager
            card_1_manager.card=card_1
            card_1.parent=card_1_manager
            card_1_manager.draw("0")
            card_1.draw()
            if "Extra Sides" in card_1_manager.data:
                for I,i in enumerate(card_1_manager.data["Extra Sides"]):
                    card_1.spells[str(I+1)]=spell.Spell(i)
                    card_1.spells[str(I+1)].card=card_1
                    card_1.spells[str(I+1)].draw(str(I+1))
                card_1.switch_trigger=card_1_manager.data["Switch Trigger"]
            self.cards.append({
                "Type":"Spell",
                "ID":p_card_1,
                "DC":card_1
            })