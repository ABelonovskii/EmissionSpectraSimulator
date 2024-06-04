# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont
import pyqtgraph as pg


class Ui_MainWindow(object):
    def setup_ui(self, MainWindow):
        self.MainWindow = MainWindow
        MainWindow.setObjectName("Spectra Simulator")
        MainWindow.resize(1251, 673)
        MainWindow.setWindowTitle("Spectra Simulator")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.setup_layout(MainWindow)
        self.setup_menu(MainWindow)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def setup_layout(self, MainWindow):
        self.splitter_main = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_main.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_main.setObjectName("splitter_main")

        self.config_area = QtWidgets.QWidget(self.splitter_main)
        self.config_layout = QtWidgets.QVBoxLayout(self.config_area)

        # Setup photonic modes group
        self.setup_photonic_modes(self.config_layout)
        self.setup_excitonic_mode(self.config_layout)
        self.setup_dynamic_configuration(self.config_layout)
        self.setup_spectra_configuration(self.config_layout)

        self.dynamics_layout = QtWidgets.QHBoxLayout()
        self.btn_calculate_dynamics = QtWidgets.QPushButton("Calculate Dynamics")
        self.dynamics_layout.addWidget(self.btn_calculate_dynamics)

        self.btn_save_dynamics = QtWidgets.QPushButton()
        self.btn_save_dynamics.setFixedSize(30, 30)
        self.btn_save_dynamics.setIcon(QtGui.QIcon("source/icons/save_icon.png"))
        self.btn_save_dynamics.setEnabled(False)
        self.dynamics_layout.addWidget(self.btn_save_dynamics)
        self.config_layout.addLayout(self.dynamics_layout)

        self.spectra_layout = QtWidgets.QHBoxLayout()
        self.btn_calculate_spectra = QtWidgets.QPushButton("Calculate Spectra")
        self.btn_calculate_spectra.setEnabled(False)
        self.spectra_layout.addWidget(self.btn_calculate_spectra)

        self.btn_save_spectra = QtWidgets.QPushButton()
        self.btn_save_spectra.setFixedSize(30, 30)
        self.btn_save_spectra.setIcon(QtGui.QIcon("source/icons/save_icon.png"))
        self.btn_save_spectra.setEnabled(False)
        self.spectra_layout.addWidget(self.btn_save_spectra)
        self.config_layout.addLayout(self.spectra_layout)

        self.graph_area = QtWidgets.QWidget(self.splitter_main)
        self.graph_layout = QtWidgets.QVBoxLayout(self.graph_area)
        self.tab_widget = QtWidgets.QTabWidget(self.graph_area)
        self.graph_layout.addWidget(self.tab_widget)

        self.graph_widget_dynamics = self.add_graph_tab("Population Dynamics")
        font = QFont()
        font.setPixelSize(12)
        font.setBold(True)
        self.graph_widget_dynamics.getAxis('left').setStyle(tickTextOffset=10, tickFont=font)
        self.graph_widget_dynamics.getAxis('left').setLabel('Number of particles', **{'font': font})
        self.graph_widget_dynamics.getAxis('bottom').setStyle(tickTextOffset=10, tickFont=font)
        self.graph_widget_dynamics.getAxis('bottom').setLabel('Time', units='s', **{'font': font})
        self.graph_widget_dynamics.showGrid(True, True)
        self.graph_widget_dynamics.addLegend()

        self.graph_widget_spectra = self.add_graph_tab("Spectra")
        self.graph_widget_spectra.getAxis('left').setStyle(tickTextOffset=10, tickFont=font)
        self.graph_widget_spectra.getAxis('left').setLabel('Intensity', **{'font': font})
        self.graph_widget_spectra.getAxis('bottom').setStyle(tickTextOffset=10, tickFont=font)
        self.graph_widget_spectra.getAxis('bottom').setLabel('Energy', units='eV', **{'font': font})
        self.graph_widget_spectra.showGrid(True, True)

        self.progress_bar = QtWidgets.QProgressBar(self.graph_area)
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        self.graph_layout.addWidget(self.progress_bar)

        self.gridLayout.addWidget(self.splitter_main, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

    def setup_photonic_modes(self, layout):
        group = QtWidgets.QGroupBox("Photonic Modes")
        layout.addWidget(group)
        form_layout = QtWidgets.QFormLayout(group)

        """" if one photon mode """
        int_validator = QtGui.QIntValidator(0, 100)
        double_validator = QtGui.QDoubleValidator(0.0, 1000.0, 20)
        double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)

        self.lineEdit_number_of_modes = QtWidgets.QLineEdit("")
        self.lineEdit_number_of_modes.setValidator(int_validator)
        self.label_number_of_modes = QtWidgets.QLabel("Number of Modes:")
        form_layout.addRow(self.label_number_of_modes, self.lineEdit_number_of_modes)
        self.lineEdit_number_of_modes.textChanged.connect(self.MainWindow.fields_changed)
        self.lineEdit_number_of_modes.textChanged.connect(self.handle_mode_change)

        self.lineEdit_photon_energy = QtWidgets.QLineEdit("")
        self.lineEdit_photon_energy.setValidator(double_validator)
        self.label_photon_energy = QtWidgets.QLabel("Photon Energy, eV:")
        form_layout.addRow(self.label_photon_energy, self.lineEdit_photon_energy)
        self.lineEdit_photon_energy.textChanged.connect(self.MainWindow.fields_changed)

        self.lineEdit_photon_damping = QtWidgets.QLineEdit("")
        self.lineEdit_photon_damping.setValidator(double_validator)
        self.label_photon_damping = QtWidgets.QLabel("Damping, eV:")
        form_layout.addRow(self.label_photon_damping, self.lineEdit_photon_damping)
        self.lineEdit_photon_damping.textChanged.connect(self.MainWindow.fields_changed)

        self.lineEdit_photon_pumping = QtWidgets.QLineEdit("")
        self.lineEdit_photon_pumping.setValidator(double_validator)
        self.label_photon_pumping = QtWidgets.QLabel("Pumping, eV:")
        form_layout.addRow(self.label_photon_pumping, self.lineEdit_photon_pumping)
        self.lineEdit_photon_pumping.textChanged.connect(self.MainWindow.fields_changed)

        self.lineEdit_photon_strength = QtWidgets.QLineEdit("")
        self.lineEdit_photon_strength.setValidator(double_validator)
        self.label_photon_strength = QtWidgets.QLabel("Strength, eV:")
        form_layout.addRow(self.label_photon_strength, self.lineEdit_photon_strength)
        self.lineEdit_photon_strength.textChanged.connect(self.MainWindow.fields_changed)

        self.lineEdit_initial_photons = QtWidgets.QLineEdit("")
        int_validator_initial = QtGui.QIntValidator(0, 1000000)
        self.lineEdit_initial_photons.setValidator(int_validator_initial)
        self.label_initial_photons = QtWidgets.QLabel("Initial Photons:")
        form_layout.addRow(self.label_initial_photons, self.lineEdit_initial_photons)
        self.lineEdit_initial_photons.textChanged.connect(self.MainWindow.fields_changed)

        """" if more than one photon mode (files)"""
        self.lineEdit_file_photon_energies = QtWidgets.QLineEdit("")
        self.button_select_file_photon_energies = QtWidgets.QPushButton("")
        self.button_select_file_photon_energies.clicked.connect(
            lambda: self.MainWindow.select_file(self.lineEdit_file_photon_energies))
        self.label_file_photon_energies = QtWidgets.QLabel("Energies file:")
        self.add_file_selection(form_layout, self.label_file_photon_energies, self.lineEdit_file_photon_energies,
                                self.button_select_file_photon_energies)
        self.lineEdit_file_photon_energies.textChanged.connect(self.MainWindow.fields_changed)

        self.lineEdit_file_photon_dampings = QtWidgets.QLineEdit("")
        self.button_select_file_photon_dampings = QtWidgets.QPushButton("")
        self.button_select_file_photon_dampings.clicked.connect(
            lambda: self.MainWindow.select_file(self.lineEdit_file_photon_dampings))
        self.label_file_photon_dampings = QtWidgets.QLabel("Dampings file:")
        self.add_file_selection(form_layout, self.label_file_photon_dampings, self.lineEdit_file_photon_dampings,
                                self.button_select_file_photon_dampings)
        self.lineEdit_file_photon_dampings.textChanged.connect(self.MainWindow.fields_changed)

        self.lineEdit_file_photon_pumpings = QtWidgets.QLineEdit("")
        self.button_select_file_photon_pumpings = QtWidgets.QPushButton("")
        self.button_select_file_photon_pumpings.clicked.connect(
            lambda: self.MainWindow.select_file(self.lineEdit_file_photon_pumpings))
        self.label_file_photon_pumpings = QtWidgets.QLabel("Pumpings file:")
        self.add_file_selection(form_layout, self.label_file_photon_pumpings, self.lineEdit_file_photon_pumpings,
                                self.button_select_file_photon_pumpings)
        self.lineEdit_file_photon_pumpings.textChanged.connect(self.MainWindow.fields_changed)

        self.lineEdit_file_initial_photon_counts = QtWidgets.QLineEdit("")
        self.button_select_file_initial_photon_counts = QtWidgets.QPushButton("")
        self.button_select_file_initial_photon_counts.clicked.connect(
            lambda: self.MainWindow.select_file(self.lineEdit_file_initial_photon_counts))
        self.label_file_initial_photon_counts = QtWidgets.QLabel("Initial counts file:")
        self.add_file_selection(form_layout, self.label_file_initial_photon_counts, self.lineEdit_file_initial_photon_counts,
                                self.button_select_file_initial_photon_counts)
        self.lineEdit_file_initial_photon_counts.textChanged.connect(self.MainWindow.fields_changed)

        self.lineEdit_file_strengths = QtWidgets.QLineEdit("")
        self.button_select_file_strengths = QtWidgets.QPushButton("")
        self.button_select_file_strengths.clicked.connect(
            lambda: self.MainWindow.select_file(self.lineEdit_file_strengths))
        self.label_file_strengths = QtWidgets.QLabel("Strengths file:")
        self.add_file_selection(form_layout, self.label_file_strengths, self.lineEdit_file_strengths,
                                self.button_select_file_strengths)
        self.lineEdit_file_strengths.textChanged.connect(self.MainWindow.fields_changed)


    def setup_excitonic_mode(self, layout):
        group = QtWidgets.QGroupBox("Excitonic Mode")
        layout.addWidget(group)
        form_layout = QtWidgets.QFormLayout(group)

        int_validator = QtGui.QIntValidator(0, 100)
        double_validator = QtGui.QDoubleValidator(0.0, 1000.0, 20)
        double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)

        self.lineEdit_exciton_energy = QtWidgets.QLineEdit("")
        self.lineEdit_exciton_energy.setValidator(double_validator)
        self.label_exciton_energy = QtWidgets.QLabel("Exciton Energy, eV:")
        form_layout.addRow(self.label_exciton_energy, self.lineEdit_exciton_energy)
        self.lineEdit_exciton_energy.textChanged.connect(self.MainWindow.fields_changed)

        self.lineEdit_exciton_damping = QtWidgets.QLineEdit("")
        self.lineEdit_exciton_damping.setValidator(double_validator)
        self.label_exciton_damping = QtWidgets.QLabel("Damping, eV:")
        form_layout.addRow(self.label_exciton_damping, self.lineEdit_exciton_damping)
        self.lineEdit_exciton_damping.textChanged.connect(self.MainWindow.fields_changed)

        self.lineEdit_exciton_pumping = QtWidgets.QLineEdit("")
        self.lineEdit_exciton_pumping.setValidator(double_validator)
        self.label_exciton_pumping = QtWidgets.QLabel("Pumping, eV:")
        form_layout.addRow(self.label_exciton_pumping, self.lineEdit_exciton_pumping)
        self.lineEdit_exciton_pumping.textChanged.connect(self.MainWindow.fields_changed)

        self.lineEdit_initial_excitons = QtWidgets.QLineEdit("")
        int_validator_initial = QtGui.QIntValidator(0, 1000000)
        self.lineEdit_initial_excitons.setValidator(int_validator_initial)
        self.label_initial_excitons = QtWidgets.QLabel("Initial Excitons:")
        form_layout.addRow(self.label_initial_excitons, self.lineEdit_initial_excitons)
        self.lineEdit_initial_excitons.textChanged.connect(self.MainWindow.fields_changed)


    def setup_dynamic_configuration(self, layout):
        group = QtWidgets.QGroupBox("Dynamic Configuration")
        layout.addWidget(group)
        form_layout = QtWidgets.QFormLayout(group)

        double_validator = QtGui.QDoubleValidator(0.0, 1e60, 500)
        double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)

        self.lineEdit_time_step = QtWidgets.QLineEdit("")
        self.lineEdit_time_step.setValidator(double_validator)
        self.label_time_step = QtWidgets.QLabel("Time Step, ps:")
        form_layout.addRow(self.label_time_step, self.lineEdit_time_step)
        self.lineEdit_time_step.textChanged.connect(self.MainWindow.fields_changed)

        self.lineEdit_time_end = QtWidgets.QLineEdit("")
        self.lineEdit_time_end.setValidator(double_validator)
        self.label_time_end = QtWidgets.QLabel("Time end, ps:")
        form_layout.addRow(self.label_time_end, self.lineEdit_time_end)
        self.lineEdit_time_end.textChanged.connect(self.MainWindow.fields_changed)

    def setup_spectra_configuration(self, layout):
        group = QtWidgets.QGroupBox("Spectra Configuration")
        layout.addWidget(group)
        form_layout = QtWidgets.QFormLayout(group)

        double_validator = QtGui.QDoubleValidator(0.0, 1e60, 500)
        double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)

        self.lineEdit_min_energy = QtWidgets.QLineEdit("")
        self.lineEdit_min_energy.setValidator(double_validator)
        form_layout.addRow("Minimum Energy, eV:", self.lineEdit_min_energy)
        self.lineEdit_min_energy.textChanged.connect(self.MainWindow.fields_changed)

        self.line_edit_energy_step = QtWidgets.QLineEdit("")
        self.line_edit_energy_step.setValidator(double_validator)
        form_layout.addRow("Energy Step, eV:", self.line_edit_energy_step)
        self.line_edit_energy_step.textChanged.connect(self.MainWindow.fields_changed)

        self.line_edit_max_energy = QtWidgets.QLineEdit("")
        self.line_edit_max_energy.setValidator(double_validator)
        form_layout.addRow("Maximum Energy, eV:", self.line_edit_max_energy)
        self.line_edit_max_energy.textChanged.connect(self.MainWindow.fields_changed)

    def handle_mode_change(self, text):
        num_modes = int(text) if text.isdigit() else 0
        if num_modes == 1:
            self.show_single_mode_ui()
            self.hide_multiple_mode_ui()
        elif num_modes > 1:
            self.hide_single_mode_ui()
            self.show_multiple_mode_ui()
        else:
            self.hide_single_mode_ui()
            self.hide_multiple_mode_ui()

    def show_single_mode_ui(self):
        self.label_photon_energy.show()
        self.label_photon_damping.show()
        self.label_photon_pumping.show()
        self.label_photon_strength.show()
        self.label_initial_photons.show()

        self.lineEdit_photon_energy.show()
        self.lineEdit_photon_damping.show()
        self.lineEdit_photon_pumping.show()
        self.lineEdit_photon_strength.show()
        self.lineEdit_initial_photons.show()

    def hide_single_mode_ui(self):
        self.label_photon_energy.hide()
        self.label_photon_damping.hide()
        self.label_photon_pumping.hide()
        self.label_photon_strength.hide()
        self.label_initial_photons.hide()

        self.lineEdit_photon_energy.hide()
        self.lineEdit_photon_damping.hide()
        self.lineEdit_photon_pumping.hide()
        self.lineEdit_photon_strength.hide()
        self.lineEdit_initial_photons.hide()

    def show_multiple_mode_ui(self):
        self.label_file_photon_energies.show()
        self.lineEdit_file_photon_energies.show()
        self.button_select_file_photon_energies.show()

        self.label_file_photon_dampings.show()
        self.lineEdit_file_photon_dampings.show()
        self.button_select_file_photon_dampings.show()

        self.label_file_photon_pumpings.show()
        self.lineEdit_file_photon_pumpings.show()
        self.button_select_file_photon_pumpings.show()

        self.label_file_initial_photon_counts.show()
        self.lineEdit_file_initial_photon_counts.show()
        self.button_select_file_initial_photon_counts.show()

        self.label_file_strengths.show()
        self.lineEdit_file_strengths.show()
        self.button_select_file_strengths.show()

    def hide_multiple_mode_ui(self):
        self.label_file_photon_energies.hide()
        self.lineEdit_file_photon_energies.hide()
        self.button_select_file_photon_energies.hide()

        self.label_file_photon_dampings.hide()
        self.lineEdit_file_photon_dampings.hide()
        self.button_select_file_photon_dampings.hide()

        self.label_file_photon_pumpings.hide()
        self.lineEdit_file_photon_pumpings.hide()
        self.button_select_file_photon_pumpings.hide()

        self.label_file_initial_photon_counts.hide()
        self.lineEdit_file_initial_photon_counts.hide()
        self.button_select_file_initial_photon_counts.hide()

        self.label_file_strengths.hide()
        self.lineEdit_file_strengths.hide()
        self.button_select_file_strengths.hide()

    def add_file_selection(self, form_layout, label_text, line_edit, button):
        button.setIcon(QtGui.QIcon('source/icons/upload_icon.png'))
        button.setFixedSize(25, 25)

        row_layout = QtWidgets.QHBoxLayout()
        row_layout.addWidget(line_edit)
        row_layout.addWidget(button)

        form_layout.addRow(label_text, row_layout)

    def setup_menu(self, MainWindow):
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1051, 21))
        MainWindow.setMenuBar(self.menubar)

        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setTitle("File")

        self.actionNewConfig = QtWidgets.QAction(MainWindow)
        self.actionNewConfig.setText("New")

        self.actionLoadConfig = QtWidgets.QAction(MainWindow)
        self.actionLoadConfig.setText("Load")

        self.actionSaveConfig = QtWidgets.QAction(MainWindow)
        self.actionSaveConfig.setText("Save")

        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setText("Exit")

        self.menuFile.addAction(self.actionNewConfig)
        self.menuFile.addAction(self.actionLoadConfig)
        self.menuFile.addAction(self.actionSaveConfig)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)

        self.menubar.addMenu(self.menuFile)

    def setup_group(self, title, layout):
        group = QtWidgets.QGroupBox(title)
        layout.addWidget(group)
        group_layout = QtWidgets.QVBoxLayout(group)
        text_edit = QtWidgets.QTextEdit()
        group_layout.addWidget(text_edit)

    def add_graph_tab(self, title):
        tab = QtWidgets.QWidget()
        self.tab_widget.addTab(tab, title)
        layout = QtWidgets.QVBoxLayout(tab)
        plot_widget = pg.PlotWidget(background='w')
        layout.addWidget(plot_widget)
        return plot_widget

