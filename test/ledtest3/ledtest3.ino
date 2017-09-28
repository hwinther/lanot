// based on an orginal sketch by Arduino forum member "danigom"
// http://forum.arduino.cc/index.php?action=profile;u=188950

#include <pgmspace.h>
#include <LedControl.h>

#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
//#include <ESP8266mDNS.h>
//#include <ArduinoJson.h>

const char* ssid = "dniHQ";
const char* password = "dotnetinternals145";
//const char* ssid = "dgn";
//const char* password = "pingvin9195";
ESP8266WebServer server(80);
const int led = 16;
const int numDevices = 4;      // number of MAX7219s used
//LedControl(int dataPin, int clkPin, int csPin, int numDevices=1);
LedControl lc = LedControl(1, 12, 14, numDevices);

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

void displayImageSmall(int mtx, int startcolumn, uint64_t image) {
  for (int i = 0; i < 5; ++i) {
    byte row = (image >> i * 8) & 0xFF;
    for (int j = 0; j < 3; ++j) {
      lc.setLed(mtx, i, startcolumn+j, bitRead(row, j));
    }
  }
}

void displayChars(char *buffer, unsigned int len) {
  int maxmtx = numDevices - 1;
  int curmtx = maxmtx;
  int column = 0;

  for(int i = 0; i < len; ++i) { //sizeof(buffer)-1
    if (buffer[i] == 0) {
      break;
    }
    
    const char *ptr = strchr(alphanum, buffer[i]);
    if (ptr) {
      int index = ptr - alphanum;
      displayImageSmall(curmtx, column, IMAGES[index]);
      column += 4; // default width and spacing
    } else {
      if (column != 0) {
        column += 2;
      }
    }
    
    if (column >= 8) {
      column = 0;
      --curmtx;

      if (curmtx < 0) {
        break; // give up
        //curmtx = maxmtx;
      }
    }

  }
}

void clearDisplay() {
  for (int x=0; x<numDevices; x++) {
    lc.clearDisplay(x);
  }
}

void setup(){ 
  for (int x=0; x<numDevices; x++) {
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
  displayChars(data1+7, strlen(data1)-7);

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
    displayChars(data, server.arg(0).length());

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

