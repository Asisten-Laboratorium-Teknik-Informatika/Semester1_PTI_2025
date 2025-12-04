import tkinter as tk
import random

snakes = {
    17: 7,
    54: 25,
    62: 37,
    98: 86,
    77: 26,
    91: 1

}
ladders = {
    3: 40,
    8: 15,
    28: 57,
    70: 89,
    10: 52,
    41: 75,
    63: 83
}

player_data = []
current_turn = 0
ladder_paths = {}
snake_paths = {}
def generate_path(start, end, steps=10):
    path = []
    x1, y1 = get_cell_center(start)
    x2, y2 = get_cell_center(end)
    for i in range(steps + 1):
        t = i / steps
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        path.append((x, y))
    return path

# ---------------- Board & drawing ----------------

def create_board(root):
    canvas = tk.Canvas(root, width=500, height=500, bg="white")
    canvas.pack()

    size = 50
    color1 = "#f0d5b0"
    color2 = "#c79c60"

    for row in range(10):
        for col in range(10):
            x1 = col * size
            y1 = row * size
            x2 = x1 + size
            y2 = y1 + size
            color = color1 if (row + col) % 2 == 0 else color2
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    add_numbers(canvas)
    draw_snakes_and_ladders(canvas)
    return canvas

def add_numbers(canvas, size=50):
    number = 1
    for row in range(9, -1, -1):
        cols = range(10) if (9 - row) % 2 == 0 else range(9, -1, -1)
        for col in cols:
            x = col * size + size / 2
            y = row * size + size / 2
            canvas.create_text(x, y, text=str(number), font=("Arial", 12))
            number += 1

def draw_snakes_and_ladders(canvas, size=50):
    for start, end in ladders.items():
        x1, y1 = get_cell_center(start, size)
        x2, y2 = get_cell_center(end, size)
        canvas.create_line(x1 - 10, y1, x2 - 10, y2, width = 6, fill = "#8B4513")
        canvas.create_line(x1 + 10, y1, x2 + 10, y2, width = 6, fill ="#8B4513")
        steps = 5
        for i in range(steps):
            t = i /steps
            sx = x1 + (x2 - x1) * t
            sy = y1 + (y2 - y1) * t
            canvas.create_line(sx - 15, sy, sx + 15, sy, width = 4, fill = "#CD853F")
    # Snakes
    for head, tail in snakes.items():
        x1, y1 = get_cell_center(head, size)
        x2, y2 = get_cell_center(tail, size)
        canvas.create_line(x1, y1, x2, y2, width=6, fill="#228b22")
        canvas.create_oval(x1 - 15, y1 - 15, x1 + 15, y1 + 15, fill="yellow", outline="")
        snake_paths[head] = [(x1, y1), (x2, y2)]

# Generate jalur tangga
    for start, end in ladders.items():
        ladder_paths[start] = generate_path(start, end)

    # untuk jalur ular
    for head, tail in snakes.items():
        snake_paths[head] = generate_path(head, tail)

def get_cell_center(number, size=50):
    number -= 1
    row = 9 - (number // 10)
    col = number % 10
    if (number // 10) % 2 == 1:
        col = 9 - col
    x = col * size + size / 2
    y = row * size + size / 2
    return x, y

def create_player_token(canvas, position=1, size=50, color="red"):
    x, y = get_cell_center(position, size)
    r = 10
    token = canvas.create_oval(x - r, y - r, x + r, y + r, fill=color)
    return token

# ---------------- Movement & animation ----------------

def move_player(canvas, token_id, position, size=50):
    x, y = get_cell_center(position, size)
    x1, y1, x2, y2 = canvas.coords(token_id)
    current_x = (x1 + x2) / 2
    current_y = (y1 + y2) / 2
    dx = x - current_x
    dy = y - current_y
    canvas.move(token_id, dx, dy)

def animate_move(canvas, token_id, start, end, delay=200, callback=None):
    if start > end:
        if callback:
            callback()
        return
    move_player(canvas, token_id, start)
    canvas.after(delay, lambda: animate_move(canvas, token_id, start + 1, end, delay, callback))

def animate_path(canvas, token_id, path, step=0, delay=100, callback=None):
    if step >= len(path):
        if callback:
            callback()
        return
    x, y = path[step]
    x1, y1, x2, y2 = canvas.coords(token_id)
    current_x = (x1 + x2) / 2
    current_y = (y1 + y2) / 2
    dx = x - current_x
    dy = y - current_y
    canvas.move(token_id, dx, dy)
    canvas.after(delay, lambda: animate_path(canvas, token_id, path, step + 1, delay, callback))

def animate_dice(root, dice_label, callback, frame=0):
    if frame < 10:
        dice_label.config(text=str(random.randint(1, 6)))
        root.after(50, lambda: animate_dice(root, dice_label, callback, frame + 1))
    else:
        callback()

def roll_dice_multi(canvas, player, dice_label, callback, roll_button):
    def finish_roll():
        dice = random.randint(1, 6)
        dice_label.config(text=str(dice))
        print(f"{player['name']} melempar dadu: {dice}")
        new_position = player["position"] + dice
        if new_position > 100:
            print("Udah hampir menang kau lek,tapi harus pas 100 yak")
            return callback()


        # Step 1: animasi ke kotak hasil dadu
        def after_dice():
            pos = new_position
            if pos in ladders:
                target = ladders[pos]
                print("Naik Tangga My Friend", pos, "->", target)
                path = ladder_paths[pos]
                animate_path(canvas, player["token"], path, callback=after_snake_ladder)
                player["position"] = target
            elif pos in snakes:
                target = snakes[pos]
                print("Aigoo kena Kena ular!", pos, "->", target)
                path = snake_paths[pos]
                animate_path(canvas, player["token"], path, callback=after_snake_ladder)
                player["position"] = target
            else:
                player["position"] = pos
                after_snake_ladder()

        def after_snake_ladder():
            if player["position"] == 100:
                win_label = tk.Label(canvas, text=f"SELAMAT, {player['name']} MENANG!",
                                      font=("Arial", 20, "bold"), fg="green", bg="white")
                win_label.place(x=80, y=220)
                roll_button.config(state="disabled")
                return
            global current_turn
            current_turn = (current_turn + 1) % len(player_data)
            callback()

        animate_move(canvas, player["token"], player["position"], new_position, callback=after_dice)

    animate_dice(canvas, dice_label, finish_roll)

# ---------------- Setup players & game flow ----------------

def setup_players(root):
    def submit():
        try:
            count = int(entry.get())
            if count < 2 or count > 4:
                raise ValueError
        except ValueError:
            label.config(text="Masukkan angka 2 sampai 4")
            return
        for widget in root.winfo_children():
            widget.destroy()
        ask_names(root, count)

    label = tk.Label(root, text="Berapa pemain? (2–4)", font=("Arial", 14))
    label.pack(pady=10)
    entry = tk.Entry(root, font=("Arial", 14))
    entry.pack(pady=5)
    button = tk.Button(root, text="Lanjut", font=("Arial", 14), command=submit)
    button.pack(pady=10)

def ask_names(root, count):
    entries = []
    def submit_names():
        colors = ["red", "blue", "green", "purple"]
        for i, e in enumerate(entries):
            name = e.get().strip()
            if not name:
                name = f"Pemain{i+1}"
            player_type = "AI" if name.lower() == "ai" else "Human"
            player_data.append({
                "name": name,
                "type": player_type,
                "position": 1,
                "token": None,
                "color": colors[i]
            })
        for widget in root.winfo_children():
            widget.destroy()
        start_game(root)

    label = tk.Label(root, text="Masukkan nama pemain (ketik 'AI' untuk bot)", font=("Arial", 14))
    label.pack(pady=10)
    for i in range(count):
        l = tk.Label(root, text=f"Pemain {i+1}:", font=("Arial", 12))
        l.pack()
        e = tk.Entry(root, font=("Arial", 12))
        e.pack()
        entries.append(e)
    button = tk.Button(root, text="Mulai Game", font=("Arial", 14), command=submit_names)
    button.pack(pady=10)

def start_game(root):
    global current_turn
    canvas = create_board(root)
    dice_label = tk.Label(root, text="", font=("Arial", 24), bg="white", width=3, relief="solid")
    dice_label.place(x=400, y=500)

    # Buat token untuk tiap pemain
    for player in player_data:
        token = create_player_token(canvas, position=1, color=player["color"])
        player["token"] = token
        player["position"] = 1

    turn_label = tk.Label(root, text="", font=("Arial", 14))
    turn_label.pack()

    roll_button = tk.Button(root, text="Roll Dice", font=("Arial", 14))
    roll_button.pack(pady=10)

    def next_turn():
        global current_turn
        player = player_data[current_turn]
        turn_label.config(text=f"Giliran: {player['name']}")
        if player["type"] == "AI":
            roll_button.config(state="disabled")
            root.after(1000, lambda: roll_dice_multi(canvas, player, dice_label, next_turn,roll_button))
        else:
            roll_button.config(state="normal",
                               command=lambda: roll_dice_multi(canvas, player, dice_label, next_turn,roll_button))

    next_turn()

# ---------------- Main ----------------

def main():
    root = tk.Tk()
    root.title("Game Ular Tangga - GUI")
    setup_players(root)
    root.mainloop()

if __name__ == "__main__":
    main()
