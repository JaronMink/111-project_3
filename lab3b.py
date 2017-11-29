#!/usr/local/cs//bin/python3

import sys #to get arguements
from enum import IntEnum, auto

#no_inconsistencies_found = True

def errorExitNum(msg, num):
    print(msg)
    exit(num)
def errorExitOne(msg):
    errorExitNum(msg, 1)

def getCSVFile():
    if(len(sys.argv) < 2):
        errorExitOne('Error, must be provided an arugment in the format: \'*.csv\'')
    if(len(sys.argv) > 2):
        errorExitOne('Error, only one arugment is allowed')

    csv_file_str = sys.argv[1]
    if(csv_file_str[-4:] != '.csv'):
        errorExitOne('Error, arguement must be of the format \'*.csv\'')

    return open(csv_file_str, 'r') #open csv file in read only

#need to know why it is being used Free, Reserved, File
#one for each block/indone
#class Spot:
 #   type = "" #File, Inode, ReservedFile, Free


class Spot(IntEnum):
    FREE = auto()
    RESERVED = auto()
    TAKEN = auto()
    

#reports if
#  any block is <0 or > highest block
#  any block takes a reserved block space
#  any block is not referenced by a freelist and not referenced by a file
#  any block is refereneced by a freelist and a file
#  any block is referenced by multiple files
def blockConsistencyAudit(csv_file):
    global no_inconsistencies_found

    #blocks = [None]*5
    #blocks[1] = Spot.FREE
    #blocks[4] = Spot.TAKEN

    '''for block in blocks:
        if(block == Spot.FREE):
            print("Free is found")
        if(block == Spot.TAKEN):
            print("Taken is found")
    '''
    
    #create list stucture for all blocks
    #add reserved list to structure
    #add free lists to structure
    
    
    #create structure to store all block info,
    #for line in csv_file:
        #checks if valid
        #try to add to list, if space is already taken(non-null), error must be reported
        
        
        #checkBlockValidity
        #checkBlockReservations
        #check if already referenced by another file
        #
        #pri

    #check if any blocks were not referenced in block list at all
def inodeAllocationAudit(csv_file):
    global no_inconsistencies_found
    

def directoryConsistencyAudit(csv_file):
    global no_inconsistencies_found


def main():
    global no_inconsistencies_found
    no_inconsistencies_found = 0
    #first get open input file    
    csv_file = getCSVFile()

    blockConsistencyAudit(csv_file)
            
    csv_file.close()
    exit(no_inconsistencies_found)

    
if __name__ == '__main__': #run main function
    main()

