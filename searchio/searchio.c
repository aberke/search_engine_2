/*
    searchio
    A Python module for interacting with CS158 Search Engine indices.
*/

#include <Python.h>

/* Module method declarations */
static PyObject *searchio_test(PyObject *self, PyObject *args);
static PyObject *searchio_tokenize(PyObject *self, PyObject *args);

/* Module method table */
static PyMethodDef SearchioMethods[] = {
    {"test", &searchio_test, METH_VARARGS, "Test that the searchio module is working."},
    {"tokenize", &searchio_tokenize, METH_VARARGS, "Obtain a viable list of tokens from a string."},
    {NULL, NULL, 0, NULL}
};

/* Initialization function */
PyMODINIT_FUNC initsearchio(void)
{
    Py_InitModule("searchio", SearchioMethods);
}

/* Method implementations */
static PyObject *searchio_test(PyObject *self, PyObject *args)
{
    Py_RETURN_TRUE;
}
static PyObject *searchio_tokenize(PyObject *self, PyObject *args)
{
    Py_RETURN_NONE;
}
