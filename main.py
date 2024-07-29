# Imports
import random
import pygame
import math
import os
from json import load as jsonLoad
from json import dump as jsonDump
from easygui import enterbox

# Inits
pygame.init()
clock = pygame.time.Clock()

# Create window
(display_width,display_height) = (1040,780+113)
display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Memory-Maze Demo')

# Timers
class Timer:
    def __init__(self, duration) -> None:
        self.duration = duration
        self.finished = False

        self.startTime = 0
        self.active = False

    def activate(self):
        self.active = True
        self.finished = False
        self.startTime = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.finished = True
        self.startTime = 0

    def update(self):
        currentTime = pygame.time.get_ticks()
        if self.active and currentTime - self.startTime >= (self.duration*(1000/60)):
            self.deactivate()

# Controls
controls = {
    'up': [pygame.K_UP],
    'down': [pygame.K_DOWN],
    'left': [pygame.K_LEFT],
    'right': [pygame.K_RIGHT],
    'interact': [pygame.K_c],
    'menu': [pygame.K_RETURN]
}
def check_input(control_scheme):
    keys = pygame.key.get_pressed()
    for key in controls[control_scheme]:
        if keys[key]:
            return True
    return False

def getNums(num: int, length: int,color=(255,255,255)):
    full_num = str(round(num,1))
    full_num = (length-len(full_num))*'0'+full_num
    i = 0
    text = pygame.Surface((21*len(full_num)+3*len(full_num)-3,21),pygame.SRCALPHA)
    for c in full_num:
        char = pygame.image.load(f'images/text/{c}.png').convert_alpha()
        char.fill(color, special_flags=pygame.BLEND_RGB_MULT)
        text.blit(char, (21*i+3*i,0))
        i += 1
    return text

# Load assets
maze1 = pygame.image.load('images/maze1.png')
maze2 = pygame.image.load('images/maze2.png')
vignette = pygame.image.load('images/vignette.png')
end = pygame.image.load('images/end.png')
key = pygame.image.load('images/key.png')
portal = pygame.image.load('images/portal.png')
player = pygame.image.load('images/player.png')
player_key = pygame.image.load('images/player_key.png')
win = pygame.image.load('images/win.png')
study_text = pygame.image.load('images/text/study.png')
runthrough_text = pygame.image.load('images/text/run-through.png')
record_text = pygame.image.load('images/text/record.png')
none_text = pygame.image.load('images/text/none.png')

portals1 = {
   (1,33): ((42,17),(0,148,255),(255,134,53)),
   (41,17): ((1,34),(255,134,53),(0,148,255)),
   (1,9): ((50,31),(124,255,140),(235,122,255)),
   (49,31): ((1,8),(235,122,255),(124,255,140)),
}
portals2 = {
   (1,1): ((27,18),(0,148,255),(255,134,53)),
   (50,1): ((27,21),(255,134,53),(124,255,140)),
   (50,37): ((24,21),(124,255,140),(235,122,255)),
   (1,37): ((24,18),(235,122,255),(0,148,255)),
}
portals = portals1
maze = maze1

free_spaces = None
player_pos = None
end_pos = None
key_pos = None
def prepare_places():
    global free_spaces,player_pos,end_pos,key_pos
    free_spaces = []
    for x in range(maze.get_width()):
        for y in range(maze.get_height()):
            if maze.get_at((x,y)) == (255,255,255,255):
                free_spaces.append((x,y))

    player_pos = list(random.choice(free_spaces))
    while True:
        player_pos = list(random.choice(free_spaces))
        exit_loop = True
        for portal_pos in portals.keys():
            if math.dist(portal_pos, player_pos) <= 15:
                exit_loop = False
                break
        if exit_loop:
            break
    end_pos = player_pos
    while True:
        end_pos = list(random.choice(free_spaces))
        if math.dist(player_pos, end_pos) > 15:
            exit_loop = True
            for portal_pos in portals.keys():
                if math.dist(portal_pos, end_pos) <= 15:
                    exit_loop = False
                    break
            if exit_loop:
                break
    key_pos = player_pos
    while True:
        key_pos = list(random.choice(free_spaces))
        if math.dist(player_pos, key_pos) > 15 and math.dist(end_pos, key_pos) > 15:
            exit_loop = True
            for portal_pos in portals.keys():
                if math.dist(portal_pos, key_pos) <= 15:
                    exit_loop = False
                    break
            if exit_loop:
                break
prepare_places()

player_name = ''
msg = ''
while player_name == '':
    inp = enterbox('Your name must be between 1 and 16 characters, and can\'t contain special characters.'+msg,'Please input your name below.',strip=True)
    msg = ''
    if inp == None:
        exit()
    elif len(inp) > 16:
        msg = '\n\nYour name can\'t be longer than 16 characters.'
    elif inp == '':
        msg = '\n\nYou must input a name.'
    else:
        for c in inp.lower():
            if not (c in '1234567890_qwertyuiopasdfghjklzxcvbnm '):
                msg = '\n\nYour name can\'t contain special characters.'
                break
    if msg == '':
        player_name = inp.lower()

if not os.path.isfile('scores.json'):
    with open('scores.json','w') as f:
        f.write('{}')
        f.close()
scores = dict(jsonLoad(open('scores.json','r')))
if not (player_name in scores.keys()):
    scores[player_name] = []

has_key = False

full_vision = True
study_time_start = pygame.time.get_ticks()
study_time = 0
runthrough_time_start = 0
runthrough_time = 0

frames_since_last_move = 10

while True:
    clock.tick(60)
    if frames_since_last_move < 10:
        frames_since_last_move += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if full_vision:
                if event.key == pygame.K_1:
                    maze = maze1
                    portals = portals1
                    prepare_places()
                elif event.key == pygame.K_2:
                    maze = maze2
                    portals = portals2
                    prepare_places()
            if event.key == pygame.K_ESCAPE:
                exit()
    moved = False
    if check_input('up') and (not moved) and frames_since_last_move >= 10:
        player_pos[1] -= 1
        moved = True
        if maze.get_at(player_pos) == (0,0,0,255):
            player_pos[1] += 1
            moved = False
        elif full_vision:
            full_vision = False
            pygame.mouse.set_visible(False)
            runthrough_time_start = pygame.time.get_ticks()
        if moved:
            frames_since_last_move = 0
    elif check_input('down') and (not moved) and frames_since_last_move >= 10:
        player_pos[1] += 1 
        moved = True
        if maze.get_at(player_pos) == (0,0,0,255):
            player_pos[1] -= 1
            moved = False
        elif full_vision:
            full_vision = False
            pygame.mouse.set_visible(False)
            runthrough_time_start = pygame.time.get_ticks()
        if moved:
            frames_since_last_move = 0
    if check_input('left') and (not moved) and frames_since_last_move >= 10:
        player_pos[0] -= 1 
        moved = True
        if maze.get_at(player_pos) == (0,0,0,255):
            player_pos[0] += 1
            moved = False
        elif full_vision:
            full_vision = False
            pygame.mouse.set_visible(False)
            runthrough_time_start = pygame.time.get_ticks()
        if moved:
            frames_since_last_move = 0
    elif check_input('right') and (not moved) and frames_since_last_move >= 10:
        player_pos[0] += 1
        moved = True
        if maze.get_at(player_pos) == (0,0,0,255):
            player_pos[0] -= 1
            moved = False
        elif full_vision:
            full_vision = False
            pygame.mouse.set_visible(False)
            runthrough_time_start = pygame.time.get_ticks()
        if moved:
            frames_since_last_move = 0
    if player_pos == key_pos:
        has_key = True
    elif has_key:
        key_pos = player_pos
    
    if tuple(player_pos) in list(portals.keys()):
       player_pos = list(portals[tuple(player_pos)][0])

    display.blit(pygame.transform.scale(maze,(1040,780)),(0,0))
    end_rect = end.get_rect()
    end_rect.topleft = (end_pos[0]*20,end_pos[1]*20)
    display.blit(end,end_rect)
    for portal_pos,data in portals.items():
        portal_rect = portal.get_rect()
        portal_rect.topleft = (portal_pos[0]*20,portal_pos[1]*20)
        portal_inner_rect  = pygame.Rect(portal_rect.left+5,portal_rect.top+5,10,10)
        pygame.draw.rect(display,data[1],portal_rect)
        pygame.draw.rect(display,data[2],portal_inner_rect)
        display.blit(portal,portal_rect)
    player_rect = player.get_rect()
    player_rect.topleft = (player_pos[0]*20,player_pos[1]*20)
    if has_key:
        display.blit(player_key,player_rect)
    else:
        display.blit(player,player_rect)
    if not has_key:
        key_rect = key.get_rect()
        key_rect.topleft = (key_pos[0]*20,key_pos[1]*20)
        display.blit(key,key_rect)
    if has_key and math.dist(player_pos, end_pos) == 0:
       display.blit(win,(0,0))
       pygame.display.flip()
       break
    if not full_vision:
        darkness = pygame.Surface(display.get_size(),pygame.SRCALPHA)
        darkness.fill('black')
        vignette_rect = vignette.get_rect()
        vignette_rect.centerx = player_pos[0]*20+10
        vignette_rect.centery = player_pos[1]*20+10
        darkness.blit(vignette,vignette_rect,special_flags=pygame.BLEND_RGBA_MIN)
        display.blit(darkness,(0,0))
    pygame.draw.rect(display,(50,50,50,255),pygame.Rect(0,780,1040,113))
    pygame.draw.rect(display,(100,100,100,255),pygame.Rect(5,785,1030,103))
    display.blit(study_text,(5+20,785+20))
    display.blit(runthrough_text,(1040-(5+20)-runthrough_text.get_width(),785+20))
    display.blit(record_text,(5+20+study_text.get_width()+21,785+20))
    display.blit(record_text,(1040-(5+20)-runthrough_text.get_width()-record_text.get_width()-21,785+20))
    if not full_vision:
        runthrough_time = pygame.time.get_ticks() - runthrough_time_start
    else:
        runthrough_time = 0
        study_time = pygame.time.get_ticks() - study_time_start
    study_time_img = getNums(study_time/1000,3)
    study_time_rect = study_time_img.get_rect()
    study_time_rect.centerx = 5+20+(study_text.get_width()/2)
    study_time_rect.top = 785+20+21*2
    display.blit(study_time_img,study_time_rect)

    if scores[player_name] != []:
        study_record_time_img = getNums(scores[player_name][0],3,(204,170,0))
        study_record_time_rect = study_record_time_img.get_rect()
        study_record_time_rect.centerx = 5+20+study_text.get_width()+21+(record_text.get_width()/2)
        study_record_time_rect.top = 785+20+21*2
        display.blit(study_record_time_img,study_record_time_rect)

        runthrough_record_time_img = getNums(scores[player_name][1],3,(204,170,0))
        runthrough_record_time_rect = runthrough_record_time_img.get_rect()
        runthrough_record_time_rect.centerx = 1040-(5+20+runthrough_text.get_width()+21+(record_text.get_width()/2))
        runthrough_record_time_rect.top = 785+20+21*2
        display.blit(runthrough_record_time_img,runthrough_record_time_rect)
    else:
        none_text_rect = none_text.get_rect()
        none_text_rect.centerx = 5+20+study_text.get_width()+21+(record_text.get_width()/2)
        none_text_rect.top = 785+20+21*2
        display.blit(none_text,none_text_rect)
        none_text_rect.centerx = 1040-(5+20+runthrough_text.get_width()+21+(record_text.get_width()/2))
        display.blit(none_text,none_text_rect)

    runthrough_time_img = getNums(runthrough_time/1000,3)
    runthrough_time_rect = runthrough_time_img.get_rect()
    runthrough_time_rect.centerx = 1040-(5+20+(runthrough_text.get_width()/2))
    runthrough_time_rect.top = 785+20+21*2
    display.blit(runthrough_time_img,runthrough_time_rect)

    pygame.display.flip()

runthrough_time = pygame.time.get_ticks() - runthrough_time_start
if scores[player_name] != []:
    if scores[player_name][0] > study_time/1000:
        scores[player_name][0] = study_time/1000
    if scores[player_name][1] > runthrough_time/1000:
        scores[player_name][1] = runthrough_time/1000
else:
    scores[player_name] = [study_time/1000,runthrough_time/1000]
jsonDump(scores,open('scores.json','w'))
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            exit()