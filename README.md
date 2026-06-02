# Arrhythmia Detection System

Detects dangerous cardiac arrhythmias from ECG signals using a CNN model trained on MIT-BIH records. Includes a real-time monitor, a CLI simulator, and a PyQt5 GUI with alerting and optional Arduino integration.

## Features
- CNN-based binary classification of dangerous arrhythmias
- Real-time simulation using MIT-BIH ECG recordings
- GUI dashboard with waveform plot, probability readout, and alerts
- Optional Pushbullet notifications and Arduino-triggered medication delivery

## Project Structure
- main.py: end-to-end training and real-time simulation
- simulate.py: run a real-time simulation with a pretrained model
- simulate_gui.py: GUI simulator with alerts and Arduino support
- config.py: dataset paths, model params, and alert thresholds
- data_processing/: data loading and preprocessing
- model/: model architecture and training logic
- monitoring/: real-time monitor and alert system
- MIT_records/: MIT-BIH ECG records used for training and simulation
- best_model.h5: pretrained model weights (used by simulators)

## Setup
1. Install Python 3.8+ (TensorFlow 2.8+ compatible).
2. Install dependencies:

```
pip install -r requirements.txt
```

## Quick Start
Train and then simulate with the freshly trained model:

```
python main.py
```

Run a real-time simulation with the pretrained model:

```
python simulate.py
```

Launch the GUI simulator:

```
python simulate_gui.py
```

## Configuration
Edit config.py to customize:
- MITBIH_PATH: path to the MIT-BIH records
- RECORD_NUMBERS: list of records used for training/simulation
- WINDOW_SIZE, SAMPLE_RATE: model and sampling parameters
- DANGER_THRESHOLD: probability cutoff for alerting
- ALERT_COOLDOWN, MEDICATION_RELOAD_TIME: alert pacing
- PUSHBULLET_API_KEY: Pushbullet access token (optional)

GUI-specific settings in simulate_gui.py:
- Arduino serial port (default COM5)
- Alert tone frequency and duration

## Notes
- MIT_records is expected to contain the MIT-BIH record files. If you replace or extend the dataset, update MITBIH_PATH and RECORD_NUMBERS accordingly.
- best_model.h5 is used by simulate.py and simulate_gui.py. If you retrain, replace this file or update the path in code.
- Pushbullet is optional; if the API key is missing or invalid, GUI alerts still work locally.

## Troubleshooting
- If wfdb cannot find records, verify MITBIH_PATH and that files like 100.hea/100.atr exist.
- If the GUI fails to open, ensure PyQt5 and pyqtgraph installed and that your environment has display support.
- If Arduino is connected but not detected, update the COM port and verify drivers.
