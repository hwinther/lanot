#picaxe 18x ''''microcontroller=18x''''
''''classname=LightControl''''
''''name
#define NAME "lc"
''''
''''capability
#define CAPABILITY "test"
''''
''''version
symbol VERSION = 1
''''
'#define DEBUG 'uncomment for debug mode

'*** Program constants
''''interface|serial|speed
symbol Serial0InputSpeed = T4800_8 ''''
symbol Serial0OutputSpeed = N4800_8
symbol Serial0InputPin = C.2
symbol Serial0OutputPin = B.7

symbol LedLeft1 = B.0
symbol LedRight1 = B.1
symbol LedSpot1 = B.2


init:
	setfreq m8 'set 8mhz
	high LedLeft1 'turn on LR
	high LedRight1
	pause 500
	high LedSpot1 'turn on spot
	pause 1000
	low LedSpot1 'turn of all
	low LedLeft1
	low LedRight1
	
	serout Serial0OutputPin, Serial0OutputSpeed, ("Init ",NAME," v",#VERSION,10)
	
	#ifdef DEBUG
		sertxd ("Init ",NAME," v",#VERSION,13,10)
	#endif
	
recvloop:

serial0recv:
	#ifdef DEBUG
		sertxd ("serin pre",13,10)
	#endif

	serin Serial0InputPin, Serial0InputSpeed, b0, b1
	
	#ifdef DEBUG
		sertxd ("serin post",#b0,"-",#b1,13,10)
	#endif DEBUG

	select case b0
	case 48 '0 ''''out|all_off=b48''''
		low LedSpot1
		low LedLeft1
		low LedRight1
		serout Serial0OutputPin, Serial0OutputSpeed, ("A0",10)
	case 49 '1 ''''out|main_on=b49''''
		high LedSpot1
		serout Serial0OutputPin, Serial0OutputSpeed, ("H1",10)
	case 50 '2 ''''out|left_on=b50''''
		high LedLeft1
		serout Serial0OutputPin, Serial0OutputSpeed, ("L1",10)
	case 51 '3 ''''out|right_on=b51''''
		high LedRight1
		serout Serial0OutputPin, Serial0OutputSpeed, ("R1",10)
	case 52 '4 ''''out|front_on=b52''''
		high LedLeft1
		high LedRight1
		serout Serial0OutputPin, Serial0OutputSpeed, ("LR1",10)
	case 53 '5 ''''out|all_on=b53''''
		high LedSpot1
		high LedLeft1
		high LedRight1
		serout Serial0OutputPin, Serial0OutputSpeed, ("A1",10)
	case 63 '? ''''out|capability=b63''''
		serout Serial0OutputPin, Serial0OutputSpeed, (CAPABILITY,10)
	case 86 'V ''''out|version=b86''''
		serout Serial0OutputPin, Serial0OutputSpeed, (NAME, " V",#VERSION,10)
	case 254 'no decorator
		serout Serial0OutputPin, Serial0OutputSpeed, ("TRY0-5",10)
	else ''''echo=undefined''''
		serout Serial0OutputPin, Serial0OutputSpeed, ("UNDEF-",#b0,"-",#b1,10)
		
	endselect
	goto serial0end 'ending

serial0end:
	' what to do
	goto recvloop
