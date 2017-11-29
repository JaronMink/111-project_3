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

def blockFromCSVLine(line):
    global superBlock
    parseLine = line.split(',')
    if parseLine[0] == 'SUPERBLOCK':
        return superBlock
    elif parseLine[0] == 'GROUP':
        #first unreserved block is the block of the i-nodes, plus the how many blocks the inodeTable is
        firstUnreservedBlockInGroup = int(parseLine[8]) + (superBlock.inodeSize*superBlock.totalInodes)/superBlock.blockSize 
        return Group(int(parseLine[4]), int(parseLine[5]), firstUnreservedBlockInGroup)
    elif parseLine[0] == 'BFREE' || parseLine[0] == 'INDIRECT' || 
        return Block(
    
class Block:
    #blockType  #Free, Reserved, Taken
    #blockNum
    #blockLevel
    #offset
    #inodeNum

    def __init__(self, blockType, blockNum, blockLevel, offset, inodeNum):
        self.blockType = blockType
        self.blockNum = blockNums
        self.blockLevel = blockLevel
        self.offset = offset
        self.inodeNum = inodeNum

class Spot(IntEnum):
    FREE = auto()
    RESERVED = auto()
    TAKEN = auto()

    
class SuperBlock:
    #totalBlocks
    #totalInodes
    #firstNonReservedInode
    
    def __init__(self, csv_file): #//totalBlocks, totalInodes, firstNonReservedInode):
        firstLine = csv_file.readline()
        parsedLine = firstLine.split(',')
        self.totalBlocks = int(parsedLine[1])
        self.totalInodes = int(parsedLine[2])
        self.blockSize = int(parsedLine[3])
        self.inodeSize = int(parsedLine[4])
        self.firstNonReservedInode = int(parsedLine[7])

class Group:
    def __init__(self, numBlocks, numInodes, firstUnreservedBlock):
        self.numBlocks = numBlocks
        self.numInodes = numInodes
        self.firstUnreservedBlock = firstUnreservedBlock

def addAllBlocks(blocks, csv_file):
    
    for line in csv_file:
        block =  
        
#reports if
#  any block is <0 or > highest block
#  any block takes a reserved block space
#  any block is not referenced by a freelist and not referenced by a file
#  any block is refereneced by a freelist and a file
#  any block is referenced by multiple files
def blockConsistencyAudit(csv_file):
    global no_inconsistencies_found
    global superBlock

    #create list stucture for all blocks
    #add reserved list to structure
    #add free lists to structure

    #create list of none for blocks
    blocks = [None]*superBlock.totalBlocks

    addAllBlocks(blocks, csv_file)
    
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
    global superBlock
    
    no_inconsistencies_found = 0
    #first get open input file    
    csv_file = getCSVFile()

    #totalBlocks, totalInodes, first nonreservedInode
    superBlock = SuperBlock(csv_file)
        
    blockConsistencyAudit(csv_file)
            
    csv_file.close()
    exit(no_inconsistencies_found)

    
if __name__ == '__main__': #run main function
    main()

