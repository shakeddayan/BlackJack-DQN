import pygame
# import graphics as G

class Slider:
    """
    A discrete stepping slider UI element for Pygame.

    Attributes:
        pos (tuple): Center position of the slider (x, y).
        size (tuple): Dimensions of the slider (width, height).
        min (int): Minimum value allowed.
        max (int): Maximum value allowed.
        steps (int): Number of discrete steps between min and max.
        step_values (List[int]): List of calculated step values.
        container_rect (pygame.Rect): Rectangle representing the slider background.
        button_rect (pygame.Rect): Rectangle representing the draggable knob.
        current_value (int): Currently selected step value.
    """

    def __init__(self, pos: tuple, size: tuple, initial_val: float, min_val: int, max_val: int, steps: int = 11) -> None:
        """
        Initialize a stepped slider.

        Args:
            pos (tuple): Center (x, y) of the slider.
            size (tuple): Width and height of the slider.
            initial_val (float): Initial position as a ratio between 0 and 1.
            min_val (int): Minimum allowed value.
            max_val (int): Maximum allowed value.
            steps (int): Number of discrete values (default: 5).
        """
        self.pos = pos
        self.size = size
        self.min = min_val
        self.max = max_val
        self.steps = max(2, steps)  # Prevent fewer than 2 steps

        # Calculate pixel bounds of the slider
        self.slider_left_pos = self.pos[0] - (size[0] // 2)
        self.slider_right_pos = self.pos[0] + (size[0] // 2)
        self.slider_top_pos = self.pos[1] - (size[1] // 2)

        # Slider container background
        self.container_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos, self.size[0], self.size[1])

        # Compute discrete step values
        self.update_step_values()

        # Find the nearest step to the initial ratio-based value
        true_initial_val = self.min + (self.max - self.min) * initial_val
        self.current_value = min(self.step_values, key=lambda v: abs(v - true_initial_val))

        # Create knob and position it
        self.button_rect = pygame.Rect(0, self.slider_top_pos, 10, self.size[1])
        self.set_value(self.current_value)

    def update_step_values(self):
        """
        Recalculate step values based on min, max, and steps.
        """
        if self.max == self.min:
            self.step_values = [self.min]  # Prevent division by zero
        else:
            self.step_values = [
                self.min + i * (self.max - self.min) // (self.steps - 1)
                for i in range(self.steps)
            ]

    def move_slider(self, mouse_pos):
        """
        Move the slider knob based on the mouse x-position.

        Args:
            mouse_pos (tuple): Current mouse position.
        """
        x = mouse_pos[0]

        # Clamp x to the slider range
        x = max(self.slider_left_pos, min(x, self.slider_right_pos))

        # Estimate value based on mouse position
        if self.max == self.min:
            estimated_val = self.min
        else:
            ratio = (x - self.slider_left_pos) / (self.slider_right_pos - self.slider_left_pos)
            estimated_val = self.min + ratio * (self.max - self.min)

        # Snap to nearest step
        closest_step = min(self.step_values, key=lambda v: abs(v - estimated_val))
        self.set_value(closest_step)

    def render(self, G, override_txt = 0):
        """
        Render the slider to the screen.

        Args:
            G: The Graphics module.
            override_txt = 0: if 0, won't override the bet text.
                                otherwise, will set the bet amount text to the given number.
        """
        # Draw the slider background
        pygame.draw.rect(G.screen, G.GRAY, self.container_rect)

        # Draw tick marks for each step value
        for val in self.step_values:
            if self.max != self.min:
                x = self.slider_left_pos + ((val - self.min) / (self.max - self.min)) * (self.slider_right_pos - self.slider_left_pos)
            else:
                x = self.slider_left_pos
            pygame.draw.line(G.screen, G.GRAY, (int(x), self.slider_top_pos - 6), (int(x), self.slider_top_pos + self.size[1] + 6), 4)

        # Draw the slider knob
        pygame.draw.rect(G.screen, G.LIGHT_GRAY, self.button_rect)

        # Draw the current value label
        bet_txt = G.MONEY_FONT.render(f' BET : {self.get_value() if override_txt == 0 else override_txt}$ ', True, G.BLACK, G.WHITE)
        bet_text_rect = bet_txt.get_rect()
        G.screen.blit(bet_txt, (self.slider_left_pos, self.slider_top_pos - bet_text_rect.height - 15), bet_text_rect)


    def get_knob(self):
        """
        Returns the index of the current step the knob is snapped to.

        Returns:
            int: Index in the step_values list (0-based).
        """
        return self.step_values.index(self.current_value)

    def get_value(self):
        """
        Get the current value selected by the slider.

        Returns:
            int: Current stepped value.
        """
        return self.current_value

    def set_value(self, value):
        """
        Set the slider to a given value and move the knob.

        Args:
            value (int): Value to snap to the nearest step.
        """
        self.update_step_values()  # Rebuild steps in case min/max changed

        # Snap to closest allowed step
        closest_step = min(self.step_values, key=lambda v: abs(v - value))
        self.current_value = closest_step

        # Move the knob visually
        if self.max == self.min:
            ratio = 0
        else:
            ratio = (closest_step - self.min) / (self.max - self.min)
        self.button_rect.centerx = int(self.slider_left_pos + ratio * (self.slider_right_pos - self.slider_left_pos))

# class Slider:
#     '''
#         A class that represents a Slider object - used for the bet
        
#         Attributes:
#             pos - the position of the slider (exact middle of the slider)
#             size - the dimentions of the slider (width, height)
#             slider_left_pos - the X value of the left side of the slider
#             slider_right_pos - the X value of the right side of the slider
#             slider_top_pos - the X value of the top of the slider
#             min - minimal value of the slider
#             max - maximum value of the slider
#             initial_val - the initial value of the slider
#             container_rect - a pygame.Rect representing the slider
#             button_rect - a pygame.Rect representing the drag handle
#         '''
#     def __init__(self, pos: tuple, size: tuple, initial_val: float, min: int, max: int) -> None:
#         '''
#         initialize a new Slider object
#         '''

#         self.pos = pos
#         self.size = size

#         self.slider_left_pos = self.pos[0] - (size[0] // 2)
#         self.slider_right_pos = self.pos[0] + (size[0] // 2)
#         self.slider_top_pos = self.pos[1] - (size[1] // 2)

#         self.min = min
#         self.max = max

#         # Correct initial value calculation
#         self.initial_val = self.min + (self.max - self.min) * initial_val  # <-- fix this

#         self.container_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos, self.size[0], self.size[1])
#         self.button_rect = pygame.Rect(self.slider_left_pos + (self.initial_val - self.min) / (self.max - self.min) * (self.slider_right_pos - self.slider_left_pos) - 5, 
#                                       self.slider_top_pos, 10, self.size[1])
        
#     def move_slider(self, mouse_pos):
#         '''
#         change slider value using the mouse
#         '''
#         pos = mouse_pos[0]
#         # Make sure the position of the button doesn't go beyond the left and right bounds
#         pos = max(self.slider_left_pos, min(pos, self.slider_right_pos))
#         self.button_rect.centerx = pos

#     def render(self, screen): 
#         '''
#         render the Slider on the given screen (Surface)
#         '''
#         pygame.draw.rect(screen, G.GRAY, self.container_rect)
#         pygame.draw.rect(screen, G.LIGHT_GRAY, self.button_rect)
#         bet_txt = G.MONEY_FONT.render(f' BET : {self.get_value()}$ ', True, G.BLACK, G.WHITE)
#         bet_text_rect = bet_txt.get_rect()
#         screen.blit(bet_txt, (self.slider_left_pos, self.slider_top_pos - bet_text_rect.height - 15), bet_text_rect)  # update balance

#     def get_value(self): 
#         '''
#         gets the value the slider is on
#         does it using:
#             the ratio of the handle position and left position of the slider
#             the ratio of the min and max values
#         '''
#         val_range = self.slider_right_pos - self.slider_left_pos - 1
#         button_val = self.button_rect.centerx - self.slider_left_pos
#         return int(min((button_val / val_range), 1) * (self.max - self.min) + self.min)

#     def set_value(self, value): 
#         '''
#         sets the value of the slider to a certain given number
#         '''
#         # Ensure value is clamped within the min and max bounds
#         if value < self.min:
#             value = self.min
#         elif value > self.max:
#             value = self.max

#         # Calculate the position of the button based on the value
#         val_range = self.max - self.min
#         val_range = val_range if val_range != 0 else 1
#         button_position = (value - self.min) / val_range * (self.slider_right_pos - self.slider_left_pos) + self.slider_left_pos

#         # Ensure the button is within the bounds of the slider (left and right)
#         self.button_rect.centerx = int(max(self.slider_left_pos, min(button_position, self.slider_right_pos)))
