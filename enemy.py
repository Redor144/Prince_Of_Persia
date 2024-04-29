import pygame
from config import *
import math
import random
from icecream import ic
from player import Spritesheet

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y,max_travel):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self,self.groups)
        
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE
        
        self.x_change = 0
        self.y_change = 0
        
        self.facing = random.choice(['left','right'])
        self.animation_loop = 1
        self.movement_loop = 0
        # self.max_travel = random.randint(30)
        self.max_travel = max_travel

        self.image = self.game.enemy_spritesheet.get_sprite(3,2,self.width,self.height)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
        self.current_health = ENEMY_MAX_HEALTH
        
        self.do_change = False
        self.attack_ratio = 0
        
    def update(self):
        self.movement()
        self.animate()
        self.collide_player()
        self.rect.x += self.x_change
        self.collide = self.collide_blocks()
        self.rect.y += self.y_change
        self.attack_player()
        self.x_change = 0
        self.y_change = 0
    
    def attack_player(self):
        if abs(self.rect.y - self.game.player.rect.y) <= 64:
            if abs(self.rect.x - self.game.player.rect.x) <= 64 and self.attack_ratio == 0:
                channel = pygame.mixer.find_channel()
                sound = pygame.mixer.Sound('resources\\sounds\\sword_fight_1.wav')
                sound.set_volume(0.15)
                channel.play(sound)
                if self.facing == 'right':
                    Attack(self.game,self.rect.x + TILESIZE,self.rect.y,'player')
                if self.facing == 'left':
                    Attack(self.game,self.rect.x - TILESIZE,self.rect.y,'player')
            if self.attack_ratio <15:
                self.attack_ratio += 0.5
            if self.attack_ratio == 15:
                self.attack_ratio = 0;
    
    def collide_player(self):
        hits = pygame.sprite.spritecollide(self, self.game.players, False)
        if hits:
            self.x_change = 0
    
    def collide_blocks(self):
        hits = pygame.sprite.spritecollide(self, self.game.collisions, False)
        if hits:
            if self.x_change > 0:
                self.rect.x = hits[0].rect.left - self.rect.width
                self.facing = 'left'
                self.facing = 'l_col'
            if self.x_change < 0:
                self.rect.x = hits[0].rect.right
                self.facing = 'right'
                self.facing = 'r_col'

    def movement(self):
        if self.facing == 'left':
            if abs(self.rect.y-self.game.player.rect.y)<=128 and abs(self.rect.x-self.game.player.rect.x)<=128:
                if self.rect.x - self.game.player.rect.x > 0:
                    self.x_change -= ENEMY_SPEED
                    self.movement_loop -= 1
                else:
                    self.facing = 'stay'
            else:
                self.x_change -= ENEMY_SPEED
                self.movement_loop -= 1
        if self.facing == 'right':
            if abs(self.rect.y-self.game.player.rect.y)<=128 and abs(self.rect.x-self.game.player.rect.x)<=128:
                if self.rect.x - self.game.player.rect.x < 0:
                    self.x_change += ENEMY_SPEED
                    self.movement_loop += 1
                else:
                    self.facing = 'stay'
            else:
                self.x_change += ENEMY_SPEED
                self.movement_loop += 1
        if self.facing == 'stay':
            if abs(self.rect.y-self.game.player.rect.y)<=128 and abs(self.rect.x-self.game.player.rect.x)<=128:
                if self.rect.x - self.game.player.rect.x >= 8:
                    self.facing = 'left'
                elif self.rect.x - self.game.player.rect.x <= -8:
                    self.facing = 'right'
                else:
                    self.facing = 'stay'
            else:
                self.facing = random.choice(['left','right'])
        if self.facing == 'l_col':
            if abs(self.rect.y-self.game.player.rect.y)>128 or self.rect.x - self.game.player.rect.x > 0 or self.rect.x - self.game.player.rect.x < -128:
                self.facing = 'left'
        if self.facing == 'r_col':
            if abs(self.rect.y-self.game.player.rect.y)>128 or self.rect.x - self.game.player.rect.x < 0 or self.rect.x - self.game.player.rect.x > 128:
                self.facing = 'right'
        
 
    
    def animate(self):
        left_animations = [self.game.enemy_spritesheet.get_sprite(3, 98, self.width, self.height),
                           self.game.enemy_spritesheet.get_sprite(35, 98, self.width, self.height),
                           self.game.enemy_spritesheet.get_sprite(68, 98, self.width, self.height)]

        right_animations = [self.game.enemy_spritesheet.get_sprite(3, 66, self.width, self.height),
                            self.game.enemy_spritesheet.get_sprite(35, 66, self.width, self.height),
                            self.game.enemy_spritesheet.get_sprite(68, 66, self.width, self.height)]
    
        
        if self.facing == "left":
            if self.x_change == 0:
                self.image = self.game.enemy_spritesheet.get_sprite(3, 98, self.width, self.height)
            else:
                self.image = left_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1
        
        if self.facing == "right":
            if self.x_change == 0:
                self.image = self.game.enemy_spritesheet.get_sprite(3, 66, self.width, self.height)
            else:
                self.image = right_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1
        
          
        
    def get_damage(self,amount):
        self.current_health -= amount
        if self.current_health <=0:
            channel = pygame.mixer.find_channel()
            sound = pygame.mixer.Sound('resources\\sounds\\harm.wav')
            sound.set_volume(0.2)
            channel.play(sound)
            self.kill()

class Attack(pygame.sprite.Sprite):
    def __init__(self, game, x, y, entity):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.attack
        pygame.sprite.Sprite.__init__(self,self.groups)
        
        self.reciever = entity
        
        self.x = x 
        self.y = y
        self.width = TILESIZE
        self.height = TILESIZE
        
        self.animation_loop = 0

        self.image = self.game.attack_spritesheet.get_sprite(0,0,self.width,self.height)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
        self.recieved = False
        
    def update(self):
        self.animate()
        self.collide()
        
    def collide(self):
        if self.reciever == 'enemy':
            hits = pygame.sprite.spritecollide(self,self.game.enemies,False)
            if hits and not self.recieved:
                self.recieved = True
                for enemy in hits:
                    enemy.get_damage(self.game.player.attack)
        if self.reciever == 'player':
            hits = pygame.sprite.spritecollide(self,self.game.players,False)
            if hits and not self.recieved:
                self.recieved = True
                for player in hits:
                    player.get_damage(self.game.player.attack)
            
    def animate(self):
        direction = self.game.player.facing
        right_animations = [self.game.attack_spritesheet.get_sprite(0, 64, self.width, self.height),
                        self.game.attack_spritesheet.get_sprite(32, 64, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(64, 64, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(96, 64, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(128, 64, self.width, self.height)]

        left_animations = [self.game.attack_spritesheet.get_sprite(0, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(32, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(64, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(96, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(128, 96, self.width, self.height)]
        if direction == 'right':
            self.image = right_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                if self.reciever == 'enemy':
                    self.game.player.is_attacking = False
                self.kill()
        
        if direction == 'left':
            self.image = left_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                if self.reciever == 'enemy':
                    self.game.player.is_attacking = False
                self.kill()
            
            