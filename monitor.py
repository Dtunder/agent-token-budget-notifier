import json
import time
import os

MAX_TOKENS = 2_000_000
POLL_INTERVAL = 0.2  # seconds

# ANSI color codes
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def monitor_budget(file_path='daily_budget.json'):
    print(f"Monitoring {file_path} for token budget usage (Max: {MAX_TOKENS})...")

    alerted_80 = False
    alerted_90 = False
    current_day = None

    while True:
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)

                day = data.get('day')
                tokens = data.get('tokens', 0)

                # Reset alerts if the day changes
                if day != current_day:
                    current_day = day
                    alerted_80 = False
                    alerted_90 = False

                usage_percent = tokens / MAX_TOKENS

                if usage_percent >= 0.9 and not alerted_90:
                    print(f"{RED}CRITICAL ALERT: Token usage for {day} crossed 90%! ({tokens:,}/{MAX_TOKENS:,} tokens){RESET}")
                    alerted_90 = True
                    alerted_80 = True # Ensure 80% isn't triggered if we skipped it
                elif usage_percent >= 0.8 and not alerted_80:
                    print(f"{YELLOW}WARNING: Token usage for {day} crossed 80%! ({tokens:,}/{MAX_TOKENS:,} tokens){RESET}")
                    alerted_80 = True

        except json.JSONDecodeError:
            # File might be in the middle of being written, ignore temporarily
            pass
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    monitor_budget()
