all: standalone run_triangle test_triangle

triangle.o: triangle.c
	gcc -c triangle.c -o triangle.o

standalone: standalone.c triangle.o
	gcc -o standalone standalone.c triangle.o

run_triangle: run_triangle.c triangle.o
	gcc -o run_triangle run_triangle.c triangle.o

test_triangle: test_triangle.c triangle.o
	gcc -o test_triangle test_triangle.c triangle.o

clean:
	rm -f standalone run_triangle test_triangle triangle.o
