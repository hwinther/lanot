// Wire Slave Receiver
// by Nicholas Zambetti <http://www.zambetti.com>

// Demonstrates use of the Wire library
// Receives data as an I2C/TWI slave device
// Refer to the "Wire Master Writer" example for use with this

// Created 29 March 2006

// This example code is in the public domain.
#include "nanosubproc.h"
#include <Wire.h>
#include <IRremote.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

IRsend irsend;
// Tell IRremote which Arduino pin is connected to the IR Receiver (TSOP4838)
int recv_pin = 11;
IRrecv irrecv(recv_pin);
state device_state;

char ir_recv_type[4];
char ir_recv_buffer[20];
unsigned long d = 0;
int b = 0;
char type[4];
void receive_event(int how_many);
void request_event();
static const unsigned long refresh_interval = 2000; // ms
static unsigned long last_refresh_time = 0;
decode_results results;        // Somewhere to store the results


void setup() {
	Wire.begin(8);                // join i2c bus with address #8
	Wire.setClock(400000L);
	Wire.onReceive(receive_event); // register event
	Wire.onRequest(request_event);
	irrecv.enableIRIn();  // Start the receiver
	Serial.begin(115200);           // start serial for output
	Serial.println("init\n");
}

//+=============================================================================
// Display IR code
//
void  ircode(decode_results *results)
{
	// Panasonic has an Address
	if (results->decode_type == PANASONIC) {
		Serial.print(results->address, HEX);
		Serial.print(":");
	}

	// Print Code
	Serial.print(results->value, HEX);
}

//+=============================================================================
// Display encoding type
//
void  encoding(decode_results *results)
{
	switch (results->decode_type) {
	default:
	case UNKNOWN:      Serial.print("UNKNOWN");      break;
	case NEC:          Serial.print("NEC");          break;
	case SONY:         Serial.print("SONY");         break;
	case RC5:          Serial.print("RC5");          break;
	case RC6:          Serial.print("RC6");          break;
	case DISH:         Serial.print("DISH");         break;
	case SHARP:        Serial.print("SHARP");        break;
	case JVC:          Serial.print("JVC");          break;
	case SANYO:        Serial.print("SANYO");        break;
	case MITSUBISHI:   Serial.print("MITSUBISHI");   break;
	case SAMSUNG:      Serial.print("SAMSUNG");      break;
	case LG:           Serial.print("LG");           break;
	case WHYNTER:      Serial.print("WHYNTER");      break;
	case AIWA_RC_T501: Serial.print("AIWA_RC_T501"); break;
	case PANASONIC:    Serial.print("PANASONIC");    break;
	case DENON:        Serial.print("Denon");        break;
	}
}

//+=============================================================================
// Dump out the decode_results structure.
//
void  dump_info(decode_results *results)
{
	// Check if the buffer overflowed
	if (results->overflow) {
		Serial.println("IR code too long. Edit IRremoteInt.h and increase RAWBUF");
		return;
	}

	// Show Encoding standard
	Serial.print("Encoding  : ");
	encoding(results);
	Serial.println("");

	// Show Code & length
	Serial.print("Code      : ");
	ircode(results);
	Serial.print(" (");
	Serial.print(results->bits, DEC);
	Serial.println(" bits)");
}

//+=============================================================================
// Dump out the decode_results structure.
//
void  dump_raw(decode_results *results)
{
	// Print Raw data
	Serial.print("Timing[");
	Serial.print(results->rawlen - 1, DEC);
	Serial.println("]: ");

	for (int i = 1; i < results->rawlen; i++) {
		unsigned long  x = results->rawbuf[i] * USECPERTICK;
		if (!(i & 1)) {  // even
			Serial.print("-");
			if (x < 1000)  Serial.print(" ");
			if (x < 100)   Serial.print(" ");
			Serial.print(x, DEC);
		}
		else {  // odd
			Serial.print("     ");
			Serial.print("+");
			if (x < 1000)  Serial.print(" ");
			if (x < 100)   Serial.print(" ");
			Serial.print(x, DEC);
			if (i < results->rawlen - 1) Serial.print(", "); //',' not needed for last one
		}
		if (!(i % 8))  Serial.println("");
	}
	Serial.println("");                    // Newline
}

//+=============================================================================
// Dump out the decode_results structure.
//
void  dump_code(decode_results *results)
{
	// Start declaration
	Serial.print("unsigned int  ");          // variable type
	Serial.print("rawData[");                // array name
	Serial.print(results->rawlen - 1, DEC);  // array size
	Serial.print("] = {");                   // Start declaration

	// Dump data
	for (int i = 1; i < results->rawlen; i++) {
		Serial.print(results->rawbuf[i] * USECPERTICK, DEC);
		if (i < results->rawlen - 1) Serial.print(","); // ',' not needed on last one
		if (!(i & 1))  Serial.print(" ");
	}

	// End declaration
	Serial.print("};");  // 

	// Comment
	Serial.print("  // ");
	encoding(results);
	Serial.print(" ");
	ircode(results);

	// Newline
	Serial.println("");

	// Now dump "known" codes
	if (results->decode_type != UNKNOWN) {

		// Some protocols have an address
		if (results->decode_type == PANASONIC) {
			Serial.print("unsigned int  addr = 0x");
			Serial.print(results->address, HEX);
			Serial.println(";");
		}

		// All protocols have data
		Serial.print("unsigned int  data = 0x");
		Serial.print(results->value, HEX);
		Serial.println(";");
	}
}

void set_state(const state st)
{
	device_state = st;
	Serial.print("setting state=");
	switch (device_state)
	{
	case idle: Serial.println("idle"); break;
	case send: Serial.println("send"); break;
	case recv: Serial.println("recv"); break;
	case recv_done: Serial.println("recv_done"); break;
	case digital_out: Serial.println("digital_out"); break;
	case digital_in: Serial.println("digital_in"); break;
	default:
		break;
	}
}

void loop() {
	/*if (millis() - last_refresh_time >= refresh_interval)
	{
		//last_refresh_time += refresh_interval;
		last_refresh_time = millis();
		Serial.print("current state=");
		switch (device_state)
		{
		case idle: Serial.println("idle"); break;
		case send: Serial.println("send"); break;
		case recv: Serial.println("recv"); break;
		case recv_done: Serial.println("recv_done"); break;
		case digital_out: Serial.println("digital_out"); break;
		case digital_in: Serial.println("digital_in"); break;
		default:
			break;
		}
	}*/

	if (device_state == send)
	{
		for (int i = 0; i < 3; i++) {
			//Serial.print(type);
			//Serial.print(" - sending: ");
			//Serial.print(d, HEX);
			//Serial.print(" / ");
			//Serial.println(b, DEC);

			//char buffer[20];
			//sprintf (buffer, "Sending type=%s data=%lx bits=%d", type, d, b);
			//Serial.println(buffer);

			if (strstr("NEC", type) != NULL)
			{
				Serial.println("sendNEC");
				irsend.sendNEC(d, b); // 0x48B78877, 32
			}
			else if (strstr("RC5", type) != NULL)
			{
				Serial.println("RC5 - sending\n");
				irsend.sendRC5(d, b);
			}
			else if (strstr("RC6", type) != NULL)
			{
				Serial.println("RC6 - sending\n");
				irsend.sendRC6(d, b);
			}
			else if (strstr("SONY", type) != NULL)
			{
				Serial.println("Sony - sending\n");
				irsend.sendSony(d, b);
			}

			delay(40);
		}

		set_state(idle);
	}
	else if (device_state == digital_out)
	{
		Serial.println("Digital out");
		Serial.println(d, DEC);
		Serial.println(b, DEC);

		if (d == 2 || d == 3 || d == 4 || d == 5 || d == 6 || d == 7 || d == 8 || d == 9 || d == 10 || d == 12)
		{
			pinMode(d, OUTPUT);
			if (b == 1)
			{
				digitalWrite(d, HIGH);
			}
			else
			{
				digitalWrite(d, LOW);
			}
		}
		else
		{
			Serial.println("Invalid data");
		}

		set_state(idle);
	}
	else if ((device_state == recv || device_state == idle || device_state == recv_done) && irrecv.decode(&results))
	{
		// Grab an IR code
		dump_info(&results);           // Output the results
		//dump_raw(&results);            // Output the results in RAW format
		//dump_code(&results);           // Output the results as source code
		//Serial.println("");           // Blank line between entries

		// Serial.println("Decoded IR");

		switch (results.decode_type) {
		default:
		case UNKNOWN:      sprintf(ir_recv_type, "UNKNOWN");       break;
		case NEC:          sprintf(ir_recv_type, "NEC");           break;
		case SONY:         sprintf(ir_recv_type, "SONY");          break;
		case RC5:          sprintf(ir_recv_type, "RC5");           break;
		case RC6:          sprintf(ir_recv_type, "RC6");           break;
		case DISH:         sprintf(ir_recv_type, "DISH");          break;
		case SHARP:        sprintf(ir_recv_type, "SHARP");         break;
		case JVC:          sprintf(ir_recv_type, "JVC");           break;
		case SANYO:        sprintf(ir_recv_type, "SANYO");         break;
		case MITSUBISHI:   sprintf(ir_recv_type, "MITSUBISHI");    break;
		case SAMSUNG:      sprintf(ir_recv_type, "SAMSUNG");       break;
		case LG:           sprintf(ir_recv_type, "LG");            break;
		case WHYNTER:      sprintf(ir_recv_type, "WHYNTER");       break;
		case AIWA_RC_T501: sprintf(ir_recv_type, "AIWA_RC_T501");  break;
		case PANASONIC:    sprintf(ir_recv_type, "PANASONIC");     break;
		case DENON:        sprintf(ir_recv_type, "DENON");         break;
		}

		sprintf(ir_recv_buffer, "%s %x %d", ir_recv_type, results.value, results.bits);
		irrecv.resume();              // Prepare for the next value
		set_state(recv_done);
	}
}

// function that executes whenever data is received from master
// this function is registered as an event, see setup()
void receive_event(int how_many) {
	// stop if not idle, unless its recv_done - in which case you can break out of recv_done state via another i2c command
	if (device_state != idle && device_state != recv_done)
	{
		Serial.print("drop state=");
		Serial.println(device_state, DEC);
		return;
	}

	int counter = 0;
	char str[50];
	const char split_char = ' ';
	char *data;
	char *bitlen;
	char buffer[100];
	int n;

	//while (1 < Wire.available()) { // loop through all but the last
	while (Wire.available())
	{
		char c = Wire.read(); // receive byte as a character
		//Serial.print(c);         // print the character
		str[counter] = c;
		counter++;
	}
	str[counter] = '\0';
	// Serial.print("str=");
	// Serial.println(str);
	d = 0;
	b = 0;

	data = strchr(str, split_char);
	if (data != NULL)
	{
		*data = 0;
		data++;

		bitlen = strchr(data, split_char);
		if (bitlen != NULL)
		{
			*bitlen = 0;
			bitlen++;
			//Serial.print("bitlen=");
			//Serial.println(bitlen);
			b = atoi(bitlen);
		}

		//Serial.print("data=");
		//Serial.println(data);
		//Serial.print("strlen=");
		//Serial.println(strlen(data), DEC);
		d = strtoul(data, NULL, 16);
	}

	strcpy(type, str);
	//int x = Wire.read();    // receive byte as an integer  
	n = sprintf(buffer, "type=%s data=%lx bits=%d\n", type, d, b);
	Serial.println(buffer);

	if (type[0] == 0)
	{
		// empty string, ignore - this will also happen with i2c scan
	}
	else if (strstr("NEC", type) != NULL || strstr("RC5", type) != NULL || strstr("RC6", type) != NULL || strstr("SONY", type) != NULL)
	{
		//Serial.println("found valid type");
		set_state(send);
	}
	else if (strstr("DO", type) != NULL)
	{
		set_state(digital_out);
	}
	else if (strstr("DI", type) != NULL)
	{
		set_state(digital_in);
	}
	else if (strstr("RECV", type) != NULL)
	{
		set_state(recv);
	}
}

// function that executes whenever data is requested by master
// this function is registered as an event, see setup()
void request_event()
{
	if (device_state == digital_in)
	{
		//Serial.print("Digital in: ");
		//Serial.print(d, DEC);
		//Serial.print(" value: ");
		const auto value = digitalRead(d);
		//Serial.println(value, DEC);
		Wire.write(value);

		set_state(idle);
	}
	else if (device_state == recv_done)
	{
		//Wire.write(buffer); //static_cast<long>(ir_recv_value)
		//Serial.print("Value: ");
		//Serial.println(ir_recv_value, DEC);
		Wire.write(ir_recv_buffer);
		//Serial.println(ir_recv_buffer);
		set_state(idle);
	}
	else
	{
		Wire.write("none");
	}
}
