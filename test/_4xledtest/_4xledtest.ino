#include "LedControl.h"
#include "FrameDisplay.h"

/*
 pin 13 is connected to the DataIn 
 pin 12 is connected to the CLK 
 pin 14 is connected to LOAD 
 We have 4 MAX7219 devices
 */
LedControl lc = LedControl(13, 12, 14, num_devices);
FrameDisplay fd = FrameDisplay();

bool shiftLoop = false;
uint8_t shiftLength = 0;
bool shiftLoopDirection = false;
uint8_t shiftPosition = 0;

bool scrollText = false;
uint8_t scrollLength = 0;
bool scrollDirection = false;
uint8_t scrollPosition = 0;

bool cylonMode = false;
int cylonPosition = 0;
bool cylonDirection = false;

void setup() {
  Serial.begin(115200);

  /*
   The MAX72XX is in power-saving mode on startup,
   we have to do a wakeup call
   */
  for (int i = 0; i < num_devices; ++i) {
    lc.shutdown(i, false);
    /* Set the brightness to a medium values */
    lc.setIntensity(i, 5);
    /* and clear the display */
    lc.clearDisplay(i);
  }

  Serial.println("\ninit");
  delay(1000);

  //letterToFrame(0, 0, 5, 3, IMAGES[0]);
  //letterToFrame(0, 4, 5, 3, IMAGES[1]);
  //letterToFrame(0, 8, 5, 3, IMAGES[2]);
  //letterToFrame(0, 12, 5, 3, IMAGES[3]);
  
  char teststr[] = "init";
  int column = fd.chars_to_frame(teststr, strlen(teststr), 1);

  //rectangle_to_frame(column+1, 0, 4, 4, false);
  //circleToFrame(column+1, 0, 2, false);

  fd.display_frame(lc);
  delay(1000);

  shiftLoop = false;
  shiftLength = 8;
  shiftLoopDirection = false;
  shiftPosition = 0;

  scrollText = false;
  scrollLength = 32;
  scrollDirection = false;
  scrollPosition = 0;

  cylonMode = true;
  cylonPosition = 0;
  cylonDirection = false;
}

void loop() {

  //Serial.print("shiftLoop=");
  //Serial.print(shiftLoop, DEC);
  //Serial.print(" shiftLoopDirection=");
  //Serial.print(shiftLoopDirection, DEC);
  //Serial.print(" shiftPosition=");
  //Serial.println(shiftPosition, DEC);

  if (cylonMode) {
    const int cylonMtx = num_devices - 1 - (cylonPosition / 8);
    
    if (cylonPosition == 0)
    {
        for (int i = 0; i < num_devices; ++i) {
          lc.setIntensity(i, 15);
          lc.clearDisplay(i);
        }
    }
    else
    {
      if ((cylonPosition % 8) -1 == -1)
      {
        lc.setLed(cylonMtx-1, 4, 7, false);
      }
      else
      {
        lc.setLed(cylonMtx, 4, (cylonPosition-1) % 8, false);
      }
    }
    
    lc.setLed(cylonMtx, 4, cylonPosition % 8, true);
    ++cylonPosition;

    if (cylonPosition == 32) {
      cylonMode = false;
      for (int i = 0; i < num_devices; ++i) {
        lc.setIntensity(i, 5);
        lc.clearDisplay(i);
      }
    }
  }

  if (shiftLoop) {
    if (shiftLoopDirection == false) {
      fd.shift_frame_left(1);
      fd.display_frame(lc);
    } else if (shiftLoopDirection == true) {
      fd.shift_frame_right(1);
      fd.display_frame(lc);
    }

    ++shiftPosition;

    if (shiftLoopDirection == true && shiftPosition > shiftLength) { // * 2
      shiftLoop = false; // stop the task
    }
    else if (shiftLoopDirection == false && shiftPosition > shiftLength) {
      shiftLoopDirection = true; // go the other way
      shiftPosition = 0;
    }
  }

  //Serial.print("scrollText=");
  //Serial.print(scrollText, DEC);
  //Serial.print(" scrollDirection=");
  //Serial.print(scrollDirection, DEC);
  //Serial.print(" scrollPosition=");
  //Serial.println(scrollPosition, DEC);

  if (scrollText) {
    if (scrollDirection == false) {
      fd.shift_frame_right(1);
      fd.display_frame(lc);
    }/* else if (scrollDirection == true) {
      shift_frame_left(1);
      displayFrame();
    }*/

    ++scrollPosition;

    if (/*scrollDirection == true &&*/ scrollPosition > scrollLength) { // * 2
      scrollText = false; // stop the task
    }/*
    else if (scrollDirection == false && scrollPosition > scrollLength) {
      scrollDirection = true; // go the other way
      scrollPosition = 0;
    }*/
  }

  delay(delaytime);
  
  /*
  shift_frame_right(16);
  displayFrame();
  delay(500);

  shift_frame_left(16);
  displayFrame();
  delay(500);
  */
}

