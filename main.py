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
wall = pygame.image.load('images/maze.png')
vignette = pygame.image.load('images/vignette.png')
gate = pygame.image.load('images/gate.png')
key = pygame.image.load('images/key.png')
portal = pygame.image.load('images/portal.png')
player = pygame.image.load('images/player.png')
player_key = pygame.image.load('images/player_key.png')

portals = {
   (1,33): (42,17),
   (41,17): (1,34),
   (1,9): (50,31),
   (49,31): (1,8),
}

free_spaces = []
for x in range(wall.get_width()):
    for y in range(wall.get_height()):
        if wall.get_at((x,y)) == (255,255,255,255):
            free_spaces.append((x,y))

player_pos = list(random.choice(free_spaces))
while True:
    player_pos = list(random.choice(free_spaces))
    exit_loop = True
    for portal_pos in portals.keys():
        if math.dist(portal_pos, player_pos) <= 10:
            exit_loop = False
            break
    if exit_loop:
        break
end_pos = player_pos
while True:
    end_pos = list(random.choice(free_spaces))
    if math.dist(player_pos, end_pos) > 10:
        exit_loop = True
        for portal_pos in portals.keys():
            if math.dist(portal_pos, end_pos) <= 10:
                exit_loop = False
                break
        if exit_loop:
            break
key_pos = player_pos
while True:
    key_pos = list(random.choice(free_spaces))
    if math.dist(player_pos, key_pos) > 10 and math.dist(end_pos, key_pos) > 10:
        exit_loop = True
        for portal_pos in portals.keys():
            if math.dist(portal_pos, key_pos) <= 10:
                exit_loop = False
                break
        if exit_loop:
            break

has_key = False

full_vision = True

while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if check_input('up'):
                player_pos[1] -= 1
                if wall.get_at(player_pos) == (0,0,0,255):
                    player_pos[1] += 1
                elif full_vision:
                    full_vision = False
            elif check_input('down'):
                player_pos[1] += 1 
                if wall.get_at(player_pos) == (0,0,0,255):
                    player_pos[1] -= 1
                elif full_vision:
                    full_vision = False
            elif check_input('left'):
                player_pos[0] -= 1 
                if wall.get_at(player_pos) == (0,0,0,255):
                    player_pos[0] += 1
                elif full_vision:
                    full_vision = False
            elif check_input('right'):
                player_pos[0] += 1
                if wall.get_at(player_pos) == (0,0,0,255):
                    player_pos[0] -= 1
                elif full_vision:
                    full_vision = False
    if player_pos == key_pos:
        has_key = True
    elif has_key:
        key_pos = player_pos
    
    if tuple(player_pos) in list(portals.keys()):
       player_pos = list(portals[tuple(player_pos)])

    display.blit(pygame.transform.scale(wall,(display_width,display_height)),(0,0))
    player_rect = vignette.get_rect()
    player_rect.topleft = (player_pos[0]*20,player_pos[1]*20)
    if has_key:
        display.blit(player_key,player_rect)
    else:
        display.blit(player,player_rect)
    gate_rect = vignette.get_rect()
    gate_rect.topleft = (end_pos[0]*20,end_pos[1]*20)
    display.blit(gate,gate_rect)
    if not has_key:
        key_rect = vignette.get_rect()
        key_rect.topleft = (key_pos[0]*20,key_pos[1]*20)
        display.blit(key,key_rect)
    for portal_pos in portals.keys():
        portal_rect = vignette.get_rect()
        portal_rect.topleft = (portal_pos[0]*20,portal_pos[1]*20)
        display.blit(portal,portal_rect)
    if not full_vision:
        darkness = pygame.Surface(display.get_size(),pygame.SRCALPHA)
        darkness.fill('black')
        vignette_rect = vignette.get_rect()
        vignette_rect.centerx = player_pos[0]*20+10
        vignette_rect.centery = player_pos[1]*20+10
        darkness.blit(vignette,vignette_rect,special_flags=pygame.BLEND_RGBA_MIN)
        display.blit(darkness,(0,0))
    pygame.display.flip()
    if has_key and math.dist(player_pos, end_pos) == 0:
       exit()