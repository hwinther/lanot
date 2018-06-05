/*

  HelloWorld.ino

  Universal 8bit Graphics Library (https://github.com/olikraus/u8g2/)

  Copyright (c) 2016, olikraus@gmail.com
  All rights reserved.

  Redistribution and use in source and binary forms, with or without modification, 
  are permitted provided that the following conditions are met:

  * Redistributions of source code must retain the above copyright notice, this list 
    of conditions and the following disclaimer.
    
  * Redistributions in binary form must reproduce the above copyright notice, this 
    list of conditions and the following disclaimer in the documentation and/or other 
    materials provided with the distribution.

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND 
  CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT 
  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, 
  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  

*/

#include <Arduino.h>
#include <U8g2lib.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

// The complete list is available here: https://github.com/olikraus/u8g2/wiki/u8g2setupcpp
// Please update the pin numbers according to your setup. Use U8X8_PIN_NONE if the reset pin is not connected
U8G2_SSD1306_128X64_NONAME_F_SW_I2C u8g2(U8G2_R0, /* clock=*/ SCL, /* data=*/ SDA, /* reset=*/ U8X8_PIN_NONE);   // All Boards without Reset of the Display

// Include the libraries we need
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ESP8266WiFi.h>

// Data wire is plugged into port 2 on the Arduino
#define ONE_WIRE_BUS 2
#define ONE_WIRE_BUS2 14

//#define SERIAL

// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);
OneWire oneWire2(ONE_WIRE_BUS2);

// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);
DallasTemperature sensors2(&oneWire2);

//const char* ssid     = "dgn.iot";
//const char* password = "umbFUTyJSvqhxNrQ";

const char* ssid     = "Augusta";
const char* password = "rettoverbondivann";

const char* host = "bondivann.wsh.no";
const char* streamId   = "bondivann";
const char* privateKey = "bondivann";

int sendCounter = 0;
float temperature = 0;
float temperature2 = 0;

void setup(void) {
  #ifdef SERIAL
  Serial.begin(115200);
  #endif
  
  u8g2.begin();

  // Start up the library
  sensors.begin();
  sensors2.begin();

  u8g2.clearBuffer();          // clear the internal memory
  u8g2.setFont(u8g2_font_ncenB14_tr); // choose a suitable font
  u8g2.drawStr(0, 20, "Starting up");  // write something to the internal memory
  u8g2.sendBuffer();          // transfer internal memory to the display

  WiFi.begin(ssid, password);

  int i = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    u8g2.clearBuffer();          // clear the internal memory
    u8g2.setFont(u8g2_font_ncenB14_tr); // choose a suitable font
    u8g2.setCursor(0,15);
    u8g2.print("Wifi: ");
    u8g2.print(i, DEC);
    u8g2.sendBuffer();          // transfer internal memory to the display
    ++i;
  }
}

void loop(void) {
  sensors.requestTemperatures(); // Send the command to get temperatures
  sensors2.requestTemperatures(); // Send the command to get temperatures
  
  u8g2.clearBuffer();					// clear the internal memory
  u8g2.setFont(u8g2_font_ncenB08_tr);	// choose a suitable font

  int cursorHeight = 8;
  int cursorHeightInc = 11;
  u8g2.setCursor(0, cursorHeight);
  u8g2.print("I:");
  u8g2.print(WiFi.localIP());

  cursorHeight += cursorHeightInc;
  u8g2.setCursor(0, cursorHeight);
  u8g2.print("Temp: ");
  temperature = sensors.getTempCByIndex(0);
  u8g2.print(temperature, DEC);

  cursorHeight += cursorHeightInc;
  u8g2.setCursor(0, cursorHeight);
  u8g2.print("Temp2: ");
  temperature2 = sensors2.getTempCByIndex(0);
  u8g2.print(temperature2, DEC);

  cursorHeight += cursorHeightInc;
  int wsHeight = cursorHeight;
  u8g2.setCursor(0, cursorHeight);
  u8g2.print("WS: Idle    ");

  cursorHeight += cursorHeightInc;
  u8g2.setCursor(0, cursorHeight);
  for(int ii = 0; ii < sendCounter; ++ii)
  {
    u8g2.print(".");
  }
  if (sendCounter == 0)
  {
    for(int ii = 0; ii < 10; ++ii)
    {
      u8g2.print(" ");
    }
  }
  
  u8g2.sendBuffer();					// transfer internal memory to the display
  ++sendCounter;
  if (sendCounter == 20) // every minute
  {
    sendCounter = 0;
    // Use WiFiClient class to create TCP connections
    WiFiClient client;
    const int httpPort = 80;
    if (!client.connect(host, httpPort)) {
      u8g2.setCursor(0, wsHeight);
      u8g2.print("WS: Con fail");
      u8g2.sendBuffer();
      #ifdef SERIAL
      Serial.println("connection failed");
      #endif
      return;
    }

    // We now create a URI for the request
    String url = "/api/";
    url += streamId;
    url += "?private_key=";
    url += privateKey;
    url += "&value=";
    url += String(temperature, 4);
    url += "&value2=";
    url += String(temperature2, 4);

    u8g2.setCursor(0, wsHeight);
    u8g2.print("WS: Sending");
    u8g2.sendBuffer();
    #ifdef SERIAL
    Serial.print("Requesting URL: ");
    Serial.println(url);
    #endif
    
    // This will send the request to the server
    client.print(String("GET ") + url + " HTTP/1.1\r\n" +
                 "Host: " + host + "\r\n" + 
                 "Connection: close\r\n\r\n");
    unsigned long timeout = millis();
    while (client.available() == 0) {
      if (millis() - timeout > 5000) {
        u8g2.setCursor(0, wsHeight);
        u8g2.print("WS: Timeout");
        u8g2.sendBuffer();
        #ifdef SERIAL
        Serial.println(">>> Client Timeout !");
        #endif
        client.stop();
        return;
      }
    }
    
    // Read all the lines of the reply from server and print them to Serial
    while(client.available()){
      u8g2.setCursor(0, wsHeight);
      u8g2.print("WS: Sent    ");
      u8g2.sendBuffer();
      String line = client.readStringUntil('\r');
      #ifdef SERIAL
      Serial.print(line);
      #endif
    }
  }
  
  delay(1000);
}

