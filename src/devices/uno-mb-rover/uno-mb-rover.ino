int pwm_a = 3;  //PWM control for motor outputs 1 and 2 
int pwm_b = 9;  //PWM control for motor outputs 3 and 4 
int dir_a = 2;  //direction control for motor outputs 1 and 2 
int dir_b = 8;  //direction control for motor outputs 3 and 4 

#include <Wire.h>
// 2, 3, 8, 9
int x = 0;
int p = 0;

const int P_SLOW = 175;
const int P_FAST = 255;

void setup()
{
  pinMode(pwm_a, OUTPUT);  //Set control pins to be outputs
  pinMode(pwm_b, OUTPUT);
  pinMode(dir_a, OUTPUT);
  pinMode(dir_b, OUTPUT);
  
  //analogWrite(pwm_a, 100);  //set both motors to run at (100/255 = 39)% duty cycle (slow)
  //analogWrite(pwm_b, 100);

  // Start the I2C Bus as Slave on address 9
  //Wire.begin(20); // A4=SDA A5=SCL
  //Wire.setClock(400000L);
  // Attach a function to trigger when something is received.
  //Wire.onReceive(receiveEvent);

  Serial.begin(115200);
  Serial.println("init");
  //Serial.onReceive(receiveEvent);
}

void receiveEvent(int bytes) {
  //x = Wire.read();    // read one character from the I2C
  x = Serial.read();
}

void loop()
{
  x = Serial.read();
  
  if (x != p) {
    p = x;

    if (x == 119) { // w
        digitalWrite(dir_a, LOW);
        digitalWrite(dir_b, LOW);

        analogWrite(pwm_a, P_SLOW);
        analogWrite(pwm_b, P_SLOW);
    }

    if (x == 87) { // W
        digitalWrite(dir_a, LOW);
        digitalWrite(dir_b, LOW);

        analogWrite(pwm_a, P_FAST);
        analogWrite(pwm_b, P_FAST);
    }

    if (x == 115) { // s
        digitalWrite(dir_a, HIGH);
        digitalWrite(dir_b, HIGH);

        analogWrite(pwm_a, P_SLOW);
        analogWrite(pwm_b, P_SLOW);
    }

    if (x == 83) { // S
        digitalWrite(dir_a, HIGH);
        digitalWrite(dir_b, HIGH);

        analogWrite(pwm_a, P_FAST);
        analogWrite(pwm_b, P_FAST);
    }

    if (x == 97) { // a
        digitalWrite(dir_a, LOW);
        digitalWrite(dir_b, HIGH);

        analogWrite(pwm_a, P_SLOW);
        analogWrite(pwm_b, P_SLOW);
    }

    if (x == 65) { // A
        digitalWrite(dir_a, LOW);
        digitalWrite(dir_b, HIGH);

        analogWrite(pwm_a, P_FAST);
        analogWrite(pwm_b, P_FAST);
    }

    if (x == 100) { // d
        digitalWrite(dir_a, HIGH);
        digitalWrite(dir_b, LOW);

        analogWrite(pwm_a, P_SLOW);
        analogWrite(pwm_b, P_SLOW);
    }

    if (x == 68) { // D
        digitalWrite(dir_a, HIGH);
        digitalWrite(dir_b, LOW);

        analogWrite(pwm_a, P_FAST);
        analogWrite(pwm_b, P_FAST);
    }

    if (x == 0) {
        // Serial.println("setting low, 0");
        analogWrite(pwm_a, 0);
        analogWrite(pwm_b, 0);
    }
  }
}


