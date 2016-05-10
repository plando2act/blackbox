#!/usr/bin/env python
# -*- coding: utf8 -*-

# ****** Changelog
#Trying to receive the raw sector data via altered Read_sector code

import RPi.GPIO as GPIO
import MFRC522
import signal
#import hashlib  future function on using hashes.. must be man made 

#set Variables
continue_reading = True
tag_a1 = 83
tag_b1 = 00
tag_master = 255

# ****** Functions
# Function to check the tag encoding after existance check
# It will ingest the whole raw sector of 16 bytes
def tag_encode_ok( raw ):
   result = ( raw[1] + raw[2] + raw[3] ) - raw[15] - raw[0]
   return result;

# Function to check the tag encoding after existance check
def tag_whois( id_nr ):
   if id_nr == tag_a1:
   	whois = "tag a1"
   elif id_nr == tag_b1:
   	whois = "tag b1"
   elif id_nr == tag_master:
	print "Masterkey.. open all doors?"
	whois = "master tag"
   else:
	whois = "UNKNOWN CARD.. INTRUDER ALERT??"
   return whois;


# ******* Onetime stuff
# Set up phase - Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print " .. aha.. Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()
# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# ******* MAIN
# Start of main loop
print "House Guard Active - Present card to enter..."

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"
    
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])

        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)
	
        # Dump the data
        #MIFAREReader.MFRC522_DumpClassic1K(key, uid)

        # Authenticate for sector 8
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            #MIFAREReader.MFRC522_Read(8)
	    (rawsector) = MIFAREReader.MFRC522_ReadSector(8)
            MIFAREReader.MFRC522_StopCrypto1()
	    print "Raw Sector "+str(rawsector)
	    sectorlength=len(rawsector)
	    for i in range(0,sectorlength):
		print rawsector[i]
	    print rawsector
        else:
            print "Authentication error"

        # ******* Check tag-id and encoding
	name = tag_whois( rawsector[0] )
	print name
	checkresult = tag_encode_ok( rawsector )
	print checkresult
	
	#perform state changes here for team A and team B
	#print on display and go into wait loop

        # wait card removed 
        print "--- Remove Card ---"
        card_removed = False
        card_removed_counter = 5
        while not card_removed:
            (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
            if status != MIFAREReader.MI_OK:
                card_removed_counter = card_removed_counter-1
                if card_removed_counter==0:
                    card_removed = True
            else:
                card_removed_counter = 5
        print "--- Card removed---"
        print "Place card again please..."

