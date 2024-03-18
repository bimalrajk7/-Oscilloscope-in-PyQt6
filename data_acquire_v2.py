import pyaudio
import serial
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import( QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox, 
                QPushButton, QLabel, QHBoxLayout, QLineEdit, QSlider, QFileDialog)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, pyqtSlot, Qt
import time
import wave
import sys
import os
from pathlib import Path
from datetime import datetime

# date: 27/04/23
#  specturm_analyzer_v5 is from specturm_analyzer_v4 
#  objective is to improve the appearance of the GUI based on reco_v1 and reco_style.css
#  It is also required to add additional programming to implement save replay etc

class Thread(QThread):
    
    result = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()

 
        

     

    @pyqtSlot()
    def run(self):
        self.is_running = True
        self.invalid_data=False
        self.serial_port_open=False 
        self.com_error=False
        self.save_data=False
        self.chart_mode=True
        self.scope_mode=False



      

        cols=9 # 8 channel
        rows=500 # maximum frame size  
        self.frame_data= np.zeros((rows,cols),dtype=int)
        self.frame_index=0
        self.zero_crossing_detected=False
        self.zero_crossing_index=[]
        self.prev_trigger=0
        self.timescale_value=100
        self.trigger_source=1
        self.trigger_level=500
        

        while not self.serial_port_open:

            #while not self.serial_port_open:
              
            try:
                if self.is_running==False:
                    break

                self.ser = serial.Serial('COM3', baudrate = 500000, timeout=1)
                print("Serial port opened successfully.")
                print("Port name:", self.ser.name)
                print("Baudrate:", self.ser.baudrate)
                print("Timeout:", self.ser.timeout)

                file_name = "serial_data.txt"
                self.data_file =open(file_name, "a") 
                self.serial_port_open=True
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                time.sleep(1)
               # break

        

            except serial.SerialException as e:
                print("An error occurred while opening the serial port:", e)
                #self.msg_text=e
                self.com_error=True
                self.result.emit((e,e))
                time.sleep(1)

            except Exception as e:
                self.com_error=True
                print("An unexpected error occurred:", e)
                #self.msg_text=e
                self.result.emit((e,e))     
                time.sleep(1)             


       
        print("Thread start")  
        self.msg_disp="Serial port opened"
        frames=[]    
        while self.serial_port_open:
            serial_read_successfully=False
            while not serial_read_successfully:              
                try:
                    data1 = self.ser.readline().decode().strip()
                    serial_read_successfully=True 
                except serial.SerialException as e:
                    self.ser.reset_input_buffer()                    
                    print("Serial port error while reading:", e)
                    time.sleep(0.1)
            
            if self.save_data:
                self.data_file.write(data1 + "\n")              
            data_list = data1.split('\t')
            # Convert each item to an integer and store in an array
            data_array=np.asarray(data_list)                    
            self.frame_data[self.frame_index]=data_array
            self.frame_index=self.frame_index+1

            if self.scope_mode:
                threshold=512
                trigger_signal=self.frame_data[self.frame_index-1,self.trigger_source] # index 0 is time, hence ch1 is at index 1
    
                if trigger_signal>self.trigger_level and self.prev_trigger<=self.trigger_level:
                    self.zero_crossing_detected=True
                    self.zero_crossing_index.append(self.frame_index-1)
                # print("zero crossing index:",self.zero_crossing_index)

                else:
                    self.zero_crossing_detected=False

                self.prev_trigger=trigger_signal
                max_frame_length=100
                frame_length=int(max_frame_length*self.timescale_value/100)
                
                if self.frame_index>=frame_length:
                    if self.frame_index>self.zero_crossing_index[0]+frame_length:
                        self.frame_index=0             
                    
                        if self.invalid_data==False:        
                
            # Compute the power spectrum of the signal using the FFT algorithm
                                        
                            
                            signals=self.frame_data[self.zero_crossing_index[0]:self.zero_crossing_index[0]+frame_length,1:9]
                            signals=signals.transpose()                    
                            signal1 =self.frame_data[self.zero_crossing_index[0]:self.zero_crossing_index[0]+frame_length,1]
                            timex=np.arange(0,len(signal1),1)
                        
                            self.zero_crossing_index.clear()
                            #spectrum=np.stack((spectrum1,spectrum2),axis=0)
                            
                            self.result.emit((signals,timex))

            if self.chart_mode:
                
                max_frame_length=500
                frame_length=int(max_frame_length*self.timescale_value/100)
                self.zero_crossing_index.insert(0,0) # when you change over from chart model to scope mode, initial zero crossing index

                if self.frame_index>=frame_length:
                    self.frame_index=0               
                signals=self.frame_data[0:frame_length,1:9]
                signals=signals.transpose() 
                signal1=self.frame_data[0:frame_length,1]
                timex=np.arange(0,len(signal1),1)
                self.result.emit((signals,timex))

 
                
            
            
            if self.is_running==False:
                print(' for loop break triggered')
                break
      
        # normal exit of thread    
        self.break_flag=True
       

        if self.serial_port_open==True:
            self.ser.close()
            self.data_file.close()
     
            print(' Serial port closed')   

        
 