# agent-token-budget-notifier

Monitoring script that parses `daily_budget.json` and issues warnings in standard out.

## Files

- `monitor.py`: The monitor script that polls `daily_budget.json` every few milliseconds/seconds. It tracks token usage and outputs colored warnings to stdout if usage exceeds 80% or 90% of the maximum allowed.
- `simulator.py`: A simulator script that increments the token budget over time to demonstrate the monitor's alerts. It writes to `daily_budget.json`.

## Configuration Setup

Both scripts can be configured by modifying the constants at the top of their respective files:

### `monitor.py`
- `MAX_TOKENS`: The maximum daily token budget (Default: `2_000_000`).
- `POLL_INTERVAL`: How frequently the script checks for updates to the JSON file in seconds (Default: `0.2`).

### `simulator.py`
- `FILE_PATH`: The output path for the simulated budget file (Default: `'daily_budget.json'`).
- `MAX_TOKENS`: The maximum daily token budget limit (Default: `2_000_000`).
- `INCREMENT_AMOUNT`: The number of tokens added per simulation step (Default: `150_000`).
- `UPDATE_INTERVAL`: Delay between simulation steps in seconds (Default: `0.5`).

## CLI Instructions

1. Start the monitor in a terminal:
   ```bash
   python3 monitor.py
   ```
   The monitor will continuously observe the token usage file for changes.

2. Open another terminal and start the simulator:
   ```bash
   python3 simulator.py
   ```
   The simulator will incrementally write to `daily_budget.json`.

The monitor will print out colored warnings when token usage crosses 80% and 90% thresholds.

## API Reference Documentation

### `monitor.py`

#### `monitor_budget(file_path='daily_budget.json')`
Monitors a JSON file for token budget usage and alerts when thresholds are crossed.
Optimized to only read the file when it has been modified (via mtime) and precomputes alert thresholds to save CPU cycles.

**Args:**
* `file_path` (str, optional): The path to the JSON file containing the daily token usage. Defaults to `'daily_budget.json'`.

**Raises:**
* `TypeError`: If `file_path` is not a string or path-like object.
* `ValueError`: If `MAX_TOKENS` is not a strictly positive number.

### `simulator.py`

#### `run_simulator()`
Simulates token budget usage by periodically writing incrementing token counts to a JSON file. Stops when token usage exceeds the maximum allowed tokens.

**Raises:**
* `ValueError`: If any of the constants (`FILE_PATH`, `MAX_TOKENS`, `INCREMENT_AMOUNT`, `UPDATE_INTERVAL`) are invalid (e.g., negative intervals, empty file paths, etc.).
