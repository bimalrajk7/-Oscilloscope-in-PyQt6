import sys
from PyQt6.QtWidgets import QApplication, QWidget,QSizePolicy
from PyQt6.QtGui import QMouseEvent, QPainter, QPen, QColor, QFont, QBrush,QConicalGradient
from PyQt6.QtCore import Qt, QPoint, QPointF, QSize, QRectF,pyqtSignal
import math

def rotate(origin, point, angle):
  
    ox, oy = origin
    px, py = point
    angle=angle*3.14159265359/180

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


class ArcWidget(QWidget):    

    result = pyqtSignal(int)

    def __init__(self, parent=None,start_angle=135,end_angle=405):
        super().__init__(parent)

        self.setWindowTitle('Arc with Circular Knob')        
        self.setSizePolicy(
        QSizePolicy.Policy.MinimumExpanding,
        QSizePolicy.Policy.MinimumExpanding,
        )     
      
        #  3 O'Clock position is zero angle , clockwise rotation +ve angle, 6 O Clock 90% , 12 O Clock:-90
        # sign convention shall be maintained
        self.guage_start_angle =start_angle
        self.guage_end_angle= end_angle        
        self.knob_angle = 270 # in degrees
        self.Max_Ribbon_angle=self.guage_end_angle-self.guage_start_angle 
        self.Max_knob_angle=self.guage_end_angle
        self.ribbon_angle =180
        self.padding=20
        self.display_value=self.ribbon_angle
        self.zero_crossing_detected=False

              

    
    def sizeHint(self):
        return QSize(400, 400)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.device_width=painter.device().width()
        self.device_height=painter.device().height()
        self.padding=int(self.device_height*0.1)

        self.arc_center_x=self.device_width//2
        self.arc_center_y=self.device_height//2
        self.arc_radius=min(self.device_width//2,self.device_height//2)-self.padding


       
        pen = QPen(QColor('#8c8c8c'))
        pen_width=int(self.arc_radius*0.2)
        pen.setWidth(pen_width)
        painter.setPen(pen)

        # Define the parameters for the arc
        
        
        #self.arc_radius= self.arc_radius-self.padding

        # negative sign for counter clockwise rotation - drawArc function
        start_angle = -self.guage_start_angle * 16  # angles are specified in 1/16th of a degree
        span_angle = -(self.guage_end_angle- self.guage_start_angle)*16

        # Calculate the top-left corner of the bounding rectangle of the arc
        x = self.arc_center_x -  self.arc_radius
        y = self.arc_center_y -  self.arc_radius

        # Draw the base arc
        painter.drawArc(x, y, 2 *  self.arc_radius, 2 *  self.arc_radius, start_angle, span_angle)

        pen.setColor(QColor('#00ff00'))  # lime
        pen.setWidth(pen_width)
        painter.setPen(pen)

        if self.knob_angle<self.guage_start_angle:
            self.knob_angle=self.guage_start_angle

        if self.knob_angle>self.guage_end_angle:
            self.knob_angle=self.guage_end_angle
        

    

        start_angle=-(self.guage_start_angle)* 16 # max ribbon_angle is limited to 270  
        self.ribbon_angle=self.knob_angle-self.guage_start_angle 
        #print(self.ribbon_angle)    
        span_angle= -int(self.ribbon_angle*16)    
       
        # drawing ribbon arc

             # Create a conical gradient
        # gradient = QConicalGradient(self.width() / 2, self.height() / 2, -45)
        # gradient.setColorAt(0, Qt.GlobalColor.red)
        # gradient.setColorAt(0.5, Qt.GlobalColor.yellow)
        # gradient.setColorAt(1, Qt.GlobalColor.green)
        # painter.setBrush(gradient)

        # arc is a line. Brush is not applicable to line

        painter.drawArc(x, y, 2 *  self.arc_radius, 2 *  self.arc_radius, start_angle, span_angle)
        
          
     
        
        point=(self.arc_center_x+ self.arc_radius,self.arc_center_y )
        origin=(self.arc_center_x,self.arc_center_y )

        # if self.knob_angle<0:
        #     self.knob_angle= 360+self.knob_angle

  

        x,y=rotate(origin,point,self.knob_angle)
        self.x_knob=x
        self.y_knob=y
        
        self.knob_radius=int(self.arc_radius*0.15)

        pen.setColor(QColor('black'))
        pen.setWidth(6)
        painter.setPen(pen)

        brush = QBrush()
        brush.setColor(QColor('red'))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        # draw knob
        painter.drawEllipse(QPointF(self.x_knob, self.y_knob),self.knob_radius,self.knob_radius)

       
        font = QFont()
        font.setFamily("Times")
        font.setBold(True)
        font_size=int(self.arc_radius*0.2)
        #print(font_size)
        font.setPointSize(font_size)
        painter.setFont(font)

        pen.setColor(QColor('#00ff00'))
        painter.setPen(pen)


        rect = QRectF(self.arc_center_x-2*font_size,self.arc_center_y-font_size,4*font_size,2*font_size)
        painter.drawText(rect, Qt.AlignmentFlag.AlignHCenter,str(self.display_value))
        painter.end()
        #print('Paint event called ')
     
    
    def mouse_moving(self,e):
        pos=e.position()
        x=pos.x()
        y=pos.y()

        if (x-self.x_knob)**2+ (y-self.y_knob)**2<=self.knob_radius**2:
            #print(f'Mouse over knob x={x},y={y}')
            angle1=math.atan2(y-self.arc_center_y, x-self.arc_center_x)
            angle1 =math.degrees(angle1)
            #print(f'Angle1 :{angle1}')

            threshold=0.1

            if angle1 < threshold and angle1>-threshold: 
                angle1=threshold

            angle =angle1

            if angle1<0:
                angle =360+angle1         

            
            if self.knob_angle<360 and self.knob_angle>270:
                if angle1>=0:
                    self.zero_crossing_detected=True

            if self.knob_angle>360 and self.knob_angle<450:
                if angle1<=0:
                    self.zero_crossing_detected=False

            if self.zero_crossing_detected:
                angle=angle1+ 360    


            #print(f'Angle :{angle}')
            self.knob_angle=angle              
            self.display_value=int(angle)   
            #self.ribbon_angle=self.knob_angle-self.guage_start_angle
            self.update()
            self.result.emit(int(self.knob_angle))
      
            
            
    def set_knob_angle(self,angle):
        if angle <=self.Max_knob_angle:
            self.knob_angle=angle
        else :
            self.knob_angle=self.Max_knob_angle
        self.update()

    def set_ribbon_angle(self,angle):
        if angle<=self.Max_Ribbon_angle:
            self.ribbon_angle=angle
        else:
            self.ribbon_angle=self.Max_Ribbon_angle
        self.update()
        

    def get_knob_angle(self):
        return(self.knob_angle)
    
    def get_ribbon_angle(self):
        return(self.ribbon_angle)
    
    def set_central_display(self,value):
        self.central_display=value
        self.upate()

    def get_central_display(self):
        return(self.display_value)
    
    def set_widget_parameters(self,knob_angle,ribbon_angle, display_value):
        self.knob_angle=knob_angle
        self.ribbon_angle=ribbon_angle
        self.display_value=display_value

    def mouseMoveEvent(self, e):
        self.mouse_moving(e)
    def mousePressEvent(self, e):
        self.mouse_moving(e)
        
    # def mouseReleaseEvent(self,e):
    #     self.display_value=self.ribbon_angle
    #     self.update()
       


# app = QApplication(sys.argv)
# window = ArcWidget()
# window.setStyleSheet('background-color: black')
# window.show()
# app.exec()
 

