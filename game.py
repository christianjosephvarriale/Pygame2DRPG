import pygame, sys, math, random, json, datetime, os
from pygame.locals import *

FPS = 20 # frames per second setting
SCREENWIDTH = 1000
SCREENHEIGHT = 500

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
UP_RIGHT = 'up-right'
UP_LEFT = 'up-left'
DOWN_RIGHT = 'down-right'
DOWN_LEFT = 'down-left'
STOP = 'stop'


MOVE = 'move'
ATTACK = 'attack'
SPELL = 'spell'
DEAD = 'dead'
COLLIDE = 'collide'

# holds all spells in the game 
RANGE_ATTACK_DIC = {}

# opposite direction dictionary
OPPOSITE_DIRECTION = {      UP:DOWN, DOWN:UP, LEFT:RIGHT, RIGHT:LEFT,
                            UP_RIGHT:DOWN_LEFT, UP_LEFT:DOWN_RIGHT,
                            DOWN_LEFT:UP_RIGHT, DOWN_RIGHT: UP_LEFT     }
                      

#        R    G    B
GRAY = (100, 100, 100)
NAVYBLUE = ( 60, 60, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = ( 0, 255, 0)
BLUE = ( 0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = ( 0, 255, 255 )
TURQ = ( 0, 128, 128 )


# eventually run an andriod application
try:
    import android
except ImportError:
    android = None

class Item(pygame.sprite.Sprite):
    ''' class for all items in the game '''

    def __init__(self, image):

        pygame.sprite.Sprite.__init__(self)

        # item image
        self.image = image

        # setup a rect reference for each tile
        self.rect = self.image.get_rect()

class Range_Attack(pygame.sprite.Sprite):
    ''' contains sprities for each range attack '''

    def __init__(self, speed):

        pygame.sprite.Sprite.__init__(self)

        # This holds all the sprite images for each direction
        self.move_frames_ul = []
        self.move_frames_ur = []
        self.move_frames_dl = []
        self.move_frames_dr = []
        self.move_frames_l = []
        self.move_frames_d = []
        self.move_frames_r = []
        self.move_frames_u = []

        self.collide_frames = []

        
        self.move_tup = (   self.move_frames_l,
                            self.move_frames_ul,
                            self.move_frames_u,
                            self.move_frames_ur,
                            self.move_frames_r,
                            self.move_frames_dr,
                            self.move_frames_d,
                            self.move_frames_dl )


        # each range attack has a direction from when it was casted
        self.direction = None

        # if the attack hits something
        self.collide = False

        # starting frame
        self.frame = 0        
        self.speed = speed

        # image
        self.image = None

    def cast_attack(self, range_sprite_lst, char):
        ''' allows the initialization of a range attack '''

        # set initalized frame and create attack rect
        self.set_range_direction(char)
        set_frame(self)
        create_range_attack_rect(self, char)

        # create the spell
        range_sprite_lst.add(self)

    def set_range_direction(self, char):
        ''' sets the direction of the spell to be the same as the player '''

        self.direction = char.direction

class Tile(pygame.sprite.Sprite):
    def __init__(self, image):
        ''' class containing the blit information
            of a layered map based on JSON data '''

        # set player set, Sprite class super reference, and the image of the
        # Tile
        pygame.sprite.Sprite.__init__(self)

        # tile image
        self.image = image

        # same as the default player speed
        self.speed = 5

        # setup a rect reference for each tile
        self.rect = self.image.get_rect()
    
    def setup_player_spawn(self, adjust_x, adjust_y):
        ''' based on the [0, 0] at the top-left
            setup map position based on char_spawn '''
        self.rect.x -= adjust_x
        self.rect.y -= adjust_y
             
    def update(self, player):
        ''' move the map in the opposite direction of player movement
            This is also used to test collisions '''
        
        if player.target_pos != (None, None):
            move_object(self, OPPOSITE_DIRECTION[player.direction])

class Character(pygame.sprite.Sprite):
    ''' super class containing all types of characters in the game '''

    def __init__(self, speed):

        # super class reference
        pygame.sprite.Sprite.__init__(self)
        
        # setup a counter to cycle through frames
        self.frame = 0

        # 15 cycles must go before the player can attack again, by default 0
        self.timer_for_attack = 0

        # setup the spell item
        self.spell_item_id = None

        # setup character health
        self.health = 100

        # where the character should move
        self.target_pos = (None,None)

        # the speed of the character
        self.speed = speed

        # setup the default character states
        self.attack_state = False
        self.give_damage_state = False
        self.dead_state = False
        self.collide_state = False
        self.spell_state = False

        # setup the character rect
        self.rect = None

        # character co-ordinates
        self.pos_x = 0
        self.pos_y = 0

        # setup character default direction
        self.direction = DOWN

        # This holds all the sprite images for each direction
        self.move_frames_ul = []
        self.move_frames_ur = []
        self.move_frames_dl = []
        self.move_frames_dr = []
        self.move_frames_l = []
        self.move_frames_d = []
        self.move_frames_r = []
        self.move_frames_u = []
        
        self.attack_frames_ul = []
        self.attack_frames_ur = []
        self.attack_frames_dl = []
        self.attack_frames_dr = []
        self.attack_frames_l = []
        self.attack_frames_d = []
        self.attack_frames_r = []
        self.attack_frames_u = []

        self.spell_frames_ul = []
        self.spell_frames_ur = []
        self.spell_frames_dl = []
        self.spell_frames_dr = []
        self.spell_frames_l = []
        self.spell_frames_d = []
        self.spell_frames_r = []
        self.spell_frames_u = []

        self.dead_frames = []

        # store all frame tuples in a tuple for processing
        self.move_tup = (       self.move_frames_u,
                                self.move_frames_l,
                                self.move_frames_d,
                                self.move_frames_r,
                                self.move_frames_dl,
                                self.move_frames_ur,
                                self.move_frames_ul,
                                self.move_frames_dr   )
        
        self.attack_tup = (     self.attack_frames_u,
                                self.attack_frames_l,
                                self.attack_frames_d,
                                self.attack_frames_r,
                                self.attack_frames_dl,
                                self.attack_frames_ur,
                                self.attack_frames_ul,
                                self.attack_frames_dr   )
        
        self.spell_tup = (      self.spell_frames_u,
                                self.spell_frames_l,
                                self.spell_frames_d,
                                self.spell_frames_r,
                                self.spell_frames_dl,
                                self.spell_frames_ur,
                                self.spell_frames_ul,
                                self.spell_frames_dr   )

        self.image = None
            
class Monster(Character):
    ''' monster class '''
    def __init__(self, speed):

        # super class reference
        Character.__init__(self, speed)
        
        # by default the monster is not finding the player
        self.find_player_state = False

        # the name of the monster
        self.name = 'jerry the skeleton'

        # the level of the monster
        self.level = 10

    def set_find_player_state(self, player):
        ''' determines if the monster should go looking for the
            player i.e. the monster is close to the player '''

        # if the player is within 200 
        if self.pos_y - player.pos_y < 200 and self.pos_x - player.pos_x < 200:
            self.find_player_state = True

        # player is too far, don't find them
        else:
            self.find_player_state = False

    def set_target_pos(self, player):
        ''' determines the target position for the monster '''

        # if the monster is attacking it cannot move
        if self.attack_state or self.spell_state:
            self.target_pos = (None,None)

        # if we are within range of the player
        elif self.find_player_state:
            self.target_pos = (player.pos_x,player.pos_y)
            
        # setup a random movement pattern by choosing a random target_pos
        else:
            if self.target_pos == (None,None):
                    
                # set a maximum walking distance
                distance = 100
                
                x_range = (self.pos_x - distance, self.pos_x + distance)
                y_range = (self.pos_y - distance, self.pos_y + distance)
                self.target_pos = (random.randint(x_range),random.randint(y_range))
    
class Player(Character):
    ''' player class '''
    def __init__(self, speed):

        # super reference
        Character.__init__(self, speed)

        # by default no weapon is equipped
        self.weapon = None

def create_map(file):
        ''' builds the tile information into all_layers '''
        
        # open and load the file
        mapfile = open(file).read()
        mapdict = json.loads(mapfile)

        # open all used images JSON
        tilesets = mapdict["tilesets"]
        imageset = []

        # load tiles from each png file
        for images in tilesets:
            image_source = images["source"]
            image_json = open(image_source).read()
            image_ele = json.loads(image_json)
            imageset.append(image_ele)
        
        # declare JSON headers
        layers = mapdict["layers"]
        height = mapdict["height"]
        width = mapdict["width"]
        all_tiles_from_sets = []

        # create tiles from all images
        for image in imageset:
                tileset_image = pygame.image.load(image["image"]).convert_alpha()
                imageheight = image["imageheight"]
                imagewidth = image["imagewidth"]
                tilewidth = image["tilewidth"]
                tileheight = image["tileheight"]
                for y in range(0, imageheight, tileheight):
                        for x in range (0, imagewidth, tilewidth):
                            tile = pygame.Surface((tilewidth, tileheight))
                            tile.blit(tileset_image, (0,0), (x, y, tilewidth, tileheight))
                            tile.set_colorkey(BLACK)
                            all_tiles_from_sets.append(tile)

        # declare dictionaries to hold layer and object data
        all_layers = {}        
        all_objects = {}

        # create different layers and collison data
        for layer in layers:
            
            # set the layer of tiles as a sprite group
            current_layer = pygame.sprite.Group()

            # see if the current layer is an object layer
            if layer["name"][-7:] == "objects":
                name = layer["name"]
                objects = layer["objects"]
                all_objects[name] = objects
                
            # the layer is a tile layer
            else:
                data = layer["data"]
                name = layer["name"]
                layerheight = layer["height"]
                layerwidth = layer["width"]
                properties = layer["properties"]
                try:
                    collision = properties["collision"]
                except KeyError:
                    collision = 0
                    
                data_pos = 0

                for y in range (0, layerheight):
                    for x in range (0, layerwidth):
                        gid = data[data_pos]
                        if gid > 0:
                            tile = Tile(all_tiles_from_sets[gid - 1])
                            # set the player at [0,0] on the map
                            tilex = x * tilewidth + SCREENWIDTH/2
                            tiley = y * tileheight + SCREENHEIGHT/2
                            tile.rect.topleft = (tilex, tiley)
                            current_layer.add(tile)
                        data_pos += 1

            all_layers[name] = [ current_layer, collision ]
            
        return all_layers, all_objects

def create_sprite_frames(path_extenstion, file_name, key):
    ''' takes the folder of images, and returns a list of matched ones '''

    # detect the current working directory
    path = os.getcwd()

    # if a folder is required in the current directory
    path += path_extenstion

    # find all files that match the specification
    file_lst = []

    # return a list of sorted images
    img_lst = []

    # read the entries
    with os.scandir(path) as listOfEntries:  
        for entry in listOfEntries:
            # print all entries that are files
            if entry.is_file():
                if file_name in entry.name:
                    file_lst.append(entry.name)
    
    sort_lst(file_lst)
    
    for file in file_lst:
        image = image_parser(path + "\\" + file, key)
        img_lst.append(image)
        
    return img_lst

def set_attack_timer(character):
    ''' if the player attacked, decrement the attack wait timer
        otherwise, set the timer and change the attack state '''

    if character.attack_state and character.timer_for_attack == 0:
        
        # 15 cycles before the character can attack again
        character.timer_for_attack = 15
        character.frame = 0

        # the character is not attacking
        character.attack_state = False

    elif character.spell_state and character.timer_for_attack == 0:
        
        # 15 cycles before the character can attack again
        character.timer_for_attack = 15
        character.frame = 0

        # the character is not attacking
        character.spell_state = False

def adjust_for_player_movement(obj, player):
    ''' moves all objects in the sprite to keep them still relative
        to the player. direction is determined by the user '''

    move_object(obj, OPPOSITE_DIRECTION[player.direction])

def set_damage_state(character):
    ''' determines whether the character can deal damage '''

    # if the frame is the last one in the attacking frames
    if character.frame == len(character.attack_frames_u) - 2:
        character.give_damage_state = True
    else:
        character.give_damage_state = False
        
def set_rect(obj):
    ''' updates the rect of the object '''
    
    # update the rect of the player to properly position the attack frame
    if type(obj) == Player:
        obj.rect = obj.image.get_rect()
        if obj.attack_state:
            if obj.direction in [DOWN, UP]:
                obj.rect.x = SCREENWIDTH/2 - (obj.rect.width)/2
                obj.rect.y = SCREENHEIGHT/2 - (obj.rect.height)/2
            elif obj.direction == RIGHT:
                obj.rect.x = SCREENWIDTH/2
                obj.rect.y = SCREENHEIGHT/2 - (obj.rect.height)/2
            elif obj.direction == LEFT:
                obj.rect.x = SCREENWIDTH/2 - obj.rect.width
                obj.rect.y = SCREENHEIGHT/2 - (obj.rect.height)/2
            else:
                obj.rect.x = SCREENWIDTH/2 - (obj.rect.width)/2
                obj.rect.y = SCREENHEIGHT/2 - (obj.rect.height)/2
        else:
            obj.rect.x = SCREENWIDTH/2 - (obj.rect.width)/2
            obj.rect.y = SCREENHEIGHT/2 - (obj.rect.height)/2
            
    # the monster's attack frames are less complex for now
    else:
        # initialize the rect
        if obj.rect == None:
            obj.rect = obj.image.get_rect()
            return
        else:
            # if we are already initialized, set the new rect with the current image
            rect_x, rect_y = obj.rect.x, obj.rect.y
            obj.rect.x, obj.rect.y = rect_x, rect_y

def update_obj_coordinate(obj):
    ''' updates the x and y coordinates of an object '''

    # the distance travelled is equal to the objects's speed
    distance = obj.speed
        
    if obj.direction == DOWN_RIGHT:
        obj.pos_x += distance
        obj.pos_y += distance
    elif obj.direction == UP_RIGHT:
        obj.pos_x += distance
        obj.pos_y -= distance
    elif obj.direction == DOWN_LEFT:
        obj.pos_x -= distance
        obj.pos_y += distance
    elif obj.direction == UP_LEFT:
        obj.pos_x -= distance
        obj.pos_y -= distance
    elif obj.direction == RIGHT:
        obj.pos_x += distance
    elif obj.direction == LEFT:
        obj.pos_x -= distance
    elif obj.direction == UP:
        obj.pos_y -= distance
    elif obj.direction == DOWN:
        obj.pos_y += distance

def set_attack_frame(obj, frame):
    ''' determines which frame is set for a char attack based on direction '''

    if obj.direction == UP_RIGHT:
        obj.image = obj.attack_frames_ur[frame]
    elif obj.direction == UP_LEFT:
        obj.image = obj.attack_frames_ul[frame]
    elif obj.direction == DOWN_RIGHT:
        obj.image = obj.attack_frames_dr[frame]
    elif obj.direction == DOWN_LEFT:
        obj.image = obj.attack_frames_dl[frame]
    elif obj.direction == RIGHT:
        obj.image = obj.attack_frames_r[frame]
    elif obj.direction == LEFT:
        obj.image = obj.attack_frames_l[frame]
    elif obj.direction == UP:
        obj.image = obj.attack_frames_u[frame]
    elif obj.direction == DOWN:
        obj.image = obj.attack_frames_d[frame]
    obj.frame += 1

def set_spell_frame(obj, frame):
    ''' determines which frame is set for a spell cast based on direction '''

    if obj.direction == UP_RIGHT:
        obj.image = obj.spell_frames_ur[frame]
    elif obj.direction == UP_LEFT:
        obj.image = obj.spell_frames_ul[frame]
    elif obj.direction == DOWN_RIGHT:
        obj.image = obj.spell_frames_dr[frame]
    elif obj.direction == DOWN_LEFT:
        obj.image = obj.spell_frames_dl[frame]
    elif obj.direction == RIGHT:
        obj.image = obj.spell_frames_r[frame]
    elif obj.direction == LEFT:
        obj.image = obj.spell_frames_l[frame]
    elif obj.direction == UP:
        obj.image = obj.spell_frames_u[frame]
    elif obj.direction == DOWN:
        obj.image = obj.spell_frames_d[frame]
    obj.frame += 1

def set_dead_frame(obj, frame):
    ''' determines which frame is set for a dead state '''

    obj.image = obj.dead_frames[frame]
    obj.frame += 1

def set_collide_frame(obj, frame):
    ''' determines which frame is set for a collide state '''

    obj.image = obj.collide_frames[frame]
    obj.frame += 1

def set_move_frame(obj, frame):
    ''' determines which frame is set for a move frame based on direction '''

    if obj.direction == UP_RIGHT:
        obj.image = obj.move_frames_ur[frame]
    elif obj.direction == UP_LEFT:
        obj.image = obj.move_frames_ul[frame]
    elif obj.direction == DOWN_RIGHT:
        obj.image = obj.move_frames_dr[frame]
    elif obj.direction == DOWN_LEFT:
        obj.image = obj.move_frames_dl[frame]
    elif obj.direction == RIGHT:
        obj.image = obj.move_frames_r[frame]
    elif obj.direction == LEFT:
        obj.image = obj.move_frames_l[frame]
    elif obj.direction == UP:
        obj.image = obj.move_frames_u[frame]
    elif obj.direction == DOWN:
        obj.image = obj.move_frames_d[frame]

    if type(obj) in [Player, Monster] and obj.target_pos != (None, None):
        obj.frame += 1
            
def set_frame(obj):
    ''' changes which frame is shown for an object '''

    # position frame is determined by counter
    frame = obj.frame

    # if the object is a Range_Attack
    if type(obj) == Range_Attack:
        if obj.collide:
            action_frame_length = len(obj.collide_frames)
            if frame < action_frame_length - 1:
                set_collide_frame(obj, frame)
            else:
                pygame.sprite.Sprite.kill(obj)
                obj.frame = 0
            return
        else:
            action_frame_length = len(obj.move_frames_u)
            if frame == action_frame_length - 1:
                obj.frame = 0
            else:
                set_move_frame(obj, frame)
            return
    
    # if the character previously attacked
    if type(obj) in [Monster, Player]:
        if obj.timer_for_attack > 0:
            obj.timer_for_attack -= 1
        
    # if the character can attack, show an attack frame
    if obj.attack_state and obj.timer_for_attack == 0:
        set_damage_state(obj)
        action_frame_length = len(obj.attack_frames_u)
        if frame < action_frame_length - 1:
            set_attack_frame(obj, frame)
        else:
            set_attack_timer(obj)
            frame = obj.frame
            set_move_frame(obj, frame)

    # if the character can cast a spell, show an attack frame
    elif obj.spell_state and obj.timer_for_attack == 0:
        action_frame_length = len(obj.spell_frames_u)            
        if frame < action_frame_length - 1:
            set_spell_frame(obj, frame)
        else:
            set_attack_timer(obj)
            frame = obj.frame
            set_move_frame(obj, frame)

    # if the player is dead, show a dying frame
    elif obj.dead_state:
        action_frame_length = len(obj.dead_frames)
        if frame < action_frame_length - 1:
            set_dead_frame(obj, frame)
        else:
            pygame.sprite.Sprite.kill(obj)
            
    # if the character is stopped, show a stopped frame
    elif obj.target_pos == (None, None):
        obj.frame = 0
        set_move_frame(obj, obj.frame)

    # the character is not stopped 
    else:
        action_frame_length = len(obj.move_frames_u)
        set_move_frame(obj, frame)
        update_obj_coordinate(obj)
        
        if type(obj) == Player: 
            # move the screen top-left coordinate by changing global variable
            update_screen_coordinate(obj.direction, obj.speed)
        
        if frame == action_frame_length - 1:
            obj.frame = 0
            
    set_rect(obj)

def set_direction(obj):
    ''' determines the direction the obj should move in to
        reach the target_pos '''

    # set a reasonable margin for the character to move in
    position_margin = 5

    # if a target_pos is set
    if obj.target_pos != (None, None):
        
        # ordinal directions
        if (obj.pos_x < obj.target_pos[0] - position_margin) and (obj.pos_y < obj.target_pos[1] - position_margin):
            obj.direction = DOWN_RIGHT
        elif (obj.pos_x > obj.target_pos[0] + position_margin) and (obj.pos_y < obj.target_pos[1] - position_margin):
            obj.direction = DOWN_LEFT
        elif (obj.pos_x < obj.target_pos[0] - position_margin) and (obj.pos_y > obj.target_pos[1] + position_margin):
            obj.direction = UP_RIGHT
        elif (obj.pos_x > obj.target_pos[0] + position_margin) and (obj.pos_y > obj.target_pos[1] + position_margin):
            obj.direction = UP_LEFT

        # cardinal directions
        elif obj.pos_x > obj.target_pos[0] + position_margin:
            obj.direction = LEFT
        elif obj.pos_x < obj.target_pos[0] - position_margin:
            obj.direction = RIGHT
        elif obj.pos_y < obj.target_pos[1] - position_margin:
            obj.direction = DOWN
        elif obj.pos_y > obj.target_pos[1] + position_margin:
            obj.direction = UP

        # we have hit the destination
        else:
            obj.target_pos = (None, None)

def image_parser(path, key):
    ''' removes the background color of the image based on the key '''

    # convert the file to an Image
    image = pygame.image.load(path).convert()

    # remove the background
    image.set_colorkey(key)

    return image

def sort_lst(lst):
    ''' mutates lst to a sorted list based on digits in files
        uses the selection sort algorithm          '''
    
    for select in range(len(lst)):
        pos = 0
        # from 0 to select is sorted
        for item in range(select,len(lst)):
            index = ''
            # find the digits in each image file
            for letter in lst[item]:
                if letter.isdigit():
                    index += letter
            if int(index) == select:
                pos = item
        val = lst.pop(pos)
        lst.insert(select,val)

def sort_images(obj, img_lst, rows, cols, action):
    ''' sorts images for all object positions
        into the respective object MOVE / ATTACK / SPELL lst '''

    # starting cell in the table
    cellindex = 0

    # we know the image is of the character class
    if action == MOVE:
        # creates a table to produce different ranges of images
        for row in range(rows):
            for col in range(cols):
                img = img_lst[cellindex]
                obj.move_tup[row].append(img)
                cellindex += 1
                
    elif action == COLLIDE:
        for col in range(cols):
            img = img_lst[cellindex]
            obj.collide_frames.append(img)
            cellindex += 1
                    
    elif action == ATTACK:
        for row in range(rows):
            for col in range(cols):
                img = img_lst[cellindex]
                obj.attack_tup[row].append(img)
                cellindex += 1

    elif action == SPELL:
        for row in range(rows):
            for col in range(cols):
                img = img_lst[cellindex]
                obj.spell_tup[row].append(img)
                cellindex += 1

    elif action == DEAD:
        for row in range(rows):
            for col in range(cols):
                img = img_lst[cellindex]
                obj.dead_frames.append(img)
                cellindex += 1

def check_collision(obj, layers, other_game_objects):
    ''' checks if there is a collision between layers or other game_objects'''

    obj.collide = False
    move_object(obj, obj.direction)
    for layer in layers.values():
        if layer[1]:
            if pygame.sprite.spritecollideany(obj, layer[0]):
                obj.collide = True
    
    if type(obj) == Monster:
        if pygame.sprite.spritecollideany(obj, other_game_objects):
            obj.spell_state = True
            obj.collide = True
        else:
            obj.spell_state = False
    if pygame.sprite.spritecollideany(obj, other_game_objects):
            obj.collide = True
            
    move_object(obj, OPPOSITE_DIRECTION[obj.direction])
    if obj.collide:
        obj.target_pos = (None,None)

def move_object(obj, direction):
    ''' test collisions, moves objects '''

    # the distance travelled is equal to the objects's speed
    distance = obj.speed

    if direction == DOWN_RIGHT:
        obj.rect.x += distance
        obj.rect.y += distance
    elif direction == UP_RIGHT:
        obj.rect.x += distance
        obj.rect.y -= distance
    elif direction == DOWN_LEFT:
        obj.rect.x -= distance
        obj.rect.y += distance
    elif direction == UP_LEFT:
        obj.rect.x -= distance
        obj.rect.y -= distance
    elif direction == RIGHT:
        obj.rect.x += distance
    elif direction == LEFT:
        obj.rect.x -= distance
    elif direction == UP:
        obj.rect.y -= distance
    elif direction == DOWN:
        obj.rect.y += distance

def create_item(item_sprite_lst, item):
    ''' creates an image to appear on the map '''

    item_sprite_lst.add(item)

def create_range_attack_rect(range_attack_obj, character):
    ''' creates the rect of the obj based on character's position '''

    range_attack_obj.rect = range_attack_obj.image.get_rect()

    if range_attack_obj.direction == RIGHT:
        rect_x, rect_y = character.rect.x + character.rect.width, character.rect.y
    elif range_attack_obj.direction == LEFT:
        rect_x, rect_y = character.rect.x - range_attack_obj.rect.width, character.rect.y
    elif range_attack_obj.direction == UP:
        rect_x, rect_y = character.rect.x, character.rect.y - character.rect.height
    elif range_attack_obj.direction == DOWN:
        rect_x, rect_y = character.rect.x, character.rect.y + character.rect.height
    else:
        rect_x, rect_y = character.rect.x, character.rect.y + character.rect.height
        
        
    range_attack_obj.rect.x, range_attack_obj.rect.y = rect_x, rect_y
        
def check_attack(char, game_object_lst):
    ''' check if the character's attack has collided with any object
        in other_char_lst '''

    # find all collisions from the attack
    char_damaged_lst = (pygame.sprite.spritecollide(char, game_object_lst, False))

    for dam_char in char_damaged_lst:
        dam_char.health -= 20
        if dam_char.health == 0:
            dam_char.frame = 0
            dam_char.dead_state = True

def update_screen_coordinate(direction, distance):
    ''' changes the coordinate of the screen (TOP-LEFT is 0,0) '''

    global SCREEN_POS_X, SCREEN_POS_Y

    if direction == DOWN_RIGHT:
        SCREEN_POS_X += distance
        SCREEN_POS_Y += distance
    elif direction == UP_RIGHT:
        SCREEN_POS_X += distance
        SCREEN_POS_Y -= distance
    elif direction == DOWN_LEFT:
        SCREEN_POS_X -= distance
        SCREEN_POS_Y += distance
    elif direction == UP_LEFT:
        SCREEN_POS_X -= distance
        SCREEN_POS_Y -= distance
    elif direction == RIGHT:
        SCREEN_POS_X += distance
    elif direction == LEFT:
        SCREEN_POS_X -= distance
    elif direction == UP:
        SCREEN_POS_Y -= distance
    elif direction == DOWN:
        SCREEN_POS_Y += distance
        
def main():
        
        global FPSCLOCK, SCREEN, SCREEN_POS_X, SCREEN_POS_Y
        pygame.init()

        # if android is available
        if android:
                android.init()
                android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)

        # setup the game window      
        FPSCLOCK = pygame.time.Clock()
        SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        pygame.display.set_caption('PYTHON GAME')

        # retrieve map data
        layers, objects = create_map("game_map.json")

        # declare sprite groups
        monster_sprite_list = pygame.sprite.Group()
        active_sprite_list = pygame.sprite.Group()
        item_sprite_list = pygame.sprite.Group()
        range_attack_sprite_list = pygame.sprite.Group()

        # create range item images
        # for now just create a fire spell
        fire_spell = Range_Attack(20)
        fire_spell_sprite_lst = create_sprite_frames('\\fire_spell','fire_spell',BLACK)
        fire_spell_collide_lst = create_sprite_frames('\\fire_spell','fire_collide',BLACK)
        sort_images(fire_spell, fire_spell_sprite_lst, 8, 8, MOVE)
        sort_images(fire_spell, fire_spell_collide_lst, 1, 15, COLLIDE)
        
        # initialize all frames of the player
        player = Player(5)
        move_pos_lst = create_sprite_frames('\orc_char','orc_move',BLACK)
        attack_pos_lst = create_sprite_frames('\orc_char','orc_attack',BLACK)
        spell_pos_lst = create_sprite_frames('\orc_char','orc_spell',BLACK)
        dead_pos_lst = create_sprite_frames('\orc_char','orc_dead',BLACK)

        # add the images to the player
        sort_images(player, move_pos_lst, 8, 9, MOVE)
        sort_images(player, attack_pos_lst, 8, 6, ATTACK)
        sort_images(player, spell_pos_lst, 8, 7, SPELL)
        sort_images(player, dead_pos_lst, 1, 6, DEAD)
        active_sprite_list.add(player)
        
        # update the player based on the starting direction
        set_frame(player)

        # setup the player to be in the middle of the screen
        player.rect = player.image.get_rect()
        distance_to_screen_left = SCREENWIDTH/2 - (player.rect.width)/2
        distance_to_screen_top = SCREENHEIGHT/2 - (player.rect.height)/2
        player.rect.x = distance_to_screen_left
        player.rect.y = distance_to_screen_top

        # create the spawn points for the player and monsters
        for obj in objects['spawn_objects']:
            if obj["name"] == "char_spawn":
                SCREEN_POS_X = obj["x"] - distance_to_screen_left
                SCREEN_POS_Y = obj["y"] - distance_to_screen_top
                player.pos_x = obj["x"]
                player.pos_y = obj["y"]
                for layer in layers.values():
                    for sprites in layer[0].sprites():
                        # move the map so that the middle is at the spawn point
                        sprites.setup_player_spawn(obj["x"],obj["y"])

            # if the spawn point is for a monster            
            if obj["name"][:7] == "monster":

                # create monster and initialize frames
                monster = Monster(3)
                move_pos_lst = create_sprite_frames('\skeleton_char','skeleton_move',BLACK)
                spell_pos_lst = create_sprite_frames('\skeleton_char','skeleton_spell',BLACK)
                dead_pos_lst = create_sprite_frames('\skeleton_char','skeleton_dead',BLACK)
    
                # add the frames to the monster
                sort_images(monster, move_pos_lst, 8, 9, MOVE)
                sort_images(monster, spell_pos_lst, 8, 13, SPELL)
                sort_images(monster, dead_pos_lst, 1, 6, DEAD)

                # setup the starting frame of the monster
                set_frame(monster)

                # setup position
                monster.rect.x = obj["x"] - SCREEN_POS_X
                monster.rect.y = obj["y"] - SCREEN_POS_Y
                monster.pos_x = obj["x"]
                monster.pos_y = obj["y"]

                monster_sprite_list.add(monster)

            
        # setup some text to be displayed
        scroll_paper = image_parser('scroll_paper.png',BLACK)
        orc_face = image_parser('orc_face.png',BLACK)
        orc_face = pygame.transform.scale(orc_face, (75,75))
        scroll_paper = pygame.transform.scale(scroll_paper, (200,400))
        scroll_paper = pygame.transform.rotate(scroll_paper, 90)
        paper = image_parser('paper.png',BLACK)
        
        fontObj = pygame.font.Font('freesansbold.ttf', 18)
        fontObj_small = pygame.font.Font('freesansbold.ttf', 10)
        health_title = fontObj.render("Health: ", True, BLACK)
        health_state = fontObj.render(str(player.health), True, BLACK)
        health_state_rect =  health_title.get_rect()
        health_title_rect = health_state.get_rect()
        health_state_rect.center = (scroll_paper.get_width()/2+100, scroll_paper.get_height()/2)
        health_title_rect.center = (scroll_paper.get_width()/2, scroll_paper.get_height()/2)

        # render paper

        # game music
        game_music = pygame.mixer.Sound('mozart.wav')
        game_music.play()

        # game loop
        while True:
                # handles each player driven event in the game
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEMOTION:
                        mouse_pos = pygame.mouse.get_pos()
                        x = SCREEN_POS_X + mouse_pos[0] 
                        y = SCREEN_POS_Y + mouse_pos[1]
                    if event.type == pygame.KEYDOWN:
                        if event.key == 115:
                            player.spell_state = True
                        elif event.key == pygame.K_SPACE:
                            player.attack_state = True
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                    if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                            mouse_pos = pygame.mouse.get_pos()
                            x = SCREEN_POS_X + mouse_pos[0] 
                            y = SCREEN_POS_Y + mouse_pos[1]
                            player.target_pos = (x, y)

                # make the surface blank
                SCREEN.fill((0,0,0))

                # update the player's frame based on direction
                if player.attack_state or player.spell_state:
                    player.target_pos = (None, None)
                    
                set_direction(player)
                
                # check if a collision exists between the player and the map, if the player isn't attacking
                if not player.attack_state:
                    check_collision(player, layers, monster_sprite_list)
                set_frame(player)

                # if the player attack, see if he hit anything
                if player.give_damage_state:
                    check_attack(player, monster_sprite_list)

                # change the frame for all range attacks
                for range_attack in range_attack_sprite_list.sprites():
                    set_frame(range_attack)
                    check_collision(range_attack, layers, active_sprite_list)
                    if not range_attack.collide:
                        move_object(range_attack, range_attack.direction)

                # if the player is casting a spell
                if player.spell_state:
                    fire_spell.cast_attack(range_attack_sprite_list, player)

                for sprite in monster_sprite_list.sprites():

                    if player.target_pos != (None, None):
                        # adjust monster position based on player movement
                        adjust_for_player_movement(sprite, player)
                        
                    sprite.set_find_player_state(player)
                    sprite.set_target_pos(player)
                    set_direction(sprite)
                    check_collision(sprite, layers, active_sprite_list)
                    set_frame(sprite)
                    if sprite.give_damage_state:
                        check_attack(sprite, active_sprite_list)

                    if sprite.target_pos != (None, None) :
                        move_object(sprite, sprite.direction)

                # draw the map
                for layer in layers.values():
                    layer[0].update(player)
                    layer[0].draw(SCREEN)

                # redraw the screen and wait for a clock tick
                active_sprite_list.draw(SCREEN)
                monster_sprite_list.draw(SCREEN)
                item_sprite_list.draw(SCREEN)
                range_attack_sprite_list.draw(SCREEN)
                SCREEN.blit(scroll_paper, (0,0))
                SCREEN.blit(health_state, health_state_rect)
                SCREEN.blit(health_title, health_title_rect)
                SCREEN.blit(orc_face, (scroll_paper.get_width()/4,scroll_paper.get_height()/3))

                # display the name, health, and level of the monster
                for sprite in monster_sprite_list:
                    if sprite.rect.collidepoint(mouse_pos):
                        name = fontObj_small.render(str(sprite.name), True, RED)
                        health = fontObj_small.render(str(sprite.health), True, RED)
                        level = fontObj_small.render(str(sprite.level), True, RED)
                        name_rect, health_rect, level_rect =  name.get_rect(), health.get_rect(), level.get_rect()
                        name_rect.center = (sprite.rect.center[0], sprite.rect.y - name_rect.height)
                        health_rect.center = (name_rect.x, name_rect.y - health_rect.height)
                        level_rect.x, level_rect.y = (sprite.rect.center[0], health_rect.y)
                        SCREEN.blit(name, name_rect)
                        SCREEN.blit(health, health_rect)
                        SCREEN.blit(level, level_rect)
                        break
                
                FPSCLOCK.tick(FPS)
                pygame.display.update()

if __name__ == '__main__':
        main()        




                                

        
