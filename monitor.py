import json
import time
import os
import logging

MAX_TOKENS = 2_000_000
POLL_INTERVAL = 0.2  # seconds

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("monitor")

def monitor_budget(file_path='daily_budget.json'):
    """
    Monitors a JSON file for token budget usage and alerts when thresholds are crossed.
    
    Optimized to only read the file when it has been modified (via mtime) and precomputes
    alert thresholds to save CPU cycles.
    """
    if not isinstance(file_path, (str, os.PathLike)):
        raise TypeError(f"file_path must be a string or path-like object, got {type(file_path).__name__}")
    if not isinstance(MAX_TOKENS, (int, float)) or MAX_TOKENS <= 0:
        raise ValueError("MAX_TOKENS must be a strictly positive number")

    logger.info(f"Monitoring {file_path} for token budget usage (Max: {MAX_TOKENS})...")
    
    alerted_80 = False
    alerted_90 = False
    current_day = None
    last_mtime = 0
    
    # Precompute thresholds
    threshold_80 = MAX_TOKENS * 0.8
    threshold_90 = MAX_TOKENS * 0.9

    while True:
        try:
            if os.path.exists(file_path):
                current_mtime = os.path.getmtime(file_path)
                if current_mtime > last_mtime:
                    last_mtime = current_mtime
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    if not isinstance(data, dict):
                        logger.error(f"JSON data must be a dictionary, got {type(data).__name__}")
                        time.sleep(POLL_INTERVAL)
                        continue
                    
                    day = data.get('day')
                    if day is not None:
                        day = str(day)
                    
                    tokens = data.get('tokens', 0)
                    if not isinstance(tokens, (int, float)):
                        logger.error(f"tokens must be a number, got {type(tokens).__name__}")
                        time.sleep(POLL_INTERVAL)
                        continue

                    if tokens < 0:
                        logger.error(f"tokens cannot be negative, got {tokens}")
                        time.sleep(POLL_INTERVAL)
                        continue

                    # Reset alerts if the day changes
                    if day != current_day:
                        if current_day is not None:
                            logger.info(f"Day changed from {current_day} to {day}. Resetting alerts.")
                        current_day = day
                        alerted_80 = False
                        alerted_90 = False

                    if tokens >= threshold_90 and not alerted_90:
                        logger.critical(f"Token usage for {day} crossed 90%! ({tokens:,}/{MAX_TOKENS:,} tokens)")
                        alerted_90 = True
                        alerted_80 = True # Ensure 80% isn't triggered if we skipped it
                    elif tokens >= threshold_80 and not alerted_80:
                        logger.warning(f"Token usage for {day} crossed 80%! ({tokens:,}/{MAX_TOKENS:,} tokens)")
                        alerted_80 = True
                    
        except json.JSONDecodeError:
            # File might be in the middle of being written, ignore temporarily
            # Reset last_mtime so it tries again
            last_mtime = 0
        except OSError as e:
            logger.error(f"OS error accessing {file_path}: {e}")
            last_mtime = 0
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            last_mtime = 0

        time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    monitor_budget()
