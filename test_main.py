import os
import json
import unittest
from unittest.mock import patch, mock_open
import sys
import io

import monitor
import simulator

class StopLoopException(Exception):
    """Exception used to gracefully exit the infinite while loops in tests."""
    pass

class TestMonitor(unittest.TestCase):
    """
    Test suite for the `monitor_budget` function in `monitor.py`.
    
    These tests use mocking extensively to simulate file reads, writes,
    time delays, and exceptions to ensure full coverage of the monitor logic.
    """
    @patch('monitor.time.sleep', side_effect=StopLoopException)
    @patch('monitor.os.path.exists', return_value=False)
    def test_file_not_exists(self, mock_exists, mock_sleep):
        """Test behavior when the daily budget JSON file does not exist."""
        with self.assertRaises(StopLoopException):
            monitor.monitor_budget('dummy_path.json')
            
    @patch('monitor.time.sleep', side_effect=StopLoopException)
    @patch('monitor.os.path.exists', return_value=True)
    @patch('monitor.os.path.getmtime', return_value=1)
    @patch('builtins.open', new_callable=mock_open, read_data='{"day": "2023-01-01", "tokens": 1000000}')
    def test_no_alert_below_80(self, mock_open_file, mock_mtime, mock_exists, mock_sleep):
        """Test that no alerts are triggered if token usage is below 80%."""
        with self.assertLogs('monitor', level='INFO') as log:
            with self.assertRaises(StopLoopException):
                monitor.monitor_budget('dummy_path.json')
        log_output = "\n".join(log.output)
        self.assertNotIn("WARNING", log_output)
        self.assertNotIn("CRITICAL", log_output)

    @patch('monitor.time.sleep', side_effect=StopLoopException)
    @patch('monitor.os.path.exists', return_value=True)
    @patch('monitor.os.path.getmtime', return_value=1)
    @patch('builtins.open', new_callable=mock_open, read_data='{"day": "2023-01-01", "tokens": 1700000}')
    def test_alert_80_percent(self, mock_open_file, mock_mtime, mock_exists, mock_sleep):
        """Test that a WARNING alert is triggered if token usage is >= 80%."""
        with self.assertLogs('monitor', level='INFO') as log:
            with self.assertRaises(StopLoopException):
                monitor.monitor_budget('dummy_path.json')
        log_output = "\n".join(log.output)
        self.assertIn("Token usage for 2023-01-01 crossed 80%", log_output)
        self.assertIn("WARNING:", log_output)

    @patch('monitor.time.sleep', side_effect=StopLoopException)
    @patch('monitor.os.path.exists', return_value=True)
    @patch('monitor.os.path.getmtime', return_value=1)
    @patch('builtins.open', new_callable=mock_open, read_data='{"day": "2023-01-01", "tokens": 1900000}')
    def test_alert_90_percent(self, mock_open_file, mock_mtime, mock_exists, mock_sleep):
        """Test that a CRITICAL alert is triggered if token usage is >= 90%."""
        with self.assertLogs('monitor', level='INFO') as log:
            with self.assertRaises(StopLoopException):
                monitor.monitor_budget('dummy_path.json')
        log_output = "\n".join(log.output)
        self.assertIn("Token usage for 2023-01-01 crossed 90%", log_output)
        self.assertIn("CRITICAL:", log_output)

    @patch('monitor.time.sleep', side_effect=StopLoopException)
    @patch('monitor.os.path.exists', return_value=True)
    @patch('monitor.os.path.getmtime', return_value=1)
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    def test_json_decode_error(self, mock_open_file, mock_mtime, mock_exists, mock_sleep):
        """Test handling of invalid JSON decoding."""
        # Should catch JSONDecodeError and pass, hitting the sleep and raising StopLoopException
        with self.assertRaises(StopLoopException):
            monitor.monitor_budget('dummy_path.json')

    @patch('monitor.time.sleep', side_effect=StopLoopException)
    @patch('monitor.os.path.exists', return_value=True)
    @patch('monitor.os.path.getmtime', return_value=1)
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_other_exception(self, mock_open_file, mock_mtime, mock_exists, mock_sleep):
        """Test that other exceptions (like PermissionError) are gracefully caught and logged."""
        with self.assertLogs('monitor', level='ERROR') as log:
            # Should catch Exception, print error, hit sleep, raise StopLoopException
            with self.assertRaises(StopLoopException):
                monitor.monitor_budget('dummy_path.json')
        log_output = "\n".join(log.output)
        self.assertIn("OS error accessing dummy_path.json", log_output)

    def test_invalid_file_path_type(self):
        """Test validation of invalid file path type."""
        with self.assertRaises(TypeError):
            monitor.monitor_budget(123)

    @patch('monitor.MAX_TOKENS', -1)
    def test_invalid_max_tokens(self):
        """Test validation of invalid maximum tokens configuration."""
        with self.assertRaises(ValueError):
            monitor.monitor_budget('dummy.json')

    @patch('monitor.time.sleep', side_effect=StopLoopException)
    @patch('monitor.os.path.exists', return_value=True)
    @patch('monitor.os.path.getmtime', return_value=1)
    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_data_not_dict(self, mock_open_file, mock_mtime, mock_exists, mock_sleep):
        """Test handling of JSON files that do not contain a dictionary."""
        with self.assertLogs('monitor', level='ERROR') as log:
            with self.assertRaises(StopLoopException):
                monitor.monitor_budget('dummy_path.json')
        log_output = "\n".join(log.output)
        self.assertIn("JSON data must be a dictionary", log_output)

    @patch('monitor.time.sleep', side_effect=StopLoopException)
    @patch('monitor.os.path.exists', return_value=True)
    @patch('monitor.os.path.getmtime', return_value=1)
    @patch('builtins.open', new_callable=mock_open, read_data='{"day": "2023-01-01", "tokens": "abc"}')
    def test_tokens_not_number(self, mock_open_file, mock_mtime, mock_exists, mock_sleep):
        """Test that string values for tokens are rejected and logged."""
        with self.assertLogs('monitor', level='ERROR') as log:
            with self.assertRaises(StopLoopException):
                monitor.monitor_budget('dummy_path.json')
        log_output = "\n".join(log.output)
        self.assertIn("tokens must be a number", log_output)

    @patch('monitor.time.sleep', side_effect=StopLoopException)
    @patch('monitor.os.path.exists', return_value=True)
    @patch('monitor.os.path.getmtime', return_value=1)
    @patch('builtins.open', new_callable=mock_open, read_data='{"day": "2023-01-01", "tokens": -500}')
    def test_tokens_negative(self, mock_open_file, mock_mtime, mock_exists, mock_sleep):
        """Test that negative token values are rejected and logged."""
        with self.assertLogs('monitor', level='ERROR') as log:
            with self.assertRaises(StopLoopException):
                monitor.monitor_budget('dummy_path.json')
        log_output = "\n".join(log.output)
        self.assertIn("tokens cannot be negative", log_output)

    def test_reset_on_new_day(self):
        """Test that alert flags are reset when the date changes."""
        # Provide multiple files with patch to mock the states over time
        # The loop reads: 
        #   1. Day 1: 1.7m (80%) -> hits sleep -> next iter
        #   2. Day 2: 0 (0%) -> hits sleep -> next iter
        #   3. Day 2: 1.9m (90%) -> hits sleep -> StopLoop
        
        call_count = 0
        def side_effect_sleep(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                raise StopLoopException()
                
        read_datas = [
            '{"day": "2023-01-01", "tokens": 1700000}',
            '{"day": "2023-01-02", "tokens": 0}',
            '{"day": "2023-01-02", "tokens": 1900000}'
        ]
        
        # We need a custom open mock to return different data sequentially
        def mock_open_func(*args, **kwargs):
            m = mock_open(read_data=read_datas[call_count])
            return m(*args, **kwargs)

        with patch('monitor.time.sleep', side_effect=side_effect_sleep), \
             patch('monitor.os.path.exists', return_value=True), \
             patch('monitor.os.path.getmtime', side_effect=[1, 2, 3]), \
             patch('builtins.open', side_effect=mock_open_func):
            with self.assertLogs('monitor', level='INFO') as log:
                with self.assertRaises(StopLoopException):
                    monitor.monitor_budget('dummy_path.json')
                
        log_output = "\n".join(log.output)
        self.assertIn("Token usage for 2023-01-01 crossed 80%", log_output)
        self.assertIn("WARNING:", log_output)
        self.assertIn("Token usage for 2023-01-02 crossed 90%", log_output)
        self.assertIn("CRITICAL:", log_output)

class TestSimulator(unittest.TestCase):
    """
    Test suite for the `run_simulator` function in `simulator.py`.
    """
    @patch('simulator.FILE_PATH', '')
    def test_invalid_file_path(self):
        """Test validation of an empty file path."""
        with self.assertRaises(ValueError):
            simulator.run_simulator()
            
    @patch('simulator.MAX_TOKENS', -1)
    def test_invalid_max_tokens(self):
        """Test validation of invalid max tokens configuration."""
        with self.assertRaises(ValueError):
            simulator.run_simulator()
            
    @patch('simulator.INCREMENT_AMOUNT', 0)
    def test_invalid_increment_amount(self):
        """Test validation of invalid token increment configuration."""
        with self.assertRaises(ValueError):
            simulator.run_simulator()

    @patch('simulator.UPDATE_INTERVAL', -1)
    def test_invalid_update_interval(self):
        """Test validation of invalid simulator update interval."""
        with self.assertRaises(ValueError):
            simulator.run_simulator()

    @patch('simulator.time.sleep', side_effect=StopLoopException)
    @patch('simulator.FILE_PATH', 'dummy_sim_path.json')
    @patch('builtins.open', side_effect=OSError("Disk full"))
    def test_simulator_os_error_writing(self, mock_open_file, mock_sleep):
        """Test that OSErrors during file writes are caught and logged."""
        with self.assertLogs('simulator', level='ERROR') as log:
            with self.assertRaises(StopLoopException):
                simulator.run_simulator()
        log_output = "\n".join(log.output)
        self.assertIn("OS error writing to dummy_sim_path.json", log_output)

    @patch('simulator.time.sleep', side_effect=StopLoopException)
    @patch('simulator.FILE_PATH', 'dummy_sim_path.json')
    @patch('builtins.open', side_effect=Exception("Unknown Error"))
    def test_simulator_unknown_error_writing(self, mock_open_file, mock_sleep):
        """Test that unexpected exceptions during file writes are caught and logged."""
        with self.assertLogs('simulator', level='ERROR') as log:
            with self.assertRaises(StopLoopException):
                simulator.run_simulator()
        log_output = "\n".join(log.output)
        self.assertIn("Error writing to dummy_sim_path.json", log_output)

    @patch('simulator.time.sleep')
    @patch('simulator.FILE_PATH', 'dummy_sim_path.json')
    def test_run_simulator(self, mock_sleep):
        """Test the normal execution loop of the token budget simulator."""
        # We need to test the file writing.
        # Use a temporary file to avoid polluting the workspace
        # but mock time.sleep so we don't wait for UPDATE_INTERVAL seconds.
        # Run it with patch on time.sleep doing nothing.
        
        # Track written data
        written_data = []
        original_open = open
        def mock_open_func(*args, **kwargs):
            if args[0] == 'dummy_sim_path.json':
                # Create a mock open that intercepts writes
                m = mock_open()
                # To intercept what's written, mock the write method of the file object
                file_mock = m()
                def write_side_effect(content):
                    if content and content.strip():
                        written_data.append(content)
                file_mock.write.side_effect = write_side_effect
                return m(*args, **kwargs)
            return original_open(*args, **kwargs)
            
        with patch('builtins.open', side_effect=mock_open_func):
            # Also patch sys.stdout to avoid printing out
            with patch('sys.stdout', new_callable=io.StringIO):
                simulator.run_simulator()
                
        # Calculate how many iterations we expect
        # It loops while current_tokens <= MAX_TOKENS + INCREMENT_AMOUNT
        # MAX_TOKENS = 2_000_000, INCREMENT_AMOUNT = 150_000
        # 0, 150_000, ..., 2_100_000 -> 2100000/150000 = 14 iterations + 1 = 15 iterations.
        expected_iterations = (simulator.MAX_TOKENS + simulator.INCREMENT_AMOUNT) // simulator.INCREMENT_AMOUNT + 1
        
        self.assertEqual(mock_sleep.call_count, expected_iterations)
        
        # Check written data content (it should contain incrementing token counts)
        self.assertTrue(len(written_data) > 0)
        # Parse the last valid json written (since json.dump might call write multiple times, we just verify the calls were made)
        # Alternatively, we could test that current_tokens reaches the expected value by parsing the json.

        # Let's instead run it and read the real temp file to simplify mocking of json.dump.
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            with patch('simulator.FILE_PATH', tmp_path):
                with patch('sys.stdout', new_callable=io.StringIO):
                    simulator.run_simulator()
            
            # Now read the tmp file
            with open(tmp_path, 'r') as f:
                data = json.load(f)
            
            # The last token count written should be 2100000 (which is > 2000000, so loop stops)
            # Actually, loop condition is current_tokens <= MAX_TOKENS + INCREMENT_AMOUNT
            # 2,100,000 <= 2,150,000 is True. Wait, 2_000_000 + 150_000 = 2_150_000.
            # 14 * 150,000 = 2,100,000. 15 * 150,000 = 2,250,000.
            # Let's just verify 'tokens' is in the written data and it's > MAX_TOKENS
            self.assertIn('tokens', data)
            self.assertTrue(data['tokens'] > simulator.MAX_TOKENS)
            self.assertIn('day', data)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == '__main__':
    unittest.main()
