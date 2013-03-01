# Build the searchio module, and symlink it into the root directory.

searchio: searchio/searchio.c
	cd searchio; python setup.py build
	ln -sf searchio/build/lib.*/searchio.so searchio.so

clean:
	cd searchio; python setup.py clean
	rm -f searchio.so
