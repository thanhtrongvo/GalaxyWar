import pygame
import os
import random
import math

# Khởi tạo Pygame
pygame.font.init()
pygame.mixer.init()

# Định nghĩa kích thước cửa sổ
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy War")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Biên giới
BORDER = pygame.Rect(WIDTH / 2 - 5, 0, 10, HEIGHT)

# Âm thanh đạn
BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'GunHit.wav'))
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'GunFire.mp3'))
MENU_MUSIC = pygame.mixer.Sound(os.path.join('Assets', 'menu.mp3'))
GAME_OVER_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'dead.wav'))
IN_GAME_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'ingame.mp3'))

# Font chữ
HEALTH_FONT = pygame.font.SysFont('didot.ttc', 40)
WINNER_FONT = pygame.font.SysFont('chalkduster.ttf', 100)
MENU_FONT = pygame.font.SysFont('chalkduster.ttf', 50)

# Cài đặt FPS và tốc độ di chuyển
FPS = 60
VEL = 5
BULLET_VEL = 7
MAX_BULLETS = 3
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40
SHOOT_PROBABILITY = 1
MAX_BOT_BULLETS = 1
BOT_VEL = 5
bot_update_count = 50
bot_update_frequency = 10
MAX_MOVE = 10
# Sự kiện khi máy bay bị bắn trúng
YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

# Load hình ảnh
YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join("Assets", "spaceship_yellow.png"))
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)
RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join("Assets", "spaceship_red.png"))
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)
SPACE = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'space.png')), (WIDTH, HEIGHT))
SPACE2 = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'space2.png')), (WIDTH, HEIGHT))

# Hàm vẽ cửa sổ game
def draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health):
    WIN.blit(SPACE, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)

    red_health_text = HEALTH_FONT.render("Health: " + str(red_health), 1, WHITE)
    yellow_health_text = HEALTH_FONT.render("Health: " + str(yellow_health), 1, WHITE)
    WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 10, 10))
    WIN.blit(yellow_health_text, (10, 10))

    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))

    for bullet in red_bullets:
        pygame.draw.rect(WIN, RED, bullet)
    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, YELLOW, bullet)

    pygame.display.update()

# Hàm xử lý di chuyển của máy bay màu vàng
def yellow_handle_movement(keys_pressed, yellow):
    if keys_pressed[pygame.K_a] and yellow.x - VEL > 0:  # LEFT
        yellow.x -= VEL
    if keys_pressed[pygame.K_d] and yellow.x + VEL + yellow.width < BORDER.x:  # RIGHT
        yellow.x += VEL
    if keys_pressed[pygame.K_w] and yellow.y - VEL > 0:  # UP
        yellow.y -= VEL
    if keys_pressed[pygame.K_s] and yellow.y + VEL + yellow.height < HEIGHT - 15:  # DOWN
        yellow.y += VEL

# Hàm xử lý di chuyển của máy bay màu đỏ
def red_handle_movement(keys_pressed, red):
    if keys_pressed[pygame.K_LEFT] and red.x - VEL > BORDER.x + BORDER.width:  # LEFT
        red.x -= VEL
    if keys_pressed[pygame.K_RIGHT] and red.x + VEL + red.width < WIDTH:  # RIGHT
        red.x += VEL
    if keys_pressed[pygame.K_UP] and red.y - VEL > 0:  # UP
        red.y -= VEL
    if keys_pressed[pygame.K_DOWN] and red.y + VEL + red.height < HEIGHT - 15:  # DOWN
        red.y += VEL

# Hàm xử lý đạn
def handle_bullets(yellow_bullets, red_bullets, yellow, red):
    for bullet in yellow_bullets:
        bullet.x += BULLET_VEL
        if red.colliderect(bullet):
            pygame.event.post(pygame.event.Event(RED_HIT))
            yellow_bullets.remove(bullet)
        elif bullet.x > WIDTH:
            yellow_bullets.remove(bullet)

    for bullet in red_bullets:
        bullet.x -= BULLET_VEL
        if yellow.colliderect(bullet):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            red_bullets.remove(bullet)
        elif bullet.x < 0:
            red_bullets.remove(bullet)

# Hàm vẽ người chiến thắng
def draw_winner(text):
    draw_text = WINNER_FONT.render(text, 1, WHITE)
    WIN.blit(draw_text, (WIDTH / 2 - draw_text.get_width() / 2, HEIGHT / 2 - draw_text.get_height() / 2))
    pygame.display.update()

    GAME_OVER_SOUND.play()

    pygame.time.delay(5000)

def detect_collision(rect1, rect2):
    return rect1.colliderect(rect2)

# Hàm giúp bot né đạn
def bot_avoid_bullet(bot_rect, bullet_rect, bullet_speed):
    # Tính toán vị trí dự kiến của đạn sau một khoảng thời gian
    future_bullet_x = bullet_rect.x + bullet_speed
    future_bullet_y = bullet_rect.y

    # Kiểm tra xem vị trí tiềm năng của đạn có chạm vào bot không
    if bot_rect.collidepoint(future_bullet_x, future_bullet_y):
        # Nếu có, di chuyển bot sang một hướng khác
        # Ví dụ: di chuyển bot sang trái
        bot_rect.x -= VEL
    else:
        # Nếu không, bot giữ nguyên vị trí
        pass

def bot_movement(bot_plane, player_plane):
    global BOT_VEL
    global bot_update_count
    global bot_update_frequency

    # # Tăng đếm lượt cập nhật
    # bot_update_count += 1
    #
    # # Chỉ cập nhật vị trí bot sau mỗi số lượt nhất định
    # if bot_update_count % bot_update_frequency == 0:
    #     # Chọn ngẫu nhiên hướng di chuyển
    #     direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
    #
    #     if direction == "UP" and bot_plane.y - BOT_VEL > 0:
    #         bot_plane.y -= BOT_VEL
    #     elif direction == "DOWN" and bot_plane.y + BOT_VEL + bot_plane.height < HEIGHT:
    #         bot_plane.y += BOT_VEL
    #     elif direction == "LEFT" and bot_plane.x - BOT_VEL > BORDER.x + BORDER.width:
    #         bot_plane.x -= BOT_VEL
    #     elif direction == "RIGHT" and bot_plane.x + BOT_VEL + bot_plane.width < WIDTH:
    #         bot_plane.x += BOT_VEL
    #
    #     # Đặt lại đếm lượt cập nhật
    #     bot_update_count = 0


    # # Calculate the distance between the bot and the player
    dx = player_plane.x - bot_plane.x
    dy = player_plane.y - bot_plane.y
    #

    #
    # # Calculate the absolute distance between the bot and the player
    distance = math.sqrt(dx**2 + dy**2)

    # If the distance is greater than the maximum move distance,
    # limit the bot's movement to move towards the player
    if distance > MAX_MOVE:
        # Calculate the normalized direction vector towards the player
        direction_x = dx / distance
        direction_y = dy / distance

        # Update the bot's position based on the direction vector and maximum move distance
        # bot_plane.x += direction_x * MAX_MOVE
        bot_plane.y += direction_y * MAX_MOVE
    else:
    #     # If the distance is less than or equal to the maximum move distance,
    #     # move the bot directly to the player's position
    #     bot_plane.x = player_plane.x
        bot_plane.y = player_plane.y


    # Ensure the bot stays within the screen boundaries
    bot_plane.x = max(BORDER.x + BORDER.width, min(bot_plane.x, WIDTH - bot_plane.width))
    bot_plane.y = max(0, min(bot_plane.y, HEIGHT - bot_plane.height - 15))


def bot_shoot(bot_plane, red_bullets):
    # Check if the bot should shoot based on the probability and the current number of bullets
    if len(red_bullets) < MAX_BOT_BULLETS and random.randint(1, SHOOT_PROBABILITY) == 1:
        # Create a bullet at the bot's position
        bullet = pygame.Rect(bot_plane.x, bot_plane.y + bot_plane.height // 2 - 2, 10, 5)
        red_bullets.append(bullet)
        BULLET_FIRE_SOUND.play()

# Hàm logic bot
def bot_logic(bot_plane, player_plane, red_bullets):
    # Move bot towards player within certain range
    bot_movement(bot_plane, player_plane)

    # Shoot randomly when player is close
    bot_shoot(bot_plane, red_bullets)

    # # Ensure bot stays within screen boundaries
    # if bot_plane.x < 0:
    #     bot_plane.x = 0
    # elif bot_plane.x > WIDTH - bot_plane.width:
    #     bot_plane.x = WIDTH - bot_plane.width
    # if bot_plane.y < 0:
    #     bot_plane.y = 0
    # elif bot_plane.y > HEIGHT - bot_plane.height:
    #     bot_plane.y = HEIGHT - bot_plane.height


# Hàm chính
def main(single_player=True):
    red = pygame.Rect(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    yellow = pygame.Rect(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

    red_bullets = []
    yellow_bullets = []

    red_health = 10
    yellow_health = 10

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(yellow.x + yellow.width, yellow.y + yellow.height // 2 - 2, 10, 5)
                    yellow_bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()

                if event.key == pygame.K_RCTRL and len(red_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(red.x, red.y + red.height // 2 - 2, 10, 5)
                    red_bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()

            if event.type == RED_HIT:
                red_health -= 1
                BULLET_HIT_SOUND.play()

            if event.type == YELLOW_HIT:
                yellow_health -= 1
                BULLET_HIT_SOUND.play()

        winner_text = ""
        if red_health <= 0:
            winner_text = "Yellow Wins!"

        if yellow_health <= 0:
            winner_text = "Red Wins!"

        if winner_text != "":
            draw_winner(winner_text)
            menu_end()
            break

        keys_pressed = pygame.key.get_pressed()
        yellow_handle_movement(keys_pressed, yellow)

        if single_player:
            bot_logic(red, yellow, red_bullets)
        else:
            red_handle_movement(keys_pressed, red)

        handle_bullets(yellow_bullets, red_bullets, yellow, red)
        draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health)

    main_menu()

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    WIN.blit(text_surface, text_rect)


def menu_end():
    MENU_MUSIC.play()
    run = True
    while run:
        WIN.blit(SPACE2, (0, 0))
        draw_text("Game Over", WINNER_FONT, WHITE, WIDTH / 2, HEIGHT / 5)
        draw_text("Press 'R' to Restart", MENU_FONT, WHITE, WIDTH / 2, HEIGHT / 2 - 50)
        draw_text("Press 'M' to Menu", MENU_FONT, WHITE, WIDTH / 2, HEIGHT / 2 + 50)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main(single_player=True)
                    MENU_MUSIC.stop()
                if event.key == pygame.K_m:
                    MENU_MUSIC.stop()
                    main_menu()
    pygame.quit()
# Hàm menu chính
def main_menu():
    pygame.mixer.Sound.play(MENU_MUSIC)  # Phát nhạc nền cho menu
    run = True
    while run:
        WIN.blit(SPACE2, (0, 0))
        draw_text("Galaxy War", WINNER_FONT, WHITE, WIDTH / 2, HEIGHT / 5)
        draw_text("Press '1' for Single Player", HEALTH_FONT, WHITE, WIDTH / 2, HEIGHT / 2 - 50)
        draw_text("Press '2' for Multiplayer", HEALTH_FONT, WHITE, WIDTH / 2, HEIGHT / 2 + 50)
        draw_text("Press ESC to Quit", HEALTH_FONT, WHITE, WIDTH / 2, HEIGHT / 2 + 150)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    pygame.mixer.Sound.stop(MENU_MUSIC)  # Dừng nhạc nền
                    main(single_player=True)
                if event.key == pygame.K_2:
                    pygame.mixer.Sound.stop(MENU_MUSIC)  # Dừng nhạc nền
                    main(single_player=False)
                if event.key == pygame.K_ESCAPE:
                    run = False
    pygame.quit()


if __name__ == "__main__":
    main_menu()