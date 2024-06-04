import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog)
from source.design import Ui_MainWindow
from source.core import Core
from source.config_manager import ConfigManager
from source.utilities import safe_int, safe_float


class MainWindow(QMainWindow):
    def __init__(self, core, config_manager):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setup_ui(self)
        self.core = core
        self.config_manager = config_manager

        #Connect signals and slots
        self.ui.actionNewConfig.triggered.connect(self.new_config)
        self.ui.actionLoadConfig.triggered.connect(self.load_config)
        self.ui.actionSaveConfig.triggered.connect(self.save_config)
        self.ui.actionExit.triggered.connect(self.exit_app)
        self.ui.btn_calculate_dynamics.clicked.connect(self.run_calculate_dynamics)
        self.ui.btn_calculate_spectra.clicked.connect(self.run_calculate_spectra)
        self.ui.btn_save_dynamics.clicked.connect(self.core.save_dynamics_result)
        self.ui.btn_save_spectra.clicked.connect(self.core.save_spectra)

        self.update_ui_inprocess = False
        self.config_manager.load_config()
        self.update_ui()

    def new_config(self):
        self.config_manager.config_data = {}
        self.update_ui()

    def load_config(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'YAML Files (*.yaml)')
        if fname:
            self.config_manager.config_path = fname
            self.config_manager.load_config()
            self.update_ui()

    def save_config(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Save file', '', 'YAML Files (*.yaml)')
        if fname:
            self.config_manager.config_path = fname
            self.config_manager.save_config()

    def select_file(self, line_edit):
        fname, _ = QFileDialog.getOpenFileName(None, 'Open file', '', 'Text Files (*.txt)')
        if fname:
            line_edit.setText(fname)

    def run_calculate_dynamics(self):
        self.core.set_config_data(self.config_manager.config_data)
        self.core.calculate_dynamics(self.ui.progress_bar, self.ui.graph_widget_dynamics)
        self.ui.btn_calculate_spectra.setEnabled(True)
        self.ui.btn_save_dynamics.setEnabled(True)
        self.ui.tab_widget.setCurrentIndex(0)

    def run_calculate_spectra(self):
        self.core.calculate_spectra(self.ui.progress_bar, self.ui.graph_widget_spectra)
        self.ui.btn_save_spectra.setEnabled(True)
        self.ui.tab_widget.setCurrentIndex(1)


    def update_ui(self):
        self.update_ui_inprocess = True
        self.ui.lineEdit_number_of_modes.setText(str(self.config_manager.get_value('photonic_modes/number_of_modes', '')))
        self.ui.lineEdit_photon_energy.setText(str(self.config_manager.get_value('photonic_modes/photon_energy_ev', '')))
        self.ui.lineEdit_photon_damping.setText(str(self.config_manager.get_value('photonic_modes/damping_ev', '')))
        self.ui.lineEdit_photon_pumping.setText(str(self.config_manager.get_value('photonic_modes/pumping_ev', '')))
        self.ui.lineEdit_photon_strength.setText(str(self.config_manager.get_value('photonic_modes/strength_ev', '')))
        self.ui.lineEdit_initial_photons.setText(str(self.config_manager.get_value('photonic_modes/initial_photons', '')))

        self.ui.lineEdit_file_photon_energies.setText(str(self.config_manager.get_value('photonic_modes/file_photon_energies', '')))
        self.ui.lineEdit_file_photon_dampings.setText(str(self.config_manager.get_value('photonic_modes/file_photon_dampings', '')))
        self.ui.lineEdit_file_photon_pumpings.setText(str(self.config_manager.get_value('photonic_modes/file_photon_pumpings', '')))
        self.ui.lineEdit_file_initial_photon_counts.setText(str(self.config_manager.get_value('photonic_modes/file_initial_photon_counts', '')))
        self.ui.lineEdit_file_strengths.setText(str(self.config_manager.get_value('photonic_modes/file_strengths', '')))

        self.ui.lineEdit_exciton_energy.setText(str(self.config_manager.get_value('excitonic_mode/exciton_energy_ev', '')))
        self.ui.lineEdit_exciton_damping.setText(str(self.config_manager.get_value('excitonic_mode/damping_ev', '')))
        self.ui.lineEdit_exciton_pumping.setText(str(self.config_manager.get_value('excitonic_mode/pumping_ev', '')))
        self.ui.lineEdit_initial_excitons.setText(str(self.config_manager.get_value('excitonic_mode/initial_excitons', '')))

        self.ui.lineEdit_time_step.setText(str(self.config_manager.get_value('dynamic_configuration/time_step_ps', '')))
        self.ui.lineEdit_time_end.setText(str(self.config_manager.get_value('dynamic_configuration/time_end_ps', '')))

        self.ui.lineEdit_min_energy.setText(str(self.config_manager.get_value('spectra_configuration/min_energy_ev', '')))
        self.ui.line_edit_energy_step.setText(str(self.config_manager.get_value('spectra_configuration/energy_step_ev', '')))
        self.ui.line_edit_max_energy.setText(str(self.config_manager.get_value('spectra_configuration/max_energy_ev', '')))

        self.update_ui_inprocess = False

    def fields_changed(self):
        if self.update_ui_inprocess:
            return
        self.config_manager.set_value('photonic_modes/number_of_modes', safe_int(self.ui.lineEdit_number_of_modes.text()))
        self.config_manager.set_value('photonic_modes/photon_energy_ev', safe_float(self.ui.lineEdit_photon_energy.text()))
        self.config_manager.set_value('photonic_modes/damping_ev', safe_float(self.ui.lineEdit_photon_damping.text()))
        self.config_manager.set_value('photonic_modes/pumping_ev', safe_float(self.ui.lineEdit_photon_pumping.text()))
        self.config_manager.set_value('photonic_modes/strength_ev', safe_float(self.ui.lineEdit_photon_strength.text()))
        self.config_manager.set_value('photonic_modes/initial_photons', safe_int(self.ui.lineEdit_initial_photons.text()))

        self.config_manager.set_value('photonic_modes/file_photon_energies', self.ui.lineEdit_file_photon_energies.text())
        self.config_manager.set_value('photonic_modes/file_photon_dampings', self.ui.lineEdit_file_photon_dampings.text())
        self.config_manager.set_value('photonic_modes/file_photon_pumpings', self.ui.lineEdit_file_photon_pumpings.text())
        self.config_manager.set_value('photonic_modes/file_initial_photon_counts', self.ui.lineEdit_file_initial_photon_counts.text())
        self.config_manager.set_value('photonic_modes/file_strengths', self.ui.lineEdit_file_strengths.text())

        self.config_manager.set_value('excitonic_mode/exciton_energy_ev', safe_float(self.ui.lineEdit_exciton_energy.text()))
        self.config_manager.set_value('excitonic_mode/damping_ev', safe_float(self.ui.lineEdit_exciton_damping.text()))
        self.config_manager.set_value('excitonic_mode/pumping_ev', safe_float(self.ui.lineEdit_exciton_pumping.text()))
        self.config_manager.set_value('excitonic_mode/initial_excitons', safe_int(self.ui.lineEdit_initial_excitons.text()))

        self.config_manager.set_value('dynamic_configuration/time_step_ps', safe_float(self.ui.lineEdit_time_step.text()))
        self.config_manager.set_value('dynamic_configuration/time_end_ps',safe_float(self.ui.lineEdit_time_end.text()))

        self.config_manager.set_value('spectra_configuration/min_energy_ev', safe_float(self.ui.lineEdit_min_energy.text()))
        self.config_manager.set_value('spectra_configuration/energy_step_ev', safe_float(self.ui.line_edit_energy_step.text()))
        self.config_manager.set_value('spectra_configuration/max_energy_ev', safe_float(self.ui.line_edit_max_energy.text()))

        self.ui.btn_calculate_spectra.setEnabled(False)
        self.ui.btn_save_dynamics.setEnabled(False)
        self.ui.btn_save_spectra.setEnabled(False)

    def exit_app(self):
        QApplication.quit()


def load_stylesheet(app):
    with open("source/style.css", "r") as file:
        app.setStyleSheet(file.read())


def main():
    app = QApplication(sys.argv)
    core = Core()
    config_manager = ConfigManager()
    main_window = MainWindow(core, config_manager)
    load_stylesheet(app)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()