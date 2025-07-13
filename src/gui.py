import pygame
import time
import copy
import os
from vehicle import Vehicle
from board import Board
from spritesheet import SpriteSheet
from solver import UCSSolver, BFSSolver, DFSSolver, IDSSolver, AStarSolver


class GUI:
    def __init__(self, board):
        pygame.init()
        self.screen_size = (1000, 800)
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Rush Hour Solver")

        # Game state variables
        self.original_board = copy.deepcopy(board)
        self.current_solution = None
        self.animation_moves = []
        self.current_move_index = 0
        self.is_playing = False
        self.is_paused = False
        self.is_solving = False
        self.animation_finished = False
        self.solution_found = False
        self.last_move_time = 0
        self.move_duration = 1000  # milliseconds (use as animation speed)
        self.solver_stats = None

        # Speed control for animation
        self.animation_speed = 1  
        self.max_speed = 4

        # Cost tracking for UCS and A*
        self.total_cost = 0  # Total cost of the solution
        self.current_cost = 0  # Current cost during animation
        self.current_h_cost = 0  # Current heuristic cost for A*
        self.current_g_cost = 0  # Current g cost for A*

        # Algorithm selectoin
        self.selected_algorithm = "BFS"
        self.algorithms = ["BFS", "DFS", "UCS", "IDS", "A*"]
        self.algorithm_index = 0

        # Map selection
        self.selected_map = 1
        self.max_maps = 10

        # Button rectangles for click detection
        self.play_btn_rect = None
        self.pause_btn_rect = None
        self.restart_btn_rect = None
        self.speedup_btn_rect = None
        self.algo_left_arrow_rect = None
        self.algo_right_arrow_rect = None
        self.map_left_arrow_rect = None
        self.map_right_arrow_rect = None

        self._load_original_images()
        self.load_map(self.selected_map)
        self.set_board(self.current_board)

    def _load_original_images(self):
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
        self.bar = pygame.image.load("assets/img/Table.png")
        self.left_arrow = SpriteSheet("assets/img/Left.png").parse_sprite("left-0")
        self.right_arrow = SpriteSheet("assets/img/Right.png").parse_sprite("right-0")
        self.finished_image = pygame.image.load("assets/img/Finish.png")
        self.measurements_box = pygame.image.load("assets/img/Window.png")
        self.play_btn = pygame.image.load("assets/img/Play_BTN.png")
        self.pause_btn = pygame.image.load("assets/img/Pause_BTN.png")
        self.replay_btn = pygame.image.load("assets/img/Replay_BTN.png")
        self.speedup_btn = pygame.image.load("assets/img/SpeedUp_BTN.png")

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
        self.bar = pygame.transform.scale(
            self.bar, (self.cell_size * 3, self.cell_size)
        )
        self.left_arrow = pygame.transform.scale(
            self.left_arrow, (self.bar.get_height() // 2, self.bar.get_height() // 2)
        )
        self.right_arrow = pygame.transform.scale(
            self.right_arrow, (self.bar.get_height() // 2, self.bar.get_height() // 2)
        )
        self.finished_image = pygame.transform.scale(
            self.finished_image, (self.cell_size, self.cell_size // 2)
        )
        self.measurements_box = pygame.transform.scale(
            self.measurements_box, (self.cell_size * 3, self.cell_size * 4)
        )
        self.play_btn = pygame.transform.scale(
            self.play_btn, (self.cell_size, self.cell_size)
        )
        self.pause_btn = pygame.transform.scale(
            self.pause_btn, (self.cell_size, self.cell_size)
        )
        self.replay_btn = pygame.transform.scale(
            self.replay_btn, (self.cell_size, self.cell_size)
        )
        self.speedup_btn = pygame.transform.scale(
            self.speedup_btn, (self.cell_size, self.cell_size)
        )

    def set_board(self, board):
        """Set a new board and adjust properties accordingly."""
        self.board = board
        self.cell_size = min(self.screen_size) // (board.width + 4)
        self.grid_width = self.board.width * self.cell_size
        self.grid_height = self.board.height * self.cell_size
        self.grid_offset = (
            (self.screen_size[0] - self.grid_width) // 2,
            (self.screen_size[1] - self.grid_height) // 2 + 30,
        )
        self._scale_images()

    def load_map(self, map_number):
        try:
            map_file = f"src/map/map{map_number:02d}.txt"

            # Read and parse the map file
            with open(map_file, "r") as f:
                content = f.read().strip()

            if not content:
                print(f"Map {map_number} is empty, using default map")
                self.current_board = self.original_board
                return

            # this to store map content
            local_vars = {}
            exec(content, {"Vehicle": Vehicle}, local_vars)

            if "vehicles" in local_vars:
                vehicles = local_vars["vehicles"]
                self.current_board = Board(6, 6, vehicles)
                print(f"Loaded map {map_number} with {len(vehicles)} vehicles")
            else:
                print(f"No vehicles found in map {map_number}, using default map")
                self.current_board = self.original_board

        except Exception as e:
            print(f"Error loading map {map_number}: {e}")
            # If there any errors, use the original board
            self.current_board = self.original_board

    def draw_logo(self):
        logo_rect = self.logo.get_rect(
            center=(self.screen_size[0] // 2, self.screen_size[1] // 8)
        )
        self.screen.blit(self.logo, logo_rect)

    def draw_bars(self):
        # Calculate positions for two bars
        bar_spacing = self.cell_size * 1.2
        bar_y_start = (self.screen_size[1] - self.cell_size * 2.5) // 2

        # Draw the algorithm selection bar (top bar)
        algo_bar_y = bar_y_start
        self.screen.blit(self.bar, (0, algo_bar_y))

        # Store algorithm arrow button rectangles for click detection
        self.algo_left_arrow_rect = pygame.Rect(
            0,
            (self.bar.get_height() - self.left_arrow.get_height()) // 2 + algo_bar_y,
            self.left_arrow.get_width(),
            self.left_arrow.get_height(),
        )
        self.algo_right_arrow_rect = pygame.Rect(
            self.bar.get_width() - self.right_arrow.get_width() - 10,
            (self.bar.get_height() - self.right_arrow.get_height()) // 2 + algo_bar_y,
            self.right_arrow.get_width(),
            self.right_arrow.get_height(),
        )

        self.screen.blit(
            self.left_arrow,
            (
                0,
                (self.bar.get_height() - self.left_arrow.get_height()) // 2
                + algo_bar_y,
            ),
        )
        self.screen.blit(
            self.right_arrow,
            (
                self.bar.get_width() - self.right_arrow.get_width() - 10,
                (self.bar.get_height() - self.right_arrow.get_height()) // 2
                + algo_bar_y,
            ),
        )

        # Draw algorithm name in the center of the bar
        if not hasattr(self, "bar_font"):
            pygame.font.init()
            self.bar_font = pygame.font.Font(
                "assets/fonts/pricedown.ttf", self.cell_size - 25
            )

        algo_text = self.bar_font.render(
            f"{self.selected_algorithm}", True, (255, 255, 255)
        )
        text_rect = algo_text.get_rect(
            center=(self.bar.get_width() // 2, algo_bar_y + self.bar.get_height() // 2)
        )
        self.screen.blit(algo_text, text_rect)

        # Draw the map selection bar (bottom bar)
        map_bar_y = algo_bar_y + bar_spacing
        self.screen.blit(self.bar, (0, map_bar_y))

        # Store map arrow button rectangles for click detection
        self.map_left_arrow_rect = pygame.Rect(
            0,
            (self.bar.get_height() - self.left_arrow.get_height()) // 2 + map_bar_y,
            self.left_arrow.get_width(),
            self.left_arrow.get_height(),
        )
        self.map_right_arrow_rect = pygame.Rect(
            self.bar.get_width() - self.right_arrow.get_width() - 10,
            (self.bar.get_height() - self.right_arrow.get_height()) // 2 + map_bar_y,
            self.right_arrow.get_width(),
            self.right_arrow.get_height(),
        )

        self.screen.blit(
            self.left_arrow,
            (
                0,
                (self.bar.get_height() - self.left_arrow.get_height()) // 2 + map_bar_y,
            ),
        )
        self.screen.blit(
            self.right_arrow,
            (
                self.bar.get_width() - self.right_arrow.get_width() - 10,
                (self.bar.get_height() - self.right_arrow.get_height()) // 2
                + map_bar_y,
            ),
        )

        # Draw map name in the center of the bar
        map_text = self.bar_font.render(
            f"Map: {self.selected_map}", True, (255, 255, 255)
        )
        text_rect = map_text.get_rect(
            center=(self.bar.get_width() // 2, map_bar_y + self.bar.get_height() // 2)
        )
        self.screen.blit(map_text, text_rect)

    def draw_measurements_box(self):
        box_x = self.grid_offset[0] + self.cell_size * self.board.width + 20
        box_y = (self.screen_size[1] - self.measurements_box.get_height()) // 2
        self.screen.blit(self.measurements_box, (box_x, box_y))

        # Initialize font if not already done
        if not hasattr(self, "font"):
            pygame.font.init()
            self.font = pygame.font.Font(None, 24)
            self.large_font = pygame.font.Font(
                "assets/fonts/pricedown.ttf", self.cell_size // 2
            )
            self.small_font = pygame.font.Font("assets/fonts/ChaletComprime-CologneSixty.otf", 20)

        # Draw title
        title_text = self.large_font.render("Statistics", True, (255, 255, 255))
        self.screen.blit(
            title_text,
            (
                box_x
                + (self.measurements_box.get_width() - title_text.get_width()) // 2,
                box_y + 5,
            ),
        )

        current_y = box_y + 50
        line_spacing = 25

        # Draw solver statistics if available
        if self.solver_stats:
            # Search time
            time_text = self.small_font.render(
                f"Search Time: {self.solver_stats['search_time']:.4f}s",
                True,
                (255, 255, 255),
            )
            self.screen.blit(time_text, (box_x + 30, current_y))
            current_y += line_spacing

            # Memory usage
            memory_text = self.small_font.render(
                f"Memory Usage: {self.solver_stats['memory_usage']:.2f} KB",
                True,
                (255, 255, 255),
            )
            self.screen.blit(memory_text, (box_x + 30, current_y))
            current_y += line_spacing

            # Nodes expanded
            nodes_text = self.small_font.render(
                f"Nodes Expanded: {self.solver_stats['nodes_expanded']}",
                True,
                (255, 255, 255),
            )
            self.screen.blit(nodes_text, (box_x + 30, current_y))
            current_y += line_spacing

        if self.is_solving:
            status_text = self.large_font.render("Solving...", True, (255, 165, 0))
            text_x = (
                box_x
                + (self.measurements_box.get_width() - status_text.get_width()) // 2
            )
            text_y = box_y + self.measurements_box.get_height() - 60
            self.screen.blit(status_text, (text_x, text_y))

        elif self.solution_found and self.current_solution:
            found_solution_text = self.large_font.render(
                "Solution Found!", True, (0, 200, 0)
            )
            text_x = (
                box_x
                + (self.measurements_box.get_width() - found_solution_text.get_width())
                // 2
            )
            text_y = box_y + self.measurements_box.get_height() - 60
            self.screen.blit(found_solution_text, (text_x, text_y))
            # Total moves
            total_text = self.small_font.render(
                f"Total Moves: {len(self.current_solution)}", True, (255, 255, 255)
            )
            self.screen.blit(total_text, (box_x + 30, current_y))
            current_y += line_spacing

            # Current move
            current_step_text = self.small_font.render(
                f"Current Move: {self.current_move_index}", True, (255, 255, 255)
            )
            self.screen.blit(current_step_text, (box_x + 30, current_y))
            current_y += line_spacing

            # Display algorithm-specific cost information
            if self.selected_algorithm == "UCS":
                # UCS: Total cost and current cost
                total_cost_text = self.small_font.render(
                    f"Total Cost: {self.total_cost}", True, (255, 255, 255)
                )
                self.screen.blit(total_cost_text, (box_x + 30, current_y))
                current_y += line_spacing

                current_cost_text = self.small_font.render(
                    f"Current Cost: {self.current_cost}", True, (255, 255, 255)
                )
                self.screen.blit(current_cost_text, (box_x + 30, current_y))
                current_y += line_spacing

            elif self.selected_algorithm == "A*":
                # A*: Total cost, g(current), and h(current)
                total_cost_text = self.small_font.render(
                    f"Total Cost: {self.total_cost}", True, (255, 255, 255)
                )
                self.screen.blit(total_cost_text, (box_x + 30, current_y))
                current_y += line_spacing

                g_cost_text = self.small_font.render(
                    f"g(current): {self.current_g_cost}", True, (255, 255, 255)
                )
                self.screen.blit(g_cost_text, (box_x + 30, current_y))
                current_y += line_spacing

                h_cost_text = self.small_font.render(
                    f"h(current): {self.current_h_cost}", True, (255, 255, 255)
                )
                self.screen.blit(h_cost_text, (box_x + 30, current_y))
                current_y += line_spacing
        elif self.solution_found == False and self.solver_stats:
            # Show "No Solution" message
            no_solution_text = self.large_font.render("No Solution", True, (200, 0, 0))
            text_x = (
                box_x
                + (self.measurements_box.get_width() - no_solution_text.get_width())
                // 2
            )
            text_y = box_y + self.measurements_box.get_height() - 60
            self.screen.blit(no_solution_text, (text_x, text_y))

    def draw_control_buttons(self):
        """Draw control buttons below the map."""
        # Position buttons below the game board
        btn_x = (self.screen_size[0] - self.play_btn.get_width()) // 2
        btn_y = self.grid_offset[1] + self.grid_height + 20
        btn_spacing = self.cell_size + 10

        # Reset button rectangles
        self.play_btn_rect = None
        self.pause_btn_rect = None
        self.restart_btn_rect = None
        self.speedup_btn_rect = None

        # Show restart/replay button on the left if any solution activity has occurred or game is in progress
        if (
            self.solution_found
            or self.is_playing
            or self.is_paused
            or self.animation_finished
            or self.solver_stats is not None
        ):
            restart_x = btn_x - btn_spacing
            self.restart_btn_rect = pygame.Rect(
                restart_x, btn_y, self.cell_size, self.cell_size
            )
            self.screen.blit(self.replay_btn, (restart_x, btn_y))  # Using replay image for both restart and replay

        # Determine which button to show in the middle
        if not self.is_playing and not self.is_paused:
            # Show play button
            self.play_btn_rect = pygame.Rect(
                btn_x, btn_y, self.cell_size, self.cell_size
            )
            self.screen.blit(self.play_btn, (btn_x, btn_y))
        elif self.is_playing and not self.is_paused:
            # Show pause button
            self.pause_btn_rect = pygame.Rect(
                btn_x, btn_y, self.cell_size, self.cell_size
            )
            self.screen.blit(self.pause_btn, (btn_x, btn_y))
        else:
            # Show play button when paused
            self.play_btn_rect = pygame.Rect(
                btn_x, btn_y, self.cell_size, self.cell_size
            )
            self.screen.blit(self.play_btn, (btn_x, btn_y))

        # Show speed up button on the right if solution is found
        if self.solution_found:
            speedup_x = btn_x + btn_spacing
            self.speedup_btn_rect = pygame.Rect(
                speedup_x, btn_y, self.cell_size, self.cell_size
            )
            self.screen.blit(self.speedup_btn, (speedup_x, btn_y))

        # Draw button labels
        if not hasattr(self, "button_font"):
            self.button_font = pygame.font.Font(None, 20)

        # Label for restart/replay button (on the left)
        if (
            self.solution_found
            or self.is_playing
            or self.is_paused
            or self.animation_finished
            or self.solver_stats is not None
        ):
            restart_x = btn_x - btn_spacing
            # Use "Replay" if there's a solution, otherwise "Restart"
            button_text = "Replay" if (self.solution_found and self.current_solution) else "Restart"
            restart_label = self.button_font.render(button_text, True, (255, 255, 255))
            self.screen.blit(
                restart_label,
                (
                    restart_x + (self.replay_btn.get_width() - restart_label.get_width()) // 2,
                    btn_y + self.cell_size + 5,
                ),
            )

        # Label for center button (play/pause)
        if self.is_playing and not self.is_paused:
            label_text = self.button_font.render("Pause", True, (255, 255, 255))
        else:
            label_text = self.button_font.render("Play", True, (255, 255, 255))
        self.screen.blit(
            label_text,
            (
                btn_x + (self.play_btn.get_width() - label_text.get_width()) // 2,
                btn_y + self.cell_size + 5,
            ),
        )

        # Label for speed up button (on the right)
        if self.solution_found:
            speedup_x = btn_x + btn_spacing
            speed_label = self.button_font.render(f"Speed: {self.animation_speed}x", True, (255, 255, 255))
            self.screen.blit(
                speed_label,
                (
                    speedup_x + (self.speedup_btn.get_width() - speed_label.get_width()) // 2,
                    btn_y + self.cell_size + 5,
                ),
            )

    def draw_background(self):
        for r in range(self.screen_size[1] // self.cell_size + 1):
            for c in range(self.screen_size[0] // self.cell_size + 1):
                self.screen.blit(
                    self.grass_image, (c * self.cell_size, r * self.cell_size)
                )
        self.draw_bars()

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
            # draw the finish line
            if r == self.board.vehicles[0].y:
                self.screen.blit(
                    self.finished_image,
                    (
                        self.grid_offset[0] + (self.board.width - 1) * self.cell_size,
                        self.grid_offset[1] + (0.5 + r) * self.cell_size,
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
            self.screen.blit(
                border_right,
                (
                    self.grid_offset[0] + self.board.width * self.cell_size,
                    self.grid_offset[1] + r * self.cell_size,
                ),
            )  # Right

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

    def draw_red_car_tracker(self):
        """Draw a semi-transparent tracking frame around the red car."""
        red_car = None
        # Find the red car object in the current board's vehicle list
        for vehicle in self.board.vehicles:
            if vehicle.id == "R":
                red_car = vehicle
                break

        if not red_car:
            return

        # --- Calculate the tracker's position and size ---
        
        # Padding to make the frame slightly larger than the car
        padding = 3  

        # Base pixel coordinates of the car on the screen
        base_x = self.grid_offset[0] + red_car.x * self.cell_size
        base_y = self.grid_offset[1] + red_car.y * self.cell_size

        # Size of the car based on its length and orientation
        if red_car.orientation == "H":
            car_width = self.cell_size * red_car.length
            car_height = self.cell_size
        else:  # "V" 
            car_width = self.cell_size
            car_height = self.cell_size * red_car.length
            
        # Create a Rect for the tracker frame, including padding
        tracker_rect = pygame.Rect(
            base_x - padding,
            base_y - padding,
            car_width + padding * 2,
            car_height + padding * 2
        )

        # --- Draw the semi-transparent rectangle ---

        # Create a new Surface with the size of the tracker frame.
        tracker_surface = pygame.Surface(tracker_rect.size, pygame.SRCALPHA)

        # Fill the surface with the chosen color and transparency.
        # The color format is (R, G, B, Alpha).
        tracker_color = (102, 255, 178, 200)  
        tracker_surface.fill(tracker_color)

        # Blit (draw) the tracker surface onto the main screen at the calculated position.
        self.screen.blit(tracker_surface, tracker_rect.topleft)

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

    def solve_puzzle(self):
        """Solve the puzzle using the selected algorithm."""
        print(f"Solving with {self.selected_algorithm}...")

        # Reset board to original state
        self.board = copy.deepcopy(self.current_board)

        # Select appropriate solver
        if self.selected_algorithm == "BFS":
            solver = BFSSolver(self.board)
        elif self.selected_algorithm == "DFS":
            solver = DFSSolver(self.board)
        elif self.selected_algorithm == "UCS":
            solver = UCSSolver(self.board)
        elif self.selected_algorithm == "IDS":
            solver = IDSSolver(self.board)
        elif self.selected_algorithm == "A*":
            solver = AStarSolver(self.board)
        else:
            self.is_solving = False
            return False

        solution = solver.solve()
        self.is_solving = False

        # Store solver statistics
        self.solver_stats = solver.get_stats()

        if solution:
            print("Solution Found!")
            self.solution_found = True
            self.current_solution = solution
            self.animation_moves = solution
            self.current_move_index = 0
            self.animation_finished = False

            # Calculate total cost for UCS and A*
            if self.selected_algorithm in ["UCS", "A*"]:
                self.total_cost = self.calculate_ucs_cost(self.current_board, solution)
            else:
                self.total_cost = 0

            # Initialize current costs
            self.current_cost = 0
            self.current_g_cost = 0
            self.current_h_cost = 0

            return True
        else:
            print("No solution found.")
            self.solution_found = False
            return False

    def start_animation(self):
        """Start the solution animation."""
        if self.current_solution:
            self.is_playing = True
            self.is_paused = False
            self.last_move_time = pygame.time.get_ticks()

    def pause_animation(self):
        """Pause the animation."""
        self.is_paused = True
        self.is_playing = False

    def restart_game(self):
        """Restart animation or reset the game."""
        if self.solution_found and self.current_solution:
            # Just restart the animation with the existing solution
            self.board = copy.deepcopy(self.current_board)
            self.current_move_index = 0
            self.animation_finished = False
            self.is_paused = False
            self.is_playing = True  # Automatically start playing
            self.last_move_time = pygame.time.get_ticks()
            # Reset costs for animation
            self.current_cost = 0
            self.current_g_cost = 0
            self.current_h_cost = 0
        else:
            # Complete reset (when there's no solution yet)
            self.board = copy.deepcopy(self.current_board)
            self.current_move_index = 0
            self.animation_finished = False
            self.is_paused = False
            self.is_playing = False
            self.solution_found = False
            self.current_solution = None
            self.animation_moves = []
            self.solver_stats = None
            self.total_cost = 0
            self.current_cost = 0
            self.current_g_cost = 0
            self.current_h_cost = 0

        # Reset animation speed
        self.animation_speed = 1
        self.move_duration = 1000

    def calculate_ucs_cost(self, original_board, moves_so_far):
        """Calculate the total cost for UCS algorithm."""
        total_cost = 0
        current_board = copy.deepcopy(original_board)

        for move in moves_so_far:
            # Find the vehicle being moved
            moved_vehicle = None
            for vehicle in current_board.vehicles:
                if vehicle.id == move.vehicle_id:
                    moved_vehicle = vehicle
                    break

            if moved_vehicle:
                # UCS cost is vehicle length * distance moved
                move_cost = moved_vehicle.length * abs(move.amount)
                total_cost += move_cost

            # Apply the move for next iteration
            current_board = current_board.apply_move(move)

        return total_cost

    def calculate_astar_costs(self, board):
        """Calculate g(n) and h(n) costs for A* algorithm."""
        # g(n) is the same as UCS cost
        g_cost = self.current_cost
        
        # Use the A* solver's heuristic function directly to get h(n)
        # This ensures consistency between solver and GUI
        astar_solver = AStarSolver(board)
        h_cost = astar_solver._heuristic(board)
        
        return g_cost, h_cost

    def update_costs(self):
        """Update cost information during animation."""
        if not self.current_solution or self.current_move_index == 0:
            self.current_cost = 0
            self.current_g_cost = 0
            self.current_h_cost = 0
            return

        # Calculate costs based on algorithm
        if self.selected_algorithm == "UCS":
            moves_applied = self.current_solution[:self.current_move_index]
            self.current_cost = self.calculate_ucs_cost(self.current_board, moves_applied)

        elif self.selected_algorithm == "A*":
            moves_applied = self.current_solution[:self.current_move_index]
            self.current_cost = self.calculate_ucs_cost(self.current_board, moves_applied)
            self.current_g_cost, self.current_h_cost = self.calculate_astar_costs(self.board)

    def update_animation(self):
        """Update the animation state."""
        if not self.is_playing or self.is_paused or self.animation_finished:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= self.move_duration:
            if self.current_move_index < len(self.animation_moves):
                # Apply the current move
                move = self.animation_moves[self.current_move_index]
                self.board = self.board.apply_move(move)
                self.current_move_index += 1
                self.last_move_time = current_time

                # Update costs after applying the move
                self.update_costs()
            else:
                # Animation finished
                self.animation_finished = True
                self.is_playing = False

    def handle_play_button(self):
        """Handle play button click."""
        if not self.solution_found:
            # Set solving state first to show "Solving..." message
            self.is_solving = True
            # Process any pending events and redraw to show the "Solving..." message
            pygame.event.pump()
            self.draw_background()
            self.draw_logo()
            self.draw_road()
            self.draw_red_car_tracker()
            self.draw_vehicles()
            self.draw_control_buttons()
            self.draw_measurements_box()
            pygame.display.flip()

            # Small delay to ensure the message is visible
            pygame.time.wait(100)

            # Now try to solve the puzzle
            if self.solve_puzzle():
                self.start_animation()
        elif self.is_paused:
            # Resume animation
            self.is_playing = True
            self.is_paused = False
            self.last_move_time = pygame.time.get_ticks()
        else:
            # Start animation if solution exists
            self.start_animation()

    def handle_pause_button(self):
        """Handle pause button click."""
        if self.is_playing:
            self.pause_animation()

    def handle_restart_button(self):
        """Handle restart button click."""
        self.restart_game()

    def handle_algorithm_selection(self, direction):
        """Handle algorithm selection with arrow keys."""
        if direction == "left":
            self.algorithm_index = (self.algorithm_index - 1) % len(self.algorithms)
        elif direction == "right":
            self.algorithm_index = (self.algorithm_index + 1) % len(self.algorithms)

        self.selected_algorithm = self.algorithms[self.algorithm_index]

        # Reset solution state when algorithm changes
        # This is a complete reset since we need to solve with the new algorithm
        self.solution_found = False
        self.current_solution = None
        self.is_playing = False
        self.is_paused = False
        self.animation_finished = False
        self.solver_stats = None
        self.total_cost = 0
        self.current_cost = 0
        self.current_g_cost = 0
        self.current_h_cost = 0
        self.board = copy.deepcopy(self.current_board)

    def handle_map_selection(self, direction):
        """Handle map selection with arrow keys."""
        if direction == "left":
            self.selected_map = (self.selected_map - 1) % self.max_maps or self.max_maps
        elif direction == "right":
            self.selected_map = self.selected_map % self.max_maps + 1

        # Load the new map
        self.load_map(self.selected_map)
        self.set_board(self.current_board)

        # Reset solution state when map changes
        self.solution_found = False
        self.current_solution = None
        self.is_playing = False
        self.is_paused = False
        self.animation_finished = False
        self.solver_stats = None
        self.total_cost = 0
        self.current_cost = 0
        self.current_g_cost = 0
        self.current_h_cost = 0

    def handle_speedup_button(self):
        """Handle speed up button click."""
        self.animation_speed = self.animation_speed % self.max_speed + 1

        # Adjust move duration based on speed
        self.move_duration = 1000 // self.animation_speed

        print(f"Animation speed set to {self.animation_speed}x")

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_pos = pygame.mouse.get_pos()

                        # Check control button clicks
                        if (
                            hasattr(self, "play_btn_rect")
                            and self.play_btn_rect
                            and self.play_btn_rect.collidepoint(mouse_pos)
                        ):
                            self.handle_play_button()
                        elif (
                            hasattr(self, "pause_btn_rect")
                            and self.pause_btn_rect
                            and self.pause_btn_rect.collidepoint(mouse_pos)
                        ):
                            self.handle_pause_button()
                        elif (
                            hasattr(self, "restart_btn_rect")
                            and self.restart_btn_rect
                            and self.restart_btn_rect.collidepoint(mouse_pos)
                        ):
                            self.handle_restart_button()
                        elif (
                            hasattr(self, "speedup_btn_rect")
                            and self.speedup_btn_rect
                            and self.speedup_btn_rect.collidepoint(mouse_pos)
                        ):
                            self.handle_speedup_button()

                        # Check algorithm selection arrows
                        elif (
                            hasattr(self, "algo_left_arrow_rect")
                            and self.algo_left_arrow_rect
                            and self.algo_left_arrow_rect.collidepoint(mouse_pos)
                        ):
                            self.handle_algorithm_selection("left")
                        elif (
                            hasattr(self, "algo_right_arrow_rect")
                            and self.algo_right_arrow_rect
                            and self.algo_right_arrow_rect.collidepoint(mouse_pos)
                        ):
                            self.handle_algorithm_selection("right")

                        # Check map selection arrows
                        elif (
                            hasattr(self, "map_left_arrow_rect")
                            and self.map_left_arrow_rect
                            and self.map_left_arrow_rect.collidepoint(mouse_pos)
                        ):
                            self.handle_map_selection("left")
                        elif (
                            hasattr(self, "map_right_arrow_rect")
                            and self.map_right_arrow_rect
                            and self.map_right_arrow_rect.collidepoint(mouse_pos)
                        ):
                            self.handle_map_selection("right")

                elif event.type == pygame.KEYDOWN:
                    # Keyboard shortcuts
                    if event.key == pygame.K_SPACE:
                        if self.is_playing:
                            self.handle_pause_button()
                        else:
                            self.handle_play_button()
                    elif event.key == pygame.K_r:
                        # 'R' key - restart/replay functionality
                        self.handle_restart_button()
                    elif event.key == pygame.K_ESCAPE:
                        # ESC key - always does a full reset
                        self.board = copy.deepcopy(self.current_board)
                        self.current_move_index = 0
                        self.animation_finished = False
                        self.is_paused = False
                        self.is_playing = False
                        self.solution_found = False
                        self.current_solution = None
                        self.animation_moves = []
                        self.solver_stats = None
                        self.total_cost = 0
                        self.current_cost = 0
                        self.current_g_cost = 0
                        self.current_h_cost = 0
                        self.animation_speed = 1
                        self.move_duration = 1000
                    elif event.key == pygame.K_s:
                        if self.solution_found:
                            self.handle_speedup_button()
                    elif event.key == pygame.K_LEFT:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                            # Shift + Left = Map selection
                            self.handle_map_selection("left")
                        else:
                            # Left = Algorithm selection
                            self.handle_algorithm_selection("left")
                    elif event.key == pygame.K_RIGHT:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                            # Shift + Right = Map selection
                            self.handle_map_selection("right")
                        else:
                            # Right = Algorithm selection
                            self.handle_algorithm_selection("right")
                    elif event.key == pygame.K_UP:
                        self.handle_algorithm_selection("left")
                    elif event.key == pygame.K_DOWN:
                        self.handle_algorithm_selection("right")

            # Update animation
            self.update_animation()

            # Draw everything
            self.draw_background()
            self.draw_logo()
            self.draw_road()
            self.draw_red_car_tracker()
            self.draw_vehicles()
            self.draw_control_buttons()
            self.draw_measurements_box()

            pygame.display.flip()
            clock.tick(60)  # 60 FPS

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
    init_board = Board(6, 6, vehicles)

    gui = GUI(init_board)
    gui.run()
