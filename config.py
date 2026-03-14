# MIT-BIH Database Configuration
MITBIH_PATH = 'MIT_records'  # Path to MIT-BIH dataset
RECORD_NUMBERS = ['100', '101', '103', '104', '105', '106', '107', '108', '109', '111', '112', '113', '114', '115', '116', '117', '118', '119', '121', '122', '123', '124', '200', '201', '202', '203', '205', '207', '208', '209', '210', '212', '213', '214', '215', '217', '219', '220', '221', '222', '223', '228', '230', '231', '232', '233', '234']  # Records to use
DANGEROUS_SYMBOLS = ['V', 'r', 'E', 'S', 'A', 'a', 'J']  # Dangerous beat annotations
#NORMAL_SYMBOL = 'N'  # Normal beat annotation

# Model Configuration
WINDOW_SIZE = 180  # 0.5 second window at 360Hz
SAMPLE_RATE = 360  # Hz
TEST_SIZE = 0.2  # Percentage of data for testing
RANDOM_STATE = 42  # For reproducibility

# Alert System Configuration
DANGER_THRESHOLD = 0.8  # Confidence threshold for dangerous arrhythmia
ALERT_COOLDOWN = 10  # Seconds between alerts
MEDICATION_RELOAD_TIME = 30  # Seconds to reload medication

# Pushbullet Configuration
PUSHBULLET_API_KEY = 'o.ZCEHv4L7dViboMnztLfCgfuuYy1Uzncu'  # Your Pushbullet API key
