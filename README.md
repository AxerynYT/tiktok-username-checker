==============================================================================
 _______  __   __  _______  ______    __   __  __    _  __   __  _______    _______  ___   _______    ___      _______  _______  ___   _  _______  ______     _______  _______  __   __  ______    _______  _______  _______ 
|   _   ||  |_|  ||       ||    _ |  |  | |  ||  |  | ||  | |  ||       |  |   _   ||   | |       |  |   |    |       ||   _   ||   | | ||       ||      |   |       ||       ||  | |  ||    _ |  |       ||       ||       |
|  |_|  ||       ||    ___||   | ||  |  |_|  ||   |_| ||  |_|  ||_     _|  |  |_|  ||   | |   _   |  |   |    |    ___||  |_|  ||   |_| ||    ___||  _    |  |  _____||   _   ||  | |  ||   | ||  |       ||    ___||  _____|
|       ||       ||   |___ |   |_||_ |       ||       ||       |  |   |    |       ||   | |  | |  |  |   |    |   |___ |       ||      _||   |___ | | |   |  | |_____ |  | |  ||  |_|  ||   |_||_ |       ||   |___ | |_____ 
|       | |     | |    ___||    __  ||_     _||  _    ||_     _|  |   |    |       ||   | |  |_|  |  |   |___ |    ___||       ||     |_ |    ___|| |_|   |  |_____  ||  |_|  ||       ||    __  ||      _||    ___||_____  |
|   _   ||   _   ||   |___ |   |  | |  |   |  | | |   |  |   |    |   |    |   _   ||   | |       |  |       ||   |___ |   _   ||    _  ||   |___ |       |   _____| ||       ||       ||   |  | ||     |_ |   |___  _____| |
|__| |__||__| |__||_______||___|  |_|  |___|  |_|  |__|  |___|    |___|    |__| |__||___| |_______|  |_______||_______||__| |__||___| |_||_______||______|   |_______||_______||_______||___|  |_||_______||_______||_______|

                              LEAKED ON GITHUB
==============================================================================

  TikTok Username Checker
  Fast async-style generator + checker for TikTok handles.

------------------------------------------------------------------------------
  WHAT IT DOES
------------------------------------------------------------------------------

  Generates random TikTok usernames at a given length and character set,
  checks each one against TikTok, and saves every available name to a
  timestamped .txt file. Optional separate file for taken names.

  Runs with a live CLI dashboard: hits, taken, errors, hit-rate, and
  requests per second.

------------------------------------------------------------------------------
  REQUIREMENTS
------------------------------------------------------------------------------

  Python 3.9+

  Install dependency:

      pip install cloudscraper

------------------------------------------------------------------------------
  USAGE
------------------------------------------------------------------------------

      python username.py

  You will be prompted for:

      length+mode      7c   = 7 chars (letters + digits)
                       7l   = 7 letters only
                       6c   = 6 chars
                       ...  any length 2-24

      target           how many available usernames to find before stopping

      workers          10-200  (higher = faster but more rate-limit risk)
                       recommended: 50 on a home IP, 10-20 behind proxies

      save taken?      y/n   (writes taken handles to a separate file)

------------------------------------------------------------------------------
  OUTPUT
------------------------------------------------------------------------------

  available_<length><mode>_<timestamp>.txt
      one available username per line, live-written as they are found

  taken_<length><mode>_<timestamp>.txt   (only if you chose to save taken)
      one taken username per line

  Example:

      available_7c_20260921_143012.txt
      taken_7c_20260921_143012.txt

------------------------------------------------------------------------------
  HOW IT WORKS
------------------------------------------------------------------------------

  1. Generate random usernames matching the requested length and charset.

  2. Send an HTTP HEAD request to https://www.tiktok.com/@<username>.

  3. Read the status code:

         404  ->  username is available
         200  ->  username is taken
         else ->  error (blocked, rate limited, timeout)

  4. Save hits immediately. Stop when target reached or Ctrl+C.

  Each worker thread has its own cloudscraper session to avoid lock
  contention and to spread cookie state.

------------------------------------------------------------------------------
  TUNING
------------------------------------------------------------------------------

  Faster:
      - raise workers (50 -> 100 -> 200)
      - run on a residential IP (home PC, old Android via Termux, VPS
        with residential IP)
      - lower latency to TikTok (US/EU residential is fastest)

  Fewer errors:
      - lower workers
      - use residential proxies (datacenter proxies are blocked)
      - don't run from Replit / AWS / GCP / Oracle / any cloud datacenter

  Better hit rate:
      - use longer usernames
          4-5 chars : ~99% taken
          6 chars   : ~90-95% taken
          7 chars   : ~30-60% taken  <- sweet spot
          8+ chars  : mostly available
      - use `c` mode (letters + digits) instead of `l` when short

------------------------------------------------------------------------------
  EXPECTED PERFORMANCE
------------------------------------------------------------------------------

  Home residential IP, 50 workers:

      error rate   : under 5%
      throughput   : 30-80 checks/sec
      hit rate 7c  : ~40%

  Replit / datacenter IP:

      error rate   : 95-100%   (TikTok blocks the IP at the edge)
      throughput   : irrelevant, everything errors

  If you see errors=100% the code is fine, the IP is the problem. Move to
  a residential network.

------------------------------------------------------------------------------
  TROUBLESHOOTING
------------------------------------------------------------------------------

  Everything returns "error":

      You are on a blocked IP (Replit, AWS, GCP, etc.). Move to a
      residential connection or use residential proxies.

  Lots of errors after a few thousand checks:

      You are being rate limited. Wait 10-30 minutes, restart your router
      to get a new IP, or add proxies.

  "ModuleNotFoundError: cloudscraper":

      pip install cloudscraper

  Slow:

      Increase workers. Check CPU usage - if it is pegged, drop workers.

==============================================================================
