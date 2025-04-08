import pygame
from math import  sqrt
from useful_stuff import *
class Button:
    def __init__(self,text="",size=20,bpc=(255,255,255),font="comicsansms",bold=False,italic=False,size2=1,border_width=3,border_radius=4,mouse_on_effect=0):
        self.text=text
        avgbpc=(bpc[0]+bpc[1]+bpc[2])/3
        sdbpc=sqrt(sum([(avgbpc-bpc[i])**2 for i in range(3)])/3)
        if sdbpc+avgbpc>=64: # Light Button Palette
            self.colors=[
                1, #Base Color
                0.5, #Text Color
                0.6, #Lower Border Color
                1.3, #Upper Border Color
            ]
        else: #Dark Color Palette
            self.colors=[
                1, #Base Color
                4, #Text Color
                1.6, #Lower Border Color
                0.9, #Upper Border Color
            ]
        self.mouse_on_effect=mouse_on_effect
        self.colors=[[min(255,max(1,bpc[i1]*i)) for i1 in range(3)] for i in self.colors]
        size2*=2
        self.text_sprite=render_text(text,size,self.colors[1],font=font,italic=italic,bold=bold)
        self.s=(self.text_sprite.get_width()*size2,self.text_sprite.get_height()*size2)
        self.sprite=pygame.Surface(self.s)
        self.sprite.set_colorkey((0,0,0))
        pygame.draw.rect(self.sprite,self.colors[3],(0,0,self.s[0],self.s[1]*0.8),0,border_top_left_radius=border_radius,border_top_right_radius=border_radius)
        pygame.draw.rect(self.sprite,self.colors[2],(0,self.s[1]*0.8,self.s[0],self.s[1]*0.2),0,border_bottom_left_radius=border_radius,border_bottom_right_radius=border_radius)
        pygame.draw.rect(self.sprite,self.colors[2],(self.s[0]*0.5,self.s[1]*0.2,self.s[0]*0.5,self.s[1]*0.6),0)
        pygame.draw.rect(self.sprite,self.colors[0],(border_width,border_width,self.s[0]-border_width*2,self.s[1]-border_width*2),0,border_width)
        center(self.text_sprite,self.sprite,self.s[0]/2,self.s[1]/2)
        self.size_q=1
        if self.mouse_on_effect==0:
            self.size_q=1
            self.size_easing=0
    def display(self,surface,x,y,mouse_pos,click):
        official_return=False
        if abs(mouse_pos[0]-x)<self.s[0]/2*self.size_q and abs(mouse_pos[1]-y)<self.s[1]/2*self.size_q:
            self.mouse_over=True
            if click[0]:
                official_return=True
        else:
            self.mouse_over=False
        if self.mouse_on_effect==0:
            center(pygame.transform.scale(self.sprite,(self.s[0]*self.size_q,self.s[1]*self.size_q)),surface,x,y)
            if self.mouse_over and self.size_easing<=4:
                self.size_easing+=1
                self.size_q-=self.size_easing/100
            elif self.size_easing>0 and not self.mouse_over:
                self.size_q+=self.size_easing/100
                self.size_easing-=1
        else:
            center(self.sprite,surface,x,y)
        return official_return
buttons={}
def display_button(text="",size=20,bpc=(255,255,255),font="Consolas",bold=False,italic=False,size2=1,border_width=3,border_radius=4,mouse_on_effect=0,surface=None,x=-1000,y=-1000,mouse_pos=[0,0],click=[False for i in range(3)]):
    button_data=(text,size,bpc,font,bold,italic,size2,border_width,border_radius,mouse_on_effect)
    if not button_data in buttons:
        buttons[button_data]=Button(text,size,bpc,font,bold,italic,size2,border_width,border_radius,mouse_on_effect)
    return buttons[button_data].display(surface,x,y,mouse_pos,click)