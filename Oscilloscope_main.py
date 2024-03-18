import random
import sys
import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import( QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox, 
                QPushButton, QLabel, QHBoxLayout, QLineEdit, QSlider, QFileDialog,QStyle,
                QSpacerItem, QSizePolicy)
from pathlib import Path
from datetime import datetime


from oscilloscope3 import Ui_MainWindow
from data_acquire_v2 import Thread



class MainWindow( QMainWindow,Ui_MainWindow):
    def __init__(self):
        super().__init__()       
        self.setupUi(self)  

        self.thread = Thread()
        self.thread.start()  # <2>
        self.thread.result.connect(self.update_plot)
        self.thread.finished.connect(self.thread_finished)
        self.widget.result.connect(self.voltscale_dial_update)
        print(
            self.thread,
            self.thread.isRunning(),
            self.thread.isFinished(),
        )

        self.statistics_timer = QTimer()
        self.statistics_timer.setInterval(500)
        self.statistics_timer.timeout.connect(self.statistics_update)
        self.statistics_timer.start()

        self.led_list=(self.ch1_led,self.ch2_led,self.ch3_led,self.ch4_led,
                         self.ch5_led,self.ch6_led,self.ch7_led,self.ch8_led)
        self.ch_btn_list=(self.ch1_btn,self.ch2_btn,self.ch3_btn,self.ch4_btn,self.ch5_btn,
                          self.ch6_btn,self.ch7_btn,self.ch8_btn)
        
        self.voltscale_value=50
        self.bias_value=np.array([0, 0 ,0 ,0 ,0 ,0 ,0 ,0])
        
        self.last_pressed_ch_btn=1
        self.input_ch_selected=False
        self.com_port_msg_flag=False
        self.signals_availability=False

        self.ch1_btn_checked=True
        self.ch2_btn_checked=False
        self.ch3_btn_checked=False
        self.ch4_btn_checked=False
        self.ch5_btn_checked=False
        self.ch6_btn_checked=False
        self.ch7_btn_checked=False
        self.ch8_btn_checked=False 

        self.Freq_graph=False
        self.Freq_button.clicked.connect(self.Freq_button_clicked) 
        self.Time_button.clicked.connect(self.Time_button_clicked)
        self.xy_btn.clicked.connect(self.xy_button_clicked)
        self.bar_btn.clicked.connect(self.bar_button_clicked)
        


        self.ch1_btn.clicked.connect(self.ch1_btn_clicked)
        self.ch2_btn.clicked.connect(self.ch2_btn_clicked)
        self.ch3_btn.clicked.connect(self.ch3_btn_clicked)
        self.ch4_btn.clicked.connect(self.ch4_btn_clicked)
        self.ch5_btn.clicked.connect(self.ch5_btn_clicked)
        self.ch6_btn.clicked.connect(self.ch6_btn_clicked)
        self.ch7_btn.clicked.connect(self.ch7_btn_clicked)
        self.ch8_btn.clicked.connect(self.ch8_btn_clicked)
        self.display_mode.currentIndexChanged.connect(self.display_mode_changed)
        

        self.save_btn.clicked.connect(self.save_btn_clicked)
        self.print_btn.clicked.connect(self.print_btn_clicked)

       

        # self.rms_btn.clicked.connect(self.rms_btn_clicked)
        # self.max_btn.clicked.connect(self.max_btn_clicked)
        # self.min_btn.clicked.connect(self.min_btn_clicked)
        # self.ppk_btn.clicked.connect(self.ppk_btn_clicked)

        #self.voltscale_dial.valueChanged.connect(self.voltscale_dial_update)
        self.timescale_dial.valueChanged.connect(self.timescale_dial_update)
        self.bias_dial.valueChanged.connect(self.bias_dial_update)
        self.trigger_dial.valueChanged.connect(self.trigger_dial_update)
        self.trigger_level_dial.valueChanged.connect(self.trigger_level_update)




        self.graph_disp.showGrid(x=True, y=True)
        self.graph_disp.addLegend()
          # Disable auto-scaling
        self.graph_disp.getViewBox().setAutoPan(x=False, y=False)  # Disable auto-panning
        self.graph_disp.getViewBox().setAutoVisible(y=False)  # Disable auto-visible


       # self.graph_disp.setLabel('left', 'Amplitude', units='dB')
       # self.graph_disp.setLabel('bottom', 'Frequency', units='Hz')
        #self.graph_disp.setXRange(20, 20000, padding=0)
        self.pen_color1 = (64, 255, 0)# yellowish 
        self.pen_color2 = (255, 128, 0)# orange  
        self.pen_color3 = (255, 255, 0)# yellow 
        self.pen_color4 = (0, 255, 255)# light blue 
        self.pen_color5 = (255, 0, 255) # pink 
        self.pen_color6 = (255, 51, 0)  # red
        self.pen_color7 = (0, 85, 255) # blue
        self.pen_color8 = ( 143, 0, 255)  # violet

        self.curve0 = self.graph_disp.plot()
        self.curve1 = self.graph_disp.plot(pen=self.pen_color1) # this is the plot data handle
        self.curve2 = self.graph_disp.plot(pen=self.pen_color2)
        self.curve3 = self.graph_disp.plot(pen=self.pen_color3)
        self.curve4 = self.graph_disp.plot(pen=self.pen_color4)
        self.curve5 = self.graph_disp.plot(pen=self.pen_color5)
        self.curve6 = self.graph_disp.plot(pen=self.pen_color6)
        self.curve7 = self.graph_disp.plot(pen=self.pen_color7)
        self.curve8 = self.graph_disp.plot(pen=self.pen_color8)
        self.curve9 = self.graph_disp.plot(pen='w')
     

        self.text_rms = pg.TextItem(color=(255, 0, 0))
        self.graph_disp.addItem(self.text_rms)
        self.text_rms.setPos(2, 12)

        self.arrow = pg.ArrowItem(angle=0, tipAngle=45, headLen=10, tailLen=10, tailWidth=5, pen={'color': 'g', 'width': 1})
        self.arrow.setBrush(pg.mkBrush('g'))
        self.arrow.setPos(0, 5)
        self.graph_disp.addItem(self.arrow)

        self.barItems = []
        for i in range(8):
            bar = pg.BarGraphItem(x=[i], height=[0], width=0.5, brush='b')  # Initial bar height is 0
            self.graph_disp.addItem(bar)
            self.barItems.append(bar)

  



        self.ch1_btn.setChecked(True)
        self.ch1_btn_clicked(True)

    def display_mode_changed(self,i):
        text=self.display_mode.itemText(i)
        if text=="Chart":
            self.thread.chart_mode=True
            self.thread.scope_mode=False

        else:
            self.thread.chart_mode=False
            self.thread.scope_mode=True
    
        
    

    def print_btn_clicked(self):
       
        exporter = pg.exporters.ImageExporter(self.graph_disp.plotItem)
        self.print_file_name ="IM"+ datetime.now().strftime("%Y%m%d%H%M%S")+".png"
        self.msg_disp.appendPlainText("print btn clicked")
            # set export parameters if needed
            #exporter.parameters()['width'] = 100   # (note this also affects height parameter)
            # save to file
        exporter.export(self.print_file_name )
        print("Image exported")

    def trigger_level_update(self,value):
        self.thread.trigger_level=value
        self.arrow.setPos(0,int(value/100))
        


    def trigger_dial_update(self,value):
        self.thread.trigger_source=value


    def bias_dial_update(self,value):
        self.bias_value[self.last_pressed_ch_btn-1]=value

    def voltscale_dial_update(self,result):
        #print(result)
        result=int((result-self.widget.guage_start_angle)/(self.widget.guage_end_angle-self.widget.guage_start_angle)*100)
        #print(result)
        self.voltscale_value=result

    def timescale_dial_update(self,value):
        self.thread.timescale_value=value
          

  

    def statistics_update(self):
        
        if self.signals_availability:            
            signals=self.signals
            match self.last_pressed_ch_btn:
                case 1:
                    sig_rms = np.sqrt(np.mean(np.square(signals[0])))
                    sig_max=np.max(signals[0])
                    sig_min=np.min(signals[0])
                    sig_ppk = sig_max - sig_min
                    sig_mean=np.mean(signals[0])

                case 2:
                    sig_rms = np.sqrt(np.mean(np.square(signals[1])))
                    sig_max=np.max(signals[1])
                    sig_min=np.min(signals[1])
                    sig_ppk = sig_max - sig_min
                    sig_mean=np.mean(signals[1])

                case 3:
                    sig_rms = np.sqrt(np.mean(np.square(signals[2])))
                    sig_max=np.max(signals[2])
                    sig_min=np.min(signals[2])
                    sig_ppk = sig_max - sig_min
                    sig_mean=np.mean(signals[2])

                case 4:
                    sig_rms = np.sqrt(np.mean(np.square(signals[3])))
                    sig_max=np.max(signals[3])
                    sig_min=np.min(signals[3])
                    sig_ppk = sig_max - sig_min
                    sig_mean=np.mean(signals[3])

                case 5:
                    sig_rms = np.sqrt(np.mean(np.square(signals[4])))
                    sig_max=np.max(signals[4])
                    sig_min=np.min(signals[4])
                    sig_ppk = sig_max - sig_min
                    sig_mean=np.mean(signals[4])

                case 6:
                    sig_rms = np.sqrt(np.mean(np.square(signals[5])))
                    sig_max=np.max(signals[5])
                    sig_min=np.min(signals[5])
                    sig_ppk = sig_max - sig_min
                    sig_mean=np.mean(signals[5])

                case 7:
                    sig_rms = np.sqrt(np.mean(np.square(signals[6])))
                    sig_max=np.max(signals[6])
                    sig_min=np.min(signals[6])
                    sig_ppk = sig_max - sig_min
                    sig_mean=np.mean(signals[6])

                case 8:
                    sig_rms = np.sqrt(np.mean(np.square(signals[7])))
                    sig_max=np.max(signals[7])
                    sig_min=np.min(signals[7])
                    sig_ppk = sig_max - sig_min
                    sig_mean=np.mean(signals[7])

                case _:
                    sig_rms = np.sqrt(np.mean(np.square(signals[0])))
                    sig_max=np.max(signals[0])
                    sig_min=np.min(signals[0])
                    sig_ppk = sig_max - sig_min
                    sig_mean=np.mean(signals[0])      

                    
            #self.rms_disp.setText((f"RMS: {sig_rms:.2f}"))      
            #self.max_disp.setText((f"Max: {sig_max:.2f}"))
            #self.min_disp.setText((f"Min: {sig_min:.2f}"))
            #self.ppk_disp.setText((f"PPk: {sig_ppk:.2f}"))
            #self.avg_disp.setText((f"Avg: {sig_mean:.2f}"))
            if self.Time_button.isChecked():
                new_text = f"CH{self.last_pressed_ch_btn}-"+ f"RMS: {sig_rms:.2f}," + f"Max: {sig_max:.2f},"+f"Min: {sig_min:.2f},"+f"Avg: {sig_mean:.2f}" # Example of dynamically changing text
            else:
                new_text=" "

            self.text_rms.setText(new_text)
            # self.text_max.setText(f"Max: {sig_max:.2f}")
            # self.text_min.setText(f"Min: {sig_min:.2f}")
            # self.text_avg.setText(f"Avg: {sig_mean:.2f}")

            
               
     


           
    def save_btn_clicked(self,checked):
        if checked:
            self.thread.save_data=True
            self.msg_disp.appendPlainText("Started saving signals")
            #print('Save btn clicked')
        else:
            self.thread.save_data=False
            self.msg_disp.appendPlainText("Stopped saving signals")

    

    def Freq_button_clicked(self, checked):
        if checked:
            self.Freq_graph=True
            self.graph_disp.setYRange(0,10 ,padding=0)
            self.Time_button.setChecked(False)
            self.xy_btn.setChecked(False)
            self.bar_btn.setChecked(False)
            #self.update_led()
            self.msg_disp.appendPlainText("Frequency btn checked")
            
        else:
            self.Freq_graph=False
            self.graph_disp.setYRange(-1,11 ,padding=0)
            self.msg_disp.appendPlainText("Frequency btn unchecked")

    def Time_button_clicked(self, checked):
        if checked:
            self.Freq_graph=False
            self.Freq_button.setChecked(False)
            self.xy_btn.setChecked(False)
            self.bar_btn.setChecked(False)
            self.graph_disp.setYRange(-1 ,11,padding=0)
            self.msg_disp.appendPlainText("Time btn checked")
        else:
            self.msg_disp.appendPlainText("Time btn uchecked")


    def xy_button_clicked(self, checked):
        if checked:            
            self.Freq_button.setChecked(False)
            self.bar_btn.setChecked(False)
            self.Time_button.setChecked(False)            
            self.msg_disp.appendPlainText("xy btn checked")
        else:
            self.msg_disp.appendPlainText("xy btn uchecked")

    def bar_button_clicked(self, checked):
        if checked:            
            self.Freq_button.setChecked(False)
            self.xy_btn.setChecked(False)
            self.Time_button.setChecked(False)            
            self.msg_disp.appendPlainText("bar btn checked")
        else:
            self.msg_disp.appendPlainText("bar btn uchecked")

    
    
       
    def ch1_btn_clicked(self, checked):
        if checked:
            self.ch1_btn_checked=True
            self.prev_pressed_ch_btn=self.last_pressed_ch_btn
            self.last_pressed_ch_btn=1            
            #self.update_led()
            self.ch1_led.setStyleSheet("background:rgb(64, 255, 0);")
            self.input_ch_selected=True
            self.msg_disp.appendPlainText("Ch1 btn checked")
            
        else:
            self.ch1_btn_checked=False
            self.ch1_led.setStyleSheet("background:white;")
            self.msg_disp.appendPlainText("Ch1 btn unchecked")
           

    def ch2_btn_clicked(self, checked):
        if checked:
            self.ch2_btn_checked=True
            self.prev_pressed_ch_btn=self.last_pressed_ch_btn
            self.last_pressed_ch_btn=2
            #self.update_led()
            self.ch2_led.setStyleSheet("background:rgb(255, 128, 0);")
            self.input_ch_selected=True   
            self.msg_disp.appendPlainText("Ch2 btn checked")    
         

            
        else:
            self.ch2_btn_checked=False
            self.ch2_led.setStyleSheet("background:white;")
            self.msg_disp.appendPlainText("Ch1 btn unchecked")

    def ch3_btn_clicked(self, checked):
        if checked:
            self.ch3_btn_checked=True
            self.prev_pressed_ch_btn=self.last_pressed_ch_btn
            self.last_pressed_ch_btn=3
            #self.update_led()
            self.ch3_led.setStyleSheet("background:rgb(255, 255, 0);")
            self.input_ch_selected=True
            self.msg_disp.appendPlainText("Ch3 btn checked")
            
        else:
            self.ch3_btn_checked=False
            self.ch3_led.setStyleSheet("background:white;")
            self.msg_disp.appendPlainText("Ch3 btn unchecked")

    def ch4_btn_clicked(self, checked):
        if checked:
            self.ch4_btn_checked=True
            self.prev_pressed_ch_btn=self.last_pressed_ch_btn
            self.last_pressed_ch_btn=4
            #self.update_led()
            self.ch4_led.setStyleSheet("background:rgb(0, 255, 255);")
            self.input_ch_selected=True
            self.msg_disp.appendPlainText("Ch4 btn checked")
            
        else:
            self.ch4_btn_checked=False
            self.ch4_led.setStyleSheet("background:white;")
            self.msg_disp.appendPlainText("Ch4 btn unchecked")

    def ch5_btn_clicked(self, checked):
        if checked:
            self.ch5_btn_checked=True
            self.prev_pressed_ch_btn=self.last_pressed_ch_btn
            self.last_pressed_ch_btn=5
            #self.update_led()
            self.ch5_led.setStyleSheet("background:rgb(255, 0, 255);")
            self.input_ch_selected=True
            self.msg_disp.appendPlainText("Ch5 btn checked")
        

        else:
            self.ch5_btn_checked=False
            self.ch5_led.setStyleSheet("background:white;")
            self.msg_disp.appendPlainText("Ch5 btn unchecked")

    def ch6_btn_clicked(self, checked):
        if checked:
            self.ch6_btn_checked=True  
            self.prev_pressed_ch_btn=self.last_pressed_ch_btn
            self.last_pressed_ch_btn=6   
            #self.update_led()     
            self.ch6_led.setStyleSheet("background:rgb(255, 51, 0) ;")
            self.input_ch_selected=True
            self.msg_disp.appendPlainText("Ch6 btn checked")

        else:
            self.ch6_btn_checked=False
            self.ch6_led.setStyleSheet("background:white;")
            self.msg_disp.appendPlainText("Ch6 btn unchecked")

    def ch7_btn_clicked(self, checked):
        if checked:
            self.ch7_btn_checked=True  
            self.prev_pressed_ch_btn=self.last_pressed_ch_btn
            self.last_pressed_ch_btn=7  
            #self.update_led()  
            self.ch7_led.setStyleSheet("background:rgb(0, 85, 255);")    
            self.input_ch_selected=True  
            self.msg_disp.appendPlainText("Ch7 btn checked")
        else:
            self.ch7_btn_checked=False
            self.ch7_led.setStyleSheet("background:white;")
            self.msg_disp.appendPlainText("Ch7 btn unchecked")

    def ch8_btn_clicked(self, checked):
        if checked:
            self.ch8_btn_checked=True 
            self.prev_pressed_ch_btn=self.last_pressed_ch_btn 
            self.last_pressed_ch_btn=8  
            #self.update_led()
            self.ch8_led.setStyleSheet("background:rgb( 143, 0, 255);")      
            self.input_ch_selected=True  
            self.msg_disp.appendPlainText("Ch8 btn checked")
        else:
            self.ch8_btn_checked=False
            self.ch8_led.setStyleSheet("background:white;")
            self.msg_disp.appendPlainText("Ch8 btn unchecked")

    def update_led(self): 
        
        btn=self.ch_btn_list[self.prev_pressed_ch_btn-1]
        if btn.isChecked():
            led=self.led_list[self.prev_pressed_ch_btn-1]
            led.setStyleSheet("background:orange;")

        if self.Freq_button.isChecked():
            for led in self.led_list:
                led.setStyleSheet("background:white;")

        led=self.led_list[self.last_pressed_ch_btn-1]
        led.setStyleSheet("background:#00ff00;")   
   



         
    def update_plot(self,result):
        
        if self.thread.com_error:
            e1,e2=result
            self.msg_disp.setPlainText(f"Error opening serial port: {str(e1)}")

        if self.com_port_msg_flag==False and self.thread.com_error==False:
            self.msg_disp.appendPlainText("Com Port opened successfully")
            self.com_port_msg_flag=True
        
       

        if self.input_ch_selected and (not self.thread.com_error):

            signals_raw, timex= result            
            signals=np.multiply(signals_raw,10/1023*self.voltscale_value/50) # for display
            self.signals_availability=True
            self.signals=signals # for stat computations
            
            
                
            self.curve0.clear()
            self.curve1.clear()
            self.curve2.clear()
            self.curve3.clear()
            self.curve4.clear()
            self.curve5.clear()
            self.curve6.clear()
            self.curve7.clear()
            self.curve8.clear()
            self.curve9.clear()
            self.arrow.hide()

            for i in range(8):
                self.barItems[i].hide()

            if self.Freq_button.isChecked():
                signal=signals[self.last_pressed_ch_btn-1]
                spectrum = np.abs(np.fft.fft(signal)/len(signal))**2
                frequency = np.fft.fftfreq(len(spectrum), 1.0/44100.0)
                mask = frequency > 0
                self.curve0.setData(frequency[mask],spectrum[mask],pen='r')

            elif self.xy_btn.isChecked():
                x=signals[self.prev_pressed_ch_btn-1]
                y=signals[self.last_pressed_ch_btn-1]
                self.curve1.setData(x,y)

            elif self.bar_btn.isChecked():
                #sig1_max=np.max(signals[0])
                # sig2_max=np.max(signals[1])
                # sig3_max=np.max(signals[2])
                # sig4_max=np.max(signals[3])
                # sig5_max=np.max(signals[4])
                # sig6_max=np.max(signals[5])
                # sig7_max=np.max(signals[6])
                # sig8_max=np.max(signals[7])

                # bar = pg.BarGraphItem(x=[1,2,3,4,5,6,7,8], height=[sig1_max,sig2_max,sig3_max,sig4_max,sig5_max,sig6_max,sig7_max,sig8_max], width=0.5, brush='b')  # Initial bar height is 0
                # self.graph_disp.addItem(bar)
       
                for i in range(8):
                    self.barItems[i].show()
                    self.barItems[i].setOpts(height=np.max(signals[i]))
            
            else:

                if self.ch1_btn_checked==True:
                    self.curve1.setData(timex, signals[0]+self.bias_value[0])
                if self.ch2_btn_checked==True: 
                    self.curve2.setData(timex, signals[1]+self.bias_value[1])
                if self.ch3_btn_checked==True:
                    self.curve3.setData(timex, signals[2]+self.bias_value[2])
                if self.ch4_btn_checked==True:
                    self.curve4.setData(timex, signals[3]+self.bias_value[3])
                if self.ch5_btn_checked==True:
                    self.curve5.setData(timex, signals[4]+self.bias_value[4])
                if self.ch6_btn_checked==True:
                    self.curve6.setData(timex, signals[5]+self.bias_value[5])
                if self.ch7_btn_checked==True:
                    self.curve7.setData(timex, signals[6]+self.bias_value[6])
                if self.ch8_btn_checked==True:
                    self.curve8.setData(timex, signals[7]+self.bias_value[7])

                if self.thread.chart_mode:
                    x=[self.thread.frame_index,self.thread.frame_index]
                    y=[0,12]
                    self.curve9.setData(x,y)

                self.graph_disp.setYRange(0,12)
                self.arrow.show()
                
               

            

                 


     

    def thread_finished(self):
        print('Thread finished function  triggerd')
        
        
        
        

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                    "Are you sure to quit?", QMessageBox.StandardButton.Yes |
                    QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            print("thread closing started")
            self.thread.is_running=False
         
            while True:
                if self.thread.isFinished():
                    break
                
            print('successfully closed GUI')       
            event.accept()
        else:

            event.ignore()
           

      


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.setStyleSheet(Path('oscilloscope_style.qss').read_text())
app.exec()