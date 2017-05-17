#include <IRremote.h>

IRsend irsend;
int incomingByte = 0;

int codeArray[26]={
    0x0, //bogus code
    0x100C, // power button
    0x1086, // audio in
    0x1039, // coax
    0x1038, // aux
    0x106C, // optical
    0x1069, // BT
    0x1087, // arc
    0x107E, // usb

    0x1016, // bass up
    0x1017, // bass down
     
    0x105A, // previous
    0x102C, // play/pause
    0x105B, // next
    0x1010, // volume up
    0x1011, // vol down
    0x100D, // mute
    0x1018, // treble up
    0x1019, // treble down
    0x1051, // sound (effect)
    0x1050, // surround off
    0x1052, // surround on
    0x10FA, // audiosync minus
    0x10FB, // audiosync plus
    0x10E9, // dim
    0x10DC, // night mode
  };

void setup() {
  Serial.begin(9600);
  Serial.write("ready\n");
}

void loop() {
  if (Serial.available() > 0) {
    incomingByte = Serial.read();

    Serial.print("I received: ");
    Serial.println(incomingByte, DEC);
    
    /*
      1 = 100C = power button
      2 = 1086 = audio in
      3 = 1039 = coax
      4 = 1038 = aux
      5 = 106C = optical
      6 = 1069 = BT
      7 = 1087 = arc
      8 = 107E = usb

      9 = 1016 = bass up
     10 = 1017 = bass down
     
     11 = 105A = previous
     12 = 102C = play/pause
     13 = 105B = next
     14 = 1010 = volume up
     15 = 1011 = vol down
     16 = 100D = mute
     17 = 1018 = treble up
     18 = 1019 = treble down
     19 = 1051 = sound (effect)
     20 = 1050 = surround off
     21 = 1052 = surround on
     22 = 10FA = audiosync minus
     23 = 10FB = audiosync plus
     24 = 10E9 = dim
     25 = 10DC = night mode
     */

    int sendCode = 0;
/*
    switch (incomingByte) {
      case 1:
        sendCode = 0x100C;
        break;
      case 2:
        sendCode = 0x1086;
        break;
      case 3:
        sendCode = 0x1039;
        break;
      case 4:
        sendCode = 0x1038;
        break;
      case 5:
        sendCode = 0x106C;
        break;
      case 6:
        sendCode = 0x1069;
        break;
      case 7:
        sendCode = 0x1087;
        break;
      case 8:
        sendCode = 0x107E;
        break;
      case 9:
        sendCode = 0x1016;
        break;
      case 10:
        sendCode = 0x1017;
        break;
      default:
        sendCode = 0;
        break;
    }*/

    if (incomingByte < sizeof(codeArray))
    {
      sendCode = codeArray[incomingByte];
    }

    //if there are issues then every other code must be += 0x10000

    if (sendCode != 0)
    {
      Serial.print("Sending code..");
      for (int i = 0; i < 3; i++)
      {
        irsend.sendRC6(sendCode, 20);
        delay(40);
      }
    }
    
  }
}
