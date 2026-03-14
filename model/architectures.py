from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (Conv1D, MaxPooling1D, Flatten, 
                                   Dense, Dropout, BatchNormalization)


def create_cnn_model(input_shape):
    """Create 1D CNN model for arrhythmia detection"""
    model = Sequential([
        Conv1D(64, 15, activation='relu', input_shape=input_shape, padding='same'),
        BatchNormalization(),
        MaxPooling1D(2),
        
        Conv1D(128, 10, activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling1D(2),
        
        Conv1D(256, 5, activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling1D(2),
        
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])
    
    return model