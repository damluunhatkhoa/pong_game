
import pygame
import sys
import random

pygame.init()

# WINDOW SETUP
WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong (a game by Luu Dam)")

CLOCK = pygame.time.Clock()
FPS = 60

# COLOURS
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREY = (100, 100, 100)
LIGHT_GREY = (180, 180, 180)
BLUE = (80, 170, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
YELLOW = (255, 220, 80)


# FONTS
TITLE_FONT = pygame.font.SysFont("monospace", 48, bold=True)
MENU_FONT = pygame.font.SysFont("monospace", 30)
SMALL_FONT = pygame.font.SysFont("monospace", 22)


# GAME SETTINGS
DIFFICULTIES = {
    "Easy": {
        "player_speed": 7,
        "ai_speed": 4,
    },
    "Medium": {
        "player_speed": 8,
        "ai_speed": 6,
    },
    "Hard": {
        "player_speed": 9,
        "ai_speed": 8,
    },
    "EasyPvP": {
        "player_speed": 9,
        "ai_speed": 9,
    },
    "MediumPvP": {
        "player_speed": 7,
        "ai_speed": 7,
    },
    "HardPvP": {
        "player_speed": 5,
        "ai_speed": 5,
    }

}

WIN_SCORE_PER_STAGE = 3
MAX_STAGE = 3


# HELPER CLASSES
class Button:
    def __init__(self, x, y, w, h, text, colour=BLUE, hover_colour=YELLOW):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.colour = colour
        self.hover_colour = hover_colour

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        current_colour = self.hover_colour if self.rect.collidepoint(mouse_pos) else self.colour
        pygame.draw.rect(screen, current_colour, self.rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, self.rect, 3, border_radius=12)

        text_surf = MENU_FONT.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class Paddle:
    def __init__(self, x, y, w, h, speed):
        self.rect = pygame.Rect(x, y, w, h)
        self.speed = speed

    def move_up(self):
        self.rect.y -= self.speed
        if self.rect.top < 0:
            self.rect.top = 0

    def move_down(self):
        self.rect.y += self.speed
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=8)


class Ball:
    def __init__(self, x, y, radius, base_speed):
        self.radius = radius
        self.base_speed = base_speed
        self.reset(direction=random.choice([-1, 1]))

    def reset(self, direction=1):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2

        angle_y = random.choice([-1, 1]) * random.uniform(2.0, 4.0)
        self.vx = self.base_speed * direction
        self.vy = angle_y

    def rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2
        )
    
    def update(self):
        self.x += self.vx
        self.y += self.vy

        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy *= -1

        if self.y + self.radius >= HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

    
    
class Slider:
    def __init__(self, x, y, width, min_value, max_value, start_value):
        self.x = x
        self.y = y
        self.width = width
        self.min_value = min_value
        self.max_value = max_value
        self.value = start_value

        self.track_rect = pygame.Rect(x, y, width, 6)
        self.handle_radius = 10
        self.dragging = False

    def get_handle_x(self):
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        return int(self.x + ratio * self.width)

    def handle_event(self, event):
        handle_x = self.get_handle_x()
        handle_rect = pygame.Rect(
            handle_x - self.handle_radius,
            self.y - self.handle_radius + 3,
            self.handle_radius * 2,
            self.handle_radius * 2
        )

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if handle_rect.collidepoint(event.pos) or self.track_rect.inflate(0, 20).collidepoint(event.pos):
                self.dragging = True
                self.update_value_from_mouse(event.pos[0])

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False

            elif event.type == pygame.MOUSEMOTION and self.dragging:
                self.update_value_from_mouse(event.pos[0])



    def update_value_from_mouse(self, mouse_x):
        mouse_x = max(self.x, min(mouse_x, self.x + self.width))
        ratio = (mouse_x - self.x) / self.width
        self.value = round(self.min_value + ratio * (self.max_value - self.min_value), 1)

    def draw(self, screen, label):
        # Track
        pygame.draw.rect(screen, GREY, self.track_rect, border_radius=3)

        # Filled part
        filled_width = self.get_handle_x() - self.x
        pygame.draw.rect(screen, BLUE, (self.x, self.y, filled_width, 6), border_radius=3)

        # Handle
        pygame.draw.circle(screen, WHITE, (self.get_handle_x(), self.y + 3), self.handle_radius)

        # Label
        label_text = SMALL_FONT.render(f"{label}: {self.value:.1f}", True, WHITE)
        screen.blit(label_text, (self.x, self.y - 35))

class MovingObstacle:
    def __init__(self, x, y, w, h, speed):
        self.rect = pygame.Rect(x, y, w, h)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed *= -1

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect, border_radius=8)


# GAME FUNCTIONS
def draw_text_center(text, font, colour, y):
    surf = font.render(text, True, colour)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    SCREEN.blit(surf, rect)


def draw_middle_line():
    for y in range(0, HEIGHT, 25):
        pygame.draw.rect(SCREEN, GREY, (WIDTH // 2 - 3, y, 6, 15))


def ai_control(ai_paddle, ball, difficulty_name):
    # Easier difficulties react more slowly / less accurately
    settings = DIFFICULTIES[difficulty_name]
    target_y = ball.y

    # Add a dead-zone so the AI does not move too perfectly
    if abs(ai_paddle.rect.centery - target_y) > 18:
        if ai_paddle.rect.centery < target_y:
            ai_paddle.move_down()
        elif ai_paddle.rect.centery > target_y:
            ai_paddle.move_up()

    # Limit to chosen difficulty speed
    ai_paddle.speed = settings["ai_speed"]


def handle_ball_paddle_collision(ball, paddle, moving_right):
    ball_rect = ball.rect()
    if ball_rect.colliderect(paddle.rect):
        # Move the ball out of the paddle to avoid repeated collisions
        if moving_right:
            ball.x = paddle.rect.left - ball.radius
            ball.vx = -abs(ball.vx)
        else:
            ball.x = paddle.rect.right + ball.radius
            ball.vx = abs(ball.vx)

        # Change vertical speed depending on impact point
        offset = (ball.y - paddle.rect.centery) / (paddle.rect.height / 2)
        ball.vy = offset * 6


def handle_ball_obstacle_collision(ball, obstacle):
    if obstacle is None:
        return

    ball_rect = ball.rect()
    if ball_rect.colliderect(obstacle.rect):
        # Determine whether to reverse x or y based on overlap
        overlap_left = ball_rect.right - obstacle.rect.left
        overlap_right = obstacle.rect.right - ball_rect.left
        overlap_top = ball_rect.bottom - obstacle.rect.top
        overlap_bottom = obstacle.rect.bottom - ball_rect.top

        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        if min_overlap in (overlap_left, overlap_right):
            ball.vx *= -1
        else:
            ball.vy *= -1


def create_stage_objects(difficulty_name, stage, ball_speed_setting):
    settings = DIFFICULTIES[difficulty_name]

    player = Paddle(40, HEIGHT // 2 - 60, 18, 120, settings["player_speed"])
    ai = Paddle(WIDTH - 58, HEIGHT // 2 - 60, 18, 120, settings["ai_speed"])

    ball_speed = ball_speed_setting + (stage - 1) * 1.2
    ball = Ball(WIDTH // 2, HEIGHT // 2, 12, ball_speed)

    obstacle = None
    if stage >= 2:
        # Stage 2 and 3 include a moving obstacle
        obstacle_height = 100 if stage == 2 else 140
        obstacle_speed = 4 if stage == 2 else 6
        obstacle = MovingObstacle(WIDTH // 2 - 10, HEIGHT // 2 - obstacle_height // 2, 20, obstacle_height, obstacle_speed)

    return player, ai, ball, obstacle


def draw_score(player_score, ai_score, stage, difficulty_name, game_mode, ball_speed_setting):
    score_text = MENU_FONT.render(f"{player_score}   :   {ai_score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, 40))
    SCREEN.blit(score_text, score_rect)

    stage_text = SMALL_FONT.render(f"Stage: {stage}/{MAX_STAGE}", True, LIGHT_GREY)
    SCREEN.blit(stage_text, (20, 80))

    mode_text = SMALL_FONT.render(f"Mode: {game_mode}", True, LIGHT_GREY)
    SCREEN.blit(mode_text, (20, 20))

    diff_text = SMALL_FONT.render(f"Difficulty: {difficulty_name}", True, LIGHT_GREY)
    SCREEN.blit(diff_text, (20, 110))

    speed_text = SMALL_FONT.render(f"Ball Speed: {ball_speed_setting:.1f}", True, LIGHT_GREY)
    SCREEN.blit(speed_text, (20,50))

def draw_score_pvp(player_score, ai_score, game_mode, ball_speed_setting):
    score_text = MENU_FONT.render(f"{player_score}   :   {ai_score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, 40))
    SCREEN.blit(score_text, score_rect)

    mode_text = SMALL_FONT.render(f"Mode: {game_mode}", True, LIGHT_GREY)
    SCREEN.blit(mode_text, (20, 20))

    speed_text = SMALL_FONT.render(f"Ball Speed: {ball_speed_setting:.1f}", True, LIGHT_GREY)
    SCREEN.blit(speed_text, (20,50))

    diff_text = SMALL_FONT.render(f"Difficulty: {difficulty_name}", True, LIGHT_GREY)
    SCREEN.blit(diff_text, (20, 80))


# BUTTONS
start_button = Button(WIDTH // 2 - 120, 220, 240, 60, "Start Game")
settings_button = Button(WIDTH // 2 - 120, 300, 240, 60, "Settings")
quit_button = Button(WIDTH // 2 - 120, 380, 240, 60, "Quit")


ai_mode_button = Button(WIDTH // 2 - 120, 240, 240, 60, "AI Mode")
pvp_mode_button = Button(WIDTH // 2 - 120, 320, 240, 60, "PvP Mode")
mode_back_button = Button(WIDTH // 2 - 120, 400, 240, 60, "Back")

difficulty_button = Button(WIDTH // 2 - 120, 240, 240, 60, "Difficulty")
ball_speed_button = Button(WIDTH // 2 -120, 320, 240, 60, "Ball Speed")
back_button = Button(WIDTH // 2 - 120, 400, 240, 60, "Back")

ai_diff_button = Button(WIDTH // 2 - -20, 140, 240, 60, "AI")
pvp_diff_button = Button(WIDTH // 2 - 260, 140, 240, 60, "PVP")

easy_button = Button(WIDTH // 2 - 120, 220, 240, 60, "Easy", GREEN)
medium_button = Button(WIDTH // 2 - 120, 300, 240, 60, "Medium", YELLOW)
hard_button = Button(WIDTH // 2 - 120, 380, 240, 60, "Hard", RED)
diff_back_button = Button(WIDTH // 2 - 120, 500, 240, 60, "Back")
bs_back_button = Button(WIDTH // 2 - 120, 500, 240, 60, "Back")

next_stage_button = Button(WIDTH // 2 - 120, 320, 240, 60, "Next Stage")
restart_button = Button(WIDTH // 2 - 120, 320, 240, 60, "Restart")
menu_button = Button(WIDTH // 2 - 120, 400, 240, 60, "Main Menu")


# INITIAL GAME STATE
game_state = "menu"  # menu, settings, playing, stage_clear, game_over, victory
difficulty_name = "Medium"
game_mode = "AI"   # AI or PvP
stage = 1
player_score = 0
ai_score = 0

ball_speed_setting = 6.0
ball_speed_slider = Slider(WIDTH // 2 - 150, 300, 300, 3.0, 12.0, ball_speed_setting)

player_paddle, ai_paddle, ball, obstacle = create_stage_objects(difficulty_name, stage, ball_speed_setting)


# MAIN LOOP
running = True
while running:
    CLOCK.tick(FPS)
    SCREEN.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        
        # MENU EVENTS
        if game_state == "menu":
            if start_button.is_clicked(event):
                game_state = "mode_select"

            if settings_button.is_clicked(event):
                game_state = "settings"

            if quit_button.is_clicked(event):
                running = False

        
        # GAME MODE EVENTS
        elif game_state == "mode_select":
            if ai_mode_button.is_clicked(event):
                game_mode = "AI"
                stage = 1
                player_score = 0
                ai_score = 0
                player_paddle, ai_paddle, ball, obstacle = create_stage_objects(difficulty_name, stage, ball_speed_setting)
                game_state = "playing"
            
            if pvp_mode_button.is_clicked(event):
                game_mode = "PvP"
                if difficulty_name == "MediumPvP":
                    stage = 2
                if difficulty_name == "HardPvP":
                    stage = 3
                player_score = 0
                ai_score = 0
                player_paddle, ai_paddle, ball, obstacle = create_stage_objects(difficulty_name, stage, ball_speed_setting)
                game_state = "playing"

            if mode_back_button.is_clicked(event):
                game_state = "menu"

        
        # SETTINGS EVENTS
        elif game_state == "settings":
            if difficulty_button.is_clicked(event):
                game_state = "difficulty"
            
            # Slider interactions
            if ball_speed_button.is_clicked(event):
                game_state = "ball_speed"
 
            if back_button.is_clicked(event):
                game_state = "menu"

        
        elif game_state == "difficulty":
            if ai_diff_button.is_clicked(event):
                game_mode = "AI"
            if pvp_diff_button.is_clicked(event):
                game_mode = "PvP"

            if game_mode == "AI":
                if easy_button.is_clicked(event):
                    difficulty_name = "Easy"
                if medium_button.is_clicked(event):
                    difficulty_name = "Medium"
                if hard_button.is_clicked(event):
                    difficulty_name = "Hard"
            else:
                if easy_button.is_clicked(event):
                    difficulty_name = "EasyPvP"
                if medium_button.is_clicked(event):
                    difficulty_name = "MediumPvP"
                if hard_button.is_clicked(event):
                    difficulty_name = "HardPvP"

            if diff_back_button.is_clicked(event):
                game_state = "settings"


        elif game_state == "ball_speed":
            ball_speed_slider.handle_event(event)
            ball_speed_setting = ball_speed_slider.value
            if bs_back_button.is_clicked(event):
                game_state = "settings"
            

        # STAGE CLEAR EVENTS
        elif game_state == "stage_clear":
            if next_stage_button.is_clicked(event):
                stage += 1
                player_score = 0
                ai_score = 0
                player_paddle, ai_paddle, ball, obstacle = create_stage_objects(difficulty_name, stage, ball_speed_setting)
                game_state = "playing"

            if menu_button.is_clicked(event):
                game_state = "menu"

        
        # GAME OVER / VICTORY EVENTS
        elif game_state in ("game_over", "victory"):
            if restart_button.is_clicked(event):
                if game_mode == "AI":
                    stage = 1
                if game_mode == "PvP":
                    if difficulty_name == "MediumPvP":
                        stage = 2
                    if difficulty_name == "HardPvP":
                        stage = 3
            
                player_score = 0
                ai_score = 0
                player_paddle, ai_paddle, ball, obstacle = create_stage_objects(difficulty_name, stage, ball_speed_setting)
                game_state = "playing"

            if menu_button.is_clicked(event):
                game_state = "menu"

        
        # Keyboard shortcut to return to menu
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state = "menu"

    
    # DRAW / UPDATE BY STATE
    if game_state == "menu":
        draw_text_center("PONG", TITLE_FONT, WHITE, 120)
        draw_text_center("a game by Luu Dam", MENU_FONT, WHITE, 170)

        start_button.draw(SCREEN)
        settings_button.draw(SCREEN)
        quit_button.draw(SCREEN)

    elif game_state == "mode_select":
        draw_text_center("SELECT GAME MODE", TITLE_FONT, WHITE, 140)

        ai_mode_button.draw(SCREEN)
        pvp_mode_button.draw(SCREEN)
        mode_back_button.draw(SCREEN)

    elif game_state == "settings":
        draw_text_center("SETTINGS", TITLE_FONT, WHITE, 140)

        # Section 1: Difficulty
        difficulty_button.draw(SCREEN)

        # Section 2: Ball Speed
        ball_speed_button.draw(SCREEN)

        # Back button
        back_button.draw(SCREEN)

    elif game_state == "difficulty":
        draw_text_center(f"Current Difficulty: {difficulty_name}", SMALL_FONT, LIGHT_GREY, 50)
        draw_text_center(f"Current Game Mode: {game_mode}", SMALL_FONT, LIGHT_GREY, 100)
        ai_diff_button.draw(SCREEN)
        pvp_diff_button.draw(SCREEN)

        easy_button.draw(SCREEN)
        medium_button.draw(SCREEN)
        hard_button.draw(SCREEN)
        diff_back_button.draw(SCREEN)
        
    elif game_state == "ball_speed":
        ball_speed_slider.draw(SCREEN, "Ball Speed")
        bs_back_button.draw(SCREEN)

    elif game_state == "playing":
        keys = pygame.key.get_pressed()
        
        # AI mode movement (right paddle)
        if game_mode == "AI":
            ai_control(ai_paddle, ball, difficulty_name)

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                player_paddle.move_up()
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                player_paddle.move_down()
            
        # PvP mode movement (left paddle)
        elif game_mode == "PvP":
            if keys[pygame.K_w]:
                player_paddle.move_up()
            if keys[pygame.K_s]:
                player_paddle.move_down()
            
            if keys[pygame.K_UP]:
                ai_paddle.move_up()
            if keys[pygame.K_DOWN]:
                ai_paddle.move_down()


        # Update ball and obstacle
        ball.update()
        if obstacle is not None:
            obstacle.update()


        # Collisions with paddles
        if ball.vx < 0:
            handle_ball_paddle_collision(ball, player_paddle, moving_right=False)
        else:
            handle_ball_paddle_collision(ball, ai_paddle, moving_right=True)


        # Collision with obstacle
        handle_ball_obstacle_collision(ball, obstacle)


        # Scoring
        if ball.x < 0:
            ai_score += 1
            ball.reset(direction=1)

        if ball.x > WIDTH:
            player_score += 1
            ball.reset(direction=-1)


        # Stage / game ending logic
        if game_mode == "AI":
            if player_score >= WIN_SCORE_PER_STAGE:
                if stage < MAX_STAGE:
                    game_state = "stage_clear"
                else:
                    game_state = "victory"
            if ai_score >= WIN_SCORE_PER_STAGE:
                game_state = "game_over"
            
        else:
            if player_score >= WIN_SCORE_PER_STAGE:
                game_state = "victory"
            
            if ai_score >= WIN_SCORE_PER_STAGE:
                game_state = "game_over"
        

        # Draw game
        if game_mode == "AI":
            draw_middle_line()
            draw_score(player_score, ai_score, stage, difficulty_name, game_mode, ball_speed_setting)
            player_paddle.draw(SCREEN)
            ai_paddle.draw(SCREEN)
            ball.draw(SCREEN)
            if obstacle is not None:
                obstacle.draw(SCREEN)
        else:
            draw_middle_line()
            draw_score_pvp(player_score, ai_score, game_mode, ball_speed_setting)
            player_paddle.draw(SCREEN)
            ai_paddle.draw(SCREEN)
            ball.draw(SCREEN)

            if difficulty_name == "MediumPvP" or difficulty_name == "HardPvP":
                obstacle.draw(SCREEN)

        # Instructions
        if game_mode == "AI":
            info = SMALL_FONT.render("Controls: W/S = Move | ESC = Menu", True, LIGHT_GREY)
        else:
            info = SMALL_FONT.render("P1: W/S   P2: UP/DOWN | ESC = Menu", True, LIGHT_GREY)
        SCREEN.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT - 35))

        

    elif game_state == "stage_clear":
        draw_text_center("STAGE CLEAR!", TITLE_FONT, GREEN, 180)
        draw_text_center(f"You completed Stage {stage}", MENU_FONT, WHITE, 240)
        next_stage_button.draw(SCREEN)
        menu_button.draw(SCREEN)

    elif game_state == "game_over":
        if game_mode == "AI":
            draw_text_center("GAME OVER", TITLE_FONT, RED, 180)
            message = "The AI won this match."
        else:
            draw_text_center("MATCH ENDED!", TITLE_FONT, GREEN, 180)
            message = "Player 2 won this match."
        
        draw_text_center(message, MENU_FONT, WHITE, 240)
        restart_button.draw(SCREEN)
        menu_button.draw(SCREEN)

    elif game_state == "victory":
        if game_mode == "AI":
            draw_text_center("YOU WIN!", TITLE_FONT, GREEN, 180)
            message = "You completed all stages."
        else:
            draw_text_center("MATCH ENDED!", TITLE_FONT, GREEN, 180)
            message = "Player 1 won the match."
        
        draw_text_center(message, MENU_FONT, WHITE, 240)
        restart_button.draw(SCREEN)
        menu_button.draw(SCREEN)

    pygame.display.flip()

pygame.quit()
sys.exit()
