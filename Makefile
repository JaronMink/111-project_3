#NAME:  Nathan Knight, Jaron Mink
#EMAIL: nathongknight@gmail.com, jaronmink@gmail.com
#ID:    004749179, 904598072

default:
	gcc -g -Wall -Wextra -o lab3a lab3a.c

dist:
	tar -czvf lab3a-904598072.tar.gz Makefile lab3a.c README

clean:
	rm -f lab3a lab3a-904598072.tar.gz
