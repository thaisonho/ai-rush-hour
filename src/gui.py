import pygame
import os
from vehicle import Vehicle
from board import Board
from spritesheet import SpriteSheet

class GUI:
    def __init__(self, board):
        pygame.init()
        self.board = board
        self.screen_size = (600, 800)
        self.cell_size = self.screen_size[0] // board.width
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Rush Hour Solver")

        self.car_images = self.load_car_images()

    def load_car_images(self):
        sprites = SpriteSheet("assets/img/bk_cars1.a.png")
        images = {
            'red': sprites.parse_sprite('red_car-0'),
            'L2': [
                sprites.parse_sprite("v2_0-0"), sprites.parse_sprite("v2_0-1"),
                sprites.parse_sprite("v2_1-0"), sprites.parse_sprite("v2_1-1"),
                sprites.parse_sprite("v2_2-0"), sprites.parse_sprite("v2_2-1"), sprites.parse_sprite("v2_2-2"),
            ],
            'L3': [
                sprites.parse_sprite("v3_0-0"),
                sprites.parse_sprite("v3_1-0"),
                sprites.parse_sprite("v3_2-0")
            ]
        }
        return images

    def load_road_images(self):
        sprites = SpriteSheet("assets/img/Road_01_Tile_05.png")
        image = sprites.parse_sprite("road-0")
        return image
    
    def draw_board(self):
        self.screen.fill((255, 255, 255))
        for r in range(self.board.height):
            for c in range(self.board.width):
                pygame.draw.rect(self.screen, (200, 200, 200), (c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size), 1)

    def draw_vehicles(self):
        for vehicle in self.board.vehicles:
            if vehicle.id == 'R':
                image = self.car_images['red']
            elif vehicle.length == 2:
                image_index = ord(vehicle.id[0]) % len(self.car_images['L2'])
                image = self.car_images['L2'][image_index]
            elif vehicle.length == 3:
                image_index = ord(vehicle.id[0]) % len(self.car_images['L3'])
                image = self.car_images['L3'][image_index]
            else:
                continue

            if vehicle.orientation == 'H':
                image = pygame.transform.rotate(image, -90)

            width = image.get_width()
            height = image.get_height()
            
            scaled_image = pygame.transform.scale(image, (width / 50 * self.cell_size, height / 50 * self.cell_size))

            self.screen.blit(scaled_image, (vehicle.x * self.cell_size, vehicle.y * self.cell_size))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw_board()
            self.draw_vehicles()
            pygame.display.flip()

        pygame.quit()

vehicles = [
        Vehicle('R', 1, 2, 2, 'H'),
        Vehicle('A', 0, 0, 2, 'H'),
        Vehicle('B', 2, 0, 2, 'H'),
        Vehicle('C', 4, 0, 2, 'V'),
        Vehicle('D', 3, 1, 2, 'V'),
        Vehicle('E', 0, 4, 2, 'H'),
        Vehicle('F', 2, 3, 3, 'V'),
        Vehicle('G', 3, 3, 3, 'H'),
        Vehicle('H', 5, 4, 2, 'V'),

    ]

# Create the game board
board = Board(6, 6, vehicles)

gui = GUI(board)
gui.run()