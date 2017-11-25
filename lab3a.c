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
#include <time.h>

int                     imgfd      = -1;
int                     numGroups  = 0;
uint8_t                 eightBitInt;
struct ext2_group_desc* groupTable = NULL;
struct ext2_super_block super;

void errorExitNum(char* msg, int exitCode){
  dprintf(2, "%s\n", msg);
  exit(exitCode);
}

void errorExitOne(char* msg){
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
  
  if(groupIndex < numGroups -1){
    //if this isn't the last group then we know it is fully used
    totalBlocks = super.s_blocks_per_group;
    totalInodes = super.s_inodes_per_group;
  }
  else{
    //then whatever is left is in this group, unless there is no remainder, then its filled
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
  /*************************************************************************
   * GROUP, group number, totalblocks in group, totalinodes in group,
   * num free blocks, num free inodes, block num of free bitmap for group,
   * block num of free inode bitmap for group, block num of first block of
   * inodes for group
   *************************************************************************/
  
  //will only ever be one in our case
  numGroups = super.s_blocks_count / super.s_blocks_per_group;

  if((super.s_blocks_count % super.s_blocks_per_group) != 0){
    //if we have a remainder, we will need another group;
    numGroups++;
  }
    
  if(groupTable == NULL){
    groupTable = malloc(sizeof(struct ext2_group_desc) * numGroups);
    //might also change sizeof... with blockSize, see if they are different
    pread(imgfd, groupTable, (sizeof(struct ext2_group_desc) * numGroups), EXT2_MIN_BLOCK_SIZE * 2);
  }

  int i;
  for(i = 0; i < numGroups; i++){
    printGroupSummary(&(groupTable[i]), i);
  }
}

void printFreeBits(__uint32_t blockNum, char* msg){
  __uint32_t bitmask = 0x1;
  long long  offset  = (1024<< super.s_log_block_size)*blockNum;

  int  currByte;
  char byteBuf;
  for(currByte = 0; currByte < (1024) << super.s_log_block_size; currByte++){
    pread(imgfd, &byteBuf, 1, offset + currByte);

    bitmask = 0x1;
    //if there is a 0 present, report it
    int i;
    for(i = 0; i < 8; i++){
      if((byteBuf & bitmask) == 0x0){
	dprintf(1, "%s,%d\n", msg, (i + 8 * currByte + 1));
      }
	
      bitmask = bitmask << 1;
    }
  }
}

void printFreeBlocks(__uint32_t bitmap){
  printFreeBits(bitmap, "BFREE");
}

void printFreeInodes(__uint32_t bitmap){
  printFreeBits(bitmap, "IFREE");
}

void printAllFreeBlocks(){
  int i;
  for(i = 0; i < numGroups; i++){  
    printFreeBlocks(groupTable[i].bg_block_bitmap);
  }
}

void printAllFreeInodes(){
  int i;
  for(i = 0; i < numGroups; i++){    
    printFreeInodes(groupTable[i].bg_inode_bitmap);
  }
}

char* secToDate(time_t time){
  //time_t time = epoch
  char*     formattedDate = malloc(sizeof(char) * 50);
  struct tm ts            = *gmtime(&time);

  strftime(formattedDate, 50, "%m/%d/%y %H:%M:%S", &ts);
  return formattedDate;
}

void printInodeSummary(struct ext2_inode* inode, int inodeNum){
  char fileType ='\0';
  
  switch(inode->i_mode & 0xF000){ //get the required bits
  case 0xA000://EXT2_S_IFLNK:
    fileType = 's';
    break;
  case 0x8000://EXT2_S_IFREG:
    fileType = 'f';
    break;
  case 0x4000://EXT2_S_IFDIR:
    fileType = 'd';
    break;
  default:
    fileType = '?';
    break;
    // errorExitOne("Error, undefined file type found");
  }

  int   mode           = inode->i_mode & 0xFFF; //last 12 bits only
  int   owner          = inode->i_uid;
  int   group          = inode->i_gid;
  int   linkCount      = inode->i_links_count;
  char* lastChangeTime = secToDate(inode->i_ctime);
  char* lastModTime    = secToDate(inode->i_mtime); 
  char* lastAccessTime = secToDate(inode->i_atime);
  int   size           = inode->i_size;
  int   blockNum       = inode->i_blocks;
	
  /*********************************************************************************
   * INODE, inodenum, filetype, mode, owner, group,
   * linkcount, last change time, mod time, last access time, size, num of blocks
   ********************************************************************************/
  dprintf(1, "%s,%d,%c,%o,%d,%d,%d,%s,%s,%s,%d,%d",
	  "INODE",
	  inodeNum,
	  fileType,
	  mode,
	  owner,
	  group,
	  linkCount,
	  lastChangeTime,
	  lastModTime,
	  lastAccessTime,
	  size,
	  blockNum);

  dprintf(1, ",%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n",
	  inode->i_block[0],
	  inode->i_block[1],
	  inode->i_block[2],
	  inode->i_block[3],
	  inode->i_block[4],
	  inode->i_block[5],
	  inode->i_block[6],
	  inode->i_block[7],
	  inode->i_block[8],
	  inode->i_block[9],
	  inode->i_block[10],
	  inode->i_block[11],
	  inode->i_block[12],
	  inode->i_block[13],
	  inode->i_block[14]);

  struct ext2_dir_entry temp;
  
  if(fileType == 'd'){
    int i;
    for(i = 0; i < EXT2_NDIR_BLOCKS; i++){
      if(inode->i_block[i] == 0){
	break;
      }

      int j;
      for(j = 0; j < 1024 << super.s_log_block_size; j += temp.rec_len){
	pread(imgfd,
	      &temp,
	      sizeof(struct ext2_dir_entry),
	      (inode->i_block[i] * 1024 << super.s_log_block_size) + j);
	if(temp.inode == 0){
	  return;
	}
	    
	dprintf(1, "%s,%d,%d,%d,%d,%d,\'%s\'\n",
		"DIRENT",
		inodeNum,
		j,
		temp.inode,
		temp.rec_len,
		temp.name_len,
		temp.name);
      }
    }
  }
}

void printInodesForGroup(__uint32_t blockNum){
  unsigned int offset = (1024 << super.s_log_block_size) * blockNum;
  //dprintf(1, "blockNum: %d\n", blockNum);

  struct ext2_inode currInode;
  unsigned int      i;
  
  for(i = 0; i < super.s_inodes_count; i++){
    pread(imgfd, &currInode, sizeof(struct ext2_inode), offset + i * sizeof(struct ext2_inode));
    if(currInode.i_mode != 0 && currInode.i_links_count != 0){
      printInodeSummary(&currInode, (i + 1));
    }
  }
}

void printAllInodeSummaries(){
  int i;
  for(i = 0; i < numGroups; i++){    
    printInodesForGroup(groupTable[i].bg_inode_table);
  }
}

void printDirectoryEntries(){
}

void printIndirectBlockReferences(){
}

int main(int argc, char *argv[]){
  if(argc != 2){
    dprintf(2, "Provide image as argument as follows: ./lab3a *.img\n");
    exit(1);
  }

  char* imgFile = argv[1];
  int   length  = (int)strlen(imgFile);
  
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
  printAllInodeSummaries();
  
  return 0;
}
