from collections import deque
import keyboard
import threading
import time
import matplotlib.pyplot as plt
import numpy as np


class KeyLogger:
    def __init__(self, n):
        self.n = n  # Number of last keystrokes to keep
        self.keystrokes = deque(maxlen=n)  # Queue to store keystrokes
        self.running = False  # To control logging status

    def start_logging(self):
        """Start logging keystrokes."""
        self.running = True
        threading.Thread(target=self._log_keys, daemon=True).start()

    def _log_keys(self):
        """Log keystrokes in a non-blocking way."""
        try:
            while self.running:
                event = keyboard.read_event(suppress=False)
                if event.event_type == keyboard.KEY_DOWN:  # Only capture key press
                    self.keystrokes.append(event.name)
                time.sleep(0.01)  # Small delay to reduce CPU usage
        except KeyboardInterrupt:
            self.stop_logging()  # Graceful stop on Ctrl+C

    def stop_logging(self):
        """Stop logging keystrokes."""
        self.running = False

    def get_last_n_keys(self, num_keys=1):
        """Get and pop the last `num_keys` keystrokes."""
        num_keys = min(num_keys, len(self.keystrokes))  # Limit to available keys
        last_keys = [self.keystrokes.popleft() for _ in range(num_keys)]
        return last_keys
    

if __name__ == "__main__":
    # Initialize key logger
    key_logger = KeyLogger(10)
    key_logger.start_logging()

    # Setup a matplotlib plot that updates in real-time
    plt.ion()
    fig, ax = plt.subplots()
    x = np.linspace(0, 2 * np.pi, 100)
    line, = ax.plot(x, np.sin(x))

    try:
        for i in range(1000):  # Update the plot multiple times
            line.set_ydata(np.sin(x + i * 0.1))
            plt.draw()
            plt.pause(0.05)  # Pause briefly to update the plot

            # Retrieve and print last keystrokes (optional)
            print("Last keystrokes:", key_logger.get_last_n_keys(1))

    except KeyboardInterrupt:
        key_logger.stop_logging()
        print("\nStopped logging.")