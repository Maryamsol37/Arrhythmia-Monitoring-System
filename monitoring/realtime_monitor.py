import time
import numpy as np
import matplotlib.pyplot as plt
from config import WINDOW_SIZE, SAMPLE_RATE, DANGER_THRESHOLD, ALERT_COOLDOWN, MEDICATION_RELOAD_TIME
from .alert_system import AlertSystem

class RealTimeECGMonitor:
    def __init__(self, model, ecg_signal):
        self.model = model
        self.ecg_signal = ecg_signal
        self.alert_system = AlertSystem(
            threshold=DANGER_THRESHOLD,
            cooldown=ALERT_COOLDOWN,
            reload_time=MEDICATION_RELOAD_TIME
        )
    
    # def process_segment(self, segment):
    #     """Process ECG segment through model"""
    #     segment = segment[np.newaxis, ..., np.newaxis]
    #     return self.model.predict(segment, verbose=0)[0][0]
    
    def process_segment(self, segment):
        """Process ECG segment through model"""
        segment = segment[np.newaxis, ..., np.newaxis]
        danger_prob = self.model.predict(segment, verbose=0)[0][0]
        print(f"Danger probability: {danger_prob:.2f}")  # Add this line
        return danger_prob

    
    def simulate_realtime(self, speed=1.0):
        """Simulate real-time monitoring of ECG signal"""
        try:
            for i in range(0, len(self.ecg_signal) - WINDOW_SIZE, WINDOW_SIZE//2):
                segment = self.ecg_signal[i:i+WINDOW_SIZE, 0]
                
                # Update plot
                self.alert_system.update_plot(segment)
                
                # Process segment
                danger_prob = self.process_segment(segment)
                
                # Check for dangerous arrhythmia
                if danger_prob > DANGER_THRESHOLD:
                    self.alert_system.trigger_alert(danger_prob)
                else:
                    self.alert_system.reset_alert()
                
                # Simulate real-time delay
                time.sleep((WINDOW_SIZE/SAMPLE_RATE/2)/speed)
        
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        finally:
            plt.close('all')