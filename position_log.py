import os
import csv
import datetime

LOG_DIR = 'motor_position_log'
LOG_PATH = os.path.join(LOG_DIR, 'position_log.csv')


def log_position(position, path=LOG_PATH):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    is_new = not os.path.exists(path)
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(['timestamp', 'axis1', 'axis2', 'axis3'])
        writer.writerow([datetime.datetime.now().isoformat(), *position])
        f.flush()
        os.fsync(f.fileno())
