'''
Functionality for expressing the constraints on behaviour (with should...)

Intended public interface:
 Classes:  BeAnything, Raise, BeEqualTo, BeType, Not, CollaborateWith 
 Functions: -
 Variables: -
 
Intended for internal use:
 Classes: Constraint

Copyright 2009 by the author(s). All rights reserved 
'''

from lancelot.comparators import Nothing, Anything, EqualsEquals, \
                                 ExceptionValue, Type
from lancelot.verification import UnmetSpecification

class Constraint:
    ''' Base constraint class '''
    
    def __init__(self, comparator=Nothing()):
        ''' Specify the comparator that is used in verification '''
        self._comparator = comparator
        self._result = None
    
    def verify(self, callable_result):
        ''' Invoke callable_result() and _verify() it meets the constraint '''
        value_to_verify = self._invoke(callable_result)
        if self.verify_value(value_to_verify):
            return
        msg = '%s, not %r' % (self.describe_constraint(), value_to_verify)
        raise UnmetSpecification(msg)
        
    def _invoke(self, callable_result):
        ''' Invoke the callable and store away the result.
        Please call from subclasses that need to override verify() itself. '''
        self._result = callable_result()
        return self._result
        
    def verify_value(self, value_to_verify):
        ''' True if value meets the constraint, False otherwise.'''
        return self._comparator.compares_to(value_to_verify)
    
    def describe_constraint(self):
        ''' Describe this constraint '''
        return 'should be nothing'    

class BeAnything(Constraint):
    ''' Catch-all should... "be anything" constraint specifier '''
    
    def __init__(self):
        ''' Specify the IsAnything comparator used in verification '''
        super().__init__(Anything())
        
    def describe_constraint(self):
        ''' Describe this constraint '''
        return 'should be anything'
    
class Raise(Constraint):
    ''' Constraint specifying should... "raise exception..." behaviour '''
    
    def __init__(self, specified):
        ''' Specify the exception that should raised.
        May be an exception type or instance '''
        super().__init__()
        self._specified = specified
        if isinstance(specified, type):
            self._specified_type = specified
            self._description = 'should raise %s' % (specified.__name__)
        else:
            self._specified_type = type(specified)
            self._description = 'should raise %r' % (specified)
        
    def verify(self, callable_result):
        ''' Invoke callable_result() and it raises an exception that 
        meets the constraint '''
        try:
            self._invoke(callable_result)
        except self._specified_type as raised_exception:
            if ExceptionValue(self._specified).compares_to(raised_exception):
                return
            msg = '%s, not %r' % (self.describe_constraint(), raised_exception)
            raise UnmetSpecification(msg)
        raise UnmetSpecification(self.describe_constraint())

    def describe_constraint(self):
        ''' Describe this constraint '''
        return self._description
        
class BeEqualTo(Constraint):
    ''' Constraint specifying should... "be == to..." behaviour '''
    
    def __init__(self, specified):
        ''' Specify the value that should be == '''
        super().__init__(EqualsEquals(specified))
        self._description = 'should be == %s' % repr(specified)
        
    def describe_constraint(self):
        ''' Describe this constraint '''
        return self._description
    
class BeType(Constraint):
    ''' Constraint specifying should... "be type of..." behaviour '''
    
    def __init__(self, specified):
        ''' Specify what type of thing it should be '''
        super().__init__(Type(specified))
        self._description = 'should be type %s' % (specified)
        
    def describe_constraint(self):
        ''' Describe this constraint '''
        return self._description
        
class Not(Constraint):
    ''' Constraint specifying should... "not..." behaviour '''
    
    def __init__(self, constraint):
        ''' Specify what other constraint it should not be '''
        super().__init__()
        self._constraint = constraint
        
    def verify(self, callable_result):
        ''' Check that the constraint is met '''
        try:
            self._constraint.verify(callable_result)
        except UnmetSpecification:
            return
        raise UnmetSpecification(self.describe_constraint())
    
    def describe_constraint(self):
        ''' Describe this constraint '''
        msg = self._constraint.describe_constraint()
        if msg.startswith('should not '):
            return msg.replace('should not ', 'should ', 1)
        elif msg.startswith('should '):
            return msg.replace('should ', 'should not ', 1)
        return 'Not: ' + msg 
    
class CollaborateWith(Constraint):
    ''' Constraint specifying should... "collaborate with" behaviour '''
    
    def __init__(self, *collaborations):
        ''' Specify what MockSpec collaborations should occur '''
        super().__init__()
        self._collaborations = collaborations
    
    def verify(self, callable_result):
        ''' Check that the constraint is met '''
        mock_specs = []
        for collaboration in self._collaborations:
            mock_specs.append(collaboration.start_collaborating())
        self._invoke(callable_result)
        for mock_spec in mock_specs:
            mock_spec.verify()
    
    def describe_constraint(self):
        ''' Describe this constraint '''
        descriptions = [collaboration.description() 
                        for collaboration in self._collaborations]
        return ','.join(descriptions)
    
#TODO: lessthan, lessthanorequalto, greaterthan, greaterthanorequalto, within
