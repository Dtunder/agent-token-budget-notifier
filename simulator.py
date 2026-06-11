import json
import time
from datetime import datetime

FILE_PATH = 'daily_budget.json'
MAX_TOKENS = 2_000_000
INCREMENT_AMOUNT = 150_000
UPDATE_INTERVAL = 0.5  # seconds

def run_simulator():
    """
    Simulates token budget usage by periodically writing incrementing token counts
    to a JSON file. Stops when token usage exceeds the maximum allowed tokens.
    """
    if not isinstance(FILE_PATH, str) or not FILE_PATH:
        raise ValueError("FILE_PATH must be a non-empty string")
    if not isinstance(MAX_TOKENS, (int, float)) or MAX_TOKENS <= 0:
        raise ValueError("MAX_TOKENS must be a strictly positive number")
    if not isinstance(INCREMENT_AMOUNT, (int, float)) or INCREMENT_AMOUNT <= 0:
        raise ValueError("INCREMENT_AMOUNT must be a strictly positive number")
    if not isinstance(UPDATE_INTERVAL, (int, float)) or UPDATE_INTERVAL <= 0:
        raise ValueError("UPDATE_INTERVAL must be a strictly positive number")

    print(f"Starting simulator. Updating {FILE_PATH} every {UPDATE_INTERVAL} seconds...")
    current_tokens = 0
    
    # Pre-calculate the maximum allowed token count to limit the while loop condition
    limit_tokens = MAX_TOKENS + INCREMENT_AMOUNT
    
    while current_tokens <= limit_tokens:
        today = datetime.now().strftime("%Y-%m-%d")
        
        data = {
            "day": today,
            "tokens": current_tokens
        }
        
        try:
            with open(FILE_PATH, 'w') as f:
                json.dump(data, f)
            print(f"Simulator wrote: {current_tokens:,} tokens")
        except OSError as e:
            print(f"OS error writing to {FILE_PATH}: {e}")
        except Exception as e:
            print(f"Error writing to {FILE_PATH}: {e}")

        current_tokens += INCREMENT_AMOUNT
        time.sleep(UPDATE_INTERVAL)
        
    print("Simulator finished.")

if __name__ == '__main__':
    run_simulator()
