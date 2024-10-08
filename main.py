"""
Maze Game!
"""

# Imports
from random import choice
from os import listdir
from os.path import isfile
from json import load as load_json, dump as save_json
import pygame
from easygui import enterbox, choicebox

# Pylint disable errors that annoy me, such as using the same variable name (e.g. i) in different circumstances, or naming varaibles in lower case in the global space (this is because despite the fact that these variables change, due to them being in the global scape, they are seen as constants.)
# pylint: disable=W0621,C0103

# Inits
pygame.init()
clock = pygame.time.Clock()

# Create window
(display_width, display_height) = (1040, 780+113)
display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Memory-Maze Demo')
icon = pygame.image.load('images/icon.png').convert_alpha()
pygame.display.set_icon(icon)

# Controls
controls = {
    'up': [pygame.K_UP, pygame.K_w],
    'down': [pygame.K_DOWN, pygame.K_s],
    'left': [pygame.K_LEFT, pygame.K_a],
    'right': [pygame.K_RIGHT, pygame.K_d],
    'menu': [pygame.K_RETURN],
    'exit': [pygame.K_ESCAPE]
}
def check_input(control_scheme):
    """
    Checks to see if any inputs in a given control scheme are currently being pressed.
    """
    keys = pygame.key.get_pressed()
    for k in controls[control_scheme]:
        if keys[k]:
            return True
    return False

# Rendering functions
def lerp(v1, v2, t):
    """
    Basic linear interpolation function.
    """
    return v1 * (1 - t) + v2 * t

def create_numerical_text(num: int | float, length: int, color=(255, 255, 255)):
    """
    Returns a pygame surface containing the given numbers after rounding, and adding starting zeros if the number isn't [length] digits long.
    """
    full_num = str(round(num, 1))
    full_num = (length-len(full_num)) * '0' + full_num
    i = 0
    text = pygame.Surface((21 * len(full_num) + 3 * len(full_num) - 3, 21), pygame.SRCALPHA)
    for c in full_num:
        char = pygame.image.load(f'images/text/{c}.png').convert_alpha()
        char.fill(color, special_flags=pygame.BLEND_RGB_MULT)
        text.blit(char, (21 * i + 3 * i, 0))
        i += 1
    return text

# Load assets
lock = pygame.image.load('images/lock.png')
key = pygame.image.load('images/key.png')
player = pygame.image.load('images/player.png')
player_with_key = pygame.image.load('images/player_with_key.png')
portal_border = pygame.image.load('images/portal_border.png')
portal_color = pygame.image.load('images/portal_color.png')
portal_to_color = pygame.image.load('images/portal_to_color.png')
win_overlay = pygame.image.load('images/win_overlay.png')
paused_overlay = pygame.image.load('images/paused_overlay.png')
instructions_screen = pygame.image.load('images/instructions_screen.png')
vignette = pygame.image.load('images/vignette.png')
study_text = pygame.image.load('images/text/study.png')
runthrough_text = pygame.image.load('images/text/run-through.png')
record_text = pygame.image.load('images/text/record.png')
none_text = pygame.image.load('images/text/none.png')

# load mazes
mazes = {}
for _name in listdir('mazes'):
    name = _name.title()
    try:
        if not isfile(f'mazes/{_name}/portals.json'):
            raise FileNotFoundError('Portals json not found.')
        maze_img = pygame.image.load(f'mazes/{_name}/maze.png')
        if maze_img.get_size() != (52, 39):
            if maze_img.get_size() == (50, 37):
                maze_img = pygame.Surface((52, 39))
                maze_img.blit(pygame.image.load(f'mazes/{_name}/maze.png'), (1, 1))
            else:
                raise ValueError('Maze size is invalid.')
        else:
            pygame.draw.line(maze_img, (0, 0, 0), (0, 0), (52, 0))
            pygame.draw.line(maze_img, (0, 0, 0), (52, 0), (52, 39))
            pygame.draw.line(maze_img, (0, 0, 0), (52, 39), (0, 39))
            pygame.draw.line(maze_img, (0, 0, 0), (0, 39), (0, 0))
        mazes[name] = {'maze': maze_img, 'portals': [], 'filepath': _name}
        portals_data = load_json(open(f'mazes/{_name}/portals.json', 'r',encoding='utf-8'))
        for portal in portals_data:
            portal_data = {}
            portal_data['pos'] = pygame.Vector2(portal['at'])
            portal_data['to_pos'] = pygame.Vector2(portal['to'])
            portal_data['color'] = tuple(portal['color'])
            portal_data['to_color'] = tuple(portal['to_color'])
            mazes[name]['portals'].append(portal_data)
    except (FileNotFoundError,ValueError):
        mazes[name] = None
        mazes.pop(name)

# Pick the default maze
maze = None
portals = None
if 'Main Maze' in mazes.keys():
    maze = mazes['Main Maze']
    portals = maze['portals']
elif len(mazes.keys()) > 0:
    maze = mazes[list(mazes.keys())[0]]
    portals = maze['portals']
else:
    raise ValueError('Error! There are no mazes to load.')

# Assign random spots for the player, lock, and key
free_spaces = None
player_pos = None
new_player_pos = None
lock_pos = None
key_pos = None
def prepare_places(min_distance):
    """
    Places the player, lock, and key on the map, ensuring they are all atleast [min_distance] away from eachother and portals.
    """
    global free_spaces, player_pos, lock_pos, key_pos, new_player_pos
    # Get empty spaces
    free_spaces = []
    for x in range(maze['maze'].get_width()):
        for y in range(maze['maze'].get_height()):
            if maze['maze'].get_at((x, y)) != (0, 0, 0, 255):
                free_spaces.append(pygame.Vector2(x,y))
    # Ensure player is not too close to the portals
    player_pos = choice(free_spaces)
    while True:
        player_pos = choice(free_spaces)
        exit_loop = True
        for portal in portals:
            if player_pos.distance_to(portal['pos']) <= min_distance:
                exit_loop = False
                break
        if exit_loop:
            break
    new_player_pos = player_pos.copy()
    # Ensure the lock is not too close to both the player and portals
    lock_pos = player_pos
    while True:
        lock_pos = choice(free_spaces)
        if lock_pos.distance_to(player_pos) > min_distance:
            exit_loop = True
            for portal in portals:
                if lock_pos.distance_to(portal['pos']) <= min_distance:
                    exit_loop = False
                    break
            if exit_loop:
                break
    # Ensure the key is not too close to the player, lock, and portals
    key_pos = player_pos
    while True:
        key_pos = choice(free_spaces)
        if key_pos.distance_to(player_pos) > min_distance and key_pos.distance_to(lock_pos) > min_distance:
            exit_loop = True
            for portal in portals:
                if key_pos.distance_to(portal['pos']) <= min_distance:
                    exit_loop = False
                    break
            if exit_loop:
                break
prepare_places(15)

# Get player name
player_name = ''
msg = ''
while player_name == '':
    inp = enterbox('This will be used to save your times.\nYour name must be between 1 and 16 characters, and can\'t contain special characters.'+msg,'Please input a name below.',strip=True)
    msg = ''
    if inp is None:
        exit()
    elif len(inp) > 16:
        msg = '\n\nYour name can\'t be longer than 16 characters.'
    elif inp == '':
        msg = '\n\nYou must input a name.'
    else:
        for c in inp.lower():
            if c not in '1234567890_-qwertyuiopasdfghjklzxcvbnm ':
                msg = '\n\nYour name can\'t contain special characters.'
                break
    if msg == '':
        player_name = inp.lower()
pygame.display.set_caption(f'Memory-Maze Demo - {player_name.title()}')

# Load player times
times = {}
def load_times():
    """
    Loads the player's record times for the current maze.
    """
    global times
    if not isfile('mazes/'+maze['filepath']+'/times.json'):
        with open('mazes/'+maze['filepath']+'/times.json','w',encoding='utf-8') as f:
            f.write('{}')
            f.close()
    times = dict(load_json(open('mazes/'+maze['filepath']+'/times.json','r',encoding='utf-8')))
    if player_name not in times.keys():
        times[player_name] = []
load_times()

# Display instructions
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if check_input('exit'):
                exit()
            else:
                waiting = False
    display.blit(instructions_screen,(0,0))
    pygame.display.flip()

# Start game
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

paused = False
paused_times = []
paused_start_time = 0
# Main game loop
while True:
    clock.tick(60)
    # Control speed of movement
    if frames_since_last_move < 10:
        frames_since_last_move += 1
    ## Handle inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            # Enter key
            if check_input('menu'):
                # Maze selection if on study phase
                if full_vision:
                    chosen = choicebox('', 'Please select a maze from below.', mazes.keys())
                    if chosen:
                        maze = mazes[chosen]
                        portals = mazes[chosen]['portals']
                        prepare_places(15)
                        load_times()
                        study_time_start = pygame.time.get_ticks()
                # Pause if on runthrough phase
                else:
                    paused = not paused
                    if paused:
                        paused_start_time = pygame.time.get_ticks()
                    else:
                        paused_times.append(pygame.time.get_ticks() - paused_start_time)
            # Escape key
            if check_input('exit'):
                exit()
    # Prevent movement if paused or currently traveling via portal
    if (not portaling) and (not paused):
        moved = False
        # Up movement
        if check_input('up') and (not moved) and frames_since_last_move >= 10:
            new_player_pos = player_pos.copy()
            new_player_pos.x = round(new_player_pos.x)
            new_player_pos.y = round(new_player_pos.y)
            new_player_pos.y -= 1
            moved = True
            # Prevent movement onto black spaces
            if maze['maze'].get_at((round(new_player_pos.x),round(new_player_pos.y))) == (0,0,0,255):
                new_player_pos.y += 1
                moved = False
            # Start runthrough mode if in study mode
            elif full_vision:
                full_vision = False
                pygame.mouse.set_visible(False)
                runthrough_time_start = pygame.time.get_ticks()
        # Down movement
        elif check_input('down') and (not moved) and frames_since_last_move >= 10:
            new_player_pos = player_pos.copy()
            new_player_pos.x = round(new_player_pos.x)
            new_player_pos.y = round(new_player_pos.y)
            new_player_pos.y += 1
            moved = True
            # Prevent movement onto black spaces
            if maze['maze'].get_at((round(new_player_pos.x),round(new_player_pos.y))) == (0,0,0,255):
                new_player_pos.y -= 1
                moved = False
            # Start runthrough mode if in study mode
            elif full_vision:
                full_vision = False
                pygame.mouse.set_visible(False)
                runthrough_time_start = pygame.time.get_ticks()
        # Left movement
        if check_input('left') and (not moved) and frames_since_last_move >= 10:
            new_player_pos = player_pos.copy()
            new_player_pos.x = round(new_player_pos.x)
            new_player_pos.y = round(new_player_pos.y)
            new_player_pos.x -= 1
            moved = True
            # Prevent movement onto black spaces
            if maze['maze'].get_at((round(new_player_pos.x),round(new_player_pos.y))) == (0,0,0,255):
                new_player_pos.x += 1
                moved = False
            # Start runthrough mode if in study mode
            elif full_vision:
                full_vision = False
                pygame.mouse.set_visible(False)
                runthrough_time_start = pygame.time.get_ticks()
        # Right movement
        elif check_input('right') and (not moved) and frames_since_last_move >= 10:
            new_player_pos = player_pos.copy()
            new_player_pos.x = round(new_player_pos.x)
            new_player_pos.y = round(new_player_pos.y)
            new_player_pos.x += 1
            moved = True
            # Prevent movement onto black spaces
            if maze['maze'].get_at((round(new_player_pos.x),round(new_player_pos.y))) == (0,0,0,255):
                new_player_pos.x -= 1
                moved = False
            # Start runthrough mode if in study mode
            elif full_vision:
                full_vision = False
                pygame.mouse.set_visible(False)
                runthrough_time_start = pygame.time.get_ticks()
    if moved:
        frames_since_last_move = 0
    # Lerp the player to the new position
    if new_player_pos != player_pos:
        player_pos = lerp(player_pos,new_player_pos,0.1*frames_since_last_move)

    if player_pos.distance_to(key_pos) < 0.5:
        has_key = True

    if new_player_pos in [portal['pos'] for portal in portals] and frames_since_last_move > 5:
        current_portal = next((portal for portal in portals if portal['pos'] == new_player_pos), None)
        player_pos = current_portal['to_pos']
        new_player_pos = player_pos.copy()
        portaling = True
        portal_frames = 0

    ## Tick up timers
    # Runthrough timer
    if not full_vision:
        runthrough_time = pygame.time.get_ticks() - runthrough_time_start
        for time in paused_times:
            runthrough_time -= time
    # Study timer
    else:
        runthrough_time = 0
        study_time = pygame.time.get_ticks() - study_time_start

    ## Rendering
    # Pause overlay
    if paused:
        display.blit(paused_overlay,(0,0))
    else:
        # Portal overlays
        if portaling:
            portal_screen = pygame.Surface(win_overlay.get_size(),pygame.SRCALPHA)
            # Get the current frame of the animation for part 1
            if portal_frames != 30:
                portal_overlay = pygame.image.load(f'images/portal_transition/color_a/{portal_frames//3}.png').convert_alpha()
            else:
                portal_overlay = pygame.image.load('images/portal_transition/color_a/0.png').convert_alpha()
            assert portal_overlay
            # Apply the portal's color
            portal_overlay.fill(current_portal['color'],special_flags=pygame.BLEND_RGB_MULT)
            portal_screen.blit(portal_overlay,(0,0))
            # Get the current frame of the animation for part 2
            if portal_frames < 30:
                portal_overlay = pygame.image.load(f'images/portal_transition/color_b/{portal_frames//3}.png').convert_alpha()
            else:
                portal_overlay = pygame.image.load('images/portal_transition/color_b/0.png').convert_alpha()
            # Apply the destination's color
            portal_overlay.fill(current_portal['to_color'],special_flags=pygame.BLEND_RGB_MULT)
            portal_screen.blit(portal_overlay,(0,0))
            # Fade in & out animations
            if portal_frames <= 10:
                portal_screen.set_alpha(lerp(0,255,0.1*portal_frames))
            elif portal_frames >= 20:
                portal_screen.set_alpha(255-lerp(0,255,0.1*(portal_frames-20)))
            # Apply to display
            display.blit(portal_screen,(0,0))
            # Tick current animation frames up
            portal_frames += 1
            if portal_frames >= 30:
                portaling = False
        else:
            # Draw the maze
            display.blit(pygame.transform.scale(maze['maze'],(1040,780)),(0,0))
            # Draw the lock
            end_rect = lock.get_rect()
            end_rect.topleft = (lock_pos.x*20,lock_pos.y*20)
            display.blit(lock,end_rect)
            # Draw the portals
            for portal in portals:
                portal_rect = portal_color.get_rect()
                portal_rect.topleft = (portal['pos'].x*20,portal['pos'].y*20)
                portal_color__ = portal_color.copy()
                portal_to_color__ = portal_to_color.copy()
                portal_color__.fill(portal['color'],special_flags=pygame.BLEND_RGB_MULT)
                portal_to_color__.fill(portal['to_color'],special_flags=pygame.BLEND_RGB_MULT)
                display.blit(portal_color__,portal_rect)
                display.blit(portal_to_color__,portal_rect)
                display.blit(portal_border,portal_rect)
            # Draw the player
            player_rect = player.get_rect()
            player_rect.topleft = (player_pos.x*20,player_pos.y*20)
            if has_key:
                display.blit(player_with_key,player_rect)
            else:
                display.blit(player,player_rect)
            # Draw the key
            if not has_key:
                key_rect = key.get_rect()
                key_rect.topleft = (key_pos.x*20,key_pos.y*20)
                display.blit(key,key_rect)
            # Draw the win overlay and end the game
            if has_key and player_pos.distance_to(lock_pos) < 0.5:
                display.blit(win_overlay,(0,0))
                pygame.display.flip()
                break
            # Draw the vignette during runthrough mode
            if not full_vision:
                darkness = pygame.Surface(display.get_size(),pygame.SRCALPHA)
                darkness.fill('black')
                vignette_rect = vignette.get_rect()
                vignette_rect.centerx = player_pos.x*20+10
                vignette_rect.centery = player_pos.y*20+10
                darkness.blit(vignette,vignette_rect,special_flags=pygame.BLEND_RGBA_MIN)
                display.blit(darkness,(0,0))
        ## Draw the times GUI
        # Draw the frame and labels
        pygame.draw.rect(display,(50,50,50,255),pygame.Rect(0,780,1040,113))
        pygame.draw.rect(display,(100,100,100,255),pygame.Rect(5,785,1030,103))
        display.blit(study_text,(5+20,785+20))
        display.blit(runthrough_text,(1040-(5+20)-runthrough_text.get_width(),785+20))
        display.blit(record_text,(5+20+study_text.get_width()+21,785+20))
        display.blit(record_text,(1040-(5+20)-runthrough_text.get_width()-record_text.get_width()-21,785+20))

        # Draw the study time
        study_time_img = create_numerical_text(study_time/1000,3)
        study_time_rect = study_time_img.get_rect()
        study_time_rect.centerx = 5+20+(study_text.get_width()/2)
        study_time_rect.top = 785+20+21*2
        display.blit(study_time_img,study_time_rect)
        # Draw the player's runthrough time
        runthrough_time_img = create_numerical_text(runthrough_time/1000,3)
        runthrough_time_rect = runthrough_time_img.get_rect()
        runthrough_time_rect.centerx = 1040-(5+20+(runthrough_text.get_width()/2))
        runthrough_time_rect.top = 785+20+21*2
        display.blit(runthrough_time_img,runthrough_time_rect)
        # Draw the player's record times
        if times[player_name] != []:
            study_record_time_img = create_numerical_text(times[player_name][0],3,(204,170,0))
            study_record_time_rect = study_record_time_img.get_rect()
            study_record_time_rect.centerx = 5+20+study_text.get_width()+21+(record_text.get_width()/2)
            study_record_time_rect.top = 785+20+21*2
            display.blit(study_record_time_img,study_record_time_rect)

            runthrough_record_time_img = create_numerical_text(times[player_name][1],3,(204,170,0))
            runthrough_record_time_rect = runthrough_record_time_img.get_rect()
            runthrough_record_time_rect.centerx = 1040-(5+20+runthrough_text.get_width()+21+(record_text.get_width()/2))
            runthrough_record_time_rect.top = 785+20+21*2
            display.blit(runthrough_record_time_img,runthrough_record_time_rect)
        # The player has no record
        else:
            none_text_rect = none_text.get_rect()
            none_text_rect.centerx = 5+20+study_text.get_width()+21+(record_text.get_width()/2)
            none_text_rect.top = 785+20+21*2
            display.blit(none_text,none_text_rect)
            none_text_rect.centerx = 1040-(5+20+runthrough_text.get_width()+21+(record_text.get_width()/2))
            display.blit(none_text,none_text_rect)
    # Update the display
    pygame.display.flip()

# End of game - Save times
runthrough_time = pygame.time.get_ticks() - runthrough_time_start
for time in paused_times:
    runthrough_time -= time
if times[player_name] != []:
    if times[player_name][0] > study_time/1000:
        times[player_name][0] = study_time/1000
    if times[player_name][1] > runthrough_time/1000:
        times[player_name][1] = runthrough_time/1000
else:
    times[player_name] = [study_time/1000,runthrough_time/1000]
save_json(times,open('mazes/'+maze['filepath']+'/times.json','w',encoding='utf-8'))
# Wait for input to close the game
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            exit()
