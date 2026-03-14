import wfdb
from monitoring.realtime_monitor import RealTimeECGMonitor
from model.trainer import ModelTrainer
from config import MITBIH_PATH, RECORD_NUMBERS

def run_simulation(record_number, speed=1.0):
    # Load pre-trained model
    trainer = ModelTrainer()
    model = trainer.load_model('best_model.h5')  # Or 'arrhythmia_model.h5'
    
    # Load the chosen record
    record = wfdb.rdsamp(f'{MITBIH_PATH}/{record_number}')[0]
    
    # Start monitoring
    monitor = RealTimeECGMonitor(model, record)
    monitor.simulate_realtime(speed=speed)

if __name__ == "__main__":
    print("Available records:", RECORD_NUMBERS)
    record_num = input("Enter record number to simulate (e.g. 101): ")
    speed = float(input("Enter simulation speed (1.0 = realtime): ") or "1.0")
    run_simulation(record_num, speed)