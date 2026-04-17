import pygame
from abc import ABC, abstractmethod
class Button(ABC): #the neccecary functions
    '''
    an abstract button class, that includes all the neccesary functions for both types of buttons (Circle, Rectangle)
    '''

    @abstractmethod
    def draw(self, screen):
        '''
        render the button on screen
        '''
        pass

    @abstractmethod #will check if the button is pressed
    def is_clicked(self, event, G = None):
        '''
        check if the button was clicked
        '''
        pass

    def __call__(self, Env, G):
        '''
        call the draw function on object call
        '''
        self.draw(G, Env)

class Circle_Button(Button):
    '''
    A class that represents a circle button

    Attributes:
    pos - the position of the button
    color - the buttons color
    radius - the buttons radius
    outline_thickness - the thickness of the button's outline
    img - the image to load on the button
    txt - the text to display on the button
    '''

    def __init__(self, type, imgPath, radius = 70, color = None, pos = None, thickness = 0, G = None):
        '''
        initialize a new circle button object
        '''
        if (pos):
            self.pos = pos #center of the circle
        else:
            self.pos = (G.SCREEN_WIDTH / 2, 100)
        if(color):
            self.color = color #filling color
        else:
            self.color = G.WHITE
        self.radius = radius #radius of the circle
        self.outline_thickness = thickness # if zero, will fill the color in the shape. if >0 will draw outline of that color
        self.img = pygame.image.load(imgPath) #the icon to use in the button
        self.txt = type #the text, the type of button (which move)
    
    def draw(self, G, Env):
        '''
        render the button on screen
        '''
        # Determine if this button should appear locked
        is_locked = (Env.state.round_phase != 'playing') or (self.txt == 'SURRENDER' and not Env.is_action_legal(4))

        # Set font size based on text length
        if len(self.txt) < 7:
            font_size = int(self.radius / 2)
        elif len(self.txt) == 7:
            font_size = int(5 * self.radius / 12)
        else:
            font_size = int(self.radius / 3)

        # Initialize font object
        font_obj = pygame.font.Font('fonts\\casino_2\\CasinoShadow.ttf', font_size)

        # Set text color
        text_color = G.BLACK if self.color != G.BLACK or is_locked else G.WHITE
        text_surface = font_obj.render(self.txt, False, text_color)

        # Set fill and outline colors
        fill_color = G.LIGHT_GRAY if is_locked else self.color
        outline_color = G.WHITE if self.color != G.BLACK or is_locked else G.BLACK

        # Draw the button circles
        pygame.draw.circle(G.wood_surf, fill_color, self.pos, self.radius, self.outline_thickness)
        pygame.draw.circle(G.wood_surf, outline_color, self.pos, self.radius + self.outline_thickness, 5)

        # Draw the icon image
        if self.txt == 'DOUBLE ':
            img_size = (int(1.3 * self.radius), int(1.3 * self.radius))
            img_pos = (self.pos[0] - 2 * self.radius / 3, self.pos[1] - 0.8 * self.radius / 2)
        else:
            img_size = (self.radius, self.radius)
            img_pos = (self.pos[0] - self.radius / 2, self.pos[1] - self.radius / 5)

        scaled_img = pygame.transform.scale(self.img, img_size)
        G.wood_surf.blit(scaled_img, img_pos)

        # Draw the text 
        if len(self.txt) < 7:
            text_pos = (self.pos[0] - 5.5 * text_surface.get_width() / 12, self.pos[1] - 2 * self.radius / 3)
        else:
            text_pos = (self.pos[0] - 5.5 * text_surface.get_width() / 12, self.pos[1] - self.radius / 2)

        G.wood_surf.blit(text_surface, text_pos, text_surface.get_rect())


    def is_clicked(self, event, G):
        '''
        Checks if the button was clicked.
        '''
        #Returns True if the mouse click occurred within the button's circle.
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos() #get mouse pos on click
            distance = ((mouse_x - self.pos[0]) ** 2 + (mouse_y - G.SCREEN_HEIGHT + 200 - self.pos[1]) ** 2) ** 0.5 # calculete the distance from the center
            if distance <= self.radius:
                return True #if the distance is smaller than the radius then the click was in the circle
        return False
    
    def lock_split(self, Env, G):
        '''
        locks the split button
        '''
        if Env.is_action_legal(2):
            self.color = G.YELLOW
        else:
            self.color = G.LIGHT_GRAY
    
    def lock_double(self, Env, G):
        '''
        locks the double button
        '''
        if Env.is_action_legal(1):
            self.color = G.LIGHT_BLUE
        else:
            self.color = G.LIGHT_GRAY

class Rectangle_Button(Button):
    '''
    A class that represents a rectanglular button (will be the lock bet button)

    Attributes:
    text - the button's text
    img - the image to display on the button
    rectangle - a pygame.Rect representing the button
    '''

    def __init__(self, pos:tuple[int, int], dimentions: tuple[int, int ], text: str, img: str, G):
        '''
        initialize a new rectangle button object
        '''
        self.text = pygame.font.Font("fonts/casino_2/CasinoFlat.ttf", 20).render(text, False, G.BLACK) #the text surface
        self.img = pygame.image.load(img) #the image
        self.rectangle = pygame.Rect(pos[0], pos[1], dimentions[0], dimentions[1], color= G.WHITE) #background rectangle
    
    def is_clicked(self, event, G = None): 
        '''
        Checks if the button was clicked.
        '''
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self.rectangle.collidepoint(pygame.mouse.get_pos())
    
    def draw(self, G, env):
        '''
        render the button on screen
        '''
        # Draw background
        pygame.draw.rect(G.screen, G.LIGHT_GREEN if env.state.round_phase == 'betting' else G.LIGHT_GRAY, self.rectangle, border_radius=5)

        # Draw image
        scaled_img = pygame.transform.scale(self.img, (self.rectangle.height, self.rectangle.height))
        G.screen.blit(scaled_img, (self.rectangle.x, self.rectangle.y))

        # Draw text
        G.screen.blit(self.text, (self.rectangle.x + scaled_img.get_width(), self.rectangle.centery - 0.4 * self.text.get_size()[1]))