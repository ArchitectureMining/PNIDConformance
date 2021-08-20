from abc import ABCMeta, abstractmethod

class Solver:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def are_equal_expr(self, a, b):
        pass

    @abstractmethod
    def true(self):
        pass

    # Integer constants
    @abstractmethod
    def num(self, n):
        pass

    # Real constants
    @abstractmethod
    def real(self, n):
        pass

    # Boolean variable with name
    @abstractmethod
    def boolvar(self, n):
        pass

    # Integer variable with name
    @abstractmethod
    def intvar(self, n):
        pass

    # Real variable with name
    @abstractmethod
    def realvar(self, n):
        pass

    # Logical conjunction
    @abstractmethod
    def land(self, l):
        pass

    # Logical disjunction
    @abstractmethod
    def lor(self, l):
        pass

    # Logical negation
    @abstractmethod
    def neg(self, a):
        pass

    # Logical implication
    @abstractmethod
    def implies(self, a, b):
        pass

    # Logical biimplication
    @abstractmethod
    def iff(self, a, b):
        pass

    # Equality of arithmetic terms
    @abstractmethod
    def eq(self, a, b):
        pass

    # Less-than on arithmetic terms
    @abstractmethod
    def lt(self, a, b):
        pass

    # Greater-or-equal on arithmetic terms
    @abstractmethod
    def ge(self, a, b):
        pass

    # Increment of arithmetic term by 1
    @abstractmethod
    def inc(self, a):
        pass

    # Subtraction
    @abstractmethod
    def minus(self, a, b):
        pass

    # Addition
    @abstractmethod
    def plus(self, a, b):
        pass

    # If-then-else
    @abstractmethod
    def ite(self, cond, a, b):
        pass

    # Minimum of two arithmetic expressions
    @abstractmethod
    def min(self, a, b):
        pass

    @abstractmethod
    def push(self):
        pass

    @abstractmethod
    def pop(self):
        pass

    # Add list of assertions
    @abstractmethod
    def require(self):
        pass

    # Minimize given expression
    @abstractmethod
    def minimize(self, e):
        pass

    # Reset context
    @abstractmethod
    def reset(self):
        pass

    # Destroy context
    @abstractmethod
    def destroy(self):
        pass

    @staticmethod
    def shutdown():
        pass

class Model:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def eval_bool(self, v):
        pass

    @abstractmethod
    def eval_int(self, v):
        pass

    @abstractmethod
    def eval_real(self, v):
        pass
