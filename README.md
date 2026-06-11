# agent-token-budget-notifier

Monitoring script that parses `daily_budget.json` and issues warnings in standard out.

## Files

- `monitor.py`: The monitor script that polls `daily_budget.json` every few milliseconds/seconds. It tracks token usage and outputs colored warnings to stdout if usage exceeds 80% or 90% of the maximum allowed.
- `simulator.py`: A simulator script that increments the token budget over time to demonstrate the monitor's alerts. It writes to `daily_budget.json`.

## Usage

1. Start the monitor in a terminal:
   ```bash
   python3 monitor.py
   ```

2. Open another terminal and start the simulator:
   ```bash
   python3 simulator.py
   ```

The monitor will print out colored warnings when token usage crosses 80% and 90% thresholds.
