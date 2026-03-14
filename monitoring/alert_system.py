import time
import threading
import numpy as np
from pushbullet import Pushbullet
import sounddevice as sd
import matplotlib.pyplot as plt
import config
from config import PUSHBULLET_API_KEY

class AlertSystem:
    def __init__(self, threshold, cooldown, reload_time):
        self.threshold = threshold
        self.cooldown = cooldown
        self.reload_time = reload_time
        
        self.alert_status = False
        self.last_alert_time = 0
        self.medication_ready = True
        self.medication_dose = 0
        
        # Setup visualization
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.line, = self.ax.plot([], [])
        self.ax.set_ylim(-2, 2)
        self.ax.set_title('Real-time ECG Monitoring')
        self.fig.canvas.draw()

        # Setup Pushbullet
        self.pb = Pushbullet(config.PUSHBULLET_API_KEY)

    def send_push_notification(self, message):
        try:
            self.pb.push_note("Arrhythmia Alert", message)
        except Exception as e:
            print(f"Push failed: {str(e)}")

    def trigger_alert(self, danger_prob):
        """Trigger visual and audible alerts"""
        current_time = time.time()
        
        if current_time - self.last_alert_time < self.cooldown:
            return

         # Log the alert
        with open('alerts.log', 'a') as f:
            f.write(f"{time.ctime()}: Arrhythmia detected (prob={danger_prob:.2f})\n")  

        # Visual alert
        self.ax.set_facecolor('red')
        self.fig.canvas.draw()
        
        # Audible alert (880Hz tone for 1 second)
        sd.play(0.5 * np.sin(2 * np.pi * 880 * np.arange(44100)/44100), samplerate=44100)
        
        print("\nALERT: Dangerous arrhythmia detected!")
        
        # Administer medication if ready
        if self.medication_ready:
            print("Administering medication via IV...")
            self.medication_dose += 1
            self.medication_ready = False
            threading.Timer(self.reload_time, self._reload_medication).start()
        
        self.alert_status = True
        self.last_alert_time = current_time
    
    def _reload_medication(self):
        """Reload medication after cooldown"""
        self.medication_ready = True
        print("Medication reloaded and ready for next dose")
    
    def reset_alert(self):
        """Reset alert status"""
        if self.alert_status:
            self.alert_status = False
            self.ax.set_facecolor('white')
            self.fig.canvas.draw()
    
    def update_plot(self, segment):
        """Update the ECG plot"""
        self.line.set_data(np.arange(len(segment)), segment)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()