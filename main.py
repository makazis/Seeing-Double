import Engine.board
from Engine.button import *
import pygame
import json
import pygame
from combat import *
from run import Run
pygame.init()

# Set up the display
screen = pygame.display.set_mode((0 , 0),pygame.FULLSCREEN)
screen_width = screen.get_width()
screen_height = screen.get_height()
pygame.mouse.set_visible(False)

win=pygame.Surface((1920,1080))
menu_board=Engine.board.Board((screen_width,screen_height))
run=True
clock=pygame.time.Clock()
menu="First"

with open("Resources/save/save.json","r") as f:
    save_data=json.loads(f.read())
    option_prefferences=save_data["Settings Prefferences"]
def save_options_prefferences():
    with open("Resources/save/save.json","w") as f:
        f.write(json.dumps(save_data,indent=2))

while run:
    clock.tick()
    dt=clock.get_fps()
    if dt==0:
        dt=1
    dt=60/dt
    dt=min(dt,4) #limits at 15 fps, then breaks if game runs slower. This is a feature, not a bug, trust
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
    menu_board.update(dt)
    win.fill((25,25,25))
    if menu=="First":
        center(render_text("Seeing Double",40,(255,255,255),"Consolas"),win,960,100)
        if display_button(surface=win,mouse_pos=menu_board.mouse_pos,click=menu_board.click,
                          x=960,y=340,text="Play",size=30,bpc=(255,255,255)):
            new_run=Run(screen,save_data)
            if new_run.victory:
                menu="Victory"
            else:
                menu="Loss"
        if display_button(surface=win,mouse_pos=menu_board.mouse_pos,click=menu_board.click,
                          x=960,y=460,text="Settings",size=30,bpc=(255,255,55)):
            menu="Settings"
        if display_button(surface=win,mouse_pos=menu_board.mouse_pos,click=menu_board.click,
                          x=960,y=580,text="Quit",size=30,bpc=(55,255,255)):
            run=False
    elif menu=="Settings":
        center(render_text("Choose Game Speed",30,(255,255,255),"Consolas"),win,230,100)
        center(render_text(f"Current Game Speed:{str_speeds[option_prefferences['Game Speed']]}",30,(255,255,255),"Consolas"),win,230,140)
        
        for i in range(4):
            
            if display_button(surface=win,mouse_pos=menu_board.mouse_pos,click=menu_board.click,
                          x=230,y=190+i*50,text=str_speeds[i],size=20,bpc=(55,155,255)):
                option_prefferences['Game Speed']=i
                save_options_prefferences()
        if display_button(surface=win,mouse_pos=menu_board.mouse_pos,click=menu_board.click,
                          x=100,y=860,text="Back",size=30,bpc=(255,55,55)):
            menu="First"
        center(render_text("Bad Apple Mode",30,(255,255,255),"Consolas"),win,530,100)
        center(render_text("Requires a beefy computer",30,(255,255,255),"Consolas"),win,530,60)
        
        if option_prefferences["Bad Apple"]:
            if display_button(surface=win,mouse_pos=menu_board.mouse_pos,click=menu_board.click,
                          x=530,y=200,text="Disable",size=30,bpc=(255,55,55)):
                option_prefferences["Bad Apple"]=False
        else:
            if display_button(surface=win,mouse_pos=menu_board.mouse_pos,click=menu_board.click,
                          x=530,y=200,text="Enable",size=30,bpc=(55,255,55)):
                option_prefferences["Bad Apple"]=True
        save_options_prefferences()
    elif menu=="Victory":
        center(render_text("You win! this is the end of the game.",40,(255,255,255),"Consolas"),win,960,100)
        if display_button(surface=win,mouse_pos=menu_board.mouse_pos,click=menu_board.click,
                          x=960,y=340,text="Main Menu",size=30,bpc=(255,255,255)):
            menu="First"
    elif menu=="Loss":
        center(render_text("You lost! this is the end of the game.",40,(255,255,255),"Consolas"),win,960,100)
        if display_button(surface=win,mouse_pos=menu_board.mouse_pos,click=menu_board.click,
                          x=960,y=340,text="Main Menu",size=30,bpc=(255,255,255)):
            menu="First"
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
    screen.blit(pygame.transform.scale(win,screen.get_size()),(0,0))
    pygame.display.update()
pygame.quit()