/*
    searchio
    A Python module for interacting with CS158 Search Engine indices.
*/

#include <Python.h>
#include "stemmer.h"

/* Constants */
#define SEARCHIO_TOKENIZER_BUFFER_SIZE 1024

/* Handy macros */
#define SEARCHIO_MAX(a, b) ((a < b) ? b : a)
#define SEARCHIO_MIN(a, b) ((a > b) ? b : a)

/* Global variables */
static char *searchio_tokenizerBuffer = NULL;

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
    searchio_tokenizerBuffer = (char *)malloc(sizeof(char) * SEARCHIO_TOKENIZER_BUFFER_SIZE);
    Py_InitModule("searchio", SearchioMethods);
}

/* Method implementations */
static PyObject *searchio_test(PyObject *self, PyObject *args)
{
    Py_RETURN_TRUE;
}
static PyObject *searchio_tokenize(PyObject *self, PyObject *args)
{
    /* get the set of stopwords, and the string to tokenize */
    PyObject *stopwords = NULL;
    const char *textString = NULL;
    
    if (!PyArg_ParseTuple(args, "Os", &stopwords, &textString))
        return NULL;
    
    /* loop over the characters in textString to normalize it */
    size_t len = SEARCHIO_MIN(strlen(textString), SEARCHIO_TOKENIZER_BUFFER_SIZE - 1);
    size_t i;
    size_t wordsFound = 1;
    for (i = 0; i < len; i++)
    {
        char c = tolower(textString[i]);
        if (isalnum(c))
            searchio_tokenizerBuffer[i] = c;
        else
        {
            searchio_tokenizerBuffer[i] = '\0';
            wordsFound++;
        }
    }
    
    /* NUL-terminate our buffer */
    searchio_tokenizerBuffer[i] = '\0';
    
    /* create a result list */
    PyObject *result = PyList_New(0);
    
    /* loop over each string, check if it's a stopword, and if not, stem it */
    char *str = searchio_tokenizerBuffer;
    for (i = 0; i < wordsFound; i++)
    {
        size_t l = strlen(str);
        
        /* convert to a Python string */
        PyObject *pystr = PyString_FromString(str);
        
        /* is it a stop word? */
        if (!PySet_Contains(stopwords, pystr))
        {
            /* stem it */
            int newEnd = stem(str, 0, (int)(l - 1));
            str[newEnd + 1] = '\0';
            
            /* add it to the list */
            PyList_Append(result, PyString_FromString(str));
        }
        
        Py_DECREF(pystr);
        str += (l + 1);
    }
    
    return result;
}
