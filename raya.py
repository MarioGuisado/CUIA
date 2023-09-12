import curses
import time
import random

# Configuración de la pantalla
screen = curses.initscr()
curses.curs_set(0)
screen_height, screen_width = screen.getmaxyx()

# Configuración de la ventana del juego
window = curses.newwin(screen_height, screen_width, 0, 0)
window.keypad(True)
window.timeout(100)

# Posición inicial de la serpiente
snake_x = screen_width // 4
snake_y = screen_height // 2
snake = [[snake_y, snake_x], [snake_y, snake_x - 1], [snake_y, snake_x - 2]]

# Posición inicial de la comida
food = [screen_height // 2, screen_width // 2]
window.addch(food[0], food[1], "*")

# Dirección inicial de la serpiente
direction = curses.KEY_RIGHT

# Bucle principal del juego
while True:
    next_direction = window.getch()
    if next_direction in [curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_UP, curses.KEY_DOWN]:
        direction = next_direction

    # Calcular la nueva cabeza de la serpiente en función de la dirección
    new_head = [snake[0][0], snake[0][1]]
    if direction == curses.KEY_DOWN:
        new_head[0] += 1
    if direction == curses.KEY_UP:
        new_head[0] -= 1
    if direction == curses.KEY_LEFT:
        new_head[1] -= 1
    if direction == curses.KEY_RIGHT:
        new_head[1] += 1

    # Insertar la nueva cabeza de la serpiente
    snake.insert(0, new_head)

    # Comprobar si la serpiente ha chocado con los bordes de la pantalla
    if snake[0][0] in [0, screen_height - 1] or snake[0][1] in [0, screen_width - 1]:
        curses.endwin()
        quit()

    # Comprobar si la serpiente ha chocado consigo misma
    if snake[0] in snake[1:]:
        curses.endwin()
        quit()

    # Comprobar si la serpiente ha comido la comida
    if snake[0] == food:
        food = None
        while food is None:
            new_food = [random.randint(1, screen_height-2), random.randint(1, screen_width-2)]
            food = new_food if new_food not in snake else None
        window.addch(food[0], food[1], "*")
    else:
        tail = snake.pop()
        window.addch(tail[0], tail[1], " ")

    # Dibujar la serpiente
    window.addch(snake[0][0], snake[0][1], "@")
    for i in range(1, len(snake)):
        window.addch(snake[i][0], snake[i][1], "o")

    # Actualizar la pantalla
    window.refresh()

    # Velocidad de la serpiente
    time.sleep(0.1)
