import pygame
import sys

class NiclaBox:
    def __init__(self, max_x, max_y, x, y, width, height, color=(255, 0, 0)):
        """Initialize the game window and rectangle parameters."""
        pygame.init()
        self.screen = pygame.display.set_mode((max_x, max_y))
        pygame.display.set_caption("Rectangle within a Box")
        self.max_x = max_x
        self.max_y = max_y
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.running = True

    def update(self, x=None, y=None, width=None, height=None):
        """Update the rectangle's position and size."""
        # Update the rectangle's position and size if new values are provided
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        
        # Ensure the rectangle stays within the specified boundaries
        self.x = max(0, min(self.x, self.max_x - self.width))
        self.y = max(0, min(self.y, self.max_y - self.height))

        # Fill the screen with a white background
        self.screen.fill((255, 255, 255))
        # Draw the updated rectangle
        pygame.draw.rect(self.screen, self.color, (self.x - self.width/2, self.y - self.height/2, self.width, self.height))
        # Update the display
        pygame.display.flip()

        

# Example usage
if __name__ == "__main__":
    niclaGUI = NiclaBox(max_x=240, max_y=160, x=120, y=80, width=120, height=80)
    while niclaGUI.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                niclaGUI.running = False
                
        niclaGUI.update(x=120, y=80, width=120, height=80)
    pygame.quit()
    sys.exit()
