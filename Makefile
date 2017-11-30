#NAME:  Jaron Mink, Nathan Knight
#EMAIL: jaronmink@gmail.com, nathongknight@gmail.com
#ID:    904598072, 004749179
default: lab3b

lab3b: lab3b.py
	cp lab3b.py lab3b

dist: lab3b.py README Makefile
	tar -czvf lab3b-904598072.tar.gz Makefile lab3b.py  README

clean:
	rm -f lab3b lab3b-904598072.tar.gz
