#!/usr/local/cs//bin/python3

import sys #to get arguements
from enum import IntEnum, auto
no_inconsistencies_found
superBlock = None
groups = []
inodes = []
freeBlocks = []
freeInodes = []
dirent = []
indirects = []

class SuperBlock:
    '''
    def __init__(self, csv_file):  # //totalBlocks, totalInodes, firstNonReservedInode):
        firstLine = csv_file.readline()

    '''
    def __init__(self, csv_line):
        parsedLine = csv_line.split(',')
        self.name = parsedLine[0]
        self.totalBlocks = int(parsedLine[1])
        self.totalInodes = int(parsedLine[2])
        self.blockSize = int(parsedLine[3])
        self.inodeSize = int(parsedLine[4])
        self.blocksPerGroup = int(parsedLine[5])
        self.inodesPerGroup = int(parsedLine[6])
        self.firstNonReservedInode = int(parsedLine[7])
class Group:
    def __init__(self, csv_line):
        parsedLine = csv_line.split(',')
        self.name = parsedLine[0]
        self.groupNum = int(parsedLine[1])
        self.totalBlocks = int(parsedLine[2])
        self.totalInodes = int(parsedLine[3])
        self.numFreeBlocks = int(parsedLine[4])
        self.numFreeInodes = int(parsedLine[5])
        self.blockBitmap = int(parsedLine[6])
        self.inodeBitmap = int(parsedLine[7])
        self.firstUnreservedBlock = int(parsedLine[8])

class FreeBlock:
    def __init__(self,csv_line):
        parsedLine = csv_line.split(',')
        self.name = parsedLine[0]
        self.blockNum= int(parsedLine[1])

class FreeInode:
    def __init__(self,csv_line):
        parsedLine = csv_line.split(',')
        self.name = parsedLine[0]
        self.blockNum= int(parsedLine[1])

class Inode:
    def __init__(self, csv_line):
        parsedLine = csv_line.split(',')
        self.name = parsedLine[0]
        self.inodeNum = int(parsedLine[1])
        self.fileType = parsedLine[2]
        self.mode = parsedLine[3]
        self.owner = parsedLine[4]
        self.group = parsedLine[5]
        self.linkCount = int(parsedLine[6])
        self. = int(parsedLine[7])
        self.firstUnreservedBlock = int(parsedLine[8])

class Block:
    def __init__(self, blockType, blockNum, blockLevel, offset, inodeNum):
        self.blockType = blockType
        self.blockNum = blockNum
        self.blockLevel = blockLevel
        self.offset = offset
        self.inodeNum = inodeNum


class Spot(IntEnum):
    FREE = auto()
    RESERVED = auto()
    TAKEN = auto()

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

def objectFromCSVLine(line):
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

def intializeDataFromCSV(csv_file):
    for line in csv_file:
        object = objectFromCSVLine(line)

#returns true if block is valid
def checkBlockValidity(block, firstUnreservedBlock, lastBlock):
    if block.blockNum < 0 or block.blockNum > lastBlock:
        print('error, invalid block')
        return False
    if block.blockNum < firstUnreservedBlock :
        print('Error, reserved block')
        return False
    return True

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

    #create list of empty lists, one lise for each open block
    blocks = [[] for i in range (superBlock.totalBlocks)]

def inodeAllocationAudit(csv_file):
    global no_inconsistencies_found


def directoryConsistencyAudit(csv_file):
    global no_inconsistencies_found


def main():


    no_inconsistencies_found = 0
    # first get open input file
    csv_file = getCSVFile()

    initializeDataFromCSV(csv_file)

    # totalBlocks, totalInodes, first nonreservedInode
    superBlock = SuperBlock(csv_file)

    blockConsistencyAudit(csv_file)

    csv_file.close()
    exit(no_inconsistencies_found)


if __name__ == '__main__':  # run main function
    main()
