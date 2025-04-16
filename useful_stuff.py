from random import *
from math import *
import pygame
def center(sprite,surface,x,y): #Centers a sprite on specific coordinates
   # print(sprite.get_width(),x)
    surface.blit(sprite,(x-sprite.get_width()/2,y-sprite.get_height()/2))
fonts={}
texts={}
def draw_fps_counter(screen,clock,font="comicsansms",size=20,color=(255,255,255),bold=False,italic=False): #Draws the fps counter
    fps=round(clock.get_fps())
    screen.blit(render_text("FPS: "+str(fps),size=size,color=color,font=font,bold=bold,italic=italic),(0,0))

def render_text(text="TEXT NOT PROVIDED",size=20,color=(255,255,255),font="comicsansms",bold=False,italic=False,antial=True): #allows you to render text fast
    font_key=str(font)+str(size)
    text_key=str(font_key)+str(text)+str(color)+str(int(antial))
    if not font_key in fonts:
        try:
            fonts[font_key]=pygame.font.SysFont(font,int(size)) #Tries to load the file from the system
        except: #If that doesn't work
            try:
                fonts[font_key]=pygame.font.Font(font,int(size)) #Tries to load the font from a specified path, Don't do italic or bold unless very neccessary, bc pygame might do some strange stuff
            except:
                fonts[font_key]=pygame.font.SysFont("comicsansms",int(size))

    if not text_key in texts:
        texts[text_key]=fonts[font_key].render(str(text),antial,color)
    return texts[text_key]
class Vector_Element:
    def __init__(self,dimensions=2): #Might extend this later into higher dimensions, but, for now, there is no reason to
        self.dimensions=dimensions
        self.set_up=False
    def setup(self,x,y,rotation=0):
        self.x=x
        self.y=y
        self.rotation=rotation
        self.vectors=[]
        self.set_up=True
    def move_with_easing_motion_to(self,destination_x,destination_y, easing_rate=20,destination_rotation=0,delta=1): #Higher easing rate means slower easing
        easing_rate/=delta
        self.x=(self.x*(easing_rate-1)+destination_x)/easing_rate
        self.y=(self.y*(easing_rate-1)+destination_y)/easing_rate
        self.rotation=(self.rotation*(easing_rate-1)+destination_rotation)/easing_rate
card_transparency_overlay=pygame.Surface((210,320))
card_transparency_overlay.set_colorkey((255,255,255))
card_transparency_color=(234,23,4)
card_transparency_overlay.fill((card_transparency_color))
pygame.draw.rect(card_transparency_overlay,(255,255,255),(0,0,210,320),0,15)

icon_sheet=pygame.image.load("Resources/Icons/Free - Raven Fantasy Icons/Full Spritesheet/32x32.png")
sword_icon=icon_sheet.subsurface((32*6,32*45,32,32))
buff_icon=icon_sheet.subsurface((32*7,32*67,32,32))
debuff_icon=icon_sheet.subsurface((32*6,32*45,32,32))
small_energy_icon=icon_sheet.subsurface((32*15,32*42,32,32))
large_energy_icon=pygame.transform.scale_by(small_energy_icon,3)
mid_energy_icon=pygame.transform.scale_by(small_energy_icon,2)
strength_icon=icon_sheet.subsurface((0,32*41,32,32))
shield_icon=icon_sheet.subsurface((32*7,32*41,32,32))
buff_icons={
    "Strength":strength_icon,
    "Vulnerable":icon_sheet.subsurface((32*12,32*53,32,32)),
    "Dexterity":icon_sheet.subsurface((32*8,32*41,32,32)),
    "Conduit":icon_sheet.subsurface((32*3,32*37,32,32)),
    "Poison":icon_sheet.subsurface((32*8,32*50,32,32)),
    "Weak":icon_sheet.subsurface((32*1,32*108,32,32)),
    "Energy":mid_energy_icon.subsurface((16,16,32,32)),
    "Antivenom":pygame.transform.scale_by(icon_sheet.subsurface((32*4,32*44,32,32)),1.5).subsurface((8,8,32,32)),
    "Immune":icon_sheet.subsurface((32*11,32*67,32,32)),
    "Hot":icon_sheet.subsurface((0,32*62,32,32)),
    "Cold":icon_sheet.subsurface((0,32*63,32,32)),
    
}
small_buff_icons={
    i:pygame.transform.scale(buff_icons[i],(16,16)) for i in buff_icons
}
dis_buff_icons={
    i:pygame.transform.scale(buff_icons[i],(24,24)) for i in buff_icons
}
map_icons={
    "Enemy":icon_sheet.subsurface((32*13,32*53,32,32)),
    "Elite":icon_sheet.subsurface((32*15,32*53,32,32)),
    "Shop":icon_sheet.subsurface((0,0,32,32)),
    "Unknown":icon_sheet.subsurface((12*32,0,32,32)),
    "Rest":icon_sheet.subsurface((6*32,32,32,32)),
    "Miniboss":pygame.image.load("Resources/Icons/Miniboss.png")
}

map_icons={
    i:pygame.transform.scale(map_icons[i],(64,64)) for i in map_icons
}
#pygame.image.save(buff_icons["Weakness"],"sword_test.png")

speeds=[0.5,1,2,4]
str_speeds=["Slow","Normal","Quick","Zoom"]

rarities=["Common", "Uncommon", "Rare","Cursed"]
rarity_weights=[140,50,10,1]
#We do 5 common cards for each synergy, 3 uncommon and 1 rare
#and we make 10 neutral cards
#The mayor synnergies should be:
# Strength Build (low cost attacks, strength gain, cheap card draw)
# Defense Build (same as before, but add barricade, block doubler and deal damage equal to block)
# Conduit Build (Conduit will increase the ammount of how much more buff you get per each buff applied to you) this makes 37 total cards, should be good for now

helpfull_buffs=["Strength"] #Conduit isn't here, so it doesn't buff itself
temporal_buffs=["Conduit","Vulnerable","Weak","Poison","Antivenom","Immune","Hot","Cold"] #every turn they lose 1 charge
conduit_buffs=["Strength","Dexterity","Poison","Vulnerable","Antivenom","Hot","Cold"]
ba_frames={} #ported here for accessibility between combats


clock=pygame.time.Clock()
dt=1
def calculate_dt():
    global dt
    clock.tick()
    dt=clock.get_fps()
    if dt==0:
        dt=1
    dt=60/dt
    dt=min(dt,4)