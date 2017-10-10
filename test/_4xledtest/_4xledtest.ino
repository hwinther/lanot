//We always have to include the library
#include "LedControlMS.h"

/*
 Now we need a LedControl to work with.
 ***** These pin numbers will probably not work with your hardware *****
 pin 12 is connected to the DataIn 
 pin 11 is connected to the CLK 
 pin 10 is connected to LOAD 
 We have only a single MAX72XX.
 */
#define NBR_MTX 4 
LedControl lc=LedControl(13, 12, 14, NBR_MTX);

String digits= "1234567890";
int digitCounter=0;
/* we always wait a bit between updates of the display */
unsigned long delaytime=300;

const char alphanum[] = "abcdefghijklmnopqrstuvwxyz0123456789";
const int alphanum_len = sizeof(alphanum);

const uint64_t IMAGES[] = {
  0x0000000505070502,
  0x0000000305070503,
  0x0000000701010107,
  0x0000000305050503,
  0x0000000701070107,
  0x0000000101070107,
  0x0000000705050107,
  0x0000000505070505,
  0x0000000101010101,
  0x0000000302020202,
  0x0000000503010305,
  0x0000000701010101,
  0x0000000505050705,
  0x0000000505070505,
  0x0000000705050507,
  0x0000000101070507,
  0x0000000107050507,
  0x0000000505030503,
  0x0000000304020106,
  0x0000000202020207,
  0x0000000705050505,
  0x0000000205050505,
  0x0000000705070505,
  0x0000000505020505,
  0x0000000202020505,
  0x0000000702040407,
  0x0000000705070507,
  0x0000000202020302,
  0x0000000701020403,
  0x0000000704060407,
  0x0000000404070506,
  0x0000000304030107,
  0x0000000705070107,
  0x0000000103060407,
  0x0000000705070507,
  0x0000000404070507
};
const int IMAGES_LEN = sizeof(IMAGES)/8;

uint32_t FRAME[8] = { 0, 0, 0, 0,  0, 0, 0, 0 }; //1,1,1,1, 1,1,1,1
/*
  0b11000000110000001100000011000000,
  0b00100000000000100000000000100000,
  0b00000000000000000000001000000000,
  0b00000001000000000000000000000000,
  0b00000000000000000000000001000000,
  0b00000000000001000000000000000000,
  0b00010000000000000000000010000000,
  0b00000000100000000100000000000010
};*/

void letterToFrame(int startRow, int startColumn, int letterHeight, int letterWidth, uint64_t image) {
  // out of bounds
  if (startRow+letterHeight >= 8)
    return;
  if (startColumn+letterWidth >= 32)
    return;
    
  for (int i = 0; i < letterHeight; ++i) {
    uint32_t row = (image >> i * 8) & 0xFF;
    //Serial.print("i=");
    //Serial.print(i, DEC);
    //Serial.print(" row=");
    //Serial.print(row, BIN);
    for (int j = 0; j < letterWidth; ++j) {
      bitWrite(FRAME[startRow+i], startColumn+j, bitRead(row, j));
    }
    //Serial.print(" frame=");
    //Serial.println(FRAME[i], BIN);
  }
}

void spacerToFrame(int column, int startRow, int endRow) {
  --endRow;
  for (int i = startRow; i < endRow; ++i) {
    bitWrite(FRAME[i], column, false);
  }
}

uint32_t reverseBits(uint32_t n) {
    n = (n >> 1) & 0x55555555 | (n << 1) & 0xaaaaaaaa;
    n = (n >> 2) & 0x33333333 | (n << 2) & 0xcccccccc;
    n = (n >> 4) & 0x0f0f0f0f | (n << 4) & 0xf0f0f0f0;
    n = (n >> 8) & 0x00ff00ff | (n << 8) & 0xff00ff00;
    n = (n >> 16) & 0x0000ffff | (n << 16) & 0xffff0000;
    return n;
}

void displayFrame(bool reverse=false) {
  for (int row = 7; row > -1; --row) {
    int mtx = NBR_MTX-1;
    int mtxColumn = 0;
    uint32_t frameRow;
    
    if (reverse) {
      frameRow = reverseBits(FRAME[row]);
    }
    else {
      frameRow = FRAME[row];
    }
    
    for (int column = 0; column < 32; ++column) {
      lc.setLed(mtx, row, mtxColumn, bitRead(frameRow, column));
      ++mtxColumn;

      if (mtxColumn >= 8) {
        mtxColumn = 0;
        --mtx;
      }

      if (mtx < 0) {
        break;
      }
    }
  }
}

void charsToFrame(char *buffer, int row=0) {
  int column = 0;
  int siz = strlen(buffer); //sizeof(buffer)-1
  Serial.print("siz=");
  Serial.println(siz, DEC);

  for(int i = 0; i < siz; ++i) {
    const char *ptr = strchr(alphanum, buffer[i]);
    Serial.print("! i=");
    Serial.print(i, DEC);
    if(ptr) {
      int index = ptr - alphanum;
      Serial.print(" image:");
      Serial.println(index, DEC);
      letterToFrame(row, column, 5, 3, IMAGES[index]);
      spacerToFrame(column+3, 1, 6);
      column += 4; // default width and spacing
    } else {
      Serial.println(" image: unknown, using space");
      if (column != 0) {
        spacerToFrame(column+1, 1, 6);
        column += 1;
      }
    }
    
    if (column >= 32) {
      Serial.println("break");
      break;
    }
  }
}

void shiftFrameLeft(int amount = 1) {
  // shift frame 1 bit to the left
  for (int j = 0; j < 8; j++) {
    FRAME[j] = FRAME[j] << amount;
  }
}

void shiftFrameRight(int amount = 1) {
  // shift frame 1 bit to the left
  for (int j = 0; j < 8; j++) {
    FRAME[j] = FRAME[j] >> amount;
  }
}

void setup() {
  Serial.begin(115200);
    
  /*
   The MAX72XX is in power-saving mode on startup,
   we have to do a wakeup call
   */
  digitCounter = 0;
  for (int i = 0; i < NBR_MTX; ++i) {
    lc.shutdown(i, false);
    /* Set the brightness to a medium values */
    lc.setIntensity(i, 5);
    /* and clear the display */
    lc.clearDisplay(i);
  }

  Serial.println("\ninit");
  char teststr[] = "abcdefghi";
  charsToFrame(teststr, 1);
  //letterToFrame(0, 0, 5, 3, IMAGES[35]);
  //letterToFrame(0, 4, 5, 3, IMAGES[34]);
  //letterToFrame(0, 8, 5, 3, IMAGES[33]);
  displayFrame();
  delay(2000);
}

void loop() {
  shiftFrameLeft(1);
  displayFrame();
  delay(500);

  shiftFrameRight(1);
  displayFrame();
  delay(500);
}

