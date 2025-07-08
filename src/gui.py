import pygame
from vehicle import Vehicle
from board import Board
from spritesheet import SpriteSheet

class GUI:
    def __init__(self, board):
        pygame.init()
        self.board = board
        self.screen_size = (1000, 800)
        self.cell_size = min(self.screen_size) // (board.width + 4)
        self.grid_width = self.board.width * self.cell_size
        self.grid_height = self.board.height * self.cell_size
        self.grid_offset = (
            (self.screen_size[0] - self.grid_width) // 2,
            (self.screen_size[1] - self.grid_height) // 2
        )
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
        road = SpriteSheet("assets/img/Road_01_Tile_05.png").parse_sprite("road-0")
        border = SpriteSheet("assets/img/Road_Side_02.png").parse_sprite("border-0")
        image = {
            'road': road,
            'border': border,
        }
        return image

    def load_bg_images(self):
        grass = SpriteSheet("assets/img/Grass_Tile.png").parse_sprite("grass-0") 
        image = {
            'grass': grass,
        }
        return image

    def draw_background(self):
        if not hasattr(self, 'bg_image'):
            self.bg_images = self.load_bg_images()
            self.grass_image = self.bg_images['grass']
            self.grass_image = pygame.transform.scale(self.grass_image, (self.cell_size, self.cell_size))
            
            for r in range(self.screen_size[1] // self.cell_size + 1):
                for c in range(self.screen_size[0] // self.cell_size + 1):
                    self.screen.blit(self.grass_image, (c * self.cell_size, r * self.cell_size))

    def draw_road(self):
        # Load images
        if not hasattr(self, 'road_images'):
            self.road_images = self.load_road_images()
            self.border_scale_factor = (self.cell_size, self.cell_size / 6)
            # Scale images once
            self.road_images['road'] = pygame.transform.scale(self.road_images['road'], (self.cell_size, self.cell_size))
            self.road_images['border'] = pygame.transform.scale(self.road_images['border'], self.border_scale_factor)

        # Draw road tiles
        for r in range(self.board.height):
            for c in range(self.board.width):
                self.screen.blit(self.road_images['road'], (self.grid_offset[0] + c * self.cell_size, self.grid_offset[1] + r * self.cell_size))

        # Prepare rotated border images
        border_top = self.road_images['border']
        border_right = pygame.transform.rotate(self.road_images['border'], -90)
        border_bottom = pygame.transform.rotate(self.road_images['border'], 180)
        border_left = pygame.transform.rotate(self.road_images['border'], 90)

        # Draw borders
        for c in range(self.board.width):
            self.screen.blit(border_top, (self.grid_offset[0] + c * self.cell_size, self.grid_offset[1] - self.border_scale_factor[1])) # Top
            self.screen.blit(border_bottom, (self.grid_offset[0] + c * self.cell_size, self.grid_offset[1] + self.board.height * self.cell_size)) # Bottom
        for r in range(self.board.height):
            self.screen.blit(border_left, (self.grid_offset[0] - self.border_scale_factor[1], self.grid_offset[1] + r * self.cell_size)) # Left
            self.screen.blit(border_right, (self.grid_offset[0] + self.board.width * self.cell_size, self.grid_offset[1] + r * self.cell_size)) # Right

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

            self.screen.blit(scaled_image, (self.grid_offset[0] + vehicle.x * self.cell_size, self.grid_offset[1] + vehicle.y * self.cell_size))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.draw_background()
            self.draw_road()
            self.draw_vehicles()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
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

