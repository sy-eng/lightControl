//This program switch on or off, OCR-05W,
//Ohm Electric.
#define OUTPIN 3
void setup() {
  pinMode(OUTPIN, OUTPUT);

  TCCR2A = 0b00010010;
  TCCR2B = 0b00000001;

  OCR2A = 210;

  Serial.begin(9600);
}

void signalOn(){
  TCCR2A = 0b00010010;  
}

void signalOff(){
  TCCR2A = 0b00000010;  
}

void switchOn(){
  //3
  signalOn();
  delayMicroseconds(2645);  //881.7*3
  //3
  signalOff();
  delayMicroseconds(2645);  //881.7*3
  //1
  signalOn();
  delayMicroseconds(881);
  //1
  signalOff();
  delayMicroseconds(881);
  //1
  signalOn();
  delayMicroseconds(881);
  //1
  signalOff();
  delayMicroseconds(881);
  //1
  signalOn();
  delayMicroseconds(881);
  //2
  signalOff();
  delayMicroseconds(1763);  //881.7*2
  //1
  signalOn();
  delayMicroseconds(881);
  //2
  signalOff();
  delayMicroseconds(1763);  //881.7*2
  //1
  signalOn();
  delayMicroseconds(881);
  //2
  signalOff();
  delayMicroseconds(1763);  //881.7*2
  //1
  signalOn();
  delayMicroseconds(881);
  //2
  signalOff();
  delayMicroseconds(1763);  //881.7*2
  //1
  signalOn();
  delayMicroseconds(881);
  //1
  signalOff();
  delayMicroseconds(881);
  //1
  signalOn();
  delayMicroseconds(881);
  //1
  signalOff();
  delayMicroseconds(881);
  //1
  signalOn();
  delayMicroseconds(881);
  signalOff();  
}

void switchOff(){
  //3
  signalOn();
  delayMicroseconds(2645);  //881.7*3
  //3
  signalOff();
  delayMicroseconds(2645);  //881.7*3
  //1
  signalOn();
  delayMicroseconds(881);
  //1
  signalOff();
  delayMicroseconds(881);
  //1
  signalOn();
  delayMicroseconds(881);
  //2
  signalOff();
  delayMicroseconds(1763);
  //1
  signalOn();
  delayMicroseconds(881);
  //1
  signalOff();
  delayMicroseconds(881);
  //1
  signalOn();
  delayMicroseconds(881);
  //1
  signalOff();
  delayMicroseconds(811);
  //1
  signalOn();
  delayMicroseconds(881);
  //2
  signalOff();
  delayMicroseconds(1763);  //881.7*2
  //1
  signalOn();
  delayMicroseconds(881);
  //1
  signalOff();
  delayMicroseconds(881);
  //1
  signalOn();
  delayMicroseconds(881);
  //2
  signalOff();
  delayMicroseconds(1763);
  //1
  signalOn();
  delayMicroseconds(881);
  //2
  signalOff();
  delayMicroseconds(1763);
  //1
  signalOn();
  delayMicroseconds(881);
  signalOff();  
}

void loop() {
  static int incoming = 0;

  if(Serial.available()){
    incoming = Serial.read();

    switch(incoming){
      case 'n':
        //send the ON signal twice.
        //The first sinal after the intialization often ignored!
        switchOn();
        delay(300);
        switchOn();
        Serial.print("on\n");
        break;
      case 'f':
        //send the OFF signal twice.
        //The first sinal after the intialization often ignored!
        switchOff();
        delay(300);
        switchOff();
        Serial.print("off\n");
        break;
      case 't':
        Serial.print("test\n");
        break;        
      default:
        break;
    } 
  }
}
