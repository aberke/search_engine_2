# Create an AST from a boolean expression. AST is a tuple
# consisting of an operator and a list of operands.
#
# Note: NOT is not supported.

# Example:
#   given a AND b
#   returns ('AND', ['a','b'])
#
# Copyright 2006, by Paul McGuire
# Modified: 02/2011 for csci1580 

import sys
sys.path.append('../pyparsing-1.5.5')

from pyparsing import *

class BoolOperand(object):
    def __init__(self,t):
        self.args = t[0][0::2]
    def __str__(self):
        sep = " %s " % self.reprsymbol
        return "(" + sep.join(map(str,self.args)) + ")"
    
class BoolAnd(BoolOperand):
    reprsymbol = 'AND'
    def eval_expr(self):
        reprsymbol = 'AND'
        list = []
        for a in self.args:
            if not isinstance(a,BoolOperand):
                elem = a
            else:
                elem = a.eval_expr()
            list.append(elem)
        tuple = (reprsymbol, list)
        return tuple

class BoolOr(BoolOperand):
    reprsymbol = 'AND'
    def eval_expr(self):
        reprsymbol = 'OR'    
        list = []
        for a in self.args:
            if not isinstance(a,BoolOperand):
               elem = a
            else:
              elem = a.eval_expr()
            list.append(elem)
        tuple = (reprsymbol, list)
        return tuple

boolOperand = Word(alphanums+"!#$%&'*+,-./:;<=>?@[]^_`{|}~\\")
boolExpr = operatorPrecedence( boolOperand,
    [
    ("AND", 2, opAssoc.LEFT,  BoolAnd),
    ("OR",  2, opAssoc.LEFT,  BoolOr),
    ])

def bool_expr_ast(expr):
  expr = expr.strip()
  parsed_expr = boolExpr.parseString(expr)[0]
  if not isinstance(parsed_expr,BoolOperand):
    return expr
  else:
    return parsed_expr.eval_expr()
