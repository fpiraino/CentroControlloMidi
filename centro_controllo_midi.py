from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QWidget, QGroupBox, QMessageBox, QTextEdit, QSlider
)
from PyQt5.QtCore import Qt
from mido import Message, get_output_names, open_output
from mido.backends import rtmidi

class CentroControlloMIDI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Centro Controllo MIDI")

        # Porta MIDI di output
        self.midi_output = None
        self.available_ports = get_output_names()

        # Layout principale
        main_layout = QVBoxLayout()

        # Selezione porta MIDI
        midi_port_group = self.create_midi_port_group()
        main_layout.addWidget(midi_port_group)

        # Riquadro LoopeRhino
        looperhino_group = self.create_looperhino_group()
        main_layout.addWidget(looperhino_group)

        # Riquadro Walrus Mako D1
        walrus_group = self.create_walrus_group()
        main_layout.addWidget(walrus_group)

        # Riquadro per log dei messaggi MIDI
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("Log dei messaggi MIDI inviati...")
        main_layout.addWidget(self.log_box)

        # Imposta layout nella finestra
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_midi_port_group(self):
        group_box = QGroupBox("Selezione Porta MIDI")
        layout = QHBoxLayout()

        port_label = QLabel("Porta MIDI:")
        self.port_dropdown = QComboBox()
        self.port_dropdown.addItems(self.available_ports if self.available_ports else ["Nessuna porta disponibile"])
        self.port_dropdown.currentTextChanged.connect(self.change_midi_port)

        layout.addWidget(port_label)
        layout.addWidget(self.port_dropdown)
        group_box.setLayout(layout)
        return group_box

    def change_midi_port(self, port_name):
        """Cambia la porta MIDI attiva."""
        if port_name != "Nessuna porta disponibile" and port_name in self.available_ports:
            try:
                self.midi_output = open_output(port_name, backend='mido.backends.rtmidi')
                self.log_message(f"Porta MIDI selezionata: {port_name}")
            except Exception as e:
                self.show_error_message(f"Errore nell'aprire la porta MIDI: {e}")
        else:
            self.midi_output = None

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

    def create_walrus_group(self):
        group_box = QGroupBox("Walrus Mako D1")
        layout = QVBoxLayout()

        # Dropdown per canale MIDI
        channel_layout = QHBoxLayout()
        channel_label = QLabel("Canale MIDI:")
        self.walrus_channel_dropdown = QComboBox()
        self.walrus_channel_dropdown.addItems([str(i) for i in range(1, 17)])
        channel_layout.addWidget(channel_label)
        channel_layout.addWidget(self.walrus_channel_dropdown)
        layout.addLayout(channel_layout)

        # Dropdown per selezione preset
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Preset:")
        self.preset_dropdown = QComboBox()
        presets = [
            "BANK A - RED", "BANK A - GREEN", "BANK A - BLUE",
            "BANK B - RED", "BANK B - GREEN", "BANK B - BLUE",
            "BANK C - RED", "BANK C - GREEN", "BANK C - BLUE"
        ]
        self.preset_dropdown.addItems(presets)
        self.preset_dropdown.currentIndexChanged.connect(self.handle_preset_change)
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_dropdown)
        layout.addLayout(preset_layout)

        # Pulsante BYPASS
        self.bypass_button = QPushButton("BYPASS")
        self.bypass_button.setCheckable(True)
        self.bypass_button.clicked.connect(self.handle_bypass)
        layout.addWidget(self.bypass_button)

        # Slider per i parametri
        sliders = {
            "Time": 14, "Repeat": 15, "Mix": 20, "Mod": 21,
            "Tone": 22, "Age": 23, "Attack": 25
        }
        for label, cc in sliders.items():
            slider_layout = QHBoxLayout()
            slider_label = QLabel(label)
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 127)
            slider.valueChanged.connect(lambda value, cc=cc: self.handle_slider_change(cc, value))
            slider_layout.addWidget(slider_label)
            slider_layout.addWidget(slider)
            layout.addLayout(slider_layout)

        # Dropdown per Progr
        progr_layout = QHBoxLayout()
        progr_label = QLabel("Progr:")
        self.progr_dropdown = QComboBox()
        progr_options = ["DIG", "MOD", "VINT", "DUAL", "REV"]
        self.progr_dropdown.addItems(progr_options)
        self.progr_dropdown.currentIndexChanged.connect(self.handle_progr_change)
        progr_layout.addWidget(progr_label)
        progr_layout.addWidget(self.progr_dropdown)
        layout.addLayout(progr_layout)

        # Dropdown per SubDiv
        subdiv_layout = QHBoxLayout()
        subdiv_label = QLabel("SubDiv:")
        self.subdiv_dropdown = QComboBox()
        subdiv_options = ["Quarter", "Eight", "Dott Eight"]
        self.subdiv_dropdown.addItems(subdiv_options)
        self.subdiv_dropdown.currentIndexChanged.connect(self.handle_subdiv_change)
        subdiv_layout.addWidget(subdiv_label)
        subdiv_layout.addWidget(self.subdiv_dropdown)
        layout.addLayout(subdiv_layout)

        group_box.setLayout(layout)
        return group_box

    def handle_preset_change(self, index):
        if self.midi_output:
            channel = int(self.walrus_channel_dropdown.currentText()) - 1
            self.midi_output.send(Message('program_change', channel=channel, program=index))
            self.log_message(f"Inviato Program Change: {index}")

    def handle_bypass(self, checked):
        if self.midi_output:
            channel = int(self.walrus_channel_dropdown.currentText()) - 1
            value = 127 if checked else 0
            self.midi_output.send(Message('control_change', channel=channel, control=29, value=value))
            self.log_message(f"Inviato BYPASS CC 29: {value}")

    def handle_slider_change(self, cc, value):
        if self.midi_output:
            channel = int(self.walrus_channel_dropdown.currentText()) - 1
            self.midi_output.send(Message('control_change', channel=channel, control=cc, value=value))
            self.log_message(f"Inviato CC {cc}: {value}")

    def handle_progr_change(self, index):
        if self.midi_output:
            channel = int(self.walrus_channel_dropdown.currentText()) - 1
            self.midi_output.send(Message('control_change', channel=channel, control=24, value=index))
            self.log_message(f"Inviato Progr CC 24: {index}")

    def handle_subdiv_change(self, index):
        if self.midi_output:
            channel = int(self.walrus_channel_dropdown.currentText()) - 1
            values = [0, 43, 86]  # Valori corrispondenti
            self.midi_output.send(Message('control_change', channel=channel, control=28, value=values[index]))
            self.log_message(f"Inviato SubDiv CC 28: {values[index]}")

    def log_message(self, message):
        """Aggiunge un messaggio al log dei messaggi MIDI."""
        self.log_box.append(str(message))

    def show_error_message(self, message):
        """Mostra un messaggio di errore all'utente."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Errore MIDI")
        msg.setText(message)
        msg.exec_()

# Avvio dell'applicazione
if __name__ == "__main__":
    app = QApplication([])
    window = CentroControlloMIDI()
    window.show()
    app.exec_()
