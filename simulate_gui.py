import sys
import serial
import serial.tools.list_ports
import time
from pushbullet import Pushbullet
import tensorflow as tf
import numpy as np
import sounddevice as sd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QLabel, QPushButton, QComboBox, QDoubleSpinBox,
                            QHBoxLayout, QMessageBox)
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg
import wfdb
from model.trainer import ModelTrainer
import config
from config import MITBIH_PATH, RECORD_NUMBERS, DANGER_THRESHOLD

class ECGMonitorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arrhythmia Detection System")
        self.setGeometry(100, 100, 1000, 600)
        
        # Load trained model once
        ####self.trainer = ModelTrainer()
        ####self.model = self.trainer.load_model('best_model.h5')
        self.current_record = None
        self.simulation_speed = 1.0
        self.is_running = False
        self.current_index = 0
        self.window_size = 180  # 0.5 second window at 360Hz
        
        # Setup UI
        self.init_ui()

        # Medication system variables
        self.medication_ready = True
        self.last_medication_time = 0
        self.medication_cooldown = 30000  # 30 seconds in ms

        # Arduino connection
        self.arduino = self.connect_to_arduino()
        
        # Initialize sound device
        self.sample_rate = 44100
        self.alert_duration = 1.0  # seconds
        self.alert_frequency = 880  # Hz (A5 note)

        try:
            self.pb = Pushbullet(config.PUSHBULLET_API_KEY)
        except Exception as e:
            print(f"Pushbullet init failed: {str(e)}")
            self.pb = None
    
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Control Panel
        control_layout = QHBoxLayout()
        
        self.record_combo = QComboBox()
        self.record_combo.addItems(RECORD_NUMBERS)
        control_layout.addWidget(QLabel("Select Record:"))
        control_layout.addWidget(self.record_combo)
        
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.1, 10.0)
        self.speed_spin.setValue(1.0)
        self.speed_spin.setSingleStep(0.1)
        control_layout.addWidget(QLabel("Speed:"))
        control_layout.addWidget(self.speed_spin)
        
        self.start_btn = QPushButton("Start Simulation")
        self.start_btn.clicked.connect(self.toggle_simulation)
        control_layout.addWidget(self.start_btn)
        
        layout.addLayout(control_layout)
        
        # ECG Plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setYRange(-2, 2)
        self.plot_widget.setLabel('left', 'Amplitude (mV)')
        self.plot_widget.setLabel('bottom', 'Samples')
        self.ecg_curve = self.plot_widget.plot(pen='b')
        layout.addWidget(self.plot_widget)
        
        # Alert Panel
        self.alert_label = QLabel("Status: Ready")
        self.alert_label.setStyleSheet("font-size: 16px;")
        self.alert_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.alert_label)
        
        # Danger Probability
        self.prob_label = QLabel("Danger Probability: 0.00")
        self.prob_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.prob_label)
        
        central_widget.setLayout(layout)
        
        # Setup timer for simulation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)

    def connect_to_arduino(self):
        # try:
        print("Initializing Arduino connection...")
        self.arduino = serial.Serial('COM5', 9600, timeout=1)
        time.sleep(2)  # Critical wait period
        
        # Clear any buffered data
        self.arduino.reset_input_buffer()
        
        # Verification handshake
        self.arduino.write(b'P\n')
        response = self.arduino.readline().decode().strip()
        print(response)
        
        if "PONG" in response:
            print("Arduino communication verified")
            return self.arduino
            
        self.arduino.close()
        # except Exception as e:
            # print(f"Arduino error: {str(e)}")
        
        # print("Falling back to simulation mode")
        return None

    def closeEvent(self, event):
        """Clean up Arduino connection when closing"""
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        event.accept()
        
    def toggle_simulation(self):
        if self.is_running:
            self.stop_simulation()
        else:
            self.start_simulation()
            
    def start_simulation(self):
        if not hasattr(self, 'model') or self.model is None:
            self.trainer = ModelTrainer()
            self.model = self.trainer.load_model('best_model.h5')
        record_num = self.record_combo.currentText()
        self.simulation_speed = self.speed_spin.value()
        
        try:
            self.current_record = wfdb.rdsamp(f'{MITBIH_PATH}/{record_num}')[0][:, 0]
            self.current_index = 0
            self.is_running = True
            self.start_btn.setText("Stop Simulation")
            self.alert_label.setText("Status: Running...")
            self.alert_label.setStyleSheet("color: black; font-size: 16px;")
            
            # Calculate interval based on speed (360 samples = 1 second)
            interval = int(1000 * (self.window_size/2) / (360 * self.simulation_speed))
            self.timer.start(interval)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load record: {str(e)}")
            
    def stop_simulation(self):
        self.timer.stop()
        self.is_running = False
        self.start_btn.setText("Start Simulation")
        self.alert_label.setText("Status: Stopped")
        self.alert_label.setStyleSheet("color: black; font-size: 16px;")
        
    def update_simulation(self):
        if self.current_index + self.window_size >= len(self.current_record):
            self.stop_simulation()
            return
            
        segment = self.current_record[self.current_index : self.current_index + self.window_size]
        self.current_index += self.window_size // 2
        
        # Update plot
        self.ecg_curve.setData(segment)
        
        # Process segment
        segment_input = segment[np.newaxis, ..., np.newaxis]
        danger_prob = self.model.predict(segment_input, verbose=0)[0][0]
        self.prob_label.setText(f"Danger Probability: {danger_prob:.2f}")
        
        # Check for dangerous arrhythmia
        if danger_prob > DANGER_THRESHOLD:
            self.trigger_alert(danger_prob)

    def deliver_medication(self):
        """Handle complete medication delivery sequence"""
        current_time = time.time() * 1000  # Convert to milliseconds
        
        if not self.medication_ready:
            remaining = (self.medication_cooldown - (current_time - self.last_medication_time)) / 1000
            print(f"Medication on cooldown: {remaining:.1f}s remaining")
            return False
            
        if self.activate_valve():
            print("Medication delivered via valve")
            self.medication_ready = False
            self.last_medication_time = current_time
            # Schedule cooldown reset
            QTimer.singleShot(self.medication_cooldown, self.reset_medication)
            return True
        return False
        
    def activate_valve(self, duration_ms=1000):
        print("Activating valve...")

        # self.arduino = self.connect_to_arduino()        
        # print(self.arduino)

        """Send command to open medication valve"""
        # if self.arduino and self.arduino.is_open:
        try:
            self.arduino.write(b'O')  # Send open command
            print(f"Valve activated for {duration_ms}ms")
            return True
        except Exception as e:
            print(f"Valve control error: {str(e)}")
            return False
        print("Valve simulation (no Arduino connected)")
        return True  # Simulate success when in test mode

    def reset_medication(self):
        """Reset medication system after cooldown"""
        self.medication_ready = True
        self.alert_label.setText("Medication system ready")
        print("Medication system ready")
            
    def trigger_alert(self, probability):
        self.alert_label.setText("ALERT: Dangerous Arrhythmia Detected!")
        self.alert_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")

        alert_msg = f"Dangerous arrhythmia detected (prob={probability:.2f})"
        
        # Flash the background
        self.plot_widget.setBackground('r')
        QTimer.singleShot(200, lambda: self.plot_widget.setBackground('w'))

        # Visual/audio alerts
        self.play_alert_sound()
        self.alert_label.setText("ALERT: Medication Delivering...")

        # Medication delivery
        if self.deliver_medication():
            alert_msg += " - MEDICATION DELIVERED"
        else:
            alert_msg += " - MEDICATION ON COOLDOWN"

        # Pushbullet notification
        self.send_push_notification(alert_msg)
        
        # Log the alert
        with open('alerts.log', 'a') as f:
            f.write(f"Dangerous arrhythmia detected (prob={probability:.2f}) at index {self.current_index}\n")

    def send_push_notification(self, message):
        """Send mobile notification via Pushbullet"""
        if self.pb is None:
            return
            
        try:
            self.pb.push_note("ECG Alert", message)
        except Exception as e:
            print(f"Push notification failed: {str(e)}")

    def play_alert_sound(self):
        """Generate and play an alert sound"""
        try:
            # Generate a simple sine wave tone
            t = np.linspace(0, self.alert_duration, int(self.sample_rate * self.alert_duration), False)
            tone = 0.5 * np.sin(2 * np.pi * self.alert_frequency * t)
            
            # Play the sound asynchronously
            sd.play(tone, self.sample_rate, blocking=False)
            
        except Exception as e:
            print(f"Audio error: {str(e)}")
            # Fallback to system beep if sounddevice fails
            import winsound
            winsound.Beep(1000, 500)  # Windows fallback

def main():
    app = QApplication(sys.argv)
    window = ECGMonitorGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()