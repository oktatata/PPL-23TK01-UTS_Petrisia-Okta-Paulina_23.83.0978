import time, sys, math, random, os, colorsys, shutil


if os.name == "nt":
    try:
        import winsound
        def beep(freq=1000, dur=50):
            try:
                winsound.Beep(int(freq), int(dur))
            except Exception:
                pass
    except Exception:
        def beep(freq=1000, dur=50): pass
else:
    def beep(freq=1000, dur=50): pass


FPS = 25.0
FRAME_SLEEP = 1.0 / FPS
MODE_DURATION = 12 
START_TIME = time.time()

BASE_TEXT = "********"
BOUNCE_MAX = 40


def term_size():
    cols, rows = shutil.get_terminal_size((100, 30))
    return int(cols), int(rows)

RESET = "\033[0m"
CLEAR = "\033c"

def hsv_to_ansi(h, s=1.0, v=0.95):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    ir = int(max(0, min(255, round(r * 255))))
    ig = int(max(0, min(255, round(g * 255))))
    ib = int(max(0, min(255, round(b * 255))))
    return f"\033[38;2;{ir};{ig};{ib}m"

def rainbow_hue(frame, offset=0.0, speed=0.12):
    return hsv_to_ansi((frame * speed + offset) % 1.0, 1.0, 0.98)

def bright_color_rgb(frame, phase=0.0):
    # strong bright RGB cycle, fallback
    r = int((math.sin(frame * 0.6 + phase) + 1) * 120 + 120)
    g = int((math.sin(frame * 0.6 + 2 + phase) + 1) * 120 + 120)
    b = int((math.sin(frame * 0.6 + 4 + phase) + 1) * 120 + 120)
    return f"\033[38;2;{r};{g};{b}m"

# ----------------- Global animation state -----------------
indent = 0
indentIncreasing = True
frame = 0.0
bounce_pos = 0
bounce_dir = 1

# ----------------- Basic effects (kept) -----------------
def wave_offset(f, idx=0, amp=2, freq=0.28):
    return int(math.sin(f * freq + idx * 0.9) * amp)

def glitch(base, f, chance=0.16):
    if len(base) == 0: return base
    if random.random() < chance:
        chars = ['#','%','@','+','✦','✧','★','X','&','Φ']
        pos = random.randint(0, len(base)-1)
        g = list(base)
        g[pos] = random.choice(chars)
        beep(1200, 40)
        return "".join(g)
    return base

def print_with_trail(local_indent, color_code, text, f):
    wave = wave_offset(f, 0)
    main_indent = max(0, local_indent + wave)
    # flash chance
    if random.random() < 0.05:
        print(f"\033[38;2;255;255;255m{' ' * main_indent}{text}{RESET}")
        return
    print(f"{color_code}{' ' * main_indent}{text}{RESET}")
    # trail
    trail_levels = [0.5, 0.30, 0.16]
    for i, fade in enumerate(trail_levels, start=1):
        r = int(255 * fade); g = int(200 * fade); b = int(255 * fade)
        tcol = f"\033[38;2;{r};{g};{b}m"
        if main_indent - i >= 0:
            print(f"{tcol}{' ' * (main_indent - i)}{text}{RESET}")

# ----------------- moving neon text (bouncing) -----------------
def moving_neon_text(f, cols):
    global bounce_pos, bounce_dir
    txt = "UTS PPL OKTA"
    max_pos = max(0, min(BOUNCE_MAX, cols - len(txt) - 4))
    bounce_pos += bounce_dir
    if bounce_pos >= max_pos or bounce_pos <= 0:
        bounce_dir *= -1
    # shadow neon
    shadow = "\033[38;2;40;0;80m"
    # per-char rainbow bright
    out = []
    for i, ch in enumerate(txt):
        out.append(rainbow_hue(f, offset=i*0.04, speed=0.22) + ch + RESET)
    print(" " * (bounce_pos + 1) + shadow + txt + RESET)
    print(" " * bounce_pos + "".join(out))

# ----------------- rocket (bigger) -----------------
BIG_ROCKET = [
"        /^\\",
"       / _ \\",
"      |.o '.|",
"      |'._.'|",
"      |     |",
"      | NASA|",
"      |     |",
"     /|##!##|\\",
"    / |##!##| \\",
"   /  '-----'  \\",
"      \\  |  /",
"       \\ | /",
"        \\ /"
]

def launch_rocket(f, cols):
    # animate short run across center
    steps = min(40, max(20, cols//4))
    for pos in range(0, steps, max(1, steps//10)):
        print(CLEAR, end="")
        # rocket lines
        for i, ln in enumerate(BIG_ROCKET):
            col = rainbow_hue(f + i*0.05, offset=0.02)
            print(" " * (pos + cols//6) + col + ln + RESET)
        # laser stream
        laser_len = min(cols - (pos + cols//3) - 6, random.randint(10, 30))
        if laser_len > 0:
            stream = "".join([rainbow_hue(f + k*0.02, offset=k*0.01) + "-" + RESET for k in range(laser_len)])
            print(" " * (pos + cols//3) + stream)
        # sparks
        for _ in range(3):
            sp = rainbow_hue(f + random.random()*0.2)
            print(" " * random.randint(0, cols-1) + sp + random.choice(['✦','✧','★','✶']) + RESET)
        time.sleep(0.04)
        # no global clear - continue to caller
    # final boom
    beep(800, 80)
    print(rainbow_hue(f) + " " * (cols//2 - 4) + "✸ BOOM ✸" + RESET)
    # small pause
    time.sleep(0.18)

# ----------------- Spiral stars canvas -----------------
def spiral_canvas(count, turns, cols, rows, f):
    canvas = [list(" " * cols) for _ in range(rows)]
    cx = rows // 2
    cy = cols // 2
    max_r = max(2, min(rows//2 - 2, cols//3))
    for i in range(count):
        t = i / float(count)
        angle = 2 * math.pi * (turns * t) + f * 0.12
        radius = max_r * t
        rpos = int(cx + math.sin(angle) * radius)
        cpos = int(cy + math.cos(angle) * radius * 1.8)
        if 0 <= rpos < rows and 0 <= cpos < cols:
            canvas[rpos][cpos] = rainbow_hue(f, offset=i*0.03) + "*" + RESET
    return canvas

# ----------------- sparks many -----------------
def many_sparks(f, cols, density=0.25):
    out = []
    for _ in range(int(6 * density * 10)):
        pos = random.randint(0, cols-1)
        out.append(" " * pos + rainbow_hue(f + random.random()*0.2) + random.choice(['✦','✧','★','✶','❇']) + RESET)
    return out

# ----------------- thunder effect -----------------
def thunder_strike(f, cols):
    if random.random() < 0.015:
        beep(180, 140)
        # flash screen quick
        print("\033[48;2;255;255;255m" + " " * cols + RESET)
        print(" " * (cols//2 - 5) + "\033[38;2;255;255;255m⚡⚡⚡" + RESET)
        time.sleep(0.05)

# ----------------- side explosions -----------------
def side_explosions(f, cols):
    parts = ['*','✦','✧','❇','+','•']
    out = []
    for _ in range(6):
        left = random.randint(0, max(1, cols//6))
        right = random.randint(max(0, cols - cols//6), max(1, cols-1))
        out.append(" " * left + rainbow_hue(f + random.random()*0.2) + random.choice(parts) + RESET)
        out.append(" " * right + rainbow_hue(f + random.random()*0.2) + random.choice(parts) + RESET)
    return out

# ----------------- MATRIX rain -----------------
MATRIX_CHARS = [chr(i) for i in range(33, 127)]
def matrix_rain(cols, rows, f):
    canvas = [list(" " * cols) for _ in range(rows)]
    drops = cols // 3
    for d in range(drops):
        x = random.randint(0, cols-1)
        h = random.randint(3, rows//2)
        for y in range(h):
            rr = (int(f*10) + y) % rows
            col = f"\033[38;2;0;{200 - y%120};{0 + y%100}m"  # green-ish gradient
            canvas[rr][x] = col + random.choice(MATRIX_CHARS) + RESET
    return canvas

# ----------------- blackhole gravity -----------------
def blackhole_particles(cols, rows, f):
    cx = rows//2; cy = cols//2
    canvas = [list(" " * cols) for _ in range(rows)]
    for i in range(120):
        angle = random.random() * 2 * math.pi + f * 0.5
        r = int((random.random() ** 1.8) * min(rows, cols) / 3)
        rr = int(cx + math.sin(angle) * r)
        cc = int(cy + math.cos(angle) * r)
        if 0 <= rr < rows and 0 <= cc < cols:
            canvas[rr][cc] = hsv_to_ansi((f*0.1 + r*0.01)%1.0, 1.0, 0.9) + random.choice(['.','•','*']) + RESET
    return canvas

# ----------------- galaxy supernova -----------------
def supernova_canvas(cols, rows, f):
    canvas = [list(" " * cols) for _ in range(rows)]
    cx = rows//2; cy = cols//2
    radius = int(1 + abs(math.sin(f * 0.3)) * min(rows, cols) / 3)
    for r in range(-radius, radius+1):
        for c in range(-radius, radius+1):
            rr = cx + r; cc = cy + c
            if 0 <= rr < rows and 0 <= cc < cols and (r*r + c*c) <= (radius*radius):
                canvas[rr][cc] = hsv_to_ansi((f*0.05 + (r+c)*0.02)%1.0, 1.0, 0.98) + random.choice(['*','✸','✶']) + RESET
    return canvas

# ----------------- ice frost -----------------
def ice_frost_canvas(cols, rows, f):
    canvas = [list(" " * cols) for _ in range(rows)]
    for _ in range((cols*rows)//80):
        rr = random.randint(0, rows-1)
        cc = random.randint(0, cols-1)
        canvas[rr][cc] = f"\033[38;2;160;220;255m" + random.choice(['❄','✻','✼','*']) + RESET
    return canvas

# ----------------- dragon neon -----------------
DRAGON = [
    "               / \\  //\\",
    "      |\\___/| /  \\//  .\\",
    "      /O  O  \\/    \\   /",
    "     /     /  \\     \\_/ ",
    "    @___@'    '._,/'"
]
def dragon_neon(cols, f):
    output = []
    base_indent = cols//3
    for i, line in enumerate(DRAGON):
        color = hsv_to_ansi((f*0.06 + i*0.03)%1.0,1.0,0.95)
        output.append(" " * base_indent + color + line + RESET)
    # add flame particles
    for _ in range(6):
        p = rainbow_hue(f + random.random()*0.3)
        output.append(" " * random.randint(0, cols-1) + p + random.choice(['🔥','✶','✸']) + RESET)
    return output

# ----------------- API BURN (screen berkobar) -----------------
def api_burn(cols, rows, f):
    segs = []
    for r in range(rows//6):
        # bands of orange/red flicker
        hue = (f*0.2 + r*0.04) % 1.0
        col = hsv_to_ansi(hue, 1.0, 0.98)
        segs.append(col + " " * cols + RESET)
    return segs

# ----------------- utility to print canvas (list of lists/strings) -----------------
def print_canvas(canvas):
    for row in canvas:
        if isinstance(row, list):
            print("".join(row))
        else:
            print(row)

# ----------------- Mode selector -----------------
MODES = [
    "RAINBOW_CORE",      # 0
    "CYBERPUNK_NEON",    # 1
    "GALAXY_SPACE",      # 2
    "API_BURN",          # 3
    "DRAGON_NEON",       # 4
    "BLACKHOLE",         # 5
    "SUPERNOVA",         # 6
    "MATRIX",            # 7
    "ICE_FROST"          # 8
]

def current_mode():
    elapsed = int(time.time() - START_TIME)
    # cycle through modes every MODE_DURATION seconds; allow wrap among big set
    idx = (elapsed // MODE_DURATION) % len(MODES)
    return MODES[idx]

# ----------------- MAIN LOOP -----------------
try:
    while True:
        cols, rows = term_size()
        rows_canvas = max(10, rows - 8)
        print(CLEAR, end="")
        t = time.time() - START_TIME
        mode = current_mode()
        # top: bouncing neon text
        moving_neon_text(t, cols)
        # small spark header
        for s in many_sparks(t, cols, density=0.5)[:4]:
            print(s)
        print()  # gap

        # mode-specific canvas
        if mode == "RAINBOW_CORE":
            canvas = spiral_canvas(40, 3, cols, rows_canvas, t)
            print_canvas(canvas)
        elif mode == "CYBERPUNK_NEON":
            # cyber grid: magenta/blue columns with neon chars
            canvas = [list(" " * cols) for _ in range(rows_canvas)]
            for c in range(0, cols, 6):
                col = hsv_to_ansi(0.85 + (c/cols)*0.1, 1.0, 0.95)
                for r in range(rows_canvas):
                    if random.random() < 0.06:
                        canvas[r][c] = col + random.choice(['█','▓','▒']) + RESET
            print_canvas(canvas)
            # neon overlays
            for line in dragon_neon(cols, t)[:3]:
                print(line)
        elif mode == "GALAXY_SPACE":
            canvas = blackhole_particles(cols, rows_canvas, t)
            # add slow rotating spiral overlay
            sp = spiral_canvas(30, 4, cols, rows_canvas, t)
            # merge print (simple)
            for r in range(rows_canvas):
                row = ""
                for c in range(cols):
                    a = canvas[r][c] if isinstance(canvas[r][c], str) and canvas[r][c] != " " else (sp[r][c] if sp[r][c] != " " else " ")
                    row += a
                print(row[:cols])
        elif mode == "API_BURN":
            segs = api_burn(cols, rows, t)
            for s in segs:
                print(s)
            # overlay small sparks
            for s in many_sparks(t, cols, density=0.8)[:6]:
                print(s)
        elif mode == "DRAGON_NEON":
            for line in dragon_neon(cols, t):
                print(line)
            # flying sparks
            for s in many_sparks(t, cols, density=0.9)[:8]:
                print(s)
        elif mode == "BLACKHOLE":
            canvas = blackhole_particles(cols, rows_canvas, t)
            print_canvas(canvas)
            # draw sucking lines
            for i in range(3):
                print(" " * (cols//2) + hsv_to_ansi((t*0.04 + i*0.1)%1.0) + "◉" + RESET)
        elif mode == "SUPERNOVA":
            canvas = supernova_canvas(cols, rows_canvas, t)
            print_canvas(canvas)
            # massive sparks overlay
            for s in many_sparks(t, cols, density=1.0)[:10]:
                print(s)
        elif mode == "MATRIX":
            canvas = matrix_rain(cols, rows_canvas, t)
            print_canvas(canvas)
        elif mode == "ICE_FROST":
            canvas = ice_frost_canvas(cols, rows_canvas, t)
            print_canvas(canvas)

        # common bottom region: main moving star + trail + side explosions + thunder occasional
        main_color = rainbow_hue(t, offset=0.02, speed=0.25)
        animated = glitch(BASE_TEXT, t, chance=0.16)
        print_with_trail(indent, main_color, animated, t)
        # side explosions
        for line in side_explosions(t, cols):
            print(line)
        # thunder
        thunder_strike(t, cols)
        # rocket occasionally
        if int(t) % 18 == 0 and random.random() < 0.6:
            launch_rocket(t, cols)
        # final many sparks
        for s in many_sparks(t, cols, density=0.8)[:8]:
            print(s)

        # pacing & movement updates
        time.sleep(FRAME_SLEEP)
        frame += FRAME_SLEEP
        # indent bounce (ke kiri-kanan)
        if indentIncreasing:
            indent += 1
            if indent >= max(1, cols//6):
                indentIncreasing = False
        else:
            indent -= 1
            if indent <= 0:
                indentIncreasing = True

except KeyboardInterrupt:
    print(RESET)
    sys.exit()
