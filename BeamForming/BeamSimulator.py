import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout


class BeamForming:
    def __init__(self, array, signal):
        self._signal= signal
        self._array=array
        self._resulted_signal=None
    
    def apply_signal_to_array(self, mode):
        signal=self._signal.get_signal_data()
        steer_vector = self._array.get_steer_vector()
        steer_vector = steer_vector.reshape(-1,1) # make s a column vector nx1
        signal = signal.reshape(1,-1) # make signal a row vector 1 X no_of_sampling points
        #each row correspond to the signal recieved/transmitted by one element in the array
        self._resulted_signal= steer_vector @ signal #shape= no_of_elements*no_of_samples
        #apply noise to the signal if recieved
        if mode== 'R':
            Nr, N= self._resulted_signal.shape[0],self._resulted_signal.shape[1] #Nr--> elements_num, N--> samples
            noise = np.random.randn( Nr, N) + 1j*np.random.randn( Nr, N)
            self._resulted_signal=  self._resulted_signal + 0.5*noise 

        return self._resulted_signal
    

    def find_beam_pattern(self, parent_widget, shape):
        if shape =='linear':
            
            steer_vector= self._array.get_steer_vector()
            antennas_num,spacing,_= self._array.get_array_factor()
            wavelength= self._signal.get_wavelength()
            phi = np.linspace(-1*np.pi/2, 1*np.pi/2, 1000)
            beam_pattern = np.abs(np.sum([steer_vector[n] * np.exp(1j * spacing/wavelength * (n) * np.sin(phi)) for n in range(antennas_num)], axis=0))
            if np.max(beam_pattern) > 0:
              beam_pattern /= np.max(beam_pattern)
            else:
              beam_pattern = np.zeros_like(beam_pattern) 
            print(phi.shape)  # Should be (1000,)
            print(beam_pattern.shape)  # Ensure it is also (1000,)

            fig = Figure(figsize=(5, 5),  facecolor='none')
            ax = fig.add_subplot(111, projection='polar', frame_on=False)
            ax.plot(phi, beam_pattern)  # Plot beam pattern            
            ax.set_theta_zero_location('N') # make 0 degrees point up
            ax.set_theta_direction(-1) # increase anticlockwise
            ax.set_thetamin(-90) # only show top half
            ax.set_thetamax(90)
            ax.tick_params(axis='x', colors='white')  # Change x-tick color
            ax.tick_params(axis='y', colors='white')  # Change x-tick color

        
        elif shape =='circular':
            steer_vector = self._array.get_steer_vector()  # Ensure steer_vector is initialized

            # Beam pattern calculation
            antennas_num,radius,beam_angle= self._array.get_array_factor()
            elements_angular_spacing= self._array.get_elements_angles()
            k = self._signal.get_wavenumber()
            phi = np.linspace(-1*np.pi, 1*np.pi, 1000)  # 360 points

            # Compute the beam pattern for all azimuthal angles
            beam_pattern = np.zeros_like(phi)  # Initialize the pattern array

            for i, angle in enumerate(phi):
                # Calculate the pattern for each azimuthal angle
                beam_pattern[i] = np.abs(np.sum([
                    steer_vector[n] * np.exp(1j * k* radius* np.cos(angle - elements_angular_spacing[n]))
                    for n in range(antennas_num)]))

            # Normalize the beam pattern
            
            beam_pattern = 10 * np.log10(beam_pattern / np.max(beam_pattern))

            # Create a polar plot
            fig = Figure(figsize=(7, 5),  facecolor='none')
            ax = fig.add_subplot(111, projection='polar', frame_on=False)
            fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
            
            ax.tick_params(axis='x', colors='white')  # Change x-tick color
            ax.tick_params(axis='y', colors='white')  # Change x-tick color
            ax.set_rmax(5)  # Extend the radial limit to 2 (or adjust as needed)
            ax.set_thetamin(0)  
            ax.set_thetamax(180)
            ax.set_ylim(-40, 0)

            # Rotate 0° to the right and maintain counterclockwise orientation
            ax.set_theta_zero_location("E")  # 0° now at the right (East)
            ax.set_theta_direction(1) 
            # Adjust gridline properties for larger concentric circles
            ax.grid(linewidth=1) 
            ax.plot(phi, beam_pattern, linewidth=1)

        # Embed plot into the PyQt widget
        canvas = FigureCanvas(fig)
        if parent_widget.layout() is None:
            layout = QVBoxLayout(parent_widget)  # Use the provided parent widget
            parent_widget.setLayout(layout)
        else:
            layout=parent_widget.layout()
            # Remove all existing widgets from the layout
            while layout.count() > 0:
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        layout.addWidget(canvas)



    def find_interference_map(self, parent_widget):
        k = self._signal.get_wavenumber()
        lambda0= self._signal.get_wavelength()
        elements_phase, elements_gain = self._array.get_elements_phases_gains()
        geometrical_phases= self._array.get_geometrical_phases()

        azimuth_points = 500  # Number of azimuth points
        range_points = 500  # Number of radial distance points

        # Precompute Cartesian coordinates
        x_coords = np.linspace(-10, 10, range_points)  # X-axis range
        y_coords = np.linspace(0,10, azimuth_points//2)  # Y-axis range
        x_grid, y_grid = np.meshgrid(x_coords, y_coords, indexing='xy')

        # Initialize field map
        field_map = np.zeros((y_coords.size, x_coords.size), dtype=complex)

        # Get array shape and positions
        array_shape = self._array.get_array_shape()
        antennas_num, spacing, _ = self._array.get_array_factor()
        if array_shape == 'linear':
            # Linear array: positions along a straight line
            positions = spacing* np.arange(antennas_num)
            shift = (positions[-1] - positions[0]) / 2
            positions = shift - positions  # Center positions at the origin

            # Compute distances and contributions for linear array
            for i, element_pos in enumerate(positions):
                dx = x_grid - element_pos
                dy = y_grid
                distance_to_point = np.sqrt(dx**2 + dy**2)

                # Compute field contribution
                phase_shift = 1j * k/(2*np.pi) * distance_to_point + geometrical_phases[i] + 1j* elements_phase[i] 
                amplitude = elements_gain[i]
                field_map += amplitude * np.exp(phase_shift)

        elif array_shape == 'circular':
            # Circular array: positions around a circle
            radius, angles = self._array.get_circular_properties()
            positions_x = radius*lambda0 * np.cos(angles)  # X-coordinates of antennas
            positions_y = radius*lambda0* np.sin(angles)  # Y-coordinates of antennas

            # Compute distances and contributions for circular array
            for i in range(antennas_num):
                dx = x_grid - positions_x[i]
                dy = y_grid - positions_y[i]
                distance_to_point = np.sqrt(dx**2 + dy**2)

                # Compute field contribution
                phase_shift = -1j * k * distance_to_point + 1j*elements_phase[i] +  geometrical_phases[i]
                amplitude = elements_gain[i]
                field_map += amplitude * np.exp(phase_shift)

        else:
            raise ValueError(f"Unsupported array shape: {array_shape}")

        # Compute normalized intensity (magnitude squared)
        intensity_map = np.real(field_map) ** 2
        intensity_map = intensity_map / np.max(intensity_map)

        # Create Cartesian plot
        fig = Figure(figsize=(7, 5), facecolor='none')
        ax = fig.add_subplot(111)
        # Plot the interference map
        im = ax.pcolormesh(x_grid, y_grid, intensity_map, shading='auto', cmap='viridis',) 
        ax.tick_params(axis='x', colors='white')  # Change x-tick color
        ax.tick_params(axis='y', colors='white')  # Change x-tick color
        

        # Plot antenna positions
        if array_shape == 'linear':
            ax.scatter(positions, np.zeros_like(positions), color='red', marker='o', label='Antennas')
        elif array_shape == 'circular':
            ax.scatter(positions_x, positions_y, color='red', marker='o', label='Antennas')

        # Label and format the plot
        ax.set_xlabel("X Position (m)", color='white')
        ax.set_ylabel("Y Position (m)",  color='white')
        #ax.set_aspect('equal', adjustable='box')  # Keep correct proportions
        ax.legend()

        # Add colorbar
        cbar= fig.colorbar(im, ax=ax, label="Normalized Intensity")
        cbar.ax.tick_params(colors='white')
        cbar.ax.yaxis.label.set_color('white')


        # Embed the plot into the parent widget
        canvas = FigureCanvas(fig)
        if parent_widget.layout() is None:
            layout = QVBoxLayout(parent_widget)
            parent_widget.setLayout(layout)
        else:
            layout = parent_widget.layout()
            # Clear the layout
            while layout.count() > 0:
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        layout.addWidget(canvas)


    # def plot_recieved_signal(self, parent_widget): #after delays and sum (conventional beamforming)
    #     fig = Figure(figsize=(8, 4), facecolor='none')
    #     ax = fig.add_subplot(111)
    #     recieved_signal= self.apply_signal_to_array('R')
    #     for element_num in range(recieved_signal.shape[0]):
    #         ax.plot(np.asarray(recieved_signal[element_num,:]).squeeze().real[0:200], label=f'Antenna{element_num}')
    #     ax.legend()
    #     ax.set_title("Plot of first 200 samples of the signal recieved by each antenna")
    #     ax.set_xlabel("time")
    #     ax.set_ylabel("amplitude")
    #     ax.tick_params(axis='x', colors='white')  # Change x-tick color
    #     ax.tick_params(axis='y', colors='white')  # Change x-tick color
    #     # Embed the plot into the parent widget
    #     canvas = FigureCanvas(fig)
    #     if parent_widget.layout() is None:
    #         layout = QVBoxLayout(parent_widget)
    #         parent_widget.setLayout(layout)
    #     else:
    #         layout = parent_widget.layout()
    #         # Clear the layout
    #         while layout.count() > 0:
    #             item = layout.takeAt(0)
    #             widget = item.widget()
    #             if widget is not None:
    #                 widget.deleteLater()

    #     layout.addWidget(canvas)

    def plot_towers_interference_map(self, parent_widget): 
        wavelength=3e8/1e9
        k= 1/(wavelength)
        spacing=10 #meters
        antennas_num=2
        beam_angle=np.radians(0)
        geometry_phases = -1j* spacing/ wavelength * np.arange(antennas_num) * np.sin(beam_angle)
        # Precompute Cartesian coordinates
        x_coords = np.linspace(-10, 10, 500)  # X-axis range
        y_coords = np.linspace(0,10, 250)  # Y-axis range
        x_grid, y_grid = np.meshgrid(x_coords, y_coords, indexing='xy')

        # Initialize field map
        field_map = np.zeros((y_coords.size, x_coords.size), dtype=complex)
        
        # Linear array: positions along a straight line
        positions = spacing * np.arange(antennas_num)
        shift = (positions[-1] - positions[0]) / 2
        positions = shift - positions  # Center positions at the origin

        # Compute distances and contributions for linear array
        for i, element_pos in enumerate(positions):
            dx = x_grid - element_pos
            dy = y_grid
            distance_to_point = np.sqrt(dx**2 + dy**2)

            # Compute field contribution
            phase_shift = 1j * k * distance_to_point + geometry_phases[i] 
            field_map += np.exp(phase_shift)

         # Compute normalized intensity (magnitude squared)
        intensity_map = np.real(field_map) ** 2
        intensity_map /= np.max(intensity_map)

        # Create Cartesian plot
        fig = Figure(figsize=(7, 5), facecolor='none')
        ax = fig.add_subplot(111)
        # Plot the interference map
        im = ax.pcolormesh(x_grid, y_grid, intensity_map, shading='auto', cmap='viridis',) 
        ax.tick_params(axis='x', colors='white')  # Change x-tick color
        ax.tick_params(axis='y', colors='white')  # Change x-tick color
        

        # Plot antenna positions
        ax.scatter(positions, np.zeros_like(positions), color='red', marker='o', label='Antennas')
       
        # Label and format the plot
        ax.set_xlabel("X Position (m)", color='white')
        ax.set_ylabel("Y Position (m)",  color='white')
        ax.set_title("Towers Interference Map", color='white')
        ax.legend()

        # Add colorbar
        cbar= fig.colorbar(im, ax=ax, label="Normalized Intensity")
        cbar.ax.tick_params(colors='white')
        cbar.ax.yaxis.label.set_color('white')


        # Embed the plot into the parent widget
        canvas = FigureCanvas(fig)
        if parent_widget.layout() is None:
            layout = QVBoxLayout(parent_widget)
            parent_widget.setLayout(layout)
        else:
            layout = parent_widget.layout()
            # Clear the layout
            while layout.count() > 0:
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        layout.addWidget(canvas)