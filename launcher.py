# seeing branch is working

import pygame
import sys
import os
from graphics import Graphics as G
import game

def show_menu():
    pygame.init()
    
    # Instantiate Graphics
    Graphics = G(0)
    screen = pygame.display.set_mode((Graphics.SCREEN_WIDTH, Graphics.SCREEN_HEIGHT))
    pygame.display.set_caption("Blackjack AI - Select Agent")
    
    try:
        title_font = pygame.font.Font("fonts\\jqkas-wild-font\\JqkasWild-w1YD6.ttf", 120)
        btn_font = pygame.font.Font("fonts\\jqkas-wild-font\\JqkasWild-w1YD6.ttf", 60)
    except FileNotFoundError:
        title_font = pygame.font.Font(None, 120)
        btn_font = pygame.font.Font(None, 60)
    
    # 1. Generate static background
    bg_surface = Graphics.create_gradient_surface(Graphics.SCREEN_WIDTH, Graphics.SCREEN_HEIGHT, Graphics.DARK_GREEN, Graphics.LIGHT_GREEN)
    
    # 2. OPTIMIZATION: "Bake" the chips onto a transparent layer ONCE
    # This stops the hard drive from reading chip images 60 times a second
    chips_layer = pygame.Surface((Graphics.SCREEN_WIDTH, Graphics.SCREEN_HEIGHT), pygame.SRCALPHA)
    Graphics.load_chips(chips_layer, 936248) # Draw the chips onto this transparent layer
    
    # 3. Load Logo
    try:
        raw_logo = pygame.image.load(os.path.join("img", "LOGO.png")).convert_alpha()
        target_width = 600
        aspect_ratio = raw_logo.get_height() / raw_logo.get_width()
        target_height = int(target_width * aspect_ratio)
        logo_img = pygame.transform.smoothscale(raw_logo, (target_width, target_height))
    except (FileNotFoundError, pygame.error):
        print("Warning: LOGO.png not found in the 'img' folder. Falling back to text title.")
        logo_img = None

    btn_width, btn_height = 500, 100
    start_x = (Graphics.SCREEN_WIDTH - btn_width) // 2
    
    buttons = [
        {"rect": pygame.Rect(start_x, 450, btn_width, btn_height), "text": "Play as Human", "val": "human", "color": Graphics.LIGHT_BLUE},
        {"rect": pygame.Rect(start_x, 600, btn_width, btn_height), "text": "Random Agent", "val": "random", "color": Graphics.ORANGE},
        {"rect": pygame.Rect(start_x, 750, btn_width, btn_height), "text": "DQN Agent", "val": "dqn", "color": Graphics.RED}
    ]
    
    clock = pygame.time.Clock()
    selected_agent = None

    while selected_agent is None:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    for btn in buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            selected_agent = btn["val"]
                            
        # --- DRAWING PHASE (Bottom to Top) ---
        
        # 1. Background Gradient
        screen.blit(bg_surface, (0, 0))
        
        # 2. Wood Bottom and Shadow (Pulled from Graphics class)
        screen.blit(Graphics.shadow_surface, (0, Graphics.SCREEN_HEIGHT - 205))
        screen.blit(Graphics.wood_surf, (0, Graphics.SCREEN_HEIGHT - 200))
        
        # 3. Blit the pre-drawn chips layer (Super fast!)
        screen.blit(chips_layer, (0, 0))
        
        # 4. Draw Logo
        if logo_img:
            logo_rect = logo_img.get_rect(center=(Graphics.SCREEN_WIDTH // 2, 220))
            screen.blit(logo_img, logo_rect)
        else:
            title_text = "BLACKJACK AI"
            shadow_surf = title_font.render(title_text, True, Graphics.BLACK)
            shadow_rect = shadow_surf.get_rect(center=(Graphics.SCREEN_WIDTH // 2 + 5, 205))
            screen.blit(shadow_surf, shadow_rect)
            title_surf = title_font.render(title_text, True, Graphics.GOLD)
            title_rect = title_surf.get_rect(center=(Graphics.SCREEN_WIDTH // 2, 200))
            screen.blit(title_surf, title_rect)
        
        # 5. Draw Buttons
        for btn in buttons:
            is_hovered = btn["rect"].collidepoint(mouse_pos)
            
            draw_rect = btn["rect"].copy()
            if is_hovered:
                draw_rect.inflate_ip(20, 10) 
                border_color = Graphics.WHITE
            else:
                border_color = Graphics.BLACK
                
            shadow_rect = draw_rect.copy()
            shadow_rect.y += 5
            pygame.draw.rect(screen, Graphics.BLACK, shadow_rect, border_radius=15)
            pygame.draw.rect(screen, btn["color"], draw_rect, border_radius=15)
            pygame.draw.rect(screen, border_color, draw_rect, width=4, border_radius=15)
            
            text_surf = btn_font.render(btn["text"], True, Graphics.BLACK)
            text_rect = text_surf.get_rect(center=draw_rect.center)
            
            text_shadow = btn_font.render(btn["text"], True, Graphics.WHITE)
            shadow_text_rect = text_shadow.get_rect(center=(draw_rect.centerx - 2, draw_rect.centery - 2))
            screen.blit(text_shadow, shadow_text_rect)
            screen.blit(text_surf, text_rect)
            
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return selected_agent

if __name__ == "__main__":
    chosen_agent = show_menu()
    game.main(chosen_agent)