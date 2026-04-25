from pygame import *
import socket
import json
from threading import Thread
import time as std_time

# ---ПУГАМЕ НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 800, 600
init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")
# ---СЕРВЕР ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080)) # ---- Підключення до сервера
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass


def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break

# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font("fonts/Pacifico-Regular.ttf", 36)

# --- ЗВУКИ ---
# ініціалізація звукової системи
mixer.init()
wall_sound = mixer.Sound("sounds/submority-boom-geomorphism-cinematic-trailer-sound-effects-123876.mp3")
platform_sound = mixer.Sound("sounds/universfield-cinematic-impact-hit-352702.mp3")

# --- ЗОБРАЖЕННЯ ----
#
ball_img = image.load("images/openclipart-vectors-football-157930_640.png")
ball_img = transform.scale(ball_img, (40, 40))
# завантажуємо картинку для фону
main_background = image.load("images/pexels-cosmos-1853491.jpg").convert()
main_background = transform.scale(main_background, (WIDTH, HEIGHT))

# фон для перемоги та поразки
win_bg = image. load("images/depositphotos_687471448-stock-illustration-you-win-prize-word-concept.jpg").convert()
win_bg = transform.scale(win_bg,(WIDTH, HEIGHT))
lose_bg = image. load ("images/depositphotos_45208547-stock-illustration-you-lose.jpg").convert()
lose_bg = transform.scale(lose_bg,  (WIDTH, HEIGHT))
# --- ГРА ---
game_over = False
winner = None
you_winner = None
my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()
while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

        # для рестарту гри
        if e.type == KEYDOWN and e.key == K_k:
            if "winner" in game_state and game_state["winner"] is not None:
                # Зупиняємо receive() потік
                game_over = True
                std_time.sleep(0.15)  # даємо потоку час завершитись

                # Скидаємо стан
                game_state = {}
                you_win = None
                game_over = False

                # Перепідключення і новий потік
                my_id, game_state, buffer, client = connect_to_server()
                Thread(target=receive, daemon=True).start()

    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.fill((0, 0, 0))
        countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, (255, 255, 255))
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        continue  # Не малюємо гру до завершення відліку

    if "winner" in game_state and game_state["winner"] is not None:
        screen.fill((20, 20, 20))

        if you_winner is None:  # Встановлюємо тільки один раз
            if game_state["winner"] == my_id:
                you_winner = True
            else:
                you_winner = False

            if you_winner:
                screen.blit(win_bg, (0, 0))
            else:
                screen.blit(lose_bg, (0, 0))
        win_text = font_win.render(text, True, (255, 215, 0))
        text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_text, text_rect)

        text = font_win.render('К - рестарт', True, (255, 215, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(text, text_rect)

        display.update()
        continue  # Блокує гру після перемоги

    if game_state:
        # screen.fill((30, 30, 30))
        screen.blit(main_background, (0, 0), )
        draw.rect(screen, (0, 255, 0), (20, game_state['paddles']['0'], 20, 100))
        draw.rect(screen, (255, 0, 255), (WIDTH - 40, game_state['paddles']['1'], 20, 100))
        # draw.circle(screen, (255, 255, 255), (game_state['ball']['x'], game_state['ball']['y']), 10)
        screen.blit(ball_img, (game_state['ball']['x'] - 10, game_state['ball']['y'] - 10))
        score_text = font_main.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH // 2 -25, 20))

        if game_state['sound_event']:
            if game_state['sound_event'] == 'wall_hit':
                # звук відбиття м'ячика від стін
                wall_sound.play()
            if game_state['sound_event'] == 'platform_hit':
                # звук відбиття м'ячика від платформи
                platform_sound.play()

    else:
        wating_text = font_main.render(f"Очікування гравців...", True, (255, 255, 255))
        screen.blit(wating_text, (WIDTH // 2 - 25, 20))

    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")
