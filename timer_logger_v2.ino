
// Electronoobs youtube channel provides good tutorial about timer interrupt handling
// this code is corrected based on the youtube video 
// Timer Interrupt ISR + Examples | Arduino101 | Set Registers & Modes video title
// This code is tested and found working with 10ms timer, timer_logger_v0 version freeze on 26/12/2023
// version 1 uses direct port (PORTB) control instead of using arduino functions,
// version 2, ADC registers are programmed directly instead of using arduino function, this is to improve the speed and control,
// ADC registers direct control working , ADC noise is high with  low clock prescalar values(2). clk prescalar changed to 16 to reduce noise

// Define the LED pin
#define ledPin 13

// These constants won't change. They're used to give names to the pins used:
const int analogInPin = A0;  // Analog input pin that the potentiometer is attached to
const int analogOutPin = 9; // Analog output pin that the LED is attached to

int sensorValue[16];        // value read from the pot
int outputValue = 0;        // value output to the PWM (analog out)
int counter=0;


// Define timer compare match register value
const int timer1_compare_match=624;
volatile int flag=0;
volatile bool LED_STATE=0;

volatile int led_counter=0;


ISR(TIMER1_COMPA_vect)
// Interrupt Service Routine for compare mode
{
  // Preload timer with compare match value
  if (flag==1)
   Serial.println("Interrupt overflow");   
   
 // TCNT1 = 0;
  //OCR1A = 6249;  

  if (led_counter<10)
    led_counter++;
    else 
    {led_counter=0;
    LED_STATE=!LED_STATE;}
    
  // Write opposite value to LED
  
  //digitalWrite(ledPin, LED_STATE);
  if (LED_STATE)
  PORTB |=B10000000;
  else
  PORTB &=B01111111;

  
  flag=1;
}

void setup()
{
 // Serial.begin(9600);
  Serial.begin(500000);

  
  // Set LED as output
  //pinMode(ledPin, OUTPUT); // PORTB PIN 7 INBUILT LED

   DDRB=B10000000;// PORTB PIN 7 IN OUTPUT MODE
  // Disable all interrupts
  noInterrupts();
  // Initialize Timer1
  TCCR1A = 0;                 // Reset entire TCCR1A to 0 
  TCCR1B = 0;                 // Reset entire TCCR1B to 0
  TCCR1B |= B00000100;        //Set CS12 to 1 so we get prescalar 256  
  TCCR1B|=(1<<WGM12);         // CTC reset counter on compare 
  TIMSK1 |= B00000010;        //Set OCIE1A to 1 so we enable compare match A
  //OCR1A = 6249;              //Finally we set compare register A to this value 
  OCR1A = 624; 
// 16000000/(prescalar*freq)-1
//prescalar is 256 in our case 
//(62500/freq)-1
//for 10 hz frequency 6249

  /*
  TCCR1A = 0;
  TCCR1B = 0;
  // Set timer1_compare_match to the correct compare match register value
  // 256 prescaler & 31246 compare match = 2Hz
  //timer1_compare_match = 31249;
//  timer1_compare_match = 624;// 10ms timer
  // Preload timer with compare match value
  TCNT1 = timer1_compare_match;
  // Set prescaler to 256
  TCCR1B |= (1 << CS12);
  // Enable timer interrupt for compare mode
  TIMSK1 |= (1 << OCIE1A);
  // Enable all interrupts*/

  DIDR0=B11111111; // DIGITAL INPUT DISABLE ON ADC PIN ( FOR LOW POWER)
  DIDR2=B11111111;
             //Bit 7 6 5 4 3 2 1 0
  ADCSRA=B10000100;    //ADEN ADSC ADATE ADIF ADIE ADPS2 ADPS1 ADPS0
             //Initial Value 0 0 0 0 0 0 0 0 LSB[2:0] are prescalar selection, ADC interrupt is disabled
  //ADCSRB   is left in the intial condition , as ADC is not in auto trigger mode, Note Mux 5 is in this register 
  // mux 5 bit has to be set for ADC7-ADC15 inputs 
  
  interrupts();
}



void loop()
{
   for(; ; )
   {if(flag==1)
       break;}
  counter++;

  ADMUX=B01000000; // ADC0, vcc reference 
  ADCSRA|=B01000000; // ADC ON , START CONVERSION
  while(bit_is_set(ADCSRA,ADSC));// wait till the conversion is complete
  sensorValue[0]=ADCL|(ADCH<<8);

  ADMUX=B01000001; // ADC1, vcc reference 
  ADCSRA|=B01000000; // ADC ON , START CONVERSION
  while(bit_is_set(ADCSRA,ADSC));// wait till the conversion is complete
  sensorValue[1]=ADCL|(ADCH<<8);

  ADMUX=B01000010; // ADC2, vcc reference 
  ADCSRA|=B01000000; // ADC ON , START CONVERSION
  while(bit_is_set(ADCSRA,ADSC));// wait till the conversion is complete
  sensorValue[2]=ADCL|(ADCH<<8);

  ADMUX=B01000011; // ADC3, vcc reference 
  ADCSRA|=B01000000; // ADC ON , START CONVERSION
  while(bit_is_set(ADCSRA,ADSC));// wait till the conversion is complete
  sensorValue[3]=ADCL|(ADCH<<8);

  ADMUX=B01000100; // ADC4, vcc reference 
  ADCSRA|=B01000000; // ADC ON , START CONVERSION
  while(bit_is_set(ADCSRA,ADSC));// wait till the conversion is complete
  sensorValue[4]=ADCL|(ADCH<<8);


  ADMUX=B01000101; // ADC5, vcc reference 
  ADCSRA|=B01000000; // ADC ON , START CONVERSION
  while(bit_is_set(ADCSRA,ADSC));// wait till the conversion is complete
  sensorValue[5]=ADCL|(ADCH<<8);

  ADMUX=B01000110; // ADC6, vcc reference 
  ADCSRA|=B01000000; // ADC ON , START CONVERSION
  while(bit_is_set(ADCSRA,ADSC));// wait till the conversion is complete
  sensorValue[6]=ADCL|(ADCH<<8);

  ADMUX=B01000111; // ADC6, vcc reference 
  ADCSRA|=B01000000; // ADC ON , START CONVERSION
  while(bit_is_set(ADCSRA,ADSC));// wait till the conversion is complete
  sensorValue[7]=ADCL|(ADCH<<8);
  
  
/*
     // read the analog in value:
  sensorValue[0] = analogRead(A0);
  sensorValue[1] = analogRead(A1);
  sensorValue[2] = analogRead(A2);
  sensorValue[3] = analogRead(A3);
  sensorValue[4] = analogRead(A4);
  sensorValue[5] = analogRead(A5);
  sensorValue[6] = analogRead(A6);
  sensorValue[7] = analogRead(A7);
  sensorValue[8] = analogRead(A8);
  sensorValue[9] = analogRead(A9);
  sensorValue[10] = analogRead(A10);
  sensorValue[11] = analogRead(A11);
  sensorValue[12] = analogRead(A12);
  sensorValue[13] = analogRead(A13);
  sensorValue[14] = analogRead(A14);
  sensorValue[15] = analogRead(A15);*/
  // map it to the range of the analog out:
 // outputValue = map(sensorValue[0], 0, 1023, 0, 255);
  // change the analog out value:
  //analogWrite(analogOutPin, outputValue); // timer1 is also used for analogWrite on pin 9. So cannot be used 

  // print the results to the Serial Monitor:
 Serial.print(counter);
  Serial.print("\t");
  for(int i=0;i<8;i++)
 { //Serial.print(i);
   //Serial.print(":");
   Serial.print(sensorValue[i]);
   Serial.print("\t");
   }
  Serial.print("\n");
  
  flag=0;
   
}
