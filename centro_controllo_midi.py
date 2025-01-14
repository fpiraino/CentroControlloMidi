from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QWidget, QGroupBox
)
from PyQt5.QtCore import Qt
from mido import Message, open_output
from mido.backends import rtmidi

class CentroControlloMIDI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Centro Controllo MIDI")

        # Porta MIDI di output
        self.midi_output = open_output('Virtual MIDI Output', backend='mido.backends.rtmidi')  # Cambia con il tuo dispositivo

        # Layout principale
        main_layout = QVBoxLayout()

        # Riquadro LoopeRhino
        looperhino_group = self.create_looperhino_group()
        main_layout.addWidget(looperhino_group)

        # Imposta layout nella finestra
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_looperhino_group(self):
        group_box = QGroupBox("LoopeRhino")
        layout = QVBoxLayout()

        # Dropdown per canale MIDI
        channel_layout = QHBoxLayout()
        channel_label = QLabel("Canale MIDI:")
        self.channel_dropdown = QComboBox()
        self.channel_dropdown.addItems([str(i) for i in range(1, 17)])
        channel_layout.addWidget(channel_label)
        channel_layout.addWidget(self.channel_dropdown)
        layout.addLayout(channel_layout)

        # Dropdown per buffer ON/OFF
        buffer_layout = QHBoxLayout()
        buffer_label = QLabel("Buffer:")
        self.buffer_dropdown = QComboBox()
        self.buffer_dropdown.addItems(["OFF", "ON"])
        self.buffer_dropdown.currentTextChanged.connect(self.handle_buffer_change)
        buffer_layout.addWidget(buffer_label)
        buffer_layout.addWidget(self.buffer_dropdown)
        layout.addLayout(buffer_layout)

        # Pulsanti Toggle
        toggle_layout = QHBoxLayout()
        self.toggle_buttons = {}
        toggle_labels = ["L1", "L2", "L3", "L4", "L5", "C1", "C2"]
        cc_values = [103, 104, 105, 106, 107, 108, 109]

        for label, cc in zip(toggle_labels, cc_values):
            button = QPushButton(label)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, cc=cc: self.handle_toggle(cc, checked))
            self.toggle_buttons[label] = button
            toggle_layout.addWidget(button)

        layout.addLayout(toggle_layout)
        group_box.setLayout(layout)
        return group_box

    def handle_buffer_change(self, value):
        """Gestisce la modifica del buffer."""
        channel = int(self.channel_dropdown.currentText()) - 1
        cc_value = 127 if value == "ON" else 0
        self.midi_output.send(Message('control_change', channel=channel, control=102, value=cc_value))

    def handle_toggle(self, cc, checked):
        """Gestisce i pulsanti toggle."""
        channel = int(self.channel_dropdown.currentText()) - 1
        value = 127 if checked else 0
        self.midi_output.send(Message('control_change', channel=channel, control=cc, value=value))

# Avvio dell'applicazione
if __name__ == "__main__":
    app = QApplication([])
    window = CentroControlloMIDI()
    window.show()
    app.exec_()
