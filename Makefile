#NAME:  Jaron Mink, Nathan Knight
#EMAIL: jaronmink@gmail.com, nathongknight@gmail.com
#ID:    904598072, 004749179
default: lab3a

lab3a: lab3a.c
	gcc -g -Wall -Wextra -o lab3a lab3a.c

dist: lab3a.c README Makefile ext2_fs.h
	tar -czvf lab3a-904598072.tar.gz Makefile lab3a.c ext2_fs.h README

clean:
	rm -f lab3a lab3a-904598072.tar.gz
