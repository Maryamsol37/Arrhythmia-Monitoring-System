import wfdb
import numpy as np
from data_processing.data_loader import get_all_records
from data_processing.preprocessor import create_dataset, preprocess_data
from model.trainer import ModelTrainer
from monitoring.realtime_monitor import RealTimeECGMonitor
from config import WINDOW_SIZE, RECORD_NUMBERS, MITBIH_PATH

def main():
    # Step 1: Load and prepare data
    print("Loading MIT-BIH records...")
    records, annotations = get_all_records()
    
    print("Creating dataset...")
    X, y = create_dataset(records, annotations)
    X, y = preprocess_data(X, y)
    
    # Step 2: Train model
    print("Training model...")
    trainer = ModelTrainer()
    history = trainer.train(X, y)
    
    # Step 3: Simulate real-time monitoring
    print("\nStarting real-time simulation...")
    record_num = RECORD_NUMBERS[0]  # Use first record for simulation
    record = wfdb.rdsamp(f'{MITBIH_PATH}/{record_num}')[0]
    
    monitor = RealTimeECGMonitor(trainer.model, record)
    monitor.simulate_realtime(speed=5.0)  # Speed up simulation 5x

if __name__ == "__main__":
    main()