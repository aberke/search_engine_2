/*
    searchio
    A Python module for interacting with CS158 Search Engine indices.
*/

#include <Python.h>
#include <fcntl.h>
#include "stemmer.h"

/* Constants */
#define SEARCHIO_TOKENIZER_BUFFER_SIZE 1024 * 1024
#define SEARCHIO_WF_SCALE 100000

/* Handy macros */
#define SEARCHIO_MAX(a, b) ((a < b) ? b : a)
#define SEARCHIO_MIN(a, b) ((a > b) ? b : a)

/* Index file structures */
#pragma pack(push, 1)
typedef struct searchio_index_header {
    uint32_t numDocuments;
    uint32_t numTerms;
    uint32_t postingsStart;
} searchio_index_header_t;

typedef struct searchio_index_term {
    uint32_t postingsOffset;
    uint32_t df;
    uint32_t numDocumentsInPostings;
    uint16_t termLength;
} searchio_index_term_t;

typedef struct searchio_index_posting {
    uint32_t pageID;
    uint32_t wf;
    uint32_t numPositions;
} searchio_index_posting_t;

#pragma pack(pop)

/* Global variables */
static char *searchio_tokenizerBuffer = NULL;

/* Module method declarations */
static PyObject *searchio_test(PyObject *self, PyObject *args);
static PyObject *searchio_tokenize(PyObject *self, PyObject *args);
static PyObject *searchio_createIndex(PyObject *self, PyObject *args);

/* Module method table */
static PyMethodDef SearchioMethods[] = {
    {"test", &searchio_test, METH_VARARGS, "Test that the searchio module is working."},
    {"tokenize", &searchio_tokenize, METH_VARARGS, "Obtain a viable list of tokens from a string."},
    {"createIndex", &searchio_createIndex, METH_VARARGS, "Create an on-disk representation of the provided index."},
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
        if (l == 0)
        {
            str += 1;
            continue;
        }
        
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
static PyObject *searchio_createIndex(PyObject *self, PyObject *args)
{
    /* grab the filename, number of documents, and our index */
    const char *filename = NULL;
    uint32_t numDocuments = 0;
    PyObject *index = NULL;
    
    if (!PyArg_ParseTuple(args, "sIO", &filename, &numDocuments, &index))
        return NULL;
    
    /* open the index file */
    int fd = open(filename, O_WRONLY|O_CREAT|O_TRUNC);
    size_t totalWritten = 0;
    
    /* get the number of terms in the index */
    Py_ssize_t numTermsPy = PyDict_Size(index);
    uint32_t numTerms = 0;
    if (numTermsPy > 0 && numTermsPy < UINT32_MAX)
        numTerms = (uint32_t)numTermsPy;
    else
    {
        PyErr_SetString(PyExc_MemoryError, "the number of terms is greater than UINT32_MAX (or less than 0)");
        return NULL;
    }
    
    /* write a document header */
    searchio_index_header_t header = {htonl(numDocuments), htonl(numTerms), 0};
    totalWritten += write(fd, (void *)&header, sizeof(header));
    
    /* loop once over index to write term entries */
    uint32_t postingsOffset = 0;
    
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    
    while (PyDict_Next(index, &pos, &key, &value))
    {
        /* create a term entry */
        searchio_index_term_t term;
        term.postingsOffset = htonl(postingsOffset);
        
        /* pull out the term, its df, and a reference to the postings list */
        const char *termStr = PyString_AS_STRING(key);
        PyObject *pydf = PyList_GetItem(value, 0);
        PyObject *postings = PyList_GetItem(value, 1);
        Py_ssize_t postingsLen = PyList_Size(postings);
        
        /* fill in the header */
        size_t termLen = strlen(termStr);
        term.df = htonl(PyInt_AsUnsignedLongMask(pydf));
        term.numDocumentsInPostings = htonl((uint32_t)postingsLen);
        term.termLength = htons((uint16_t)termLen);
        
        /* write out the header, and its term */
        totalWritten += write(fd, (void *)&term, sizeof(term));
        totalWritten += write(fd, termStr, termLen);
        
        /* determine the on-disk size of the posting list */
        uint32_t totalSize = 0;
        Py_ssize_t i;
        for (i = 0; i < postingsLen; i++)
        {
            PyObject *entryList = PyList_GetItem(postings, i);
            PyObject *positions = PyList_GetItem(entryList, 2);
            Py_ssize_t positionLen = PyList_Size(positions);
            
            /* on-disk size is size of a posting struct, plus sizeof(uint32_t) * positions */
            totalSize += (uint32_t)sizeof(searchio_index_posting_t) + (uint32_t)(positionLen * sizeof(uint32_t));
        }
        
        /* increment the postings offset */
        postingsOffset += totalSize;
    }
    
    /* update the postings offset */
    header.postingsStart = htonl(totalWritten);
    
    /* loop again to write postings lists */
    while (PyDict_Next(index, &pos, &key, &value))
    {
        /* get the postings list and its length */
        PyObject *postings = PyList_GetItem(value, 1);
        Py_ssize_t postingsLen = PyList_Size(postings);
        
        /* loop over each entry in the postings list and write it out */
        Py_ssize_t i;
        for (i = 0; i < postingsLen; i++)
        {
            /* pull out some values */
            PyObject *entryList = PyList_GetItem(postings, i);
            PyObject *pypageID = PyList_GetItem(entryList, 0);
            PyObject *pywf = PyList_GetItem(entryList, 1);
            PyObject *positions = PyList_GetItem(entryList, 2);
            Py_ssize_t positionsLen = PyList_Size(positions);
            
            /* create a header */
            searchio_index_posting_t posting;
            posting.pageID = htonl((uint32_t)PyInt_AsUnsignedLongMask(pypageID));
            posting.wf = htonl((uint32_t)(PyFloat_AsDouble(pywf) * SEARCHIO_WF_SCALE));
            posting.numPositions = htonl((uint32_t)positionsLen);
            
            /* write the header */
            write(fd, (void *)&posting, sizeof(posting));
            
            /* write each of the positions */
            Py_ssize_t j;
            for (j = 0; j < positionsLen; j++)
            {
                PyObject *item = PyList_GetItem(positions, i);
                uint32_t p = htonl((uint32_t)PyInt_AsUnsignedLongMask(item));
                write(fd, (void *)&p, sizeof(p));
            }
        }
    }
    
    /* rewrite the header with correct offsets */
    lseek(fd, 0, SEEK_SET);
    write(fd, (void *)&header, sizeof(header));
    
    /* close the index */
    close(fd);
    
    /* no meaningful return value here */
    Py_RETURN_NONE;
}
