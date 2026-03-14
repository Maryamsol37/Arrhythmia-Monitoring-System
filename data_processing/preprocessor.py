import numpy as np
from config import WINDOW_SIZE, DANGEROUS_SYMBOLS

def create_dataset(records, annotations):
    """Create labeled dataset from records and annotations"""
    X = []
    y = []
    
    for signal, ann in zip(records, annotations):
        # Get annotation samples and symbols
        ann_samples = ann.sample
        ann_symbols = ann.symbol
        
        # Create segments around each annotation
        for sample, symbol in zip(ann_samples, ann_symbols):
            # Skip if annotation is at the very start or end
            if sample < WINDOW_SIZE//2 or sample + WINDOW_SIZE//2 > len(signal):
                continue
                
            # Extract segment (using lead 0)
            segment = signal[sample - WINDOW_SIZE//2 : sample + WINDOW_SIZE//2, 0]
            
            # Label segment
            label = 1 if symbol in DANGEROUS_SYMBOLS else 0
                
            X.append(segment)
            y.append(label)
    
    return np.array(X), np.array(y)

def preprocess_data(X, y):
    """Normalize and reshape data for model input"""
    # Normalize each segment
    X = (X - np.mean(X, axis=1, keepdims=True)) / (np.std(X, axis=1, keepdims=True) + 1e-8)
    
    # Add channel dimension
    X = X[..., np.newaxis]
    
    return X, y