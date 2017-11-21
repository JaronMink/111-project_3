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
  fprintf(stdrr, "%s\n", msg);
  exit(exitCode);
}

void errorExitOne(char* msg)
{
  errorExitNum(msg, 1);
}

void superblockSummary(){
  //blocks, inodes, blocksize, inodesize, blockspergroup,inodespergroup,firstnonreservedinode
  long numBlocks = super.s_blocks_count;
  long blockSize= 1024 << super.s_log_block_size;
  long numInodes = super.inodes_count;
  long inodeSize = super.s_inode_size;
  long blocksPerGroup = super.s_blocks_per_group;
  long inodesPerGroup = super.s_inodes_per_group;
  long firstFreeInode = 
  dprintf(1, "%s,%d,%d,%d,%d,%d,%d,%d\n", "SUPERBLOCK",
	  super.s_blocks_count, super.inodes_count,);


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
  
  imgfd = open(imgFile, O_RDONLY);

  if(imgfd == -1){
    errorExitOne("Error opening image file descriptor!");
  }
  
  pread(imgfd, &super, sizeof(struct ext2_super_block), EXT2_MIN_BLOCK_SIZE);
  superblockSummary();

  return 0;
}
