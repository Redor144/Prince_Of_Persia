import pygame
from config import *
import math
import random

class Enemy(pygame.sprite.Sprite):
    """Abstract class for the enemies and boss in the game."""
    def __init__(self, game, x, y, speed, attack, attack_ratio_max, sprite_sheet):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE
        self.speed = speed
        self.attack = attack
        self.attack_ratio_max = attack_ratio_max
        self.current_health = ENEMY_MAX_HEALTH
        
        self.animation_loop = 1
        self.movement_loop = 0
        self.x_change = 0
        self.facing = 'right'
        self.attack_ratio = 0
        
        self.left_animations = sprite_sheet.get_sprites(3, 98, self.width, self.height, 1, 3)
        self.right_animations = sprite_sheet.get_sprites(3, 66, self.width, self.height, 1, 3)
        
        self.image = self.right_animations[0]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
    def update(self):
        self.movement()
        self.animate()
        self.collide_player()
        self.rect.x += self.x_change
        self.collide_blocks()
        self.attack_player(0)
        self.x_change = 0
    
    def attack_player(self, y):
        player_distance_y = abs(self.rect.y - self.game.player.rect.y)
        player_distance_x = abs(self.rect.x - self.game.player.rect.x)

        if player_distance_y <= 64 and player_distance_x <= 64 and self.attack_ratio == 0:
            attack_x = self.rect.x + TILESIZE if self.facing == 'right' else self.rect.x - TILESIZE
            Attack(self.game, attack_x, self.rect.y + y * TILESIZE, 'player', self.attack, self.facing)
        
        if self.attack_ratio < self.attack_ratio_max:
            self.attack_ratio += 0.5
        
        if self.attack_ratio >= self.attack_ratio_max:
            self.attack_ratio = 0
    
    def collide_player(self):
        hits = pygame.sprite.spritecollide(self, self.game.players, False)
        if hits:
            self.x_change = 0
    
    def collide_blocks(self):
        hits = pygame.sprite.spritecollide(self, self.game.collisions.sprites() + self.game.fakes.sprites(), False)
        if hits:
            hit = hits[0]
            if self.x_change != 0:
                if self.x_change > 0:
                    self.rect.x = hit.rect.left - self.rect.width
                    self.facing = 'l_col'
                else:
                    self.rect.x = hit.rect.right
                    self.facing = 'r_col'
                self.x_change = 0

    def animate(self):
        animations = self.left_animations if self.facing == "left" else self.right_animations
        if self.x_change == 0:
            self.image = animations[0]
        else:
            self.image = animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.1
            if self.animation_loop >= 3:
                self.animation_loop = 1
                
    def movement(self):
        player_distance_x = self.rect.x - self.game.player.rect.x
        player_distance_y = abs(self.rect.y - self.game.player.rect.y)

        if self.facing in ['left', 'right']:
            if player_distance_y <= 128 and abs(player_distance_x) <= 128:
                if (self.facing == 'left' and player_distance_x > 0) or (self.facing == 'right' and player_distance_x < 0):
                    self.x_change += self.speed if self.facing == 'right' else -self.speed
                    self.movement_loop += 1 if self.facing == 'right' else -1
                else:
                    self.facing = 'stay'
            else:
                self.x_change += self.speed if self.facing == 'right' else -self.speed
                self.movement_loop += 1 if self.facing == 'right' else -1

        if self.facing == 'stay':
            if player_distance_y <= 128:
                if player_distance_x >= 8:
                    self.facing = 'left'
                elif player_distance_x <= -8:
                    self.facing = 'right'
            else:
                self.facing = random.choice(['left', 'right'])

        if self.facing == 'l_col' and (player_distance_y > 128 or player_distance_x > 0 or player_distance_x < -128):
            self.facing = 'left'
        if self.facing == 'r_col' and (player_distance_y > 128 or player_distance_x < 0 or player_distance_x > 128):
            self.facing = 'right'
    
    def get_damage(self, amount):
        self.current_health -= amount
        if self.current_health <= 0:
            play_sound(GET_DAMAGE_SOUND_PATH, 0.2)
            self.kill()

class EnemyGreen(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, ENEMY_GREEN_SPEED, ENEMY_GREEN_DAMAGE, ENEMY_GREEN_ATTACK_RATIO, ENEMY_GREEN_SPRITESHEET)

class EnemyBlue(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, ENEMY_BLUE_SPEED, ENEMY_BLUE_DAMAGE, ENEMY_BLUE_ATTACK_RATIO, ENEMY_BLUE_SPRITESHEET)

class EnemyRed(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, ENEMY_RED_SPEED, ENEMY_RED_DAMAGE, ENEMY_RED_ATTACK_RATIO, ENEMY_RED_SPRITESHEET)

class Boss(Enemy):
    """Class for final boss. Inherits from enemy, has more health and when is activate shoots a bow."""
    def __init__(self, game, x, y):
        super().__init__(game, x, y, ENEMY_RED_SPEED, ENEMY_GREEN_DAMAGE * 3.5, ENEMY_GREEN_ATTACK_RATIO, BOSS_SPRITESHEET)
        self.current_health = ENEMY_MAX_HEALTH * 6.5
        
        self.width = TILESIZE - 4
        self.height = 2 * TILESIZE
    
        self.rect = pygame.Rect(x * TILESIZE, (y + 1) * TILESIZE - self.height, self.width, self.height)
        self.right_animations = BOSS_SPRITESHEET.get_sprites(0, 7, self.width, self.height, 1, 3)
        self.left_animations = [pygame.transform.flip(img, True, False) for img in self.right_animations]
        self.image = self.right_animations[0]
        self.image.set_colorkey(BLACK)

        self.change_time = 0
        self.activate = False
        self.magic = 0
        self.arrow_time = 0

    def random_version(self):
        return random.randint(8, 39)

    def magic_changes(self):
        curr_time = pygame.time.get_ticks()
        if curr_time > self.change_time + 5000:
            self.fix_magic_sequence()
            self.magic = self.random_version() % 4 + 1
            self.change_time = curr_time
            if self.magic == 1:
                self.game.player.speed *= 0.5
            elif self.magic == 2:
                self.game.player.attack *= 0.5
            elif self.magic == 3:
                self.rect.x = self.random_version() * TILESIZE
            elif self.magic == 4:
                self.game.player.current_health += 8

    def activation(self):
        if math.sqrt((self.rect.x - self.game.player.rect.x)**2 + (self.rect.y - self.game.player.rect.y)**2) < 3:
            self.activate = True

    def fix_magic_sequence(self):
        if self.magic == 1:
            self.game.player.speed *= 2
        elif self.magic == 2:
            self.game.player.attack *= 2
    
    def get_damage(self, amount):
        self.current_health -= amount
        if self.current_health <= 0:
            self.fix_magic_sequence()
            play_sound(GET_DAMAGE_SOUND_PATH, 0.2)
            for sprite in self.game.gate.sprites():
                sprite.kill()
            self.kill()
 
    def cupids_arrow(self):
        curr_time = pygame.time.get_ticks()
        if abs(self.rect.x - self.game.player.rect.x) > 2 * TILESIZE:
            if curr_time >= self.arrow_time + 2000:
                Arrow(self.game, self.rect.x, self.rect.y + 32, self.facing)
                self.arrow_time = curr_time

    def update(self):
        self.activation()
        self.cupids_arrow()
        if self.activate:
            self.magic_changes()
        self.movement()
        self.animate()
        self.collide_player()
        self.rect.x += self.x_change
        self.collide_blocks()
        self.attack_player(1)
        self.x_change = 0

class Attack(pygame.sprite.Sprite):
    def __init__(self, game, x, y, entity, attack, direction):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.attack
        pygame.sprite.Sprite.__init__(self,self.groups)
    
        self.reciever = entity
        self.attack = attack
        self.direction = direction
        self.x = x 
        self.y = y
        self.width = TILESIZE
        self.height = TILESIZE
        self.recieved = False
        self.animation_loop = 0

        sprite_y_offset = 64 if self.direction == 'right' else 96
        self.animations = ATTACK_SPRITESHEET.get_sprites(0, sprite_y_offset, self.width, self.height, 1, 5)
        self.image = self.animations[0]
        
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        play_sound(ATTACK_SOUND_PATH, 0.15)
        
    def update(self):
        self.animate()
        self.collide()
        
    def collide(self):
        target_group = self.game.enemies if self.reciever == 'enemy' else self.game.players
        hits = pygame.sprite.spritecollide(self, target_group, False)
        if hits and not self.recieved:
            self.recieved = True
            for target in hits:
                if self.reciever == 'player' and not target.damage_resistance:
                    target.get_damage(self.attack)
                elif self.reciever == 'enemy':
                    target.get_damage(self.attack)
            
    def animate(self):
        self.image = self.animations[math.floor(self.animation_loop)]
        self.animation_loop += 0.5
        if self.animation_loop >= len(self.animations):
            if self.reciever == 'enemy':
                self.game.player.is_attacking = False
            self.kill()

class Arrow(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.arrows
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.direction = direction
        self.width = TILESIZE
        self.height = TILESIZE

        self.image = ARROW_SPRITESHEET.get_sprite(0, 0, self.width + 2, self.height)
        if self.direction == 'right':
            self.x, self.y = x + TILESIZE, y
        else:
            self.image = pygame.transform.flip(self.image, True, False)
            self.x, self.y = x - TILESIZE, y

        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def change_possition(self):
        if self.direction == 'right':
            self.rect.x += 7
        else:
            self.rect.x -= 7

    def check_collisions(self):
        colissions_player = pygame.sprite.spritecollide(self, self.game.players, False)
        if colissions_player:
            self.game.player.get_damage(16)
            self.kill()
        if self.rect.x >= 38 * TILESIZE or self.rect.x <= 7 * TILESIZE:
            self.kill()

    def update(self):
        self.change_possition()
        self.check_collisions()