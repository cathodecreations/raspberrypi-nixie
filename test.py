#!/usr/bin/python

#import modules
import sys
import time
import RPi.GPIO as GPIO
import xml.etree.ElementTree as ET
import os
from os import system

#Number of active Nixie Tubes
tubes = 6

#Decimal to Binary function
def d2b(y):
#	return bin(int(y))[2:]
        return d2b(y/2) + [y%2] if y > 1 else [y]

#Send a pulse out the indicated strobe pin
def pulseGPIO(pin):
	GPIO.output(pin, True)
	time.sleep(0.001)
	GPIO.output(pin, False)


#Display digits on Nixies, bit by bit
def nixiebit(digit):
	digit = int(max(0, min( int(digit), 15)))
	for d in range (3, -1, -1):
		GPIO.output(11, bool(digit & (1 << d)) )
		pulseGPIO(12)
#	digitbin = d2b(x)
#	#print digitbin
#	arrsize = len(digitbin)	
#	for d in range (0, 4-arrsize):
#		GPIO.output(11, False)
#		pulseGPIO(12)
#		#print 'Wrote: 0 {EOD}'
#	for d in range (0, min(arrsize,4)):
##		GPIO.output(11, digitbin[d] == '1')
#		GPIO.output(11, bool(digitbin[d]))
#		pulseGPIO(12)
#		#print 'Wrote: ',digitbin[d]


#Display String of digits
def nixieString(x):
	digitString = str(x)
	lastIndex = len(digitString) - 1
	#print "Number length: ",i
	for i in range(lastIndex, -1, -1):
		try:
			nixiebit(int(digitString[i]))
		except ValueError:
			nixiebit(15)
	#Display number on Nixies
	pulseGPIO(8)
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
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

GPIO.output(8, False)
GPIO.output(11, False)
GPIO.output(12, False)


#I just have a thing for clean screens...
system("clear")

emptyString='     '
keepLooping=True;
print 'Hit Ctrl-C to Exit'
try:
	while keepLooping:
		#keepLooping=sweepNixieString()
		keepLooping=userNixieString()
except:
	# Do normal cleanup
	print "Exception detected"

#Cleanup...
nixieString('aaaaaa')
print "Exiting..."
GPIO.cleanup()
#system("clear")


	
