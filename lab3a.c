//NAME:  Nathan Knight, Jaron Mink
//EMAIL: nathongknight@gmail.com, jaronmink@gmail.com
//ID:    004749179, 904598072

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include "ext2_fs.h"

int                     imgfd      = -1;
int                     numGroups  = 0;
uint8_t                 eightBitInt;
struct ext2_group_desc* groupTable = NULL;
struct ext2_super_block super;

void errorExitNum(char* msg, int exitCode)
{
  fprintf(stderr, "%s\n", msg);
  exit(exitCode);
}

void errorExitOne(char* msg)
{
  errorExitNum(msg, 1);
}

void printSuperblockSummary(){
  //blocks, inodes, blocksize, inodesize, blockspergroup,inodespergroup,firstnonreservedinode
  int numBlocks      = super.s_blocks_count;
  int numInodes      = super.s_inodes_count;
  int blockSize      = 1024 << super.s_log_block_size;
  int inodeSize      = super.s_inode_size;
  int blocksPerGroup = super.s_blocks_per_group;
  int inodesPerGroup = super.s_inodes_per_group;
  int firstFreeInode = super.s_first_ino;
  dprintf(1, "%s,%d,%d,%d,%d,%d,%d,%d\n",
	  "SUPERBLOCK",
	  numBlocks,
	  numInodes,
	  blockSize,
	  inodeSize,
	  blocksPerGroup,
	  inodesPerGroup,
	  firstFreeInode);
}

void printGroupSummary(struct ext2_group_desc* groupDesc,int groupIndex){     
  int  totalBlocks;
  int  totalInodes;
  uint blocksLeft = super.s_blocks_count % super.s_blocks_per_group;
  uint inodesLeft = super.s_inodes_count % super.s_inodes_per_group;
  
  if(groupIndex < numGroups -1){ //if this isn't the last group then we know it is fully used
    totalBlocks = super.s_blocks_per_group;
    totalInodes = super.s_inodes_per_group;
  }
  else{ //then whatever is left is in this group, unless there is no remainder, then its filled
    totalBlocks = (blocksLeft == 0) ? super.s_blocks_per_group : blocksLeft;
    totalInodes = (inodesLeft == 0) ? super.s_inodes_per_group : inodesLeft;
  }
    
  int numFreeBlocks       = groupDesc->bg_free_blocks_count;
  int numFreeInodes       = groupDesc->bg_free_inodes_count;
  int blockBitmapBlock    = groupDesc->bg_block_bitmap;
  int inodeBitmapBlock    = groupDesc->bg_inode_bitmap;
  int firstFreeInodeBlock = groupDesc->bg_inode_table;

  dprintf(1, "%s,%d,%d,%d,%d,%d,%d,%d,%d\n",
	 "GROUP",
	 groupIndex,
	 totalBlocks,
	 totalInodes,
	 numFreeBlocks,
	 numFreeInodes,
	 blockBitmapBlock,
	 inodeBitmapBlock,
	 firstFreeInodeBlock);
}

void printAllGroupSummaries(){
  //GROUP, group number, totalblocks in group, totalinodes in group,
  //num free blocks, num free inodes, block num of free bitmap for group,
  //block num of free inode bitmap for group, block num of first block of
  //inodes for group
  
  //will only ever be one in our case
  numGroups = super.s_blocks_count / super.s_blocks_per_group;

  if((super.s_blocks_count % super.s_blocks_per_group) != 0) //if we have a remainder, we will need another group;
    numGroups++;
  
  //purley for testing, make sure to take out after!///////////////////////////////////////////////////////
  if(numGroups != 1) {//////////////////////////////////////////////////////////////////////////////////////////
    errorExitOne("Error! number of groups exceed 1!");/////////////////////////////////////////////////////////////
  }

  if(groupTable == NULL) {
    groupTable = malloc(sizeof(struct ext2_group_desc) * numGroups);
    //might also change sizeof... with blockSize, see if they are different
    pread(imgfd, groupTable, (sizeof(struct ext2_group_desc) * numGroups), EXT2_MIN_BLOCK_SIZE * 2);
  }

  int i;
  for(i = 0; i < numGroups; i++) {
    //  pread(imgfd, &groupTable[i], sizeof(struct ext2_group_desc), EXT2_MIN_BLOCK_SIZE * 2 + i * sizeof(struct ext2_group_desc));
    printGroupSummary(&(groupTable[i]), i);
  }
}

//need to print from the bitmap, currently we give it the block number,
//not the actual bitmap, we need to read the bitmap and traverse it
void printFreeBits(__uint32_t blockNum, int len, char* msg){
  
  __uint32_t bitmask = 0x1;
  long long offset = (1024<< super.s_log_block_size)*blockNum;//2048 + (blockNum - 1)*(1024 << super.s_log_b

  int currByte;
  char byteBuf;
  for(currByte = 0; currByte < (1024) << super.s_log_block_size; currByte++) {
    pread(imfd, &byteBuf, 1, offset + currByte);

    bitmask = 0x1;
    //if there is a 0 present, report it
    int i;
    for(i = 0; i < 8; i++){
      if((bitmap & bitmask) == 0x0)
	dprintf(1, "%s,%d\n", msg, i);
      bitmask = bitmask << 1;
    }
  }
}


void printFreeBlocks(__uint32_t bitmap, int len) {
  printFreeBits(bitmap, len, "BFREE");
}

void printFreeInodes(__uint32_t bitmap, int len) {
  printFreeBits(bitmap, len, "IFREE");
}


void printAllFreeBlocks(){
  
  int  totalBlocks = -1;
  uint blocksLeft  = super.s_blocks_count % super.s_blocks_per_group;
  
  int i;
  for(i = 0; i < numGroups; i++){  
    /*if(i < numGroups -1) { //if this isn't the last group then we know it is fully used
      totalBlocks = super.s_blocks_per_group;
    }
    else { //then whatever is left is in this group, unless there is no remainder, then its filled
      totalBlocks = (blocksLeft == 0) ? super.s_blocks_per_group : blocksLeft;
    }    
    int blockNum = groupTable[i].bg_block_bitmap;
    */
    printFreeBits((groupTable[i].bg_block_bitmap), totalBlocks, "BFREE");
  }
  

  /*
  int i;

  for(i = 0; i < numGroups; i++){
    int j;
    for(j = 0; j < (1024 << super.s_log_block_size); j++){
      pread(imgfd, &eightBitInt, 1, groupTable[i].bg_block_bitmap * (1024 << super.s_log_block_size) + j);
      
      int k;
      for(k = 0; k < 8; k++){
	if((eightBitInt & (1 << k)) == 0){
	  dprintf(1, "%s,%d\n", "BFREE", (i * super.s_blocks_per_group) + (j * 8) + (k + 1));
	}
      }
    }
    }*/
}

void printAllFreeInodes(){
  int i;
  for(i = 0; i < numGroups; i++){
    int  totalInodes;
    uint inodesLeft = super.s_inodes_count % super.s_inodes_per_group;

    if(i < numGroups -1) { //if this isn't the last group then we know it is fully used
      totalInodes = super.s_inodes_per_group;
    }
    else {
      //then whatever is left is in this group, unless there is no remainder, then its filled
      totalInodes = (inodesLeft == 0) ? super.s_inodes_per_group : inodesLeft;
    }        
    
    printFreeBits((groupTable[i].bg_inode_bitmap), totalInodes, "IFREE");
  }
}

void printInodeSummary(){
}

void printDirectoryEntries(){
}

void printIndirectBlockReferences(){
}

int main(int argc, char *argv[]){
  
  if(argc != 2){
    fprintf(stderr, "Provide image as argument as follows: ./lab3a *.img\n");
    exit(1);
  }

  char *imgFile = argv[1];
  int  length   = (int)strlen(imgFile);
  
  if(imgFile[length - 1] != 'g' ||
     imgFile[length - 2] != 'm' ||
     imgFile[length - 3] != 'i' ||
     imgFile[length - 4] != '.'){    
    errorExitOne("File input is not of type *.img");
  }
  
  if((imgfd = open(imgFile, O_RDONLY)) == -1){
    errorExitOne("Error opening image file descriptor!");
  }

  pread(imgfd, &super, sizeof(struct ext2_super_block), EXT2_MIN_BLOCK_SIZE);
  if(super.s_magic != EXT2_SUPER_MAGIC){
    errorExitOne("Error, file system is not in EXT2 format");
  }    

  printSuperblockSummary();
  printAllGroupSummaries();
  printAllFreeBlocks();
  printAllFreeInodes();
  
  return 0;
}
