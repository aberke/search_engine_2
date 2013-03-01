# Build the searchio module, and symlink it into the root directory.

searchio: searchio/setup.py searchio/searchio.c searchio/stemmer.c
	cd searchio; python setup.py build
	ln -sf searchio/build/lib.*/searchio.so searchio.so

clean:
	cd searchio; python setup.py clean
	rm -f searchio.so
