from PyQt5.QtWidgets import QMainWindow, QButtonGroup, QProgressBar ,QMessageBox, QApplication,QPushButton,QListWidget, QDoubleSpinBox ,QSpinBox, QWidget, QLabel ,  QSlider, QRadioButton, QComboBox, QTableWidget, QTableWidgetItem, QCheckBox,QMenu,QTextEdit, QDialog, QFileDialog, QInputDialog, QSizePolicy,QScrollArea,QVBoxLayout,QHBoxLayout
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer

import sys
import os
from Browse import Browse
from OutputViewer import OutputViewer
from InputViewer import InputViewer , SelectableLabel
import logging
from Mixer import Mixer
from MixingWorker import MixingWorker
from SignalEmitter import SignalEmitter
from SignalEmitter import global_signal_emitter
from SignalEmitter import global_signal_emitter_2


class MainWindow2(QMainWindow):
    def __init__(self):
        super(MainWindow2, self).__init__()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        loadUi("../MainWindow.ui", self)

        logging.basicConfig(
            filename='app.log',           # Log file name
            level=logging.DEBUG,          # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format='%(asctime)s - %(levelname)s - %(message)s'  # Log message format
                )

        self.mixer=Mixer()
        self.progressbar= self.findChild(QProgressBar, "progressBar" )
        self.output1 = self.findChild(QWidget, "output1")
        self.output2 = self.findChild(QWidget, "output2")
        self.mixButton = self.findChild(QPushButton, "mixer")        
        self.RadioButton1 = self.findChild(QRadioButton, "radioButton1")
        self.RadioButton2 = self.findChild(QRadioButton, "radioButton2")
        self.isInner_radiobutton=self.findChild(QRadioButton,"insideRegion")
        self.isOuter_radiobutton=self.findChild(QRadioButton,"outsideRegion")
        self.image1 = self.findChild(QWidget, "image1")
        self.image2 = self.findChild(QWidget, "image2")
        self.image3 = self.findChild(QWidget, "image3")
        self.image4 = self.findChild(QWidget, "image4")

        self.RadioButton1.setChecked(True)


        # Create Button Groups
        self.group1 = QButtonGroup(self)  
        self.group2 = QButtonGroup(self)  
        self.signal_emit=global_signal_emitter
        self.signal_emit_2=global_signal_emitter_2

        # Add Buttons to Groups
        self.group1.addButton(self.RadioButton1)
        self.group1.addButton(self.RadioButton2)
        
        self.group2.addButton(self.isInner_radiobutton)
        self.group2.addButton(self.isOuter_radiobutton)

        self.images_widgets=[self.image1,self.image2,self.image3,self.image4]
        
        self.fft_widget1 = self.findChild(QWidget, "component_image1")
        self.fft_widget2 = self.findChild(QWidget, "component_image2")
        self.fft_widget3 = self.findChild(QWidget, "component_image3")
        self.fft_widget4 = self.findChild(QWidget, "component_image4")

        self.fft_widgets=[self.fft_widget1,self.fft_widget2,self.fft_widget3,self.fft_widget4]

        self.image1_combobox=self.findChild(QComboBox, "combo1")
        self.image2_combobox=self.findChild(QComboBox, "combo2")
        self.image3_combobox=self.findChild(QComboBox, "combo3")
        self.image4_combobox=self.findChild(QComboBox, "combo4")
        self.isInner_radiobutton.setChecked(True)
        self.deselect_region= self.findChild(QPushButton,"Deselect")

        self.isInner_radiobutton.clicked.connect(self.trigger_mixing)
        self.isOuter_radiobutton.clicked.connect(self.trigger_mixing)

        self.signal_emit.function_done.connect(self.trigger_mixing)
        self.signal_emit_2.function_done.connect(self.trigger_mixing)


        self.image1_slider=self.findChild(QSlider,"Slider_weight1")
        self.image2_slider=self.findChild(QSlider,"Slider_weight2")
        self.image3_slider=self.findChild(QSlider,"Slider_weight3")
        self.image4_slider=self.findChild(QSlider,"Slider_weight4")

        self.image1_slider.setRange(0,100)
        self.image1_slider.setSingleStep(10)
        self.image1_slider.setValue(100)
        self.slider1_label = self.findChild(QLabel, 'label_7')
        self.image1_slider.valueChanged.connect(self. update_slider_val)
        self.image1_slider.valueChanged.connect(self.trigger_mixing)

        self.image2_slider.setRange(0,100)
        self.image2_slider.setSingleStep(10)
        self.image2_slider.setValue(100)
        self.slider2_label = self.findChild(QLabel, 'label_11')
        self.image2_slider.valueChanged.connect(self. update_slider_val)
        self.image2_slider.valueChanged.connect(self.trigger_mixing)



        self.image3_slider.setRange(0,100)
        self.image3_slider.setSingleStep(10)
        self.image3_slider.setValue(100)
        self.slider3_label = self.findChild(QLabel, 'label_9')
        self.image3_slider.valueChanged.connect(self. update_slider_val)
        self.image3_slider.valueChanged.connect(self.trigger_mixing)

        self.image4_slider.setRange(0,100)
        self.image4_slider.setSingleStep(10)
        self.image4_slider.setValue(100)
        self.slider4_label = self.findChild(QLabel, 'label_13')
        self.image4_slider.valueChanged.connect(self.trigger_mixing)
        self.image4_slider.valueChanged.connect(self. update_slider_val)
        self.input_viewer = InputViewer()
        self.input_viewer.set_image_fft_widgets(self.images_widgets,self.fft_widgets) 
        self.deselect_region.clicked.connect(self.clear_region) 
        
        # self.input_viewer.selectRegion(self.input_viewer.images,self.input_viewer.labels)
        self.isInner_radiobutton.clicked.connect(self.inner_region_state)
        self.isOuter_radiobutton.clicked.connect(self.outer_region_state)
        self.deselect_region.clicked.connect(self.full_region_state)

        self.image1_slider.valueChanged.connect(lambda: self.update_componant1_weight(0))
        self.image2_slider.valueChanged.connect(lambda: self.update_componant2_weight(1))
        self.image3_slider.valueChanged.connect(lambda: self.update_componant3_weight(2))
        self.image4_slider.valueChanged.connect(lambda: self.update_componant4_weight(3))

        self.input_image1 = Browse(self.image1,0,self.input_viewer)
        self.input_image2 = Browse(self.image2,1,self.input_viewer)
        self.input_image3 = Browse(self.image3,2,self.input_viewer)
        self.input_image4 = Browse(self.image4,3,self.input_viewer)



        self.input_image1.set_image()
        self.input_image2.set_image()
        self.input_image3.set_image()
        self.input_image4.set_image()

        self.image1_combobox.currentIndexChanged.connect(self.trigger_mixing)
        self.image2_combobox.currentIndexChanged.connect(self.trigger_mixing)
        self.image3_combobox.currentIndexChanged.connect(self.trigger_mixing)
        self.image4_combobox.currentIndexChanged.connect(self.trigger_mixing)

        
        self.image1_combobox.currentIndexChanged.connect(
            lambda index: self.on_combobox_change(self.input_viewer.image_paths[0], 0, self.input_image1._is_grey, index)
        )

        self.image2_combobox.currentIndexChanged.connect(
            lambda index: self.on_combobox_change(self.input_viewer.image_paths[1], 1, self.input_image2._is_grey, index)
        )
        self.image3_combobox.currentIndexChanged.connect(
            lambda index: self.on_combobox_change(self.input_viewer.image_paths[2], 2, self.input_image3._is_grey, index)
        )
        self.image4_combobox.currentIndexChanged.connect(
            lambda index: self.on_combobox_change(self.input_viewer.image_paths[3], 3, self.input_image4._is_grey, index)
        )



        


        self.output_viewer = OutputViewer(self.output1, self.output2, self.RadioButton1, self.RadioButton2, self.progressbar)
                
        self.mixing_timer = QTimer()
        self.mixing_timer.setSingleShot(True)
        self.output_viewer = OutputViewer(self.output1, self.output2, self.RadioButton1, self.RadioButton2, self.progressbar)
        self.mixing_timer.timeout.connect(self.start_mixing)
        self.mixButton.clicked.connect(self.start_mixing)
        self.RadioButton1.clicked.connect(self.trigger_mixing)
        self.RadioButton2.clicked.connect(self.trigger_mixing)

        self.worker = None
        self.mixButton.clicked.connect(self.start_mixing)



    def update_slider_val(self):
      value=self.image1_slider.value()
      self.slider1_label.setText(f"{value}% ")
      value=self.image2_slider.value()
      self.slider2_label.setText(f"{value}% ")
      value=self.image3_slider.value()
      self.slider3_label.setText(f"{value}% ")
      value=self.image4_slider.value()
      self.slider4_label.setText(f"{value}% ")


    def on_combobox_change(self, input_image, image_num,is_grey, index):
     """Handle combo box changes efficiently."""
     self.input_viewer.displayImage(input_image, image_num, is_grey, index)
     self.trigger_mixing()  # Trigger mixing only after updating the displayed image

    def clear_region(self):
        self.input_viewer.clearRectangle()
        self.isInner_radiobutton.setChecked(False)
        self.isOuter_radiobutton.setChecked(False)
        self.trigger_mixing()
    def trigger_mixing(self):
        """Trigger the mixing process with debouncing."""
        if not self.mixing_timer.isActive():
         self.mixing_timer.start(10) 
    def closeEvent(self, event):
        if self.worker is not None:
            self.worker.stop()
            self.worker.wait()
        event.accept()

        
    def update_componant1_weight(self,image_num):
        self.input_viewer.set_components_weights(image_num,self.image1_slider.value())
        print(self.input_viewer.fft_components[image_num][1].shape)
        self.trigger_mixing() 

    def update_componant2_weight(self,image_num):
        self.input_viewer.set_components_weights(image_num,self.image2_slider.value())
        self.trigger_mixing() 
    def update_componant3_weight(self,image_num):
        self.input_viewer.set_components_weights(image_num,self.image3_slider.value())
        self.trigger_mixing() 
    def update_componant4_weight(self,image_num):
        self.input_viewer.set_components_weights(image_num,self.image4_slider.value())
        self.trigger_mixing() 


    def inner_region_state(self):
        self.input_viewer.isInner=True
        self.input_viewer.useFullRegion=False
        self.trigger_mixing()
    def outer_region_state(self):
        self.input_viewer.isInner=False
        self.input_viewer.useFullRegion=False
        self.trigger_mixing()
    def full_region_state(self):
        self.input_viewer.useFullRegion=True    
        self.isInner_radiobutton.setChecked(False)
        self.isOuter_radiobutton.setChecked(False)    
        self.trigger_mixing()
    def start_mixing(self):
        if self.worker is not None:
            self.worker.stop()
            self.worker.wait()

        self.worker = MixingWorker(self.mixer, self.input_viewer)
        self.worker.progress.connect(self.output_viewer.loading)
        self.worker.finished.connect(self.display_output)
        self.worker.start()

    def display_output(self,mixed_image):
        self.output_viewer.DisplayOutput(mixed_image)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow2()
    window.show()
    window.showMaximized()
    sys.exit(app.exec_())        