#!/usr/local/cs//bin/python3

import sys #to get arguements
#from enum import IntEnum, auto
no_inconsistencies_found = 0
superBlock = None
groups = []
inodes = []
freeBlocks = []
freeInodes = []
directories = []
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
        self.firstNonReservedInode = int(parsedLine[8])
        #self.firstUnreservedBlock = self.firstUnreservedInode

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
        self.lastInodeChange = parsedLine[7]
        self.timeOfLastModification = parsedLine[8]
        self.timeOfLastAccess = parsedLine[9]
        self.fileSize = int(parsedLine[6])
        self.numBlocks = int(parsedLine[6])

class Directory:
    def __init__(self,csv_line):
        parsedLine = csv_line.split(',')
        self.name = parsedLine[0]
        self.parentInodeNum= int(parsedLine[1])
        self.logicalByteOffset= int(parsedLine[2])
        self.inodeNum= int(parsedLine[3])
        self.entryLen= int(parsedLine[4])
        self.nameLen= int(parsedLine[5])
        self.name= parsedLine[6][:-1]
        #print(self.name, end="")

class Indirect:
    def __init__(self, csv_line):
        parsedLine = csv_line.split(',')
        self.name = parsedLine[0]
        self.owningInodeNum = int(parsedLine[1])
        self.indirectionLevel = int(parsedLine[2])
        self.logicalOffset = int(parsedLine[3])
        self.indirectBlockNum = int(parsedLine[4])
        self.referencedBlockNum = int(parsedLine[5])
'''
class Block:
    def __init__(self, blockType, blockNum, blockLevel, offset, inodeNum):
        self.blockType = blockType
        self.blockNum = blockNum
        self.blockLevel = blockLevel
        self.offset = offset
        self.inodeNum = inodeNum
        '''
'''class Spot(IntEnum):
    FREE = auto()
    RESERVED = auto()
    TAKEN = auto()
'''
#define numeric constants to use, values do not matter
FREE = 1
RESERVED = 2
TAKEN = 3

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

def addObjectFromCSVLine(line):
    global no_inconsistencies_found
    global superBlock
    global groups
    global inodes
    global freeBlocks
    global freeInodes
    global directories
    global indirects

    parseLine = line.split(',')
    if parseLine[0] == 'SUPERBLOCK':
        object = SuperBlock(line)
        superBlock = object
    elif parseLine[0] == 'GROUP':
        object = Group(line)
        groups.append(object)
    elif parseLine[0] == 'BFREE':
        object = FreeBlock(line)
        freeBlocks.append(object)
    elif parseLine[0] == 'IFREE':
        object = FreeInode(line)
        freeInodes.append(object)
    elif parseLine[0] == 'INODE':
        object = Inode(line)
        inodes.append(object)
    elif parseLine[0] == 'DIRENT':
        object = Directory(line)
        directories.append(object)
    elif parseLine[0] == 'INDIRECT':
        object = Indirect(line)
        indirects.append(object)
    else:
        errorExitOne("Error, csv file not formatted properly")

def initializeDataFromCSV(csv_file):
    for line in csv_file:
        addObjectFromCSVLine(line)

#returns true if block is valid
def checkBlockValidity(block, lastBlock):
    if block.blockNum < 0 or block.blockNum > lastBlock:
        print('error, invalid block')
        return False
    #if block.blockNum < firstUnreservedBlock :
     #   print('Error, reserved block')
      #  return False
    return True

def checkIfFreeOrReserved(blocks, block):
    if blocks[block.blockNum] == FREE:
        print('Error, allocated Free Block')
        return True
    elif blocks[block.blockNum] == RESERVED:
        print('Error, block is reserved')
        return False
    else:
        return True

def addAllBlocks(blockList):
    global FREE
    global RESERVED
    global no_inconsistencies_found
    global superBlock
    global groups
    global inodes
    global freeBlocks
    global freeInodes
    global directories
    global indirects
    #add reserved blocks
    #since only 1 block, we can find all restricted blocks through first group
    firstUnreservedBlock = groups[0].firstNonReservedInode + (superBlock.inodeSize * superBlock.totalInodes/superBlock.blockSize)
    blockList[:firstUnreservedBlock] = firstUnreservedBlock*[RESERVED]

    #addFreeBlocks
    for block in freeBlocks:
        if(checkBlockValidity(block, superBlock.totalBlocks - 1)):
            blockList[block.blockNum] = [FREE]
    
    #add indirectBlocks
    for block in indirects:
        if(checkBlockValidity(block, superBlock.totalBlocks - 1) and checkIfFreeOrReserved(blockList, block)):
            blockList[block.blockNum] = blockList[block.blockNum].append(block)

    for block in


    #add

    #for

#reports if
#  any block is <0 or > highest block
#  any block takes a reserved block space
#  any block is not referenced by a freelist and not referenced by a file
#  any block is refereneced by a freelist and a file
#  any block is referenced by multiple files
def blockConsistencyAudit():
    global no_inconsistencies_found
    global superBlock

    #create list stucture for all blocks
    #add reserved list to structure
    #add free lists to structure
    #create list of empty lists, one lise for each open block
    blocks = [[] for i in range (superBlock.totalBlocks)]
    addAllBlocks(blocks)


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
    blockConsistencyAudit()

    csv_file.close()
    exit(no_inconsistencies_found)


if __name__ == '__main__':  # run main function
    main()
