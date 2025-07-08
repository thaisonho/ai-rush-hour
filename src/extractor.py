import pygame
import os

# Initialize pygame
pygame.init()

# Load the spritesheet
spritesheet_path = "assets/img/bk_cars1.a.png"
spritesheet = pygame.image.load(spritesheet_path)
width, height = spritesheet.get_size()

print(f"Spritesheet size: {width}x{height}")

# --- Extraction Logic ---
# Define the regions for each car image (x, y, width, height)
car_regions = [
    (72, 24, 56, 96),      # Car 1 (Horizontal)
    (0, 80, 160, 80),     # Car 2 (Horizontal)
    (0, 160, 80, 160),    # Car 3 (Vertical)
    (80, 160, 80, 160),   # Car 4 (Vertical)
    (160, 0, 80, 160),    # Car 5 (Vertical)
    (160, 160, 160, 80),  # Car 6 (Horizontal)
    (240, 0, 160, 80),    # Car 7 (Horizontal)
    (240, 80, 80, 160),   # Car 8 (Vertical)
]

# Create the output directory if it doesn't exist
output_dir = "assets/img/cars"
os.makedirs(output_dir, exist_ok=True)

# Extract and save each car image
for i, region in enumerate(car_regions):
    car_image = spritesheet.subsurface(pygame.Rect(region))
    output_path = os.path.join(output_dir, f"car_{i+1}.png")
    pygame.image.save(car_image, output_path)
    print(f"Saved car {i+1} to {output_path}")

print("\nExtraction complete!")
