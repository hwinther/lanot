// based on an orginal sketch by Arduino forum member "danigom"
// http://forum.arduino.cc/index.php?action=profile;u=188950

#include <pgmspace.h>
#include "LedControl.h"
#include "FrameDisplay.h"

#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
//#include <ESP8266mDNS.h>
//#include <ArduinoJson.h>

//const char* ssid = "dniHQ";
//const char* password = "dotnetinternals145";
const char* ssid = "dgn.iot";
const char* password = "umbFUTyJSvqhxNrQ";
ESP8266WebServer server(80);
const int led = 16;

// const int dataPin, const int clkPin, const int csPin
LedControl lc = LedControl(13, 12, 14, num_devices);
FrameDisplay fd = FrameDisplay();

bool scrollText = false;
uint8_t scrollLength = 0;
bool scrollDirection = false;
uint8_t scrollPosition = 0;

// Generally, you should use "unsigned long" for variables that hold time
// The value will quickly become too large for an int to store
unsigned long previousMillis = 0;        // will store last time LED was updated

void clearDisplay() {
  for (int x = 0; x < num_devices; ++x) {
    lc.clearDisplay(x);
  }
}

void setup(){ 
  for (int x = 0; x < num_devices; ++x) {
      lc.shutdown(x, false);       //The MAX72XX is in power-saving mode on startup
      lc.setIntensity(x, 8);       // Set the brightness to default value
      lc.clearDisplay(x);         // and clear the display
  }

  pinMode(led, OUTPUT);
  digitalWrite(led, 0);
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.println("");

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  //if (MDNS.begin("esp8266")) {
    //Serial.println("MDNS responder started");
  //}

  IPAddress _address = WiFi.localIP();
  char data1[16];
  _address.toString().toCharArray(data1, sizeof(data1));
  fd.chars_to_frame(data1+7, strlen(data1)-7, 1);
  fd.display_frame(lc);

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
    fd.clear_frame();
    //displayChars(data, server.arg(0).length());
    fd.chars_to_frame(data, server.arg(0).length(), 1);
    fd.display_frame(lc);

    server.send ( 200, "text/plain", data );
  });

  server.on("/settext2", [](){
    char data[16];
    server.arg(0).toCharArray(data, sizeof(data));
    clearDisplay();
    fd.clear_frame();
    fd.chars_to_frame(data, server.arg(0).length(), 1);
    fd.display_frame(lc);

    server.send ( 200, "text/plain", data );

    scrollText = true;
    scrollLength = 64;
    scrollDirection = false;
    scrollPosition = 0;
  });
  
  server.onNotFound(handleNotFound);
  server.begin();
  Serial.println("HTTP server started");

  digitalWrite(led, 1);
}

void loop()
{
  server.handleClient();

  // check to see if it's time to toggle the LED; that is, if the
  // difference between the current time and last time you blinked
  // the LED is bigger than the interval at which you want to
  // blink the LED.
  unsigned long currentMillis = millis();

  if (scrollText && currentMillis - previousMillis >= delaytime) {    
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

    // save the time you should have toggled the LED
    previousMillis = millis();
  }

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

