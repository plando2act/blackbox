#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print " .. aha.. Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

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
        else:
            print "Authentication error"

        # Stop
        #MIFAREReader.MFRC522_StopCrypto1()
        
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

