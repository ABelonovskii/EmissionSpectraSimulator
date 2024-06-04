from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QApplication
from scipy import integrate
import matplotlib.cm as cm
import scipy.linalg as scl
import pyqtgraph as pg
import numpy as np


class Core:

    def __init__(self):
        self.N = 0 # all modes
        self.W = None
        self.gamma = None
        self.P = None
        self.g = None
        self.initial_count = None
        self.n = None
        self.G = None
        self.N = 0
        self.time_step = 0
        self.time_end = 0
        self.min_energy = 0
        self.energy_step = 0
        self.max_energy = 0
        self.k = 0
        self.dynamics_result = None

    def set_config_data(self, config_data):
        self.config_data = config_data
        self.setup_parameters()

    def setup_parameters(self):
        number_of_modes = self.config_data['photonic_modes']['number_of_modes']
        self.N = number_of_modes + 1  # +1 for excitons

        # Initializing Arrays
        self.W = np.zeros(self.N) # Energies
        self.gamma = np.zeros(self.N) # Dampings
        self.P = np.zeros(self.N) # Pumping
        self.g = np.zeros(self.N) # Strengths
        self.initial_count = np.zeros(self.N)

        # For exciton
        self.W[0] = self.config_data['excitonic_mode']['exciton_energy_ev']
        self.gamma[0] = self.config_data['excitonic_mode']['damping_ev']
        self.P[0] = self.config_data['excitonic_mode']['pumping_ev']
        self.initial_count[0] = self.config_data['excitonic_mode']['initial_excitons']

        # loading data from files if the number of mods is more than 1 else use load_single_mode.
        if number_of_modes > 1:
            self.load_from_files(number_of_modes)
        else:
            self.load_single_mode()

        # For Dynamic calculations
        self.time_step = self.config_data['dynamic_configuration']['time_step_ps']
        self.time_step = self.time_step / (6.582119569 * 10 ** (-4)) #  convert
        self.time_end = self.config_data['dynamic_configuration']['time_end_ps']
        self.time_end = self.time_end / (6.582119569 * 10 ** (-4))  # convert

        # For Spectra calculations
        self.min_energy = self.config_data['spectra_configuration']['min_energy_ev']
        self.energy_step = self.config_data['spectra_configuration']['energy_step_ev']
        self.max_energy = self.config_data['spectra_configuration']['max_energy_ev']

    def load_from_files(self, number_of_modes):
        self.W[1:] = np.loadtxt(self.config_data['photonic_modes']['file_photon_energies'])
        self.gamma[1:] = np.loadtxt(self.config_data['photonic_modes']['file_photon_dampings'])
        self.P[1:] = np.loadtxt(self.config_data['photonic_modes']['file_photon_pumpings'])
        self.g[1:] = np.loadtxt(self.config_data['photonic_modes']['file_strengths'])
        self.initial_count[1:] = np.loadtxt(self.config_data['photonic_modes']['file_initial_photon_counts'])

    def load_single_mode(self):
        self.W[1] = self.config_data['photonic_modes']['photon_energy_ev']
        self.gamma[1] = self.config_data['photonic_modes']['damping_ev']
        self.P[1] = self.config_data['photonic_modes']['pumping_ev']
        self.g[1] = self.config_data['photonic_modes']['strength_ev']
        self.initial_count[1] = self.config_data['photonic_modes']['initial_photons']

    def odeintz(self, func, z0, t, **kwargs):
        """An odeint-like function for complex valued differential equations."""

        # Disallow Jacobian-related arguments.
        _unsupported_odeint_args = ['Dfun', 'col_deriv', 'ml', 'mu']
        bad_args = [arg for arg in kwargs if arg in _unsupported_odeint_args]
        if len(bad_args) > 0:
            raise ValueError("The odeint argument %r is not supported by "
                             "odeintz." % (bad_args[0],))

        # Make sure z0 is a numpy array of type np.complex128.
        z0 = np.array(z0, dtype=np.complex128, ndmin=1)

        def realfunc(x, t, *args):

            self.progress_bar.setValue(int(t / self.time_end * 100))
            QApplication.processEvents()

            z = x.view(np.complex128)
            dzdt = func(z, t, *args)
            # func might return a python list, so convert its return
            # value to an array with type np.complex128, and then return
            # a np.float64 view of that array.
            return np.asarray(dzdt, dtype=np.complex128).view(np.float64)

        result = integrate.odeint(realfunc, z0.view(np.float64), t, **kwargs)

        if kwargs.get('full_output', False):
            z = result[0].view(np.complex128)
            infodict = result[1]
            return z, infodict
        else:
            z = result.view(np.complex128)
            return z

    def create_dynamics_matrix(self, n, t):
        V = np.zeros(shape=(self.N * self.N), dtype=np.complex);
        V[0] = self.P[0] - self.G[0] * n[0] + 1j * sum([self.g[i] * (n[self.N * i] - n[i]) for i in range(1, self.N)])
        for i in range(1, self.N):
            V[i] = 1j * (self.W[0] - self.W[i]) * n[i] - 1j * self.g[i] * n[0] - (self.G[0] + self.G[i]) / 2 * n[i] \
                   + 1j * sum([self.g[j] * n[j * self.N + i] for j in range(1, self.N)]) + 2 * 1j * self.k * n[0] * n[i]
            V[i * self.N] = np.conj(V[i])
            for j in range(1, self.N):
                V[self.N * i + j] = 1j * (self.W[i] - self.W[j]) * n[self.N * i + j] - 1j * self.g[j] * n[self.N * i] + 1j * self.g[i] * n[j] \
                                    - (self.G[i] + self.G[j]) / 2 * n[self.N * i + j] + (self.P[i] if (i == j) else 0)
        return V

    def emd(self, M, D, t):
        return (np.dot(scl.expm(M * t), D)).trace()


    def calculate_dynamics(self, progress_bar, plot_widget):
        """ solving the equation of motion of the coupled system"""

        self.progress_bar = progress_bar

        self.G = self.gamma - self.P
        self.k = 0 # Exciton-exciton interaction
        self.n = np.zeros(shape=(self.N * self.N), dtype=np.complex)

        for i in range(self.N):
            self.n[i * self.N + i] = self.initial_count[i]

        self.all_time = np.linspace(0, self.time_end, int(self.time_end / self.time_step) + 1)

        self.dynamics_result = self.odeintz(self.create_dynamics_matrix, self.n, self.all_time)

        self.progress_bar.setValue(100)
        QApplication.processEvents()

        self.time_for_graph = self.all_time * 6.582119569 * 10 ** (-4) * 10 ** (-12) # reverse conference in s

        color_map = cm.get_cmap('Accent', self.N)
        QColors = [QColor(*[int(255 * x) for x in color_map(i)[:3]]) for i in range(self.N)]

        plot_widget.plot(self.time_for_graph, np.real(self.dynamics_result[:, 0]), pen=pg.mkPen(color=QColors[0], width=3),
                         name='Number of excitons', clear=True)
        for i in range(1, self.N):
            plot_widget.plot(self.time_for_graph, np.real(self.dynamics_result[:, i * self.N + i]), pen=pg.mkPen(color=QColors[i], width=3),
                             name=f'Number of photons in mode {i}')


    def calculate_spectra(self, progress_bar, plot_widget):
        """ Calculate Spectra """

        self.progress_bar = progress_bar

        # integrate matrix of all numbers of particles
        int_n = np.zeros(shape=(self.N, self.N), dtype=np.complex)
        for time_ in range(len(self.dynamics_result)):
            for i in range(self.N):
                for j in range(self.N):
                    int_n[i][j] += self.dynamics_result[time_][i * self.N + j] * self.time_step

        # ratio
        sum = 0
        for j in range(1, self.N):
            sum += int_n[j][j]

        D = np.zeros(shape=(self.N, self.N), dtype=np.complex)
        for i in range(self.N):
            for j in range(1, self.N):
                D[i][j] = int_n[j][i] / (np.pi * sum)

        # matrix M
        M = np.zeros(shape=(self.N, self.N), dtype=np.complex)
        M[0][0] = -1j * self.W[0] - self.G[0] / 2
        for i in range(1, self.N):
            M[i][i] = -1j * self.W[i] - self.G[i] / 2
            M[0][i] = -1j * self.g[i]
            M[i][0] = -1j * self.g[i]

        self.spectra = np.zeros(shape=((int((self.max_energy - self.min_energy) / self.energy_step) + 1)), dtype=np.complex)
        self.energy_interval = np.linspace(self.min_energy, self.max_energy, int((self.max_energy - self.min_energy) / self.energy_step) + 1)

        int_emd = np.zeros(shape=(int(self.time_end / self.time_step) + 1), dtype=np.complex)
        for i in range(len(self.all_time)):
            int_emd[i] = self.emd(M,  D, self.all_time[i])

        currentEnergy = self.min_energy
        j = 0
        while currentEnergy <= self.max_energy:
            S = 0
            for i in range(len(self.all_time)):
                S += int_emd[i] * np.exp(1j * currentEnergy * self.all_time[i]) * self.time_step

            self.progress_bar.setValue((currentEnergy - self.min_energy) / (self.max_energy - self.min_energy) * 100)
            QApplication.processEvents()

            self.spectra[j] = S
            currentEnergy = np.round(currentEnergy + self.energy_step, 5)
            j += 1

        pen = pg.mkPen(color='r', width=3)
        brush = pg.mkBrush(QColor(255, 0, 0, 50))
        plot_widget.plot(self.energy_interval, np.real(self.spectra), pen=pen, brush=brush, fillLevel=0,  clear=True)

    def save_dynamics_result(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(None, "Save Dynamics Result", "dynamics_result.txt",
                                                   "Text Files (*.txt)", options=options)
        if file_name:
            with open(file_name, 'w') as file:

                header = "Time (s)\tNumber of Excitons"
                for i in range(1, self.N):
                    header += f"\tNumber of Photons in Mode {i}"
                file.write(header + "\n")

                for i in range(len(self.time_for_graph)):
                    line = f"{self.time_for_graph[i]}\t{np.real(self.dynamics_result[i, 0])}"
                    for j in range(1, self.N):
                        line += f"\t{np.real(self.dynamics_result[i, j * self.N + j])}"
                    file.write(line + "\n")
            print("Dynamics result saved to", file_name)

    def save_spectra(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(None, "Save Spectra", "spectra.txt", "Text Files (*.txt)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write("Energy (eV)\tIntensity\n")
                for i in range(len(self.energy_interval)):
                    file.write(f"{self.energy_interval[i]}\t{np.real(self.spectra[i])}\n")
        print("Spectra saved to", file_name)