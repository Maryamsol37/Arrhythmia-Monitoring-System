import wfdb
import numpy as np
from config import MITBIH_PATH, RECORD_NUMBERS

def load_mitbih_records(record_numbers):
    """Load MIT-BIH records and annotations"""
    records = []
    annotations = []
    
    for record in record_numbers:
        try:
            # Read record
            record_path = f'{MITBIH_PATH}/{record}'
            signal, _ = wfdb.rdsamp(record_path)
            annotation = wfdb.rdann(record_path, 'atr')
            
            records.append(signal)
            annotations.append(annotation)
        except Exception as e:
            print(f"Error loading record {record}: {e}")
    
    return records, annotations

def get_all_records():
    """Load all configured records"""
    return load_mitbih_records(RECORD_NUMBERS)