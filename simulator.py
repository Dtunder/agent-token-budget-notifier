import json
import time
from datetime import datetime

FILE_PATH = 'daily_budget.json'
MAX_TOKENS = 2_000_000
INCREMENT_AMOUNT = 150_000
UPDATE_INTERVAL = 0.5  # seconds

def run_simulator():
    print(f"Starting simulator. Updating {FILE_PATH} every {UPDATE_INTERVAL} seconds...")
    current_tokens = 0
    
    while current_tokens <= MAX_TOKENS + INCREMENT_AMOUNT:
        today = datetime.now().strftime("%Y-%m-%d")
        
        data = {
            "day": today,
            "tokens": current_tokens
        }
        
        with open(FILE_PATH, 'w') as f:
            json.dump(data, f)
            
        print(f"Simulator wrote: {current_tokens:,} tokens")
        current_tokens += INCREMENT_AMOUNT
        time.sleep(UPDATE_INTERVAL)
        
    print("Simulator finished.")

if __name__ == '__main__':
    run_simulator()
