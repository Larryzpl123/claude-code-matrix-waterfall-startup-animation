#!/usr/bin/env python3
"""Matrix rain splash screen for Claude Code."""

import curses
import random
import time
import sys

CHARS = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    "!@#$%^&*()_+-=[]{}|;:,.<>?"
    "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
)

CLAUDE_ART = [
    r" ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗",
    r"██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝",
    r"██║     ██║     ███████║██║   ██║██║  ██║█████╗  ",
    r"██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝  ",
    r"╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗",
    r" ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝╚══════╝",
    r"",
    r"        ██████╗ ██████╗ ██████╗ ███████╗          ",
    r"       ██╔════╝██╔═══██╗██╔══██╗██╔════╝          ",
    r"       ██║     ██║   ██║██║  ██║█████╗            ",
    r"       ██║     ██║   ██║██║  ██║██╔══╝            ",
    r"       ╚██████╗╚██████╔╝██████╔╝███████╗          ",
    r"        ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝          ",
]

TAGLINE = "[ Enter the Matrix ]"


def make_column(height, width, x):
    return {
        "x": x,
        "y": random.randint(-height, 0),
        "speed": random.uniform(0.3, 1.0),
        "length": random.randint(6, height // 2),
        "next_tick": 0.0,
        "chars": [random.choice(CHARS) for _ in range(height + 40)],
    }


def run(stdscr, duration=3.5, freeze=1.8):
    curses.curs_set(0)
    stdscr.nodelay(True)
    curses.start_color()
    curses.use_default_colors()

    # Color pairs
    curses.init_pair(1, curses.COLOR_GREEN, -1)       # normal green
    curses.init_pair(2, curses.COLOR_WHITE, -1)        # head (white)
    curses.init_pair(3, curses.COLOR_GREEN, -1)        # dim green (reuse, use dim attr)
    curses.init_pair(4, curses.COLOR_CYAN, -1)         # claude art cyan
    curses.init_pair(5, curses.COLOR_WHITE, -1)        # claude art white bold
    curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)  # art bg

    height, width = stdscr.getmaxyx()
    col_spacing = 2
    columns = [make_column(height, width, x) for x in range(0, width, col_spacing)]

    start = time.time()
    frame_delay = 0.04

    # Phase 1: falling rain
    while True:
        now = time.time()
        elapsed = now - start

        if elapsed >= duration:
            break

        stdscr.erase()

        for col in columns:
            if now >= col["next_tick"]:
                col["y"] += 1
                col["next_tick"] = now + col["speed"] * frame_delay * 6
                # randomize a char in the trail occasionally
                if random.random() < 0.2:
                    idx = random.randint(0, len(col["chars"]) - 1)
                    col["chars"][idx] = random.choice(CHARS)
            if col["y"] - col["length"] > height:
                col["y"] = random.randint(-height // 2, 0)
                col["speed"] = random.uniform(0.3, 1.0)
                col["length"] = random.randint(6, height // 2)

            for i in range(col["length"]):
                y = col["y"] - i
                if 0 <= y < height - 1 and col["x"] < width - 1:
                    ch = col["chars"][y % len(col["chars"])]
                    if i == 0:
                        attr = curses.color_pair(2) | curses.A_BOLD
                    elif i < 3:
                        attr = curses.color_pair(1) | curses.A_BOLD
                    elif i < col["length"] // 2:
                        attr = curses.color_pair(1)
                    else:
                        attr = curses.color_pair(1) | curses.A_DIM
                    try:
                        stdscr.addch(y, col["x"], ch, attr)
                    except curses.error:
                        pass

        stdscr.refresh()
        time.sleep(frame_delay)

        key = stdscr.getch()
        if key == ord("q") or key == 27:
            return

    # Phase 2: freeze rain, reveal CLAUDE CODE art
    art_h = len(CLAUDE_ART)
    art_w = max(len(line) for line in CLAUDE_ART)
    start_row = max(0, (height - art_h - 3) // 2)
    start_col = max(0, (width - art_w) // 2)

    reveal_start = time.time()
    total_chars = sum(len(line) for line in CLAUDE_ART)
    chars_revealed = 0

    while True:
        now = time.time()
        elapsed = now - reveal_start
        if elapsed >= freeze:
            break

        progress = min(1.0, elapsed / (freeze * 0.7))
        chars_to_show = int(progress * total_chars)

        stdscr.erase()

        # keep rain static in background (dim)
        for col in columns:
            for i in range(col["length"]):
                y = col["y"] - i
                if 0 <= y < height - 1 and col["x"] < width - 1:
                    ch = col["chars"][y % len(col["chars"])]
                    try:
                        stdscr.addch(y, col["x"], ch, curses.color_pair(1) | curses.A_DIM)
                    except curses.error:
                        pass

        # draw art
        drawn = 0
        for r, line in enumerate(CLAUDE_ART):
            row = start_row + r
            if row >= height - 1:
                break
            for c, ch in enumerate(line):
                if drawn >= chars_to_show:
                    break
                col_pos = start_col + c
                if col_pos >= width - 1:
                    continue
                if ch != " ":
                    flicker = random.random() < (1.0 - progress) * 0.4
                    display_ch = random.choice(CHARS) if flicker else ch
                    attr = curses.color_pair(4) | curses.A_BOLD
                    try:
                        stdscr.addch(row, col_pos, display_ch, attr)
                    except curses.error:
                        pass
                drawn += 1

        # tagline
        tagline_row = start_row + art_h + 1
        if tagline_row < height - 1 and progress > 0.8:
            tag_col = max(0, (width - len(TAGLINE)) // 2)
            fade_progress = (progress - 0.8) / 0.2
            tag_attr = curses.color_pair(2) | curses.A_BOLD if fade_progress > 0.5 else curses.color_pair(1)
            try:
                stdscr.addstr(tagline_row, tag_col, TAGLINE, tag_attr)
            except curses.error:
                pass

        stdscr.refresh()
        time.sleep(0.03)

        key = stdscr.getch()
        if key == ord("q") or key == 27:
            return

    # brief full-bright hold
    time.sleep(0.3)


def main():
    duration = float(sys.argv[1]) if len(sys.argv) > 1 else 3.5
    freeze = float(sys.argv[2]) if len(sys.argv) > 2 else 1.8
    try:
        curses.wrapper(lambda s: run(s, duration, freeze))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
