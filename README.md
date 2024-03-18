# -Oscilloscope-in-PyQt6
 Oscilloscope in PyQt6
PC-Oscilloscope-in-PyQt6

Implementation of a PC Oscilloscope which displays Arduino Atmega2560 data
Oscilloscope
Description

This project displays analog data sent from an Arduino ATMEGA 2560.
ATMEGA Program Details

    The ATMEGA program (available in timer_logger_v2) configures a timer interrupt to generate interrupts every 10 milliseconds.
    It utilizes a prescaler of 256 to divide the clock frequency.
    Analog readings are implemented directly by configuring the registers for faster execution.
    Once data is acquired, it's sent to the computer using RS232 serial communication with a baud rate of 500000.

UI Design

    The UI (gui_oscilloscope.ui) is created in Qt Designer (community edition).
    A custom widget (pyqtgraph) is added to the GUI.
    Another custom widget ArcWidget (in arcwidget_v1.py) is added for volt_scale control. This is to provide an example for creating custom widget in pyqt6. It has got control also.	

    The UI file is converted into a Python script using the command: pyuic6 gui_oscilloscope.ui -o oscilloscope3.py.
    The UI_MainWindow class, implementing the UI interface widgets, is contained in this file.
    The MainWindow class in Oscilloscope_main inherits the UI_MainWindow.
    Making layouts in Qt Designer involves using H and V layouts. Set the layout object properties' margins to a minimum of 5px for easier layout manipulation.
    Layout stretch can be adjusted to change the default widget sizes.
    Hardcode widget sizes by setting min and max width and height.

Data Acquisition

    The data acquisition process, including opening and reading the serial port and converting the string into NumPy array, is implemented in data_acquire_v2.py.
    The results are emitted once the operations are completed, with MainWindow displaying the result.
    The array for signals for plotting is created in data_acquire_v2.py, capable of running in scope mode and chart mode (hardcoded for scope mode in the present version).

User Interaction

    Users can select the display source by pressing the "ch" buttons. By default, ch1 in time domain is selected, with additional channels selectable by pressing the buttons.Selected button led indicators will be glowing. 
 
    Statistical parameters of the signal, such as RMS value, Min Max are displayed. This is for the latest selected channel.  The spectrum of the signal can be displayed by selecting the frequency button, and selecting "xy" displays an XY plot. In Bar mode the average max value of all the signals are displayed.
    The "Save" button saves data into the text file "serial_data.txt".
    Amplitude scaling of the signals is linked to the "volts/div" dial.


   The "time/div" dial ajusts the frame size .
   Zero crossing detection is used for generating the trigger in scope mode.Trigger level and trigger source can be selected. Bias can be added to the signals. Filters are also not implemented.

Print
Pressing the print button causes the image to be exported. File name is provided automatically(by date and time)



