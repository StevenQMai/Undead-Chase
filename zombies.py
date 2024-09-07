import pygame, sys, os, random, time
from pygame.locals import *
import math

pygame.init()

#CONSTANTS
SIZE = WIDTH, HEIGHT = (1000,600)
DISPLAY = pygame.display.set_mode(SIZE)
FPS = pygame.time.Clock()
BASE_SPEED = 7
BASE_HEALTH = 300
GREEN = (0,255,0) #(R,G,B)
RED = (255,0,0)
RED_OVERLAY = (255,50,50)
BACKGROUND = pygame.image.load(os.path.join("Assets", "PokemonBackground.png")).convert()
FONT = pygame.font.SysFont("Arial", 60)

pygame.display.set_caption("Zombies")

#=======CHARACTER CLASSES=======

class Character(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.walk_animation = [ #makeshift walking animation by flipping through frames
            pygame.image.load(os.path.join("Assets", type, f"{type}_Standing.png")).convert_alpha(),
            pygame.image.load(os.path.join("Assets", type, f"{type}_L_Step.png")).convert_alpha(),
            pygame.image.load(os.path.join("Assets", type, f"{type}_Standing.png")).convert_alpha(),
            pygame.image.load(os.path.join("Assets", type, f"{type}_R_Step.png")).convert_alpha()
        ]
        self.surface = pygame.Surface((85, 140)) #coordinates for surface object (character)
        self.direction = 1 #1 is right, 0 is left
        self.step_count = 0


class Hero(Character):
    def __init__(self):
        Character.__init__(self, "Hero")
        self.hurt = pygame.image.load(os.path.join("Assets", "Hero", "Hero_Hurt.png")).convert_alpha()
        self.rect = self.surface.get_rect(center=(WIDTH/2, HEIGHT/2))
        self.x_speed = BASE_SPEED
        self.y_speed = BASE_SPEED
        self.health = BASE_HEALTH
        self.is_hurt = False

    def normalize_vector(self, x, y):
        magnitude = math.sqrt(x**2 + y**2)
        if magnitude == 0:
            return 0,0

        return x/magnitude, y/magnitude

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        x_input = 0
        y_input = 0
        self.is_hurt = False

        # Collect input from the user
        if self.rect.left > 0 and (pressed_keys[K_LEFT] or pressed_keys[K_a]):
            x_input = -1
            if self.direction == 1:
                self.step_count = 0
            self.direction = 0


        if self.rect.left < 0 or self.rect.right > WIDTH or self.rect.bottom > HEIGHT or self.rect.top < 0:
            hero.health -= 1
            self.is_hurt = True

            #draw_window.display.fill(RED_OVERLAY, special_flags = BLEND_MULT)
    

        if self.rect.right < WIDTH and (pressed_keys[K_RIGHT] or pressed_keys[K_d]):
            x_input = 1
            if self.direction == 0:
                self.step_count = 0
            self.direction = 1

        if self.rect.top > 0 and (pressed_keys[K_UP] or pressed_keys[K_w]):
            y_input = -1

        if self.rect.bottom < HEIGHT and (pressed_keys[K_DOWN] or pressed_keys[K_s]):
            y_input = 1

        # Normalize the input vector
        normalized_x, normalized_y = self.normalize_vector(x_input, y_input)

        # Move the character according to normalized direction and speed
        self.rect.move_ip(normalized_x * self.x_speed, normalized_y * self.y_speed)

        #logic to prevent the hero from moving out of bounds
        """
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        """

        # Update step count if the player is moving
        if x_input != 0 or y_input != 0:
            self.step_count += 1

        # Reset step count if necessary
        if self.step_count >= 59:
            self.step_count = 0


    def check_collision_powerups(self, power_ups):
    # Get all colliding power-ups and remove them from the group
        collided_power_ups = pygame.sprite.spritecollide(self, power_ups, True)
        if collided_power_ups:
            self.health = min(BASE_HEALTH, self.health + 50)  # Restore health

        
class Zombie(Character):
    def __init__(self):
        Character.__init__(self, "Zombie")
        self.rect = self.surface.get_rect(center=(random.randint(50, WIDTH-50), random.randint(75, HEIGHT-75)))
        self.x_speed = random.randint(1,5)
        self.y_speed = random.randint(1,5)

    def move(self):
        if self.step_count >= 59:
            self.step_count = 0

        self.rect.move_ip(self.x_speed, self.y_speed)

        if (self.rect.right > WIDTH) or (self.rect.left < 0): 
            #if the horizontal edges of the object has moved past the bounds of the window
            self.x_speed *= -1
            self.direction *= -1 
            #makes the character bounce off the edges of the window if it tries to leave the bounds


        if (self.rect.bottom > HEIGHT) or (self.rect.top < 0):
            #if the vertical edges of the object has moved above or below the window's bounds
            self.y_speed *= -1
            #makes the character bounce off the vertical edges of the window

        self.step_count += 1


#=======ITEM CLASSES=======

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        original_image = pygame.image.load(os.path.join("Assets", "PowerUps", "Medkit2.png")).convert_alpha()
        new_size = (50,50)
        self.image = pygame.transform.scale(original_image, new_size)
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)))

    def update(self):
        pass



#DRAWING THE ENTIRE FRAME
def draw_window(display, background, hero, zombies, power_ups):

    #DRAW THE MAIN BACKGROUND
    display.blit(background, (0,0))
    #DRAW ZOMBIES
    for character in zombies: #draw each zombie
        current_zomb_sprite = character.walk_animation[character.step_count//15] #shows each frame per multiple steps
        if character.direction == -1: #moving left
            current_zomb_sprite = pygame.transform.flip(current_zomb_sprite, True, False) #reverses the zombie sprite if it moves to the left
        display.blit(current_zomb_sprite, character.rect) #draws the current frame of the animation at the location of the character rectangle


    #DRAW POWER-UPS
    for power_up in power_ups:
        display.blit(power_up.image, power_up.rect)


    #CHECK FOR COLLISIONS
    if pygame.sprite.spritecollideany(hero, zombies):
        hero.health -= 1
        current_hero_sprite = hero.hurt
        display.fill(RED_OVERLAY, special_flags = BLEND_MULT)
    else:
        if hero.is_hurt:
            current_hero_sprite = hero.hurt
        else:
            current_hero_sprite = hero.walk_animation[hero.step_count // 15]

    #DRAW HERO
    if hero.direction == 0: #if the hero moves in the left direction
        current_hero_sprite = pygame.transform.flip(current_hero_sprite, True, False)
    display.blit(current_hero_sprite, hero.rect) #displays the current hero sprite at the location of the hero rectangle (hitbox)

    #DRAW HEALTH
    pygame.draw.rect(display, GREEN, (20, 20, hero.health, 20))
    pygame.draw.rect(display, RED, (hero.health + 20, 20, BASE_HEALTH - hero.health, 20))

    #DRAW CURRENT SCORE
    score_text = FONT.render(f"TIME SURVIVED: {score//60}", True, (255,255,255))
    display.blit(score_text, (WIDTH/2.5 + 20, 5))


    #draw hitbox around the hero (debugging)
    pygame.draw.rect(display, (255, 0, 0), hero.rect, 2)
    #pygame.draw.rect(display, (255,0,0), zombie.rect, 2)


    pygame.display.update()
    
    #ON LOSE
def game_over():
#TEXT TO RENDER
    game_over_text = FONT.render(f"GAME OVER", True, (255,0,0))
    score_text = FONT.render(f"SURVIVED FOR {score//60} SECONDS", True, (255, 0, 0))
    zombie_count_text = FONT.render(f"ZOMBIE COUNT: {zombie_count}", True, (255,0,0))
    
    #DRAWING ELEMENTS
    DISPLAY.fill((0,0,0))
    DISPLAY.blit(game_over_text, (WIDTH/2 - (game_over_text.get_width()/2), HEIGHT/2 - game_over_text.get_height()/2))
    DISPLAY.blit(score_text, (WIDTH/2 - (score_text.get_width()/2), (HEIGHT/2 + score_text.get_height() * 1.5)))
    DISPLAY.blit(zombie_count_text, (WIDTH/2 - (zombie_count_text.get_width()/2), (HEIGHT/2 + zombie_count_text.get_height() * 2.5)))

    for character in all_sprites:
        character.kill()

    pygame.display.update()
    time.sleep(5)
    pygame.quit()
    sys.exit()


def draw_lava_border(screen, hero_rect, border_thickness=10):
    screen_rect = screen.get_rect()
    border_color = (255,0,0)

    if hero_rect.left <= 0 or hero_rect.right > WIDTH or hero_rect.bottom > HEIGHT or hero_rect.top < 0 and hero.is_hurt:
        pygame.draw.rect(screen, border_color, (0, 0, screen_rect.width, border_thickness)) #draw top border
        pygame.draw.rect(screen, border_color, (0,screen_rect.height - border_thickness, screen_rect.width, border_thickness)) #draw bottom border
        pygame.draw.rect(screen, border_color, (0,0,border_thickness, screen_rect.width)) #draw left border
        pygame.draw.rect(screen, border_color, (screen_rect.width - border_thickness, 0, border_thickness, screen_rect.height)) #draw right border

#=======INITIALIZE=======

#USER EVENTS
SPAWN_ENEMY = pygame.USEREVENT + 1
SPAWN_POWERUP = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_ENEMY, 3000) #spawns enemies every 3 seconds
pygame.time.set_timer(SPAWN_POWERUP, 10000) 

#SPRITES
hero = Hero()
zombie = Zombie()
zombie_count = 1
zombies = pygame.sprite.Group()
zombies.add(zombie)
all_sprites = pygame.sprite.Group()
all_sprites.add(zombies, hero)

score = 0

#GAME LOOP


# Initialize the power-ups group
power_ups = pygame.sprite.Group()
all_sprites.add(power_ups)


# Create and add power-ups to the group
for _ in range(5):  # Example: Adding 5 power-ups
    power_up = PowerUp()
    power_ups.add(power_up)



while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SPAWN_ENEMY:
            new_zombie = Zombie()
            zombies.add(new_zombie)
            all_sprites.add(new_zombie)
            zombie_count += 1
        if event.type == SPAWN_POWERUP:
            new_power_up = PowerUp()
            power_ups.add(new_power_up)
            all_sprites.add(new_power_up)

    if hero.health <= 0:
        game_over()

    score += 1

    hero.check_collision_powerups(power_ups)

    draw_window(DISPLAY, BACKGROUND, hero, zombies, power_ups)

    for character in all_sprites:
        if hasattr(character, 'move'):
            character.move()

    draw_lava_border(DISPLAY, hero.rect)


    pygame.display.flip()

    FPS.tick(60)
