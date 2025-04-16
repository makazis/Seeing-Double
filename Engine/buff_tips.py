from random import *
from math import *
from useful_stuff import *
pygame.init()
buff_tip_texts={
    "Vulnerable": "Vulnerable creatures take 50% more attack damage, lasts X turns",
    "Strength":   "Attacks from creatures with X Strength deal X additional attack damage",
    "Weak":       "Creatures with Weak deal 25% less attack damage lasts X turns",

    "Poison":     "Creatures with X Poison lose X HP at the start of their turn, then Poison decreases by 1",
    "Dexterity":  "Blocking moves from creatures with X Dexterity gain X aditional block" ,
    "Conduit":    "ALL other buffs and debuffs apply X additional charges, if a creature has X Conduit ",

    "Antivenom": "While you have Antivenom , you don't take damage from Poison ",
    "Immune": "Creatures with X Immune can't take combat damage, for X turns",
    "Cold": "Cold : Negates X Hot , reduced by 1 each turn",
    "Hot": "Hot : Negates X Cold , reduced by 1 each turn"
}
textify_memory={}
def textify(text,border=200,color=(205,205,205)):
    if not text in textify_memory:
        split=text.split(" ")
        lines=[]
        while len(split)>0:
            x_size=0
            iterator=0
            while x_size<border and iterator<=len(split):
                iterator+=1
                p_x_size=x_size
                x_size=0
                for i in split[:iterator]:
                    if i in buff_icons:
                        x_size+=16+render_text(" ",15,(205,205,205),"comicsansms",antial= False).get_width()
                    else:
                        x_size+=render_text(i+" ",15,(205,205,205),"comicsansms",antial= False).get_width()
            iterator-=1
            lines.append((split[:iterator],(210-p_x_size)/2))
            for i in range(iterator):
                split.pop(0)
        sprite=pygame.Surface((210,20+20*len( lines)))
        sprite.fill((card_transparency_color))
        sprite.set_colorkey((card_transparency_color))
        #pygame.draw.rect( sprite,(55,55,55),(0,0,210,20+20*len( lines)),0,15)
        #pygame.draw.rect( sprite,(105,105,105),(0,0,210,20+20*len( lines)),3,15)
        for I,i in enumerate(lines):
            x_pos=i[1]
            for ii in i[0]:
                if ii in buff_icons:
                    sprite.blit(small_buff_icons[ii],(x_pos,10+I*20))
                    x_pos+=16
                    sprite.blit(render_text(" ",15,color,"comicsansms",antial= False),(x_pos,10+I*20))
                    x_pos+=render_text(" ",15,(205,205,205),"comicsansms",antial= False).get_width()
                else:
                    sprite.blit(render_text(ii+" ",15,color,"comicsansms",antial= False),(x_pos,10+I*20))
                    x_pos+=render_text(ii+" ",15,(205,205,205),"comicsansms",antial= False).get_width()
        textify_memory[text]=sprite
    return textify_memory[text]
buff_tips={i:textify(buff_tip_texts[i]) for i in buff_tip_texts}