# Imports
import random
import pygame
import math
import os
from json import load as jsonLoad
from json import dump as jsonDump
from easygui import enterbox,choicebox

# Inits
pygame.init()
clock = pygame.time.Clock()

# Create window
(display_width,display_height) = (1040,780+113)
display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Memory-Maze Demo')
icon = pygame.image.load('images/icon.png').convert_alpha()
pygame.display.set_icon(icon)

# Controls
controls = {
    'up': [pygame.K_UP],
    'down': [pygame.K_DOWN],
    'left': [pygame.K_LEFT],
    'right': [pygame.K_RIGHT],
    'menu': [pygame.K_RETURN]
}
def check_input(control_scheme):
    keys = pygame.key.get_pressed()
    for key in controls[control_scheme]:
        if keys[key]:
            return True
    return False

def lerp(v1,v2,time):
    return v1 * (1 - time) + v2 * time

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

mazes = {
    'Main Maze': {
        'maze':pygame.image.load('mazes/Main Maze/maze.png'),
        'portals': {
            (1,33): ((42,17),(0,148,255),(255,134,53)),
            (41,17): ((1,34),(255,134,53),(0,148,255)),
            (1,9): ((50,31),(124,255,140),(235,122,255)),
            (49,31): ((1,8),(235,122,255),(124,255,140)),
        }
    },
    'Quarants Maze': {
        'maze':pygame.image.load('mazes/Quarants Maze/maze.png'),
        'portals': {
            (1,1): ((27,18),(0,148,255),(255,134,53)),
            (50,1): ((27,21),(255,134,53),(124,255,140)),
            (50,37): ((24,21),(124,255,140),(235,122,255)),
            (1,37): ((24,18),(235,122,255),(0,148,255)),
        }
    }
}
maze = mazes['Main Maze']['maze']
portals = mazes['Main Maze']['portals']

free_spaces = None
player_pos = None
new_player_pos = None
end_pos = None
key_pos = None
def prepare_places():
    global free_spaces,player_pos,end_pos,key_pos,new_player_pos
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
    new_player_pos = player_pos.copy()
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
pygame.display.set_caption(f'Memory-Maze Demo - {player_name.title()}')

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
portal_frames = 0
portaling = False
current_portal = None

while True:
    clock.tick(60)
    if frames_since_last_move < 10:
        frames_since_last_move += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if full_vision:
                if check_input('menu'):
                    chosen = choicebox('', 'Please select a maze from below.', mazes.keys())
                    if chosen:
                        maze = mazes[chosen]['maze']
                        portals = mazes[chosen]['portals']
                        prepare_places()
                        study_time_start = pygame.time.get_ticks()
            if event.key == pygame.K_ESCAPE:
                exit()
    if not portaling:
        moved = False
        if check_input('up') and (not moved) and frames_since_last_move >= 10:
            new_player_pos = player_pos.copy()
            new_player_pos[0] = round(new_player_pos[0])
            new_player_pos[1] = round(new_player_pos[1])
            new_player_pos[1] -= 1
            moved = True
            if maze.get_at(new_player_pos) == (0,0,0,255):
                new_player_pos[1] += 1
                moved = False
            elif full_vision:
                full_vision = False
                pygame.mouse.set_visible(False)
                runthrough_time_start = pygame.time.get_ticks()
        elif check_input('down') and (not moved) and frames_since_last_move >= 10:
            new_player_pos = player_pos.copy()
            new_player_pos[0] = round(new_player_pos[0])
            new_player_pos[1] = round(new_player_pos[1])
            new_player_pos[1] += 1 
            moved = True
            if maze.get_at(new_player_pos) == (0,0,0,255):
                new_player_pos[1] -= 1
                moved = False
            elif full_vision:
                full_vision = False
                pygame.mouse.set_visible(False)
                runthrough_time_start = pygame.time.get_ticks()
        if check_input('left') and (not moved) and frames_since_last_move >= 10:
            new_player_pos = player_pos.copy()
            new_player_pos[0] = round(new_player_pos[0])
            new_player_pos[1] = round(new_player_pos[1])
            new_player_pos[0] -= 1 
            moved = True
            if maze.get_at(new_player_pos) == (0,0,0,255):
                new_player_pos[0] += 1
                moved = False
            elif full_vision:
                full_vision = False
                pygame.mouse.set_visible(False)
                runthrough_time_start = pygame.time.get_ticks()
        elif check_input('right') and (not moved) and frames_since_last_move >= 10:
            new_player_pos = player_pos.copy()
            new_player_pos[0] = round(new_player_pos[0])
            new_player_pos[1] = round(new_player_pos[1])
            new_player_pos[0] += 1
            moved = True
            if maze.get_at(new_player_pos) == (0,0,0,255):
                new_player_pos[0] -= 1
                moved = False
            elif full_vision:
                full_vision = False
                pygame.mouse.set_visible(False)
                runthrough_time_start = pygame.time.get_ticks()
    if moved:
        frames_since_last_move = 0
    if not (new_player_pos == player_pos):
        player_pos = lerp(pygame.Vector2(player_pos),pygame.Vector2(new_player_pos),0.1*frames_since_last_move)
        player_pos = [player_pos.x,player_pos.y]

    if math.dist(player_pos, key_pos) < 0.5:
        has_key = True
    
    if tuple(player_pos) in list(portals.keys()):
        current_portal = portals[tuple(player_pos)]
        player_pos = list(current_portal[0])
        new_player_pos = player_pos.copy()
        portaling = True
        portal_frames = 0
    if portaling:
        portal_screen = pygame.Surface(win.get_size(),pygame.SRCALPHA)
        if portal_frames != 30:
            portal_overlay = pygame.image.load(f'images/portal_transition/color_a/{portal_frames//3}.png').convert_alpha()
        else:
            portal_overlay = pygame.image.load('images/portal_transition/color_a/0.png').convert_alpha()
        assert portal_overlay
        portal_overlay.fill(current_portal[1],special_flags=pygame.BLEND_RGB_MULT)
        portal_screen.blit(portal_overlay,(0,0))
        if portal_frames < 30:
            portal_overlay = pygame.image.load(f'images/portal_transition/color_b/{portal_frames//3}.png').convert_alpha()
        else:
            portal_overlay = pygame.image.load('images/portal_transition/color_b/0.png').convert_alpha()
        assert portal_overlay
        portal_overlay.fill(current_portal[2],special_flags=pygame.BLEND_RGB_MULT)
        portal_screen.blit(portal_overlay,(0,0))
        if portal_frames <= 10:
            portal_screen.set_alpha(lerp(0,255,0.1*portal_frames))
        elif portal_frames >= 20:
            portal_screen.set_alpha(255-lerp(0,255,0.1*(portal_frames-20)))
        display.blit(portal_screen,(0,0))
        portal_frames += 1
        if portal_frames >= 30:
            portaling = False
    else:
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
        if has_key and math.dist(player_pos, end_pos) < 0.5:
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