// based on an orginal sketch by Arduino forum member "danigom"
// http://forum.arduino.cc/index.php?action=profile;u=188950

#include <pgmspace.h>
#include <LedControl.h>

#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
//#include <ESP8266mDNS.h>
//#include <ArduinoJson.h>

//const char* ssid = "dniHQ";
//const char* password = "dotnetinternals145";
const char* ssid = "dgn";
const char* password = "pingvin9195";
ESP8266WebServer server(80);
const int led = 16;
const int numDevices = 4;      // number of MAX7219s used

LedControl lc = LedControl(13, 12, 14, numDevices);

const char alphanum[] = "abcdefghijklmnopqrstuvwxyz0123456789.";
const int alphanum_len = sizeof(alphanum);
// https://xantorohara.github.io/led-matrix-editor/#0000000505070502|0000000305070503|0000000701010107|0000000305050503|0000000701070107|0000000101070107|0000000705050107|0000000505070505|0000000101010101|0000000302020202|0000000503010305|0000000701010101|0000000505050705|0000000505070505|0000000705050507|0000000101070507|0000000107050507|0000000505030503|0000000304020106|0000000202020207|0000000705050505|0000000205050505|0000000705070505|0000000505020505|0000000202020505|0000000702040407|0000000705050507|0000000202020302|0000000701020403|0000000704060407|0000000404070506|0000000304030107|0000000705070107|0000000103060407|0000000705070507|0000000404070507|0000000200000000
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
  0x0000000705050507,
  0x0000000202020302,
  0x0000000701020403,
  0x0000000704060407,
  0x0000000404070506,
  0x0000000304030107,
  0x0000000705070107,
  0x0000000103060407,
  0x0000000705070507,
  0x0000000404070507,
  0x0000000200000000
};
const int IMAGES_LEN = sizeof(IMAGES)/8;

uint32_t FRAME[8] = { 0, 0, 0, 0,  0, 0, 0, 0 };

void letterToFrame(int startRow, int startColumn, int letterHeight, int letterWidth, uint64_t image) {
  // out of bounds
  if (startRow+letterHeight >= 8)
    return;
  if (startColumn+letterWidth >= 32)
    return;
    
  for (int i = 0; i < letterHeight; ++i) {
    uint32_t row = (image >> i * 8) & 0xFF;
    for (int j = 0; j < letterWidth; ++j) {
      bitWrite(FRAME[startRow+i], startColumn+j, bitRead(row, j));
    }
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
    int mtx = numDevices - 1;
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

void charsToFrame(char *buffer, int siz, int row=0) {
  int column = 0;

  for(int i = 0; i < siz; ++i) {
    const char *ptr = strchr(alphanum, buffer[i]);
    if(ptr) {
      int index = ptr - alphanum;
      letterToFrame(row, column, 5, 3, IMAGES[index]);
      spacerToFrame(column+3, 1, 6);
      column += 4; // default width and spacing
    } else {
      if (column != 0) {
        spacerToFrame(column+1, 1, 6);
        column += 1;
      }
    }
    
    if (column >= 32) {
      break;
    }
  }
}

void shiftFrameLeft(int amount = 1) {
  // shift frame 1 bit to the left
  for (int i = 0; i < 8; i++) {
    FRAME[i] = FRAME[i] << amount;
  }
}

void shiftFrameRight(int amount = 1) {
  // shift frame 1 bit to the left
  for (int i = 0; i < 8; i++) {
    FRAME[i] = FRAME[i] >> amount;
  }
}

void clearDisplay() {
  for (int x = 0; x < numDevices; ++x) {
    lc.clearDisplay(x);
  }
}

void clearFrame() {
  for (int i = 0; i < 8; i++) {
    FRAME[i] = 0;
  }
}

void setup(){ 
  for (int x = 0; x < numDevices; ++x) {
      lc.shutdown(x, false);       //The MAX72XX is in power-saving mode on startup
      lc.setIntensity(x, 8);       // Set the brightness to default value
      lc.clearDisplay(x);         // and clear the display
  }

  pinMode(led, OUTPUT);
  digitalWrite(led, 0);
  //Serial.begin(115200);
  WiFi.begin(ssid, password);
  //Serial.println("");

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    //Serial.print(".");
  }
  //Serial.println("");
  //Serial.print("Connected to ");
  //Serial.println(ssid);
  //Serial.print("IP address: ");
  //Serial.println(WiFi.localIP());

  //if (MDNS.begin("esp8266")) {
    //Serial.println("MDNS responder started");
  //}

  IPAddress _address = WiFi.localIP();
  char data1[16];
  _address.toString().toCharArray(data1, sizeof(data1));
  charsToFrame(data1+7, strlen(data1)-7);
  displayFrame();

  server.on("/", handleRoot);

  server.on("/led/on", [](){
    server.send(200, "text/plain", "on");
    digitalWrite(led, 0);
  });

  server.on("/led/off", [](){
    server.send(200, "text/plain", "off");
    digitalWrite(led, 1);
  });

  /*server.on("/config/set", HTTP_POST, [](){
    StaticJsonBuffer<200> newBuffer;
    JsonObject& newjson = newBuffer.parseObject(server.arg("plain"));
    unsigned char* txt = newjson["text"];
    scrollMessage(txt);
    server.send ( 200, "text/json", "{success:true}" );
  });*/

  server.on("/settext", [](){
    char data[16];
    server.arg(0).toCharArray(data, sizeof(data));
    clearDisplay();
    clearFrame();
    //displayChars(data, server.arg(0).length());
    charsToFrame(data, server.arg(0).length(), 1);
    displayFrame();

    server.send ( 200, "text/plain", data );
  });
  
  server.onNotFound(handleNotFound);
  server.begin();
  //Serial.println("HTTP server started");

  digitalWrite(led, 1);
}

void loop()
{
  server.handleClient();
}

void handleRoot() {
  server.send(200, "text/plain", "hello from esp8266!");
}

void handleNotFound(){
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET)?"GET":"POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";
  for (uint8_t i=0; i<server.args(); i++){
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }
  server.send(404, "text/plain", message);
}

