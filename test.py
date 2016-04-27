#!/usr/bin/python

#import modules
import sys
import time
import RPi.GPIO as GPIO
import xml.etree.ElementTree as ET
import os
from os import system

#Decimal to Binary function
def d2b(y):
        return d2b(y/2) + [y%2] if y > 1 else [y]

#Display digits on Nixies, bit by bit
def nixiebit(x):
	digitbin = d2b(x)
	while len(digitbin) < 4:
		digitbin.insert(0,0)
	print digitbin
	d = 0
	digit = 1
	arrsize = len(digitbin)
	while digit <= 4:
		if d < arrsize:
			GPIO.output(11, bool(digitbin[d]))
			GPIO.output(12, True)
			time.sleep(0.001)
			GPIO.output(12, False)
			#print 'Wrote: ',digitbin[d]
			d+=1
		else:
			GPIO.output(11, False)
                        GPIO.output(12, True)
			time.sleep(0.001)
                        GPIO.output(12, False)
			#print 'Wrote: 0 {EOD}'
		digit+=1

#init the GPIO pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

GPIO.output(8, False)
GPIO.output(11, False)
GPIO.output(12, False)

#Number of active Nixie Tubes
tubes = 6

#I just have a thing for clean screens...
system("clear")

#Get Number
while 1:
        try:
		nixienumber = str(raw_input('Numer to Display: ')).rjust(tubes,'a')
		print tubes
		print str(nixienumber)
		if nixienumber == 'exit':
			#Cleanup...
			print "Exiting..."
			GPIO.cleanup()
			sys.exit()
		i = (len(str(nixienumber))) - 1
		#print "Number length: ",i
		while i >= 0:
			try:
				nixiebit(int(str(nixienumber)[i]))
			except ValueError:
				nixiebit(15)
			i-=1
		#Display number on Nixies
		GPIO.output(8, True)
		time.sleep(0.001)
		GPIO.output(8, False)
		#print 'Outputted to Nixies'
        except KeyboardInterrupt:
                print "Exiting..."
                #Cleanup...
                GPIO.cleanup()
		system("clear")
                break
