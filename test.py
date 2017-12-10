#!/usr/bin/python

import time
import RPi.GPIO as GPIO
from os import system

#Number of active Nixie Tubes
tubes = 6

# GPIO mapping
gpioData = 11
gpioSerialClock = 12
gpioParallelLoad = 8


#Send a pulse out the indicated strobe pin
def pulseGPIO(pin, direction=True, duration=0.001):
	GPIO.output(pin, direction)
	time.sleep(duration)
	GPIO.output(pin, not(direction))


#Display digits on Nixies, bit by bit
def nixiebit(digit):
	digit = int(max(0, min( int(digit), 15)))
	for d in reversed(range (0, 4)):
		GPIO.output(gpioData, bool(digit & (1 << d)) )
		pulseGPIO(gpioSerialClock)


#Display String of digits
def nixieString(digitString):
	for c in reversed(str(digitString)):
		try:
			nixiebit(int(c))
		except ValueError:
			nixiebit(15)
	#Display number on Nixies
	pulseGPIO(gpioParallelLoad)
	#print 'Outputted to Nixies'


#Ask User for string to display
def userNixieString():
	userInput = str(raw_input('Number to Display: '))
	if userInput == 'exit':
		return False
	print tubes
	nixienumber = userInput.rjust(tubes,'a')
	print nixienumber
	nixieString(nixienumber)
	return True


#Sweep Counting nixie display
def sweepNixieString():
	emptyString=' ' * (tubes - 1)
	for digit in '1234567890':
		for i in range (0,tubes):
			x=emptyString[:i] + digit + emptyString[i:]
			#print x
			nixieString(x)
			time.sleep(0.1)
		for i in range (tubes-2, 0, -1):
			x=emptyString[:i] + digit + emptyString[i:]
			#print x
			nixieString(x)
			time.sleep(0.1)
	return True


#init the GPIO pins
def nixieInit():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(gpioParallelLoad, GPIO.OUT)
	GPIO.setup(gpioSerialClock, GPIO.OUT)
	GPIO.setup(gpioData, GPIO.OUT)

	GPIO.output(gpioParallelLoad, False)
	GPIO.output(gpioSerialClock, False)
	GPIO.output(gpioData, False)


if __name__=="__main__":
	nixieInit()

	#I just have a thing for clean screens...
	system("clear")

	keepLooping=True
	print 'Hit Ctrl-C to Exit'
	try:
		while keepLooping:
			#keepLooping=sweepNixieString()
			keepLooping=userNixieString()
	except:
		# Do normal cleanup
		print "Exception detected"

	#Cleanup...
	nixieString('a' * tubes)
	print "Exiting..."
	GPIO.cleanup()
	#system("clear")
