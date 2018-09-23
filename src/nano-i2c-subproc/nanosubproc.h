// nanosubproc.h

#ifndef _NANOSUBPROC_H
#define _NANOSUBPROC_H

#if defined(ARDUINO) && ARDUINO >= 100
	#include "arduino.h"
#else
	#include "WProgram.h"
#endif

typedef enum {
	idle,
	send,
	recv,
	recv_done,
	digital_out,
	digital_in
} state;

void set_state(state st);

#endif

