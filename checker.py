import cloudscraper
import random
import string
import time
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime

BANNER = r""" _______  __   __  _______  ______    __   __  __    _  __   __  _______    _______  ___   _______    ___      _______  _______  ___   _  _______  ______     _______  _______  __   __  ______    _______  _______  _______ 
|   _   ||  |_|  ||       ||    _ |  |  | |  ||  |  | ||  | |  ||       |  |   _   ||   | |       |  |   |    |       ||   _   ||   | | ||       ||      |   |       ||       ||  | |  ||    _ |  |       ||       ||       |
|  |_|  ||       ||    ___||   | ||  |  |_|  ||   |_| ||  |_|  ||_     _|  |  |_|  ||   | |   _   |  |   |    |    ___||  |_|  ||   |_| ||    ___||  _    |  |  _____||   _   ||  | |  ||   | ||  |       ||    ___||  _____|
|       ||       ||   |___ |   |_||_ |       ||       ||       |  |   |    |       ||   | |  | |  |  |   |    |   |___ |       ||      _||   |___ | | |   |  | |_____ |  | |  ||  |_|  ||   |_||_ |       ||   |___ | |_____ 
|       | |     | |    ___||    __  ||_     _||  _    ||_     _|  |   |    |       ||   | |  |_|  |  |   |___ |    ___||       ||     |_ |    ___|| |_|   |  |_____  ||  |_|  ||       ||    __  ||      _||    ___||_____  |
|   _   ||   _   ||   |___ |   |  | |  |   |  | | |   |  |   |    |   |    |   _   ||   | |       |  |       ||   |___ |   _   ||    _  ||   |___ |       |   _____| ||       ||       ||   |  | ||     |_ |   |___  _____| |
|__| |__||__| |__||_______||___|  |_|  |___|  |_|  |__|  |___|    |___|    |__| |__||___| |_______|  |_______||_______||__| |__||___| |_||_______||______|   |_______||_______||_______||___|  |_||_______||_______||_______|"""

R = "\033[0m"
G = "\033[92m"
RD = "\033[91m"
Y = "\033[93m"
C = "\033[96m"
M = "\033[95m"
B = "\033[1m"
D = "\033[2m"

LETTERS = string.ascii_lowercase
ALNUM = string.ascii_lowercase + string.digits

local = threading.local()
stats = {"checked": 0, "found": 0, "taken": 0, "errors": 0}


def get_scraper():
    if not hasattr(local, "s"):
        local.s = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
    return local.s


def check(username):
    s = get_scraper()
    url = f"https://www.tiktok.com/@{username}"
    try:
        r = s.head(url, allow_redirects=True, timeout=8)
        code = r.status_code
        if code == 404:
            return username, "available"
        if code == 200:
            return username, "taken"
        return username, "error"
    except Exception:
        return username, "error"


def gen(mode, length):
    pool = LETTERS if mode == "l" else ALNUM
    return "".join(random.choices(pool, k=length))


def banner():
    print(C + B + BANNER + R)
    print(M + B + " " * 60 + "LEAKED ON GITHUB" + R)
    print()


def ask(prompt, default=None):
    val = input(prompt).strip()
    if not val and default is not None:
        return default
    return val


def run():
    banner()

    print(C + B + "  ┌─────────────────────────────────────────────┐" + R)
    print(C + B + "  │              CONFIGURATION                  │" + R)
    print(C + B + "  └─────────────────────────────────────────────┘" + R)
    print(D + "    mode:  l = letters only    c = letters + digits" + R)
    print()

    spec = ask(D + "    length+mode (e.g. 7c, 6l, 8c): " + R, "7c")
    try:
        length = int(spec[:-1])
        mode = spec[-1].lower()
        if mode not in ("l", "c"):
            mode = "c"
        if length < 2 or length > 24:
            length = 7
    except Exception:
        length, mode = 7, "c"

    try:
        target = int(ask(D + "    how many available to find: " + R, "100"))
    except ValueError:
        target = 100

    try:
        workers = int(ask(D + "    workers (10-200): " + R, "50"))
    except ValueError:
        workers = 50
    workers = max(5, min(200, workers))

    save_taken = ask(D + "    also save taken list? (y/n): " + R, "n").lower() == "y"

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    avail_file = f"available_{length}{mode}_{ts}.txt"
    taken_file = f"taken_{length}{mode}_{ts}.txt"
    open(avail_file, "w").close()
    if save_taken:
        open(taken_file, "w").close()

    print()
    print(C + B + "  ┌─────────────────────────────────────────────┐" + R)
    print(C + B + "  │                 RUNNING                     │" + R)
    print(C + B + "  └─────────────────────────────────────────────┘" + R)
    print(f"    length:   {B}{length}{R}")
    print(f"    mode:     {B}{mode}{R}")
    print(f"    target:   {B}{target}{R} available")
    print(f"    workers:  {B}{workers}{R}")
    print(f"    output:   {B}{avail_file}{R}")
    if save_taken:
        print(f"    taken:    {B}{taken_file}{R}")
    print()

    start = time.time()
    seen = set()
    af = open(avail_file, "a")
    tf = open(taken_file, "a") if save_taken else None
    last_report = 0

    try:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = set()
            max_in_flight = workers * 4

            while stats["found"] < target:
                while len(futures) < max_in_flight:
                    u = gen(mode, length)
                    if u in seen:
                        continue
                    seen.add(u)
                    futures.add(ex.submit(check, u))

                done, futures = wait(futures, return_when=FIRST_COMPLETED)

                for f in done:
                    username, status = f.result()
                    stats["checked"] += 1

                    if status == "available":
                        stats["found"] += 1
                        print(G + B + f"    [+] {username}" + R + D + f"  ({stats['found']}/{target})" + R)
                        af.write(username + "\n")
                        af.flush()
                        if stats["found"] >= target:
                            break
                    elif status == "taken":
                        stats["taken"] += 1
                        if tf:
                            tf.write(username + "\n")
                            tf.flush()
                    else:
                        stats["errors"] += 1

                if stats["checked"] - last_report >= 100:
                    last_report = stats["checked"]
                    elapsed = time.time() - start
                    rate = stats["checked"] / elapsed if elapsed else 0
                    err_pct = stats["errors"] / stats["checked"] * 100
                    hit_pct = stats["found"] / stats["checked"] * 100
                    print(
                        Y + f"    [~] " + R
                        + D + f"checked={stats['checked']}  " + R
                        + G + f"found={stats['found']}  " + R
                        + RD + f"taken={stats['taken']}  " + R
                        + Y + f"err={stats['errors']} ({err_pct:.0f}%)  " + R
                        + D + f"hit={hit_pct:.1f}%  {rate:.0f}/s" + R
                    )
    except KeyboardInterrupt:
        print()
        print(Y + B + "    [!] interrupted by user" + R)
    finally:
        af.close()
        if tf:
            tf.close()

    elapsed = time.time() - start
    print()
    print(C + B + "  ┌─────────────────────────────────────────────┐" + R)
    print(C + B + "  │                  DONE                       │" + R)
    print(C + B + "  └─────────────────────────────────────────────┘" + R)
    print(f"    {G}available:{R} {B}{stats['found']}{R}")
    print(f"    {RD}taken:    {R} {B}{stats['taken']}{R}")
    print(f"    {Y}errors:   {R} {B}{stats['errors']}{R}")
    print(f"    {D}total:    {R} {B}{stats['checked']}{R}")
    print(f"    {D}time:     {R} {B}{elapsed:.1f}s{R}")
    if elapsed:
        print(f"    {D}rate:     {R} {B}{stats['checked'] / elapsed:.0f}/s{R}")
    print(f"    {C}saved to: {R} {B}{avail_file}{R}")
    if save_taken and stats["taken"]:
        print(f"    {C}taken to: {R} {B}{taken_file}{R}")
    print()


if __name__ == "__main__":
    run()
