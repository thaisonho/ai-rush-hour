import pygame
from vehicle import Vehicle
from board import Board
from spritesheet import SpriteSheet


class GUI:
    def __init__(self, board):
        pygame.init()
        self.screen_size = (1000, 800)
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Rush Hour Solver")

        self._load_original_images()
        self.set_board(board)

    def _load_original_images(self):
        """Load all images once and store the original surfaces."""
        sprites = SpriteSheet("assets/img/bk_cars1.a.png")
        self.original_car_images = {
            "red": sprites.parse_sprite("red_car-0"),
            "L2": [
                sprites.parse_sprite("v2_0-0"),
                sprites.parse_sprite("v2_0-1"),
                sprites.parse_sprite("v2_1-0"),
                sprites.parse_sprite("v2_1-1"),
                sprites.parse_sprite("v2_2-0"),
                sprites.parse_sprite("v2_2-1"),
                sprites.parse_sprite("v2_2-2"),
            ],
            "L3": [
                sprites.parse_sprite("v3_0-0"),
                sprites.parse_sprite("v3_1-0"),
                sprites.parse_sprite("v3_2-0"),
            ],
        }
        self.original_road_images = {
            "road": SpriteSheet("assets/img/Road_01_Tile_05.png").parse_sprite(
                "road-0"
            ),
            "border": SpriteSheet("assets/img/Road_Side_02.png").parse_sprite(
                "border-0"
            ),
            "corner": SpriteSheet("assets/img/Road_Round_Corner.png").parse_sprite(
                "corner-0"
            ),
        }
        self.original_bg_images = {
            "grass": SpriteSheet("assets/img/Grass_Tile.png").parse_sprite("grass-0"),
        }
        self.logo_image = pygame.image.load("assets/img/logo.png")

    def _scale_images(self):
        """Rescale all images based on the current cell_size."""
        self.car_images = {
            "red": self.original_car_images["red"],  # Will be scaled in draw_vehicles
            "L2": self.original_car_images["L2"],
            "L3": self.original_car_images["L3"],
        }

        self.border_scale_factor = (self.cell_size, self.cell_size / 6)
        self.road_images = {
            "road": pygame.transform.scale(
                self.original_road_images["road"], (self.cell_size, self.cell_size)
            ),
            "border": pygame.transform.scale(
                self.original_road_images["border"], self.border_scale_factor
            ),
            "corner": pygame.transform.scale(
                self.original_road_images["corner"],
                (self.border_scale_factor[1] + 5, self.border_scale_factor[1] + 5),
            ),
        }
        self.grass_image = pygame.transform.scale(
            self.original_bg_images["grass"], (self.cell_size, self.cell_size)
        )
        self.logo = pygame.transform.scale(
            self.logo_image,
            (self.logo_image.get_width() // 3, self.logo_image.get_height() // 3),
        )

    def set_board(self, board):
        """Set a new board and recalculate all board-dependent properties."""
        self.board = board
        self.cell_size = min(self.screen_size) // (board.width + 4)
        self.grid_width = self.board.width * self.cell_size
        self.grid_height = self.board.height * self.cell_size
        self.grid_offset = (
            (self.screen_size[0] - self.grid_width) // 2,
            (self.screen_size[1] - self.grid_height) // 2 + 30,
        )
        self._scale_images()

    def draw_logo(self):
        logo_rect = self.logo.get_rect(
            center=(self.screen_size[0] // 2, self.screen_size[1] // 8)
        )
        self.screen.blit(self.logo, logo_rect)

    def draw_background(self):
        for r in range(self.screen_size[1] // self.cell_size + 1):
            for c in range(self.screen_size[0] // self.cell_size + 1):
                self.screen.blit(
                    self.grass_image, (c * self.cell_size, r * self.cell_size)
                )

    def draw_road(self):
        # Draw road tiles
        for r in range(self.board.height):
            for c in range(self.board.width):
                self.screen.blit(
                    self.road_images["road"],
                    (
                        self.grid_offset[0] + c * self.cell_size,
                        self.grid_offset[1] + r * self.cell_size,
                    ),
                )

            # draw the exit road
            if self.board.vehicles[0].id == "R" and r == self.board.vehicles[0].y:
                for c in range(
                    self.board.width, self.screen_size[0] // self.cell_size + 1
                ):
                    self.screen.blit(
                        self.road_images["road"],
                        (
                            self.grid_offset[0] + c * self.cell_size,
                            self.grid_offset[1] + r * self.cell_size,
                        ),
                    )

        # Prepare rotated border images
        border_top = self.road_images["border"]
        border_right = pygame.transform.rotate(self.road_images["border"], -90)
        border_bottom = pygame.transform.rotate(self.road_images["border"], 180)
        border_left = pygame.transform.rotate(self.road_images["border"], 90)

        # Draw borders
        for c in range(self.board.width):
            self.screen.blit(
                border_top,
                (
                    self.grid_offset[0] + c * self.cell_size,
                    self.grid_offset[1] - self.border_scale_factor[1],
                ),
            )  # Top
            self.screen.blit(
                border_bottom,
                (
                    self.grid_offset[0] + c * self.cell_size,
                    self.grid_offset[1] + self.board.height * self.cell_size,
                ),
            )  # Bottom
        for r in range(self.board.height):
            self.screen.blit(
                border_left,
                (
                    self.grid_offset[0] - self.border_scale_factor[1],
                    self.grid_offset[1] + r * self.cell_size,
                ),
            )  # Left
            if self.board.vehicles[0].id == "R" and r == self.board.vehicles[0].y:
                continue
            self.screen.blit(
                border_right,
                (
                    self.grid_offset[0] + self.board.width * self.cell_size,
                    self.grid_offset[1] + r * self.cell_size,
                ),
            )  # Right

        # Draw border for the exit road
        for c in range(self.board.width, self.screen_size[0] // self.cell_size + 1):
            self.screen.blit(
                border_top,
                (
                    self.grid_offset[0] + c * self.cell_size,
                    self.grid_offset[1]
                    - self.border_scale_factor[1]
                    + self.cell_size * self.board.vehicles[0].y,
                ),
            )
            self.screen.blit(
                border_bottom,
                (
                    self.grid_offset[0] + c * self.cell_size,
                    self.grid_offset[1]
                    + (self.board.vehicles[0].y + 1) * self.cell_size,
                ),
            )

        # Draw corners
        self.screen.blit(
            self.road_images["corner"],
            (
                self.grid_offset[0] - self.border_scale_factor[1],
                self.grid_offset[1] - self.border_scale_factor[1],
            ),
        )  # Top-left
        self.screen.blit(
            self.road_images["corner"],
            (
                self.grid_offset[0]
                + self.board.width * self.cell_size
                - self.border_scale_factor[1] / 3,
                self.grid_offset[1] - self.border_scale_factor[1],
            ),
        )  # Top-right
        self.screen.blit(
            self.road_images["corner"],
            (
                self.grid_offset[0] - self.border_scale_factor[1],
                self.grid_offset[1]
                + self.board.height * self.cell_size
                - self.border_scale_factor[1] / 3,
            ),
        )  # Bottom-left
        self.screen.blit(
            self.road_images["corner"],
            (
                self.grid_offset[0]
                + self.board.width * self.cell_size
                - self.border_scale_factor[1] / 3,
                self.grid_offset[1]
                + self.board.height * self.cell_size
                - self.border_scale_factor[1] / 3,
            ),
        )  # Bottom-right

    def draw_vehicles(self):
        for vehicle in self.board.vehicles:
            if vehicle.id == "R":
                image = self.car_images["red"]
            elif vehicle.length == 2:
                image_index = ord(vehicle.id[0]) % len(self.car_images["L2"])
                image = self.car_images["L2"][image_index]
            elif vehicle.length == 3:
                image_index = ord(vehicle.id[0]) % len(self.car_images["L3"])
                image = self.car_images["L3"][image_index]
            else:
                continue

            scaled_image = pygame.transform.scale(
                image, (self.cell_size, self.cell_size * vehicle.length)
            )

            if vehicle.orientation == "H":
                scaled_image = pygame.transform.rotate(scaled_image, -90)

            self.screen.blit(
                scaled_image,
                (
                    self.grid_offset[0] + vehicle.x * self.cell_size,
                    self.grid_offset[1] + vehicle.y * self.cell_size,
                ),
            )

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.draw_background()
            self.draw_logo()
            self.draw_road()
            self.draw_vehicles()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    vehicles = [
        Vehicle("R", 1, 2, 2, "H"),
        Vehicle("A", 0, 0, 2, "H"),
        Vehicle("B", 2, 0, 2, "H"),
        Vehicle("C", 4, 0, 2, "V"),
        Vehicle("D", 3, 1, 2, "V"),
        Vehicle("E", 0, 4, 2, "H"),
        Vehicle("F", 2, 3, 3, "V"),
        Vehicle("G", 3, 3, 3, "H"),
        Vehicle("H", 5, 4, 2, "V"),
    ]

    # Create the game board
    board = Board(6, 6, vehicles)

    gui = GUI(board)
    gui.run()
