import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from sklearn.model_selection import train_test_split
from config import TEST_SIZE, RANDOM_STATE, WINDOW_SIZE
from .architectures import create_cnn_model

class ModelTrainer:
    def __init__(self):
        self.model = None
        
    def train(self, X, y, epochs=30, batch_size=64):
        """Train the arrhythmia detection model"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
        )
        
        # Create model
        input_shape = (WINDOW_SIZE, 1)
        self.model = create_cnn_model(input_shape)
        
        # Compile model
        self.model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC()]
        )
        
        # Callbacks
        callbacks = [
            ModelCheckpoint('best_model.h5', save_best_only=True, monitor='val_auc', mode='max'),
            EarlyStopping(patience=5, monitor='val_auc', mode='max')
        ]
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks
        )
        
        return history
    
    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        if self.model is None:
            raise ValueError("Model has not been trained yet")
        return self.model.evaluate(X_test, y_test)
    
    def save_model(self, path):
        """Save trained model"""
        if self.model is None:
            raise ValueError("Model has not been trained yet")
        self.model.save(path)
    
    def load_model(self, path):
        """Load pretrained model"""
        self.model = tf.keras.models.load_model(path)
        return self.model