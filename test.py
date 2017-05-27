#!/usr/bin/python

#import modules
from time import sleep
import RPi.GPIO as GPIO
from subprocess import check_output, call
from datetime import datetime, date
from pytz import timezone

#Number of active Nixie Tubes
tubes = 6
tz = timezone('US/Eastern')

#Send a pulse out the indicated strobe pin
def pulseGPIO(pin, direction=True, duration=0.001):
	GPIO.output(pin, direction)
	sleep(duration)
	GPIO.output(pin, not(direction))


#Display digits on Nixies, bit by bit
def nixiebit(digit):
	digit = int(max(0, min( int(digit), 15)))
	for d in reversed(range (0, 4)):
		GPIO.output(11, bool(digit & (1 << d)) )
		pulseGPIO(12)


#Display String of digits
def nixieString(digitString):
	for c in reversed(str(digitString)):
		try:
			nixiebit(int(c))
		except ValueError:
			nixiebit(15)
	#Display number on Nixies
	pulseGPIO(8)
	#print 'Outputted to Nixies'
	

#Ask User for string to display
def userNixieString():
	userInput = str(raw_input('Number to Display ( or "exit" ) : '))
	if userInput == 'exit':
		return False
	print tubes
	nixienumber = userInput.rjust(tubes,'a')
	print nixienumber
	nixieString(nixienumber)
	return True

#Sweep Counting nixie display
def sweepNixieString():
	for digit in '1234567890':
		for i in range (0,tubes):
			x=emptyString[:i] + digit + emptyString[i:]
			#print x
			nixieString(x)
			sleep(0.1)
		for i in range (tubes-2, 0, -1):
			x=emptyString[:i] + digit + emptyString[i:]
			#print x
			nixieString(x)
			sleep(0.1)
	return True



def mpcString():
	output = check_output(["/usr/bin/mpc", "status"])
	x = output.splitlines()
	y = x[1].split()
	if (y[0] != "[playing]" ):
		return dateTimeString()
	z=y[3].strip("(%)").rjust(2,"0") + y[2].split("/", 2)[1].replace(":","").rjust(4," ")
	#print z
	nixieString(z)
	sleep(0.1)
	return True
	


def dateTimeString():
#	nixieString( datetime.now().strftime(" %H%M ") )
	timeStamp = datetime.now(tz)
	if timeStamp.second == 13 and  dateTimeString.offset == 0 :
		dateTimeString.offset=1
		dateTimeString.frame = 0
	if dateTimeString.offset != 0:
		x = timeStamp.strftime(" %H%M%S %Y %m %d      ")
		if dateTimeString.offset > (len(x) - 6):
			dateTimeString.offset=0
		elif dateTimeString.frame > 15:
			dateTimeString.offset += dateTimeString.direction
			dateTimeString.frame = 0
	elif timeStamp.microsecond < 500000:
#		x = timeStamp.strftime("%Y%m%d %H%M%S%f") 
		x = timeStamp.strftime("%H%M%S") 
	else:
		x = timeStamp.strftime("%H%M  ") 
#		x = timeStamp.strftime("%Y%m%d %H%M%S%f") 
#	if dateTimeString.offset > (len(x) - 9):
#		dateTimeString.offset=(len(x) - 9)
#		dateTimeString.direction=-1
#		dateTimeString.frame = -12
#	elif dateTimeString.offset < 0:
#		dateTimeString.offset=0
#		dateTimeString.direction=1
#		dateTimeString.frame = -6
#	#dateTimeString.offset=(len(x) - 9)
#	dateTimeString.offset=0
	nixieString( x[dateTimeString.offset:dateTimeString.offset+6] )
	sleep(0.1)
	dateTimeString.frame += 10
	return True;

dateTimeString.offset = 0
dateTimeString.direction = 1
dateTimeString.frame = 0

#init the GPIO pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

GPIO.output(8, False)
GPIO.output(11, False)
GPIO.output(12, False)


#I just have a thing for clean screens...
call("clear")

emptyString='     '
keepLooping=True;
print 'Hit Ctrl-C to Exit'
try:
	while keepLooping:
		#keepLooping=sweepNixieString()
		#keepLooping=dateTimeString()
		keepLooping=mpcString()
		#keepLooping=userNixieString()
except KeyboardInterrupt:
	# Do normal cleanup
	print "Exception detected"

#Cleanup...
nixieString('aaaaaa')
print "Exiting..."
GPIO.cleanup()
#call("clear")


	
