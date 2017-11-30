#!/usr/local/cs//bin/python3

import sys #to get arguements
#from enum import IntEnum, auto
exitCode = 0
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
        self.firstUnreservedInode = int(parsedLine[7])
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
        self.firstUnreservedInode = int(parsedLine[8])
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
        self.inodeNum= int(parsedLine[1])

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
        self.fileSize = int(parsedLine[10])
        self.numBlocks = int(parsedLine[11])
        self.i_blocks = parsedLine[12:]

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

class Direct:
    def __init__(self, name, blockNum, inodeNum, logicalOffset):
        self.name = name
        self.blockNum = int(blockNum)
        self.inodeNum = int(inodeNum)
        self.logicalOffset = int(logicalOffset)



class Indirect:
    def __init__(self, csv_line):
        parsedLine = csv_line.split(',')
        self.name = parsedLine[0]
        self.owningInodeNum = int(parsedLine[1])
        self.indirectionLevel = int(parsedLine[2])
        self.logicalOffset = int(parsedLine[3])
        self.indirectBlockNum = int(parsedLine[4])
        self.blockNum = int(parsedLine[5])
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
    global exitCode
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
    global exitCode
    if block.blockNum < 0 or block.blockNum > lastBlock:
        if(block.name == 'DIRECT'):
            name = 'BLOCK'
        elif(block.name == 'SINGLE'):
            name = 'INDIRECT BLOCK'
        elif (block.name == 'DOUBLE'):
            name = 'DOUBLE INDIRECT BLOCK'
        elif (block.name == 'TRIPLE'):
            name = 'TRIPLE INDIRECT BLOCK'

        print('INVALID %s %d IN INODE %d AT OFFSET %d' % (name, block.blockNum, block.inodeNum, block.logicalOffset))
        exitCode = 2
        return False
    #if block.blockNum < firstUnreservedBlock :
     #   print('Error, reserved block')
      #  return False
    return True

def checkIfFreeOrReserved(blocks, block):
    global exitCode
    if (block.name == 'DIRECT'):
        name = 'BLOCK'
    elif (block.name == 'SINGLE'):
        name = 'INDIRECT BLOCK'
    elif (block.name == 'DOUBLE'):
        name = 'DOUBLE INDIRECT BLOCK'
    elif (block.name == 'TRIPLE'):
        name = 'TRIPLE INDIRECT BLOCK'

    if blocks[block.blockNum] == FREE:
        print('ALLOCATED %s %d ON FREELIST' %(name, block.blockNum))
        exitCode = 2
        return False
    elif blocks[block.blockNum] == RESERVED:
        #print('Error, block is reserved')
        print('RESERVED %s %d IN INODE %d AT OFFSET %d' % (name, block.blockNum, block.inodeNum, block.logicalOffset))
        exitCode = 2
        return False
    else:
        return True

def addAllBlocks(blockList):
    global FREE
    global RESERVED
    global exitCode
    global superBlock
    global groups
    global inodes
    global freeBlocks
    global freeInodes
    global directories
    global indirects
    #add reserved blocks
    #since only 1 block, we can find all restricted blocks through first group
    firstUnreservedBlock = groups[0].firstUnreservedInode + (superBlock.inodeSize * superBlock.totalInodes/superBlock.blockSize)
    blockList[:firstUnreservedBlock] = firstUnreservedBlock*[RESERVED]

    #addFreeBlocks
    for freeBlock in freeBlocks:
        if(checkBlockValidity(freeBlock, superBlock.totalBlocks - 1)):
            blockList[freeBlock.blockNum] = FREE

    #add indirectBlocks references
    for indirectBlock in indirects:
        if(checkBlockValidity(indirectBlock, superBlock.totalBlocks - 1) and checkIfFreeOrReserved(blockList, indirectBlock)):
            blockList[indirectBlock.blockNum].append(indirectBlock)

    #for each direct, singly, doubly, and triply indirect block, add
    for inode in inodes:
        for i in range(0, 12): #may need to include indirect pointers???? see later
            if int(inode.i_blocks[i]) == 0:
                continue
            directBlock = Direct('DIRECT', int(inode.i_blocks[i]), inode.inodeNum, 0)
            if(checkBlockValidity(directBlock, superBlock.totalBlocks -1) and checkIfFreeOrReserved(blockList, directBlock)):
                blockList[directBlock.blockNum].append(directBlock)
        for i in range(12, 15):
            if int(inode.i_blocks[i]) == 0:
                continue
            if i == 12: #single indirect
                singleIndirectBlock = Direct('SINGLE', int(inode.i_blocks[i]), inode.inodeNum, 12)
                if (checkBlockValidity(singleIndirectBlock, superBlock.totalBlocks - 1) and checkIfFreeOrReserved(blockList,singleIndirectBlock)):
                    blockList[singleIndirectBlock.blockNum].append(singleIndirectBlock)
            if i == 13: #doubleindirect
                singleIndirectBlock = Direct('DOUBLE', int(inode.i_blocks[i]), inode.inodeNum, 268)
                if (checkBlockValidity(singleIndirectBlock, superBlock.totalBlocks - 1) and checkIfFreeOrReserved(blockList,singleIndirectBlock)):
                    blockList[singleIndirectBlock.blockNum].append(singleIndirectBlock)
            if i == 14: #triple indirect
                singleIndirectBlock = Direct('TRIPLE', int(inode.i_blocks[i]), inode.inodeNum, 65804)
                if (checkBlockValidity(singleIndirectBlock, superBlock.totalBlocks - 1) and checkIfFreeOrReserved(blockList,singleIndirectBlock)):
                    blockList[singleIndirectBlock.blockNum].append(singleIndirectBlock)

def checkForUnreferenced(blocks):
    global exitCode
    for block in blocks:
        if not block:
            print('UNREFERENCED BLOCK %d' % blocks.index(block))
            exitCode = 2

def checkForUnreferencedInodes(inodeList):
    global exitCode
    for inode in inodeList:
        if not inode:
            print('UNREFERENCED BLOCK %d' % (inodeList.index(inode) + 1))
            exitCode = 2

def printAllDuplicates(blockList):
    for block in blockList:
        if (block.name == 'DIRECT'):
            name = 'BLOCK'
        elif (block.name == 'SINGLE'):
            name = 'INDIRECT BLOCK'
        elif (block.name == 'DOUBLE'):
            name = 'DOUBLE INDIRECT BLOCK'
        elif (block.name == 'TRIPLE'):
            name = 'TRIPLE INDIRECT BLOCK'
        print('DUPLICATE %s %d IN INODE %d AT OFFSET %d' %(name, block.blockNum, block.inodeNum, block.logicalOffset))

def checkForDuplicated(blocks):
    global exitCode
    for block in blocks:
        if block != FREE and block != RESERVED and len(block) > 1:
            printAllDuplicates(block)
            exitCode = 2

#reports if
#  any block is <0 or > highest block
#  any block takes a reserved block space
#  any block is not referenced by a freelist and not referenced by a file
#  any block is refereneced by a freelist and a file
#  any block is referenced by multiple files
def blockConsistencyAudit():
    global exitCode
    global superBlock

    #create list stucture for all blocks
    #add reserved list to structure
    #add free lists to structure
    #create list of empty lists, one lise for each open block
    blocks = [[] for i in range (superBlock.totalBlocks)]
    addAllBlocks(blocks)
    checkForUnreferenced(blocks)
    checkForDuplicated(blocks)

def checkIfFreeInode(inodeList, inode):
    global exitCode
    if inodeList[inode.inodeNum - 1] == RESERVED:
        return False
    if inodeList[inode.inodeNum - 1] == FREE:
        print('ALLOCATED INODE %d ON FREELIST' % (inode.inodeNum))
        exitCode = 2
        return False
    else:
        return True

def addAllInodes(inodeList):
    global superBlock
    #add reserved spots
    firstUnreservedInode = superBlock.firstUnreservedInode
    inodeList[:firstUnreservedInode-1] = (firstUnreservedInode-1)*[RESERVED]
    for freeInode in freeInodes:
        inodeList[freeInode.inodeNum - 1] = FREE

    for inode in inodes:
        if checkIfFreeInode(inodeList, inode):
            inodeList[inode.inodeNum - 1].append(inode)

def inodeAllocationAudit():
    global exitCode
    global superBlock
    inodeList = [[] for i in range(superBlock.totalInodes)]
    addAllInodes(inodeList)
    checkForUnreferencedInodes(inodeList)
    #checkForDuplicated()


def directoryConsistencyAudit(csv_file):
    global exitCode


def main():
    global exitCode
    exitCode = 0
    # first get open input file
    csv_file = getCSVFile()

    initializeDataFromCSV(csv_file)

    blockConsistencyAudit()
    inodeAllocationAudit()

    csv_file.close()
    exit(exitCode)


if __name__ == '__main__':  # run main function
    main()
