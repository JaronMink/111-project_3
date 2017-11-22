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

int                     imgfd;
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

void printGroupSummary(struct ext2_group_desc* groupDesc,int groupIndex) {

  
  int totalBlocks = super.s_blocks_count;
  int totalInodes = super.s
  int numFreeBlocks;
  int numFreeInodes;
  int blockBitmapBlock;
  int inodeBitmapBlock;
  int freeInodeBlock;

  dprintf(1, "%s,%d,%d,%d,%d,%d,%d,%d,%d\n",
	 "GROUP",
	 groupIndex,
	 totalBlocks,
	 totalInodes,
	 numFreeBlocks,
	 numFreeInodes,
	 blockBitmapBlock,
	 inodeBitmapBlock,
	 freeInodeBlock);
}

void printAllGroupSummaries(int numGroups){
  //GROUP, group number, totalblocks in group, totalinodes in group,
  //num free blocks, num free inodes, block num of free bitmap for group,
  //block num of free inode bitmap for group, block num of first block of
  //inodes for group

  struct ext2_group_desc* groupTable = malloc(sizeof(ext2_group_desc)*numGroups);
  //might also change sizeof... with blockSize, see if they are different
  pread(imgfd ,&groupTable, (sizeof(ext2_group_desc)*numGroups), EXT2_MIN_BLOCK_SIZE*2);

  
  int i;
  for(i = 0; i <numGroups; i++) {
    printGroupSummary(&groupTable[i], i);
  }
}

void printFreeBlockEntries(){
}

void printFreeInodeEntries(){
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
  
  if((imgfd = open(imgFile, O_RDONLY))==-1){
    errorExitOne("Error opening image file descriptor!");
  }

  pread(imgfd, &super, sizeof(struct ext2_super_block), EXT2_MIN_BLOCK_SIZE);
  if(super.s_magic != EXT2_SUPER_MAGIC){
    errorExitOne("Error, file system is not in EXT2 format");
  }    
  printSuperblockSummary();

  //will only ever be one in our case
  int numGroups = super.s_blocks_count /super.s_blocks_per_group + 1;
  
  if(numGroups != 1) {
    errorExit("Error! number of groups exceed 1!");
  }

  printAllGroupSummaries();
  
  return 0;
}
