# Imports
import random
import pygame
import math

# Inits
pygame.init()
clock = pygame.time.Clock()

# Create window
(display_width,display_height) = (1040,780)
display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Memory-Maze Demo')
# icon = pygame.image.load('images/gui/icon.png').convert_alpha()
# pygame.display.set_icon(icon)

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

portals1 = {
   (1,33): ((42,17),(0,148,255),(255,134,53)),
   (41,17): ((1,34),(255,134,53),(0,148,255)),
   (1,9): ((50,31),(124,255,140),(235,122,255)),
   (49,31): ((1,8),(235,122,255),(124,255,140)),
}
portals2 = {
   (1,1): ((50,2),(0,148,255),(255,134,53)),
   (50,1): ((50,36),(255,134,53),(124,255,140)),
   (50,37): ((1,36),(124,255,140),(235,122,255)),
   (1,37): ((1,2),(235,122,255),(0,148,255)),
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
has_key = False

full_vision = True

frames_since_last_move = 10

while True:
    clock.tick(60)
    if frames_since_last_move < 10:
        frames_since_last_move += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN and full_vision:
            if event.key == pygame.K_1:
                maze = maze1
                portals = portals1
                prepare_places()
            elif event.key == pygame.K_2:
                maze = maze2
                portals = portals2
                prepare_places()
    moved = False
    if check_input('up') and (not moved) and frames_since_last_move >= 10:
        player_pos[1] -= 1
        moved = True
        if maze.get_at(player_pos) == (0,0,0,255):
            player_pos[1] += 1
            moved = False
        elif full_vision:
            full_vision = False
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
        if moved:
            frames_since_last_move = 0
    if player_pos == key_pos:
        has_key = True
    elif has_key:
        key_pos = player_pos
    
    if tuple(player_pos) in list(portals.keys()):
       player_pos = list(portals[tuple(player_pos)][0])

    display.blit(pygame.transform.scale(maze,(display_width,display_height)),(0,0))
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
    pygame.display.flip()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            exit()