#!/usr/bin/env python3
import pygame
import sys
import time
import random
from collections import deque

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BROWN = (210, 180, 140)
DARK_BROWN = (139, 69, 19)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class OldRiceGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("古米マーケット (Old Rice Market)")
        
        # Game state
        self.current_sequence = ""
        self.target_sequence = ""
        self.target_sequences = []
        self.current_target_index = 0
        self.full_target_string = ""  # The full continuous string of all sequences
        self.inventory = deque()  # Store sets of rice
        self.game_running = False
        self.game_state = "intro"  # intro, playing, game_over
        self.start_time = 0
        self.elapsed_time = 0
        self.consumption_constant = 0.5  # Constant for consumption rate
        self.score = 0
        self.error_flash = 0  # Counter for error flash effect
        self.error_penalty = 0  # Counter for error penalty (in frames)
        self.error_penalty_time = 3 * 60  # 3 seconds at 60 FPS
        self.consumption_boost = 1.0  # Multiplier for consumption speed (increases on error)
        self.error_count = 0  # Count of errors made
        self.max_errors = 3  # Maximum allowed errors
        
        # Fonts
        self.title_font = pygame.font.SysFont('notosanscjkjp', 48)
        self.large_font = pygame.font.SysFont('notosanscjkjp', 32)
        self.medium_font = pygame.font.SysFont('notosanscjkjp', 24)
        self.small_font = pygame.font.SysFont('notosanscjkjp', 18)
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        
        # Generate initial target sequence
        self.generate_target_sequence()

    def generate_target_sequence(self):
        """Generate a continuous string of multiple sequences"""
        # Generate sequences until we have at least 20 characters
        self.target_sequences = []
        self.full_target_string = ""
        
        while len(self.full_target_string) < 20:
            # Generate a sequence with 1-5 "古" followed by "米"
            num_old = random.randint(1, 5)
            sequence = "古" * num_old + "米"
            self.target_sequences.append(sequence)
            self.full_target_string += sequence
        
        # Set the current target to the first sequence
        self.current_target_index = 0
        self.target_sequence = self.target_sequences[self.current_target_index]
        
    def add_new_sequence(self):
        """Add a new sequence to maintain at least 20 characters"""
        # Generate a new sequence
        num_old = random.randint(1, 5)
        sequence = "古" * num_old + "米"
        
        # Add to our lists
        self.target_sequences.append(sequence)
        self.full_target_string += sequence

    def draw_text(self, text, font, color, x, y, align="left"):
        """Draw text on screen with alignment options"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        if align == "center":
            text_rect.center = (x, y)
        elif align == "right":
            text_rect.right = x
            text_rect.top = y
        else:  # left
            text_rect.left = x
            text_rect.top = y
            
        self.screen.blit(text_surface, text_rect)
        return text_rect

    def show_intro(self):
        """Display game introduction screen"""
        self.screen.fill(LIGHT_BROWN)
        
        # Title
        self.draw_text("古米マーケット", self.title_font, DARK_BROWN, SCREEN_WIDTH//2, 100, "center")
        self.draw_text("Old Rice Market", self.large_font, DARK_BROWN, SCREEN_WIDTH//2, 150, "center")
        
        # Key instructions
        key_instructions = [
            "【操作方法】",
            "「f」キー: 「古」を入力",
            "「j」キー: 「米」を入力"
        ]
        
        y_pos = 210
        for line in key_instructions:
            self.draw_text(line, self.medium_font, BLACK, SCREEN_WIDTH//2, y_pos, "center")
            y_pos += 30
        
        # Simple instructions (3 lines)
        instructions = [
            "古米を入力し米不足を解消せよ！",
            "ミスは3回まで！消化速度が2倍に！",
            "在庫を長く維持するほど高得点！"
        ]
        
        y_pos = 330
        for line in instructions:
            self.draw_text(line, self.large_font, BLACK, SCREEN_WIDTH//2, y_pos, "center")
            y_pos += 50
        
        # Start prompt - make button wider to fit text
        button_width = 350
        pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH//2 - button_width//2, 500, button_width, 50), border_radius=10)
        self.draw_text("Enterキーを押してスタート", self.medium_font, WHITE, SCREEN_WIDTH//2, 525, "center")
        
        pygame.display.flip()

    def show_game_over(self):
        """Display game over screen"""
        self.screen.fill(LIGHT_BROWN)
        
        # Game over title
        self.draw_text("ゲーム終了！", self.title_font, DARK_BROWN, SCREEN_WIDTH//2, 100, "center")
        
        # Show reason for game over
        if self.error_count >= self.max_errors:
            self.draw_text("ミス回数オーバー！", self.large_font, RED, SCREEN_WIDTH//2, 160, "center")
        else:
            self.draw_text("在庫切れ！", self.large_font, RED, SCREEN_WIDTH//2, 160, "center")
        
        # Score - changed from "スコア" to "維持時間"
        self.draw_text(f"維持時間: {self.score:.1f}秒", self.large_font, BLACK, SCREEN_WIDTH//2, 220, "center")
        
        # Restart prompt - make button wider to fit text
        button_width = 350
        pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH//2 - button_width//2, 320, button_width, 50), border_radius=10)
        self.draw_text("Enterキーでもう一度プレイ", self.medium_font, WHITE, SCREEN_WIDTH//2, 345, "center")
        
        # Quit prompt
        pygame.draw.rect(self.screen, RED, (SCREEN_WIDTH//2 - button_width//2, 390, button_width, 50), border_radius=10)
        self.draw_text("Escキーで終了", self.medium_font, WHITE, SCREEN_WIDTH//2, 415, "center")
        
        pygame.display.flip()

    def update_game_display(self):
        """Update the main game display"""
        self.screen.fill(LIGHT_BROWN)
        
        # Update elapsed time
        self.elapsed_time = time.time() - self.start_time
        
        # Display time
        self.draw_text(f"経過時間: {self.elapsed_time:.1f}秒", self.medium_font, BLACK, 20, 20)
        
        # Display consumption boost
        boost_text = f"消化速度: {self.consumption_boost:.1f}倍"
        boost_color = RED if self.consumption_boost > 1.0 else BLACK
        self.draw_text(boost_text, self.medium_font, boost_color, SCREEN_WIDTH - 20, 20, "right")
        
        # Display error count
        error_text = f"ミス: {self.error_count}/{self.max_errors}"
        error_color = RED if self.error_count > 0 else BLACK
        self.draw_text(error_text, self.medium_font, error_color, SCREEN_WIDTH - 20, 50, "right")
        
        # Display progress through sequences
        progress_text = f"進捗: {self.current_target_index + 1}/{len(self.target_sequences)}"
        self.draw_text(progress_text, self.medium_font, BLACK, SCREEN_WIDTH - 20, 80, "right")
        
        # Display key instructions
        self.draw_text("f:「古」 j:「米」", self.small_font, DARK_BROWN, SCREEN_WIDTH//2, 20, "center")
        
        # Display the full target string with the current sequence highlighted - moved much lower
        self.draw_text("目標:", self.medium_font, BLACK, 20, 120)
        
        # Display the full target string - moved down to avoid overlap
        if self.full_target_string:
            # Draw the full string in gray
            self.draw_text(self.full_target_string, self.large_font, (100, 100, 100), 100, 120)
            
            # Draw the current target in blue (overlay on top of the gray text)
            self.draw_text(self.target_sequence, self.large_font, BLUE, 100, 120)
        
        # Display current sequence - also moved down
        self.draw_text("入力:", self.medium_font, BLACK, 20, 160)
        
        # Display current input with color coding
        x_pos = 100
        for i, char in enumerate(self.current_sequence):
            if i < len(self.target_sequence) and char == self.target_sequence[i]:
                color = GREEN
            else:
                color = RED
            char_rect = self.draw_text(char, self.large_font, color, x_pos, 160)
            x_pos = char_rect.right
        
        # Add visual indicator for next expected character
        if len(self.current_sequence) < len(self.target_sequence) and self.error_penalty == 0:
            next_char = self.target_sequence[len(self.current_sequence)]
            # Make the hint more transparent
            self.draw_text(next_char, self.large_font, (100, 100, 100, 128), x_pos, 160)  # Semi-transparent hint
        
        # Display error flash and penalty if active
        if self.error_flash > 0:
            # No red rectangle anymore - removed as requested
            self.error_flash -= 1
            
            # Show error message - moved down to avoid overlap
            self.draw_text("入力ミス! 最初からやり直してください", self.medium_font, RED, SCREEN_WIDTH//2, 210, "center")
            
            # Show penalty countdown
            if self.error_penalty > 0:
                seconds_left = self.error_penalty / 60  # Convert frames to seconds
                self.draw_text(f"入力再開まで: {seconds_left:.1f}秒", self.medium_font, RED, SCREEN_WIDTH//2, 240, "center")
                self.error_penalty -= 1
                
                # Reset current sequence when penalty ends
                if self.error_penalty == 1:  # Reset just before penalty ends
                    self.current_sequence = ""
        
        # Display inventory count
        self.draw_text(f"在庫セット数: {len(self.inventory)}", self.medium_font, BLACK, 20, 270)
        
        # Display inventory details
        if self.inventory:
            self.draw_text("【在庫状況】", self.medium_font, BLACK, 20, 300)
            
            y_pos = 340
            for i, (rice_set, remaining) in enumerate(self.inventory):
                if y_pos > SCREEN_HEIGHT - 50:  # Prevent drawing outside screen
                    self.draw_text("...", self.medium_font, BLACK, 20, y_pos)
                    break
                
                # Highlight the currently consuming item
                bg_color = None
                if i == 0:  # First item is being consuming
                    # Draw a light highlight behind the first item
                    highlight_rect = pygame.Rect(15, y_pos - 5, 580, 35)
                    pygame.draw.rect(self.screen, (255, 240, 200), highlight_rect)
                    self.draw_text("消化中 ▶", self.small_font, DARK_BROWN, 20, y_pos)
                    item_x = 100
                else:
                    item_x = 20
                
                # Draw set text - moved to left side
                set_text = f"{i+1}. {rice_set}"
                self.draw_text(set_text, self.medium_font, BLACK, item_x, y_pos)
                
                # Calculate width of the set text to position progress bar properly
                set_text_width = self.medium_font.size(set_text)[0]
                progress_bar_start = max(item_x + set_text_width + 20, 250)  # Add padding
                
                # Draw progress bar - adjusted position
                progress = remaining / len(rice_set)
                bar_width = 250
                pygame.draw.rect(self.screen, GRAY, (progress_bar_start, y_pos + 5, bar_width, 20))
                pygame.draw.rect(self.screen, GREEN, (progress_bar_start, y_pos + 5, int(bar_width * progress), 20))
                
                # Draw remaining text - adjusted position
                self.draw_text(f"{remaining:.1f}/{len(rice_set)}", self.small_font, BLACK, 
                               progress_bar_start + bar_width + 10, y_pos + 5)
                
                y_pos += 40
        
        pygame.display.flip()

    def consume_inventory(self):
        """Consume inventory sets one at a time (serially)"""
        if not self.inventory:
            return False  # No change in inventory
        
        # Only process the first item in inventory (FIFO)
        rice_set, remaining = self.inventory[0]
        
        # Reduce remaining based on length, applying consumption boost
        consumption_rate = 0.016 / (len(rice_set) * self.consumption_constant) * self.consumption_boost
        new_remaining = remaining - consumption_rate
        
        if new_remaining <= 0:
            # Remove the consumed item
            self.inventory.popleft()
            return True
        else:
            # Update the remaining value
            self.inventory[0] = (rice_set, new_remaining)
            return True
        
        return False

    def process_input(self, key):
        """Process keyboard input during gameplay"""
        # If in penalty period, ignore input
        if self.error_penalty > 0:
            return False
            
        if key == pygame.K_f:
            # Check if this would be an error
            if len(self.current_sequence) < len(self.target_sequence) and self.target_sequence[len(self.current_sequence)] == "古":
                self.current_sequence += "古"
            else:
                # Error - wrong key
                self.error_flash = self.error_penalty_time  # Set error flash for entire penalty period
                self.error_penalty = self.error_penalty_time  # Set penalty timer
                # Keep the current sequence visible during the error period
                # It will be reset when the penalty ends
                
                # Increase consumption speed as penalty - now +1.0 (doubling) per error
                self.consumption_boost += 1.0  # Increase by 100%
                
                # Increment error count
                self.error_count += 1
                
                # Check if max errors reached
                if self.error_count >= self.max_errors:
                    # Game over due to too many errors
                    self.game_state = "game_over"
                    self.game_running = False
                    self.score = self.elapsed_time
                
                return True
            
            return True
            
        elif key == pygame.K_j:
            # Check if this would be an error
            if len(self.current_sequence) < len(self.target_sequence) and self.target_sequence[len(self.current_sequence)] == "米":
                self.current_sequence += "米"
            else:
                # Error - wrong key
                self.error_flash = self.error_penalty_time  # Set error flash for entire penalty period
                self.error_penalty = self.error_penalty_time  # Set penalty timer
                # Keep the current sequence visible during the error period
                # It will be reset when the penalty ends
                
                # Increase consumption speed as penalty - now +1.0 (doubling) per error
                self.consumption_boost += 1.0  # Increase by 100%
                
                # Increment error count
                self.error_count += 1
                
                # Check if max errors reached
                if self.error_count >= self.max_errors:
                    # Game over due to too many errors
                    self.game_state = "game_over"
                    self.game_running = False
                    self.score = self.elapsed_time
                
                return True
            
            # Check if the sequence matches the target
            if self.current_sequence == self.target_sequence:
                # Add to inventory
                self.inventory.append((self.current_sequence, len(self.current_sequence)))
                
                # Remove the completed sequence from the full target string
                self.full_target_string = self.full_target_string[len(self.target_sequence):]
                
                # Move to next target sequence
                self.current_target_index += 1
                
                # Check if we need to add more sequences to maintain 20 characters
                while len(self.full_target_string) < 20:
                    self.add_new_sequence()
                
                # Set the next target sequence
                if self.current_target_index < len(self.target_sequences):
                    self.target_sequence = self.target_sequences[self.current_target_index]
                else:
                    # This shouldn't happen with the while loop above, but just in case
                    self.add_new_sequence()
                    self.target_sequence = self.target_sequences[self.current_target_index]
                
                # Reset current sequence
                self.current_sequence = ""
            
            return True
        
        return False

    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if self.game_state == "intro":
                        if event.key == pygame.K_RETURN:
                            self.game_state = "playing"
                            self.game_running = True
                            self.start_time = time.time()
                            self.current_sequence = ""
                            self.inventory.clear()
                            self.consumption_boost = 1.0  # Reset consumption boost
                            self.error_count = 0  # Reset error count
                            self.error_flash = 0  # Reset error flash
                            self.error_penalty = 0  # Reset error penalty
                            self.generate_target_sequence()
                            
                            # Add an initial inventory item to prevent immediate game over
                            self.inventory.append(("古米", 2))
                    
                    elif self.game_state == "playing":
                        self.process_input(event.key)
                        
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = "game_over"
                            self.game_running = False
                            self.score = self.elapsed_time
                    
                    elif self.game_state == "game_over":
                        if event.key == pygame.K_RETURN:
                            self.game_state = "playing"
                            self.game_running = True
                            self.start_time = time.time()
                            self.current_sequence = ""
                            self.inventory.clear()
                            self.consumption_boost = 1.0  # Reset consumption boost
                            self.error_count = 0  # Reset error count
                            self.error_flash = 0  # Reset error flash
                            self.error_penalty = 0  # Reset error penalty
                            self.generate_target_sequence()
                            
                            # Add an initial inventory item to prevent immediate game over
                            self.inventory.append(("古米", 2))
                            
                        elif event.key == pygame.K_ESCAPE:
                            running = False
            
            # Update game state
            if self.game_state == "intro":
                self.show_intro()
            
            elif self.game_state == "playing":
                # Update inventory consumption
                inventory_changed = self.consume_inventory()
                
                # Check if game is over - immediately end if inventory is empty
                if not self.inventory:
                    self.game_state = "game_over"
                    self.game_running = False
                    self.score = self.elapsed_time
                
                # Check if we need to generate new sequences
                if not self.full_target_string and self.current_target_index >= len(self.target_sequences):
                    self.generate_target_sequence()
                
                # Update display
                self.update_game_display()
            
            elif self.game_state == "game_over":
                self.show_game_over()
            
            # Control frame rate
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = OldRiceGame()
    game.run()
