#include "FrameDisplay.h"

FrameDisplay::FrameDisplay()
{
	frame[0] = 0;
	frame[1] = 0;
	frame[2] = 0;
	frame[3] = 0;

	frame[4] = 0;
	frame[5] = 0;
	frame[6] = 0;
	frame[7] = 0;
	//= { 0, 0, 0, 0,  0, 0, 0, 0 }; //1,1,1,1, 1,1,1,1
	// if you use uint64_t for frame storage, then you have 16 bits on left and right side of undisplayed bits
	// so you've got to use an offset to draw and read of the center of this wider frame
	frame_offset = 0; //0 with uint32_t frame
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
	
}


FrameDisplay::~FrameDisplay()
{
}


void FrameDisplay::letter_to_frame(int start_row, int start_column, const int letter_height, const int letter_width, const uint64_t image) {
	// out of bounds
	if (start_row + letter_height >= 8)
		return;
	//if (start_column + letter_width >= 32)
	//  return;

	for (int i = 0; i < letter_height; ++i) {
		uint32_t row = (image >> i * 8) & 0xFF;
		//Serial.print("i=");
		//Serial.print(i, DEC);
		//Serial.print(" row=");
		//Serial.print(row, BIN);
		for (int j = 0; j < letter_width; ++j) {
			bitWrite(frame[start_row + i], frame_offset + start_column + j, bitRead(row, j));
			Serial.print(" frame_offset + start_column + j=");
			Serial.println(frame_offset + start_column + j, DEC);
		}
		//Serial.print(" frame=");
		//Serial.println(FRAME[i], BIN);
	}
}

void FrameDisplay::spacer_to_frame(int column, const int start_row, int end_row) {
	--end_row;
	for (int i = start_row; i < end_row; ++i) {
		bitWrite(frame[i], frame_offset + column, false);
	}
}

uint32_t FrameDisplay::reverse_bits(uint32_t n) { // this should no longer work - its 64 bit
	n = (n >> 1) & 0x55555555 | (n << 1) & 0xaaaaaaaa;
	n = (n >> 2) & 0x33333333 | (n << 2) & 0xcccccccc;
	n = (n >> 4) & 0x0f0f0f0f | (n << 4) & 0xf0f0f0f0;
	n = (n >> 8) & 0x00ff00ff | (n << 8) & 0xff00ff00;
	n = (n >> 16) & 0x0000ffff | (n << 16) & 0xffff0000;
	return n;
}

void FrameDisplay::display_frame(LedControl led_control, const bool reverse) {
	for (int row = 7; row > -1; --row) {
		int mtx = num_devices - 1;
		int mtxColumn = 0;
		uint64_t frameRow; //32 vs 64 diff spot

		if (reverse) {
			frameRow = reverse_bits(frame[row]);
		}
		else {
			frameRow = frame[row];
		}

		//Serial.print("frame=");
		//Serial.println(frameRow, HEX);

		for (int column = 0; column < 32; ++column) {
			led_control.setLed(mtx, row, mtxColumn, bitRead(frameRow, frame_offset + column));
			//Serial.print(" FRAME_OFFSET + column=");
			//Serial.println(FRAME_OFFSET + column, DEC);
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

int FrameDisplay::chars_to_frame(char *buffer, const int buffer_size, const int row = 0) {
	int column = 0;
	//const int siz = strlen(buffer);
	//Serial.print("siz=");
	//Serial.println(buffer_size, DEC);

	for (int i = 0; i < buffer_size; ++i) {
		const char *ptr = strchr(alphanum, buffer[i]);
		Serial.print("! i=");
		Serial.print(i, DEC);
    Serial.print(" buffer[i]=");
    Serial.print(buffer[i], DEC);
		if (ptr) {
			const int index = ptr - alphanum;
			Serial.print(" image:");
			Serial.print(index, DEC);
			Serial.print(" letterwidths[index]=");
			Serial.println(letterwidths[index], DEC);
			letter_to_frame(row, column, 5, letterwidths[index], images[index]);
			spacer_to_frame(column + letterwidths[index], 1, 6);
			column += letterwidths[index] + 1; // default width and spacing
		}
		else {
			Serial.println(" image: unknown"); //, using space
			/*if (column != 0) {
				spacer_to_frame(column + 1, 1, 6);
				column += 1;
			}*/
		}

		/*if (column >= 32) {
		Serial.println("break");
		break;
		}*/ // TODO: we should be able to write on both sides of the invisible frame portions?
	}

	return column;
}

int FrameDisplay::rectangle_to_frame(int start_column, int start_row, int height, int width, bool infill = false) {
	for (int i = 0; i < height; ++i) {
		for (int j = 0; j < width; ++j) {
			bitWrite(frame[start_row + i], frame_offset + start_column + j, infill || i == 0 || i == height - 1 || j == 0 || j == width - 1);
		}
	}
	return start_column + width;
}

int FrameDisplay::pth(const int x, const int y) {
	return sqrt(pow(x, 2) + pow(y, 2));
}

int FrameDisplay::circle_to_frame(int start_column, int start_row, const int radius, bool infill = false) {
	const int width = radius;
	const int length = radius*1.5;

	for (int y = width; y >= -width; y -= 2) {
		for (int x = -length; x <= length; ++x) {

			if ((int)pth(x, y) == radius) {
				//cout << "*"; 
				bitWrite(frame[start_row + x], frame_offset + start_column + y, true);
			}
			else {
				//cout << " ";
				bitWrite(frame[start_row + x], frame_offset + start_column + y, false);
			}

		}
		//cout << "\n";
	}

	return start_column + width;
}

void FrameDisplay::shift_frame_left(const int amount = 1) {
	// shift frame 1 bit to the left - if shifted further than FRAME_OFFSET, bits may be lost
	for (int j = 0; j < 8; j++) {
		frame[j] = frame[j] << amount;
	}
}

void FrameDisplay::shift_frame_right(const int amount = 1) {
	// shift frame 1 bit to the left
	for (int j = 0; j < 8; j++) {
		frame[j] = frame[j] >> amount;
	}
}

void FrameDisplay::clear_frame() {
  for (int i = 0; i < 8; i++) {
    frame[i] = 0;
  }
}

