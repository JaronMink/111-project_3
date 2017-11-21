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

int imgfd;

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
    
    fprintf(stderr, "File input is not of type *.img\n");
    exit(1);
  }
  
  imgfd = open(imgFile, O_RDONLY);

  if(imgfd == -1){
    fprintf(stderr, "Error opening image file descriptor!\n");
    exit(1);
  }

  return 0;
}
