int pwm_right = 3;  //PWM control for motor outputs 1 and 2 
int pwm_left = 9;  //PWM control for motor outputs 3 and 4 
int dir_right = 2;  //direction control for motor outputs 1 and 2 
int dir_left = 8;  //direction control for motor outputs 3 and 4 

#include <Wire.h>
// 2, 3, 8, 9
int x = 0;
int p = 0;

const int P_SLOW = 175;
const int P_FAST = 255;
const int D_BACKWARD = HIGH;
const int D_FORWARD = LOW;

void setup()
{
  pinMode(pwm_right, OUTPUT);  //Set control pins to be outputs
  pinMode(pwm_left, OUTPUT);
  pinMode(dir_right, OUTPUT);
  pinMode(dir_left, OUTPUT);
  
  //analogWrite(pwm_right, 100);  //set both motors to run at (100/255 = 39)% duty cycle (slow)
  //analogWrite(pwm_left, 100);

  // Start the I2C Bus as Slave on address 9
  // this doesnt work atm due to volage differences - need a converter
  //Wire.begin(20); // A4=SDA A5=SCL
  //Wire.setClock(400000L);
  // Attach a function to trigger when something is received.
  //Wire.onReceive(receiveEvent);

  Serial.begin(115200);
  Serial.println("init");
  //Serial.onReceive(receiveEvent);

//digitalWrite(dir_right, D_BACKWARD);
//analogWrite(pwm_right, P_SLOW);
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

    if (x == 119) { // w - forward
        digitalWrite(dir_right, D_FORWARD);
        digitalWrite(dir_left, D_FORWARD);

        analogWrite(pwm_right, P_SLOW);
        analogWrite(pwm_left, P_SLOW);
    }

    if (x == 87) { // W - forward fast
        digitalWrite(dir_right, D_FORWARD);
        digitalWrite(dir_left, D_FORWARD);

        analogWrite(pwm_right, P_FAST);
        analogWrite(pwm_left, P_FAST);
    }

    if (x == 115) { // s - back
        digitalWrite(dir_right, D_BACKWARD);
        digitalWrite(dir_left, D_BACKWARD);

        analogWrite(pwm_right, P_SLOW);
        analogWrite(pwm_left, P_SLOW);
    }

    if (x == 83) { // S - back fast
        digitalWrite(dir_right, D_BACKWARD);
        digitalWrite(dir_left, D_BACKWARD);

        analogWrite(pwm_right, P_FAST);
        analogWrite(pwm_left, P_FAST);
    }

    if (x == 97) { // a - left
        digitalWrite(dir_right, D_FORWARD);
        digitalWrite(dir_left, D_BACKWARD);

        analogWrite(pwm_right, P_SLOW);
        analogWrite(pwm_left, P_SLOW);
    }

    if (x == 65) { // A - left fast
        digitalWrite(dir_right, D_FORWARD);
        digitalWrite(dir_left, D_BACKWARD);

        analogWrite(pwm_right, P_FAST);
        analogWrite(pwm_left, P_FAST);
    }

    if (x == 100) { // d - right
        digitalWrite(dir_right, D_BACKWARD);
        digitalWrite(dir_left, D_FORWARD);

        analogWrite(pwm_right, P_SLOW);
        analogWrite(pwm_left, P_SLOW);
    }

    if (x == 68) { // D - right fast
        digitalWrite(dir_right, D_BACKWARD);
        digitalWrite(dir_left, D_FORWARD);

        analogWrite(pwm_right, P_FAST);
        analogWrite(pwm_left, P_FAST);
    }

    //
    // combinations
    //
//    if (x == 113) { // q - strafe forward left
//        digitalWrite(dir_right, D_BACKWARD); // low is backward, high is forward
//        digitalWrite(dir_left, D_FORWARD);
//
//        analogWrite(pwm_right, P_SLOW);
//        analogWrite(pwm_left, P_SLOW);
//    }

    if (x == 81) { // Q - strafe forward left fast
        digitalWrite(dir_right, D_FORWARD);
        digitalWrite(dir_left, D_FORWARD);

        analogWrite(pwm_right, P_SLOW);
        analogWrite(pwm_left, P_FAST);
    }

//    if (x == 101) { // e - strafe forward right
//        digitalWrite(dir_right, D_FORWARD);
//        digitalWrite(dir_left, D_BACKWARD);
//
//        analogWrite(pwm_right, P_FAST);
//        analogWrite(pwm_left, P_FAST);
//    }

    if (x == 69) { // E - strafe forward right fast
        digitalWrite(dir_right, D_FORWARD);
        digitalWrite(dir_left, D_FORWARD);

        analogWrite(pwm_right, P_FAST);
        analogWrite(pwm_left, P_SLOW);
    }

//    if (x == 122) { // z - strafe backward left
//        digitalWrite(dir_right, D_BACKWARD);
//        digitalWrite(dir_left, D_FORWARD);
//
//        analogWrite(pwm_right, P_SLOW);
//        analogWrite(pwm_left, P_SLOW);
//    }

    if (x == 90) { // Z - strafe backward left fast
        digitalWrite(dir_right, D_BACKWARD);
        digitalWrite(dir_left, D_BACKWARD);

        analogWrite(pwm_right, P_FAST);
        analogWrite(pwm_left, P_SLOW);
    }

//    if (x == 99) { // c - strafe backward right
//        digitalWrite(dir_right, D_BACKWARD);
//        digitalWrite(dir_left, D_FORWARD);
//
//        analogWrite(pwm_right, P_FAST);
//        analogWrite(pwm_left, P_FAST);
//    }

    if (x == 67) { // C - strafe backward right fast
        digitalWrite(dir_right, D_BACKWARD);
        digitalWrite(dir_left, D_BACKWARD);

        analogWrite(pwm_right, P_SLOW);
        analogWrite(pwm_left, P_FAST);
    }
    // end combinations

    if (x == 0 || x == 48) {
        // Serial.println("setting low, 0");
        analogWrite(pwm_right, 0);
        analogWrite(pwm_left, 0);
    }
  }
}


