#!/usr/bin/python

#import modules
import socket
from time import sleep
import RPi.GPIO as GPIO
from subprocess import check_output, call, CalledProcessError
from datetime import datetime, date
from pytz import timezone

try:
	from mpd import MPDClient, ConnectionError
	mpdClient = MPDClient()
except ImportError:
	print 'python-mpd not installed disabling mpdsupport'
	mpdClient = None

#Number of active Nixie Tubes
tubes = 6
TZ = timezone('US/Eastern')
MPD_HOST = "localhost"
MPD_PORT = "6600"
FRAME_TIME = 0.1


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


def mpcString(client):
	if(client):
		if (mpcString.mpcHoldoff > 0):
			mpcString.mpcHoldoff -= 1
			if (mpcString.mpcHoldoff <= 0):
				try:
					client.connect(MPD_HOST, MPD_PORT)
				except socket.error:
					print "Failed to reconnect MPD client"
			return dateTimeString()
		try:
			status=client.status()
			if(mpcString.oldVolume!=status['volume']):
				mpcString.volumeDisplayTimer = 10
				mpcString.oldVolume = status['volume']
			if(mpcString.volumeDisplayTimer > 0):
				mpcString.volumeDisplayTimer -= 1
				nixieString("  "+status['volume'].rjust(2,"0")+"  ")
				sleep(FRAME_TIME)
				return True			
			#print status
			if(status['state']=="play"):
				#volume = status['volume']
				songid = status['songid']
				timeFields = status['time'].split(":")
				#elTime = int(timeFields[0])
				elMin, elSec = divmod(int(timeFields[0]), 60)
				#totTime = time(second=int(timeFields[1]))
				digitString = songid.rjust(2,"0") + str(elMin).rjust(2," ") + str(elSec).rjust(2,"0")
				#print digitString
				nixieString(digitString)
				sleep(FRAME_TIME)
				return True
		except (socket.error, ConnectionError):
			print "ConnectionError"
			mpcString.mpcHoldoff = 300
			try:
				client.disconnect()
#				client.timeout = FRAME_TIME
#				client.connect(MPD_HOST, MPD_PORT)
			except (socket.error, ConnectionError):
				print "Cleanup-ConnectionError"
	return dateTimeString()
mpcString.oldVolume = 0
mpcString.volumeDisplayTimer = 0
mpcString.mpcHoldoff = 1

		

def dateTimeString():
#	nixieString( datetime.now().strftime(" %H%M ") )
	TIME_DATE_MAX_OFFSET = len(" HHMMSS CCYY MM DD      ") - 6
	timeStamp = datetime.now(TZ)
	if dateTimeString.offset > 0 and dateTimeString.offset <= TIME_DATE_MAX_OFFSET:
		x = timeStamp.strftime(" %H%M%S %Y %m %d      ")
		if dateTimeString.frame > 15:
			dateTimeString.offset += dateTimeString.direction
			dateTimeString.frame = 0
	elif timeStamp.second == 13:
		x = timeStamp.strftime(" %H%M%S %Y %m %d      ")
		dateTimeString.offset=1
		dateTimeString.frame = 0
	elif timeStamp.microsecond < 500000:
#		x = timeStamp.strftime("%Y%m%d %H%M%S%f") 
		x = timeStamp.strftime("%H%M%S") 
		dateTimeString.offset=0
	else:
		x = timeStamp.strftime("%H%M  ") 
		dateTimeString.offset=0
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
	sleep(FRAME_TIME)
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
#call("clear")

emptyString='     '
keepLooping=True
print 'Hit Ctrl-C to Exit'
try:
	if(mpdClient):
		mpdClient.timeout = FRAME_TIME
		#mpdClient.connect(MPD_HOST, MPD_PORT)
	while keepLooping:
		#keepLooping=sweepNixieString()
		#keepLooping=dateTimeString()
		keepLooping=mpcString(mpdClient)
		#keepLooping=userNixieString()
except KeyboardInterrupt:
	# Do normal cleanup
	print "Exception detected"

#Cleanup...
nixieString('aaaaaa')
print "Exiting..."
if(mpdClient):
	mpdClient.close()
	mpdClient.disconnect()
GPIO.cleanup()
#call("clear")


	
