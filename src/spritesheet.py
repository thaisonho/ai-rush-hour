import pygame
import json

class SpriteSheet:
    def __init__(self, filename):
        self.filename = filename
        self.spritesheet = pygame.image.load(filename).convert_alpha()
        with open(filename.replace('.png', '.json'), 'r') as f:
            self.data = json.load(f)

    def parse_sprite(self, name):
        sprite_info = self.data['frames'][name]['frame']
        x, y, w, h = sprite_info['x'], sprite_info['y'], sprite_info['w'], sprite_info['h']
        image = pygame.Surface((w, h), pygame.SRCALPHA)
        image.blit(self.spritesheet, (0, 0), (x, y, w, h))
        return image