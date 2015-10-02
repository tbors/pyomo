#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________
#
# Unit Tests for Set() Objects
#
# PyomoModel            Base test class
# SimpleSetA            Testing simple set of integers
# SimpleSetAordered     Testing simple set of ordered integers
# TestRangeSet          Testing the RangeSet class
# TestRangeSet1         More testing of the RangeSet class
# SimpleSetB            Testing simple set of string values
# SimpleSetC            Testing simple set of tuples
# ArraySet              Testing arrays of sets
# RealSetTests          Testing the RealSet class
# IntegerSetTests       Testing the IntegerSet class
# SetArgs1              Testing arguments for simple set
# SetArgs2              Testing arguments for arrays of sets
# Misc                  Misc tests
# SetIO                 Testing Set IO formats
#

import itertools
import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep

from pyutilib.misc import flatten_tuple as pyutilib_misc_flatten_tuple
import pyutilib.th as unittest

import pyomo.core.base
from pyomo.core.base.set_types import _AnySet
from pyomo.environ import *

_has_numpy = False
try:
    import numpy
    _has_numpy = True
except:
    pass

class PyomoModel(unittest.TestCase):

    def setUp(self):
        self.model = AbstractModel()

    def construct(self,filename):
        self.instance = self.model.create_instance(filename)


class SimpleSetA(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write( "data; set A := 1 3 5 7; end;\n" )
        OUTPUT.close()
        #
        # Create model instance
        #
        self.model.A = Set()
        #
        # Misc datasets
        #
        self.model.tmpset1 = Set(initialize=[1,3,5,7])
        self.model.tmpset2 = Set(initialize=[1,2,3,5,7])
        self.model.tmpset3 = Set(initialize=[2,3,5,7,9])

        self.model.setunion = Set(initialize=[1,2,3,5,7,9])
        self.model.setintersection = Set(initialize=[3,5,7])
        self.model.setxor = Set(initialize=[1,2,9])
        self.model.setdiff = Set(initialize=[1])
        self.model.setmul = Set(initialize=[(1,2), (1,3), (1,5), (1,7), (1,9),
                                      (3,2), (3,3), (3,5), (3,7), (3,9),
                                      (5,2), (5,3), (5,5), (5,7), (5,9),
                                      (7,2), (7,3), (7,5), (7,7), (7,9)])

        self.instance = self.model.create_instance(currdir+"setA.dat")

        self.e1=1
        self.e2=2
        self.e3=3
        self.e4=4
        self.e5=5
        self.e6=6

    def tearDown(self):
        #
        # Remove Set 'A' data file
        #
        if os.path.exists(currdir+"setA.dat"):
            os.remove(currdir+"setA.dat")

    def test_len(self):
        """Check that a simple set of numeric elements has the right size"""
        self.assertEqual( len(self.instance.A), 4)

    def test_data(self):
        """Check that we can access the underlying set data"""
        self.assertEqual( len(self.instance.A.data()), 4)

    def test_dim(self):
        """Check that a simple set has dimension zero for its indexing"""
        self.assertEqual( self.instance.A.dim(), 0)

    def test_clear(self):
        """Check the clear() method empties the set"""
        self.instance.A.clear()
        self.assertEqual( len(self.instance.A), 0)

    def test_virtual(self):
        """Check if this is not a virtual set"""
        self.assertEqual( self.instance.A.virtual, False)

    def test_bounds(self):
        """Verify the bounds on this set"""
        self.assertEqual( self.instance.A.bounds(), (1,7))

    def test_check_values(self):
        """Check if the values added to this set are valid"""
        #
        # This should not throw an exception here
        #
        self.instance.A.check_values()

    def test_addValid(self):
        """Check that we can add valid set elements"""
        self.instance.A.add(self.e2,self.e4)
        self.assertEqual( len(self.instance.A), 6)
        self.assertFalse( self.e2 not in self.instance.A, "Cannot find new element in A")
        self.assertFalse( self.e4 not in self.instance.A, "Cannot find new element in A")

    def test_addInvalid(self):
        """Check that we get an error when adding invalid set elements"""
        #
        # This verifies that by default, all set elements are valid.  That
        # is, the default within is None
        #
        self.assertEqual( self.instance.A.domain, None)
        self.instance.A.add('2','3','4')
        self.assertFalse( '2' not in self.instance.A, "Found invalid new element in A")

    def test_removeValid(self):
        """Check that we can remove a valid set element"""
        self.instance.A.remove(self.e3)
        self.assertEqual( len(self.instance.A), 3)
        self.assertFalse( 3 in self.instance.A, "Found element in A that we removed")

    def test_removeInvalid(self):
        """Check that we fail to remove an invalid set element"""
        self.assertRaises(KeyError, self.instance.A.remove, 2)
        self.assertEqual( len(self.instance.A), 4)

    def test_discardValid(self):
        """Check that we can discard a valid set element"""
        self.instance.A.discard(self.e3)
        self.assertEqual( len(self.instance.A), 3)
        self.assertFalse( 3 in self.instance.A, "Found element in A that we removed")

    def test_discardInvalid(self):
        """Check that we fail to remove an invalid set element without an exception"""
        self.instance.A.discard(self.e2)
        self.assertEqual( len(self.instance.A), 4)

    def test_iterator(self):
        """Check that we can iterate through the set"""
        self.tmp = set()
        for val in self.instance.A:
            self.tmp.add(val)
        self.assertFalse( self.tmp != self.instance.A.data(), "Set values found by the iterator appear to be different from the underlying set (%s) (%s)" % (str(self.tmp), str(self.instance.A.data())))

    def test_eq1(self):
        """Various checks for set equality and inequality (1)"""
        self.assertEqual( self.instance.A == self.instance.tmpset1, True)
        self.assertEqual( self.instance.tmpset1 == self.instance.A, True)
        self.assertEqual( self.instance.A != self.instance.tmpset1, False)
        self.assertEqual( self.instance.tmpset1 != self.instance.A, False)

    def test_eq2(self):
        """Various checks for set equality and inequality (2)"""
        self.assertEqual( self.instance.A == self.instance.tmpset2, False)
        self.assertEqual( self.instance.tmpset2 == self.instance.A, False)
        self.assertEqual( self.instance.A != self.instance.tmpset2, True)
        self.assertEqual( self.instance.tmpset2 != self.instance.A, True)

    def test_le1(self):
        """Various checks for set subset (1)"""
        self.assertEqual( self.instance.A < self.instance.tmpset1, False)
        self.assertEqual( self.instance.A <= self.instance.tmpset1, True)
        self.assertEqual( self.instance.A > self.instance.tmpset1, False)
        self.assertEqual( self.instance.A >= self.instance.tmpset1, True)
        self.assertEqual( self.instance.tmpset1 < self.instance.A, False)
        self.assertEqual( self.instance.tmpset1 <= self.instance.A, True)
        self.assertEqual( self.instance.tmpset1 > self.instance.A, False)
        self.assertEqual( self.instance.tmpset1 >= self.instance.A, True)

    def test_le2(self):
        """Various checks for set subset (2)"""
        self.assertEqual( self.instance.A < self.instance.tmpset2, True)
        self.assertEqual( self.instance.A <= self.instance.tmpset2, True)
        self.assertEqual( self.instance.A > self.instance.tmpset2, False)
        self.assertEqual( self.instance.A >= self.instance.tmpset2, False)
        self.assertEqual( self.instance.tmpset2 < self.instance.A, False)
        self.assertEqual( self.instance.tmpset2 <= self.instance.A, False)
        self.assertEqual( self.instance.tmpset2 > self.instance.A, True)
        self.assertEqual( self.instance.tmpset2 >= self.instance.A, True)

    def test_le3(self):
        """Various checks for set subset (3)"""
        self.assertEqual( self.instance.A < self.instance.tmpset3, False)
        self.assertEqual( self.instance.A <= self.instance.tmpset3, False)
        self.assertEqual( self.instance.A > self.instance.tmpset3, False)
        self.assertEqual( self.instance.A >= self.instance.tmpset3, False)
        self.assertEqual( self.instance.tmpset3 < self.instance.A, False)
        self.assertEqual( self.instance.tmpset3 <= self.instance.A, False)
        self.assertEqual( self.instance.tmpset3 > self.instance.A, False)
        self.assertEqual( self.instance.tmpset3 >= self.instance.A, False)

    def test_contains(self):
        """Various checks for contains() method"""
        self.assertEqual( self.e1 in self.instance.A, True)
        self.assertEqual( self.e2 in self.instance.A, False)
        self.assertEqual( '2' in self.instance.A, False)

    def test_or(self):
        """Check that set union works"""
        self.instance.tmp = self.instance.A | self.instance.tmpset3
        self.instance.tmp.construct()
        self.assertEqual( self.instance.tmp == self.instance.setunion, True)

    def test_and(self):
        """Check that set intersection works"""
        self.instance.tmp = self.instance.A & self.instance.tmpset3
        self.instance.tmp.construct()
        self.assertEqual( self.instance.tmp == self.instance.setintersection, True)

    def test_xor(self):
        """Check that set exclusive or works"""
        self.instance.tmp = self.instance.A ^ self.instance.tmpset3
        self.instance.tmp.construct()
        self.assertEqual( self.instance.tmp == self.instance.setxor, True)

    def test_diff(self):
        """Check that set difference works"""
        self.instance.tmp = self.instance.A - self.instance.tmpset3
        self.instance.tmp.construct()
        self.assertEqual( self.instance.tmp == self.instance.setdiff, True)

    def test_mul(self):
        """Check that set cross-product works"""
        self.instance.tmp = self.instance.A * self.instance.tmpset3
        self.instance.tmp.construct()
        self.assertEqual( self.instance.tmp == self.instance.setmul, True)

    def test_filter_constructor(self):
        """ Check that sets can filter out unwanted elements """
        def evenFilter(model, el):
            return el % 2 == 0
        self.instance.tmp = Set(initialize=range(0,10), filter=evenFilter)
        #self.instance.tmp.construct()
        self.assertEqual(sorted([x for x in self.instance.tmp]), [0,2,4,6,8])

    def test_filter_attribute(self):
        """ Check that sets can filter out unwanted elements """
        def evenFilter(model, el):
            return el % 2 == 0
        # Note: we cannot use the (concrete) instance here: the set
        # would be immediately constructed and would never see the
        # filter
        m = AbstractModel()
        m.tmp = Set(initialize=range(0,10))
        m.tmp.filter = evenFilter
        m.tmp.construct()
        self.assertEqual(sorted([x for x in m.tmp]), [0,2,4,6,8])

class SimpleSetAordered(SimpleSetA):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set A := 1 3 5 7; end;\n")
        OUTPUT.close()
        #
        # Create model instance
        #
        self.model.A = Set(ordered=True)
        #
        # Misc datasets
        #
        self.model.tmpset1 = Set(initialize=[1,3,5,7])
        self.model.tmpset2 = Set(initialize=[1,2,3,5,7])
        self.model.tmpset3 = Set(initialize=[2,3,5,7,9])

        self.model.setunion = Set(initialize=[1,2,3,5,7,9])
        self.model.setintersection = Set(initialize=[3,5,7])
        self.model.setxor = Set(initialize=[1,2,9])
        self.model.setdiff = Set(initialize=[1])
        self.model.setmul = Set(initialize=[(1,2), (1,3), (1,5), (1,7), (1,9),
                                      (3,2), (3,3), (3,5), (3,7), (3,9),
                                      (5,2), (5,3), (5,5), (5,7), (5,9),
                                      (7,2), (7,3), (7,5), (7,7), (7,9)])

        self.instance = self.model.create_instance(currdir+"setA.dat")

        self.e1=1
        self.e2=2
        self.e3=3
        self.e4=4
        self.e5=5
        self.e6=6

    def test_first(self):
        """Check that we can get the 'first' value in the set"""
        self.tmp = self.instance.A.first()
        self.assertNotEqual( self.tmp, None )
        self.assertEqual( self.tmp, 1 )

    def test_ordered(self):
        tmp=[]
        for val in self.instance.A:
            tmp.append(val)
        self.assertEqual( tmp, [1,3,5,7] )

    def test_getitem(self):
        self.assertEqual( self.instance.A[1], 1 )
        self.assertEqual( self.instance.A[2], 3 )
        self.assertEqual( self.instance.A[3], 5 )
        self.assertEqual( self.instance.A[4], 7 )
        self.assertEqual( self.instance.A[-1], 7 )
        self.assertEqual( self.instance.A[-2], 5 )
        self.assertEqual( self.instance.A[-3], 3 )
        self.assertEqual( self.instance.A[-4], 1 )
        self.assertRaises( IndexError, self.instance.A.__getitem__, 5)
        self.assertRaises( IndexError, self.instance.A.__getitem__, 0)
        self.assertRaises( IndexError, self.instance.A.__getitem__, -5)


class TestRangeSet(SimpleSetA):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.A = RangeSet(1,5)
        #
        # Misc datasets
        #
        self.model.tmpset1 = Set(initialize=[1,2,3,4,5])
        self.model.tmpset2 = Set(initialize=[1,2,3,4,5,7])
        self.model.tmpset3 = Set(initialize=[2,3,5,7,9])

        self.model.setunion = Set(initialize=[1,2,3,4,5,7,9])
        self.model.setintersection = Set(initialize=[2,3,5])
        self.model.setxor = Set(initialize=[1,4,7,9])
        self.model.setdiff = Set(initialize=[1,4])
        self.model.setmul = Set(initialize=[(1,2), (1,3), (1,5), (1,7), (1,9),
                                      (2,2), (2,3), (2,5), (2,7), (2,9),
                                      (3,2), (3,3), (3,5), (3,7), (3,9),
                                      (4,2), (4,3), (4,5), (4,7), (4,9),
                                      (5,2), (5,3), (5,5), (5,7), (5,9)])

        self.instance = self.model.create_instance()

        self.e1=1
        self.e2=2
        self.e3=3
        self.e4=4
        self.e5=5
        self.e6=6

    def test_clear(self):
        """Check the clear() method empties the set"""
        try:
            self.instance.A.clear()
            self.fail("Expected TypeError because a RangeSet is a virtual set")
        except TypeError:
            pass

    def test_virtual(self):
        """Check if this is a virtual set"""
        self.assertEqual( self.instance.A.virtual, True)

    def test_ordered_getitem(self):
        """Check if this is a virtual set"""
        self.assertEqual( self.instance.A[1], 1)
        self.assertEqual( self.instance.A[2], 2)
        self.assertEqual( self.instance.A[3], 3)
        self.assertEqual( self.instance.A[4], 4)
        self.assertEqual( self.instance.A[5], 5)
        self.assertEqual( self.instance.A[-1], 5)
        self.assertEqual( self.instance.A[-2], 4)
        self.assertEqual( self.instance.A[-3], 3)
        self.assertEqual( self.instance.A[-4], 2)
        self.assertEqual( self.instance.A[-5], 1)
        self.assertRaises( IndexError, self.instance.A.__getitem__, 6)
        self.assertRaises( IndexError, self.instance.A.__getitem__, 0)
        self.assertRaises( IndexError, self.instance.A.__getitem__, -6)

    def test_bounds(self):
        """Verify the bounds on this set"""
        self.assertEqual( self.instance.A.bounds(), (1,5))

    def test_addValid(self):
        """Check that we can add valid set elements"""
        pass

    def test_addInvalid(self):
        """Check that we get an error when adding invalid set elements"""
        #
        # This verifies that by default, all set elements are valid.  That
        # is, the default within is None
        #
        try:
            self.instance.A.add('2','3','4')
            self.fail("Expected to generate an error when we remove an element from a RangeSet")
        except TypeError:
            pass
        self.assertFalse( '2' in self.instance.A, "Value we attempted to add is not in A")

    def test_removeValid(self):
        """Check that we can remove a valid set element"""
        try:
            self.instance.A.remove(self.e3)
            self.fail("Expected to generate an error when we remove an element from a RangeSet")
        except KeyError:
            pass
        self.assertEqual( len(self.instance.A), 5)
        self.assertTrue( self.e3 in self.instance.A, "Element is still in A")

    def test_removeInvalid(self):
        """Check that we fail to remove an invalid set element"""
        self.assertRaises(KeyError, self.instance.A.remove, 6)
        self.assertEqual( len(self.instance.A), 5)

    def test_remove(self):
        """ Check that the elements are properly removed  by .remove """
        pass

    def test_discardValid(self):
        """Check that we can discard a valid set element"""
        try:
            self.instance.A.discard(self.e3)
            self.fail("Expected to generate an error when we discare an element from a RangeSet")
        except KeyError:
            pass
        self.assertEqual( len(self.instance.A), 5)
        self.assertTrue( self.e3 in self.instance.A, "Found element in A that attemped to discard")

    def test_discardInvalid(self):
        """Check that we fail to remove an invalid set element without an exception"""
        pass

    def test_contains(self):
        """Various checks for contains() method"""
        self.assertEqual( self.e1 in self.instance.A, True)
        self.assertEqual( self.e2 in self.instance.A, True)
        self.assertEqual( '2' in self.instance.A, False)

    def test_len(self):
        """Check that a simple set of numeric elements has the right size"""
        self.assertEqual( len(self.instance.A), 5)

    def test_data(self):
        """Check that we can access the underlying set data"""
        self.assertEqual( len(self.instance.A.data()), 5)

    def test_filter_constructor(self):
        """ Check that RangeSets can filter out unwanted elements """
        def evenFilter(model, el):
            return el % 2 == 0
        self.instance.tmp = RangeSet(0,10, filter=evenFilter)
        #self.instance.tmp.construct()
        self.assertEqual(sorted([x for x in self.instance.tmp]), [0,2,4,6,8,10])

    def test_filter_attribute(self):
        """ Check that RangeSets can filter out unwanted elements """
        def evenFilter(model, el):
            return el % 2 == 0
        self.instance.tmp = RangeSet(0,10)
        self.instance.tmp.filter = evenFilter
        self.instance.tmp.construct()
        self.assertEqual(sorted([x for x in self.instance.tmp]), [0,2,4,6,8,10])


class TestRangeSet2(TestRangeSet):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        def validate_fn(model, val):
            return (val >= 1) and (val <= 5)

        self.model.A = RangeSet(1,10, validate=validate_fn)
        #
        # Misc datasets
        #
        self.model.tmpset1 = Set(initialize=[1,2,3,4,5])
        self.model.tmpset2 = Set(initialize=[1,2,3,4,5,7])
        self.model.tmpset3 = Set(initialize=[2,3,5,7,9])

        self.model.setunion = Set(initialize=[1,2,3,4,5,7,9])
        self.model.setintersection = Set(initialize=[2,3,5])
        self.model.setxor = Set(initialize=[1,4,7,9])
        self.model.setdiff = Set(initialize=[1,4])
        self.model.setmul = Set(initialize=[(1,2), (1,3), (1,5), (1,7), (1,9),
                                      (2,2), (2,3), (2,5), (2,7), (2,9),
                                      (3,2), (3,3), (3,5), (3,7), (3,9),
                                      (4,2), (4,3), (4,5), (4,7), (4,9),
                                      (5,2), (5,3), (5,5), (5,7), (5,9)])

        self.instance = self.model.create_instance()

        self.e1=1
        self.e2=2
        self.e3=3
        self.e4=4
        self.e5=5
        self.e6=6


class TestRangeSet3(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.A = RangeSet(1.0,5.0,0.8)
        #
        # Misc datasets
        #
        self.model.tmpset1 = Set(initialize=[1,2,3,4,5])
        self.model.tmpset2 = Set(initialize=[1,2,3,4,5,7])
        self.model.tmpset3 = Set(initialize=[2,3,5,7,9])

        self.model.setunion = Set(initialize=[1,2,3,4,5,7,9])
        self.model.setintersection = Set(initialize=[2,3,5])
        self.model.setxor = Set(initialize=[1,4,7,9])
        self.model.setdiff = Set(initialize=[1,4])
        self.model.setmul = Set(initialize=[(1,2), (1,3), (1,5), (1,7), (1,9),
                                      (2,2), (2,3), (2,5), (2,7), (2,9),
                                      (3,2), (3,3), (3,5), (3,7), (3,9),
                                      (4,2), (4,3), (4,5), (4,7), (4,9),
                                      (5,2), (5,3), (5,5), (5,7), (5,9)])

        self.instance = self.model.create_instance()

        self.e1=1
        self.e2=2
        self.e3=3
        self.e4=4
        self.e5=5
        self.e6=6

    def test_bounds(self):
        """Verify the bounds on this set"""
        self.assertEqual( self.instance.A.bounds(), (1,5))


class TestRangeSet_AltArgs(PyomoModel):

    def test_ImmutableParams(self):
        model = ConcreteModel()
        model.lb = Param(initialize=1)
        model.ub = Param(initialize=5)
        model.A = RangeSet(model.lb, model.ub)
        self.assertEqual( model.A.data(), set([1,2,3,4,5]) )

    def test_MutableParams(self):
        model = ConcreteModel()
        model.lb = Param(initialize=1, mutable=True)
        model.ub = Param(initialize=5, mutable=True)
        model.A = RangeSet(model.lb, model.ub)
        self.assertEqual( model.A.data(), set([1,2,3,4,5]) )

        model.lb = 2
        model.ub = 4
        model.B = RangeSet(model.lb, model.ub)
        # Note: rangesets are constant -- even if the mutable param
        # under the hood changes
        self.assertEqual( model.A.data(), set([1,2,3,4,5]) )
        self.assertEqual( model.B.data(), set([2,3,4]) )

    def test_Expressions(self):
        model = ConcreteModel()
        model.p = Param(initialize=1, mutable=True)
        model.lb = Expression(expr=model.p*2-1)
        model.ub = Expression(expr=model.p*5)
        model.A = RangeSet(model.lb, model.ub)
        self.assertEqual( model.A.data(), set([1,2,3,4,5]) )

        model.p = 2
        model.B = RangeSet(model.lb, model.ub)
        # Note: rangesets are constant -- even if the mutable param
        # under the hood changes
        self.assertEqual( model.A.data(), set([1,2,3,4,5]) )
        self.assertEqual( model.B.data(), set([3,4,5,6,7,8,9,10]) )



class TestRangeSetMisc(unittest.TestCase):

    def test_constructor1(self):
        a=RangeSet(10)
        a.construct()
        tmp=[]
        for i in a:
            tmp.append(i)
        self.assertEqual(tmp, list(range(1,11)))
        self.assertEqual( a.bounds(), (1,10))


    def test_constructor2(self):
        a=RangeSet(1,10,2)
        a.construct()
        tmp=[]
        for i in a:
            tmp.append(i)
        self.assertEqual(tmp, list(range(1,11,2)))
        self.assertEqual( a.bounds(), (1,9))

    def test_constructor3(self):
        model=AbstractModel()
        model.a=Param(initialize=1)
        model.b=Param(initialize=2)
        model.c=Param(initialize=10)
        model.d=RangeSet( model.a*model.a, model.c*model.a, model.a*model.b)
        instance=model.create_instance()
        tmp=[]
        for i in instance.d:
            tmp.append(i)
        self.assertEqual(tmp, list(range(1,11,2)))
        self.assertEqual( instance.d.bounds(), (1,9))

class SimpleSetB(SimpleSetA):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set A := A1 A3 A5 A7; end;\n")
        OUTPUT.close()
        #
        # Create model instance
        #
        self.model.A = Set()
        #
        # Debugging
        #
        # Misc datasets
        #
        self.model.tmpset1 = Set(initialize=['A1','A3','A5','A7'])
        self.model.tmpset2 = Set(initialize=['A1','A2','A3','A5','A7'])
        self.model.tmpset3 = Set(initialize=['A2','A3','A5','A7','A9'])

        self.model.setunion = Set(initialize=['A1','A2','A3','A5','A7','A9'])
        self.model.setintersection = Set(initialize=['A3','A5','A7'])
        self.model.setxor = Set(initialize=['A1','A2','A9'])
        self.model.setdiff = Set(initialize=['A1'])
        self.model.setmul = Set(initialize=[('A1','A2'), ('A1','A3'), ('A1','A5'), ('A1','A7'), ('A1','A9'),
                                      ('A3','A2'), ('A3','A3'), ('A3','A5'), ('A3','A7'), ('A3','A9'),
                                      ('A5','A2'), ('A5','A3'), ('A5','A5'), ('A5','A7'), ('A5','A9'),
                                      ('A7','A2'), ('A7','A3'), ('A7','A5'), ('A7','A7'), ('A7','A9')])

        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.e1='A1'
        self.e2='A2'
        self.e3='A3'
        self.e4='A4'
        self.e5='A5'
        self.e6='A6'

    def test_bounds(self):
        self.assertEqual( self.instance.A.bounds(), None)

class SimpleSetC(SimpleSetA):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set A := (A1,1) (A3,1) (A5,1) (A7,1); end;\n")
        OUTPUT.close()
        #
        # Create model instance
        #
        self.model.A = Set(dimen=2)
        #
        # Debugging
        #
        # Misc datasets
        #
        self.model.tmpset1 = Set(initialize=[('A1',1), ('A3',1), ('A5',1), ('A7',1)])
        self.model.tmpset2 = Set(initialize=[('A1',1),('A2',1),('A3',1),('A5',1),('A7',1)])
        self.model.tmpset3 = Set(initialize=[('A2',1),('A3',1),('A5',1),('A7',1),('A9',1)])

        self.model.setunion = Set(initialize=[('A1',1),('A2',1),('A3',1),('A5',1),('A7',1),('A9',1)])
        self.model.setintersection = Set(initialize=[('A3',1),('A5',1),('A7',1)])
        self.model.setxor = Set(initialize=[('A1',1),('A2',1),('A9',1)])
        self.model.setdiff = Set(initialize=[('A1',1)])
        self.model.setmul = Set(initialize=[(('A1',1,'A2',1)), (('A1',1,'A3',1)), (('A1',1,'A5',1)), (('A1',1,'A7',1)), (('A1',1,'A9',1)),
                                      (('A3',1,'A2',1)), (('A3',1,'A3',1)), (('A3',1,'A5',1)), (('A3',1,'A7',1)), (('A3',1,'A9',1)),
                                      (('A5',1,'A2',1)), (('A5',1,'A3',1)), (('A5',1,'A5',1)), (('A5',1,'A7',1)), (('A5',1,'A9',1)),
                                      (('A7',1,'A2',1)), (('A7',1,'A3',1)), (('A7',1,'A5',1)), (('A7',1,'A7',1)), (('A7',1,'A9',1))])

        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.e1=('A1',1)
        self.e2=('A2',1)
        self.e3=('A3',1)
        self.e4=('A4',1)
        self.e5=('A5',1)
        self.e6=('A6',1)

    def tearDown(self):
        #
        # Remove Set 'A' data file
        #
        os.remove(currdir+"setA.dat")

    def test_bounds(self):
        self.assertEqual( self.instance.A.bounds(), None)

    def test_addInvalid(self):
        """Check that we get an error when adding invalid set elements"""
        #
        # This verifies that by default, all set elements are valid.  That
        # is, the default within is None
        #
        self.assertEqual( self.instance.A.domain, None)
        try:
            self.instance.A.add('2','3','4')
        except ValueError:
            pass
        else:
            self.fail("fail test_addInvalid")
        self.assertFalse( '2' in self.instance.A, "Found invalid new element in A")
        self.instance.A.add(('2','3'))

@unittest.skipIf(not _has_numpy, "Numpy is not installed")
class SimpleSetNumpy(SimpleSetA):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set A := 1.0 3 5.0 7.0; end;\n")
        OUTPUT.close()
        #
        # Create model instance
        #
        self.model.A = Set()
        #
        # Debugging
        #
        # Misc datasets
        #
        self.model.tmpset1 = Set(initialize=[1.0,3.0,5,7])
        self.model.tmpset2 = Set(initialize=[1.0,2,3.0,5,7])
        self.model.tmpset3 = Set(initialize=[2,3.0,5,7,9.1])

        self.model.setunion = Set(initialize=[1.0,2,3.0,5,7,9.1])
        self.model.setintersection = Set(initialize=[3.0,5,7])
        self.model.setxor = Set(initialize=[1.0,2,9.1])
        self.model.setdiff = Set(initialize=[1.0])
        self.model.setmul = Set(initialize=[(1.0,2), (1.0,3.0), (1.0,5), (1.0,7), (1.0,9.1),
                                      (3.0,2), (3.0,3.0), (3.0,5), (3.0,7), (3.0,9.1),
                                      (5,2), (5,3.0), (5,5), (5,7), (5,9.1),
                                      (7,2), (7,3.0), (7,5), (7,7), (7,9.1)])

        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.e1=numpy.bool_(1)
        self.e2=numpy.int_(2)
        self.e3=numpy.float_(3.0)
        self.e4=numpy.int_(4)
        self.e5=numpy.int_(5)
        self.e6=numpy.int_(6)

    def test_numpy_bool(self):
        model = ConcreteModel()
        model.A = Set(initialize=[numpy.bool_(False), numpy.bool_(True)])
        self.assertEqual( model.A.bounds(), None)

    def test_numpy_int(self):
        model = ConcreteModel()
        model.A = Set(initialize=[numpy.int_(1.0), numpy.int_(0.0)])
        self.assertEqual( model.A.bounds(), (0,1))

    def test_numpy_float(self):
        model = ConcreteModel()
        model.A = Set(initialize=[numpy.float_(1.0), numpy.float_(0.0)])
        self.assertEqual( model.A.bounds(), (0,1))


class ArraySet(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set Z := A C; set A[A] := 1 3 5 7; set A[C] := 3 5 7 9; end;\n")
        OUTPUT.close()
        #
        # Create model instance
        #
        self.model.Z = Set()
        self.model.A = Set(self.model.Z)
        #
        # Debugging
        #
        # Misc datasets
        #
        self.model.tmpset1 = Set()
        self.model.tmpset2 = Set()
        self.model.tmpset3 = Set()

        self.model.S = RangeSet(0,5)
        self.model.T = RangeSet(0,5)
        self.model.R = RangeSet(0,3)
        self.model.Q_a = Set(initialize=[1,3,5,7])
        self.model.Q_c = Set(initialize=[3,5,7,9])

        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.e1=('A1',1)

    def Xtest_bounds(self):
        self.assertEqual( self.instance.A.bounds(), None)

    def test_getitem(self):
        """Check the access to items"""
        try:
            tmp=[]
            for val in self.instance.A['A']:
                tmp.append(val)
            tmp.sort()
        except:
            self.fail("Problems getting a valid set from a set array")
        self.assertEqual( tmp, [1,3,5,7])
        try:
            tmp = self.instance.A['D']
        except KeyError:
            pass
        else:
            self.fail("Problems getting an invalid set from a set array")

    def test_setitem(self):
        """Check the access to items"""
        try:
            self.model.Z = Set(initialize=['A','C'])
            self.model.A = Set(self.model.Z,initialize={'A':[1]})
            self.instance = self.model.create_instance()
            tmp=[1,6,9]
            self.instance.A['A'] = tmp
            self.instance.A['C'] = tmp
        except:
            self.fail("Problems setting a valid set into a set array")
        try:
            self.instance.A['D'] = tmp
        except KeyError:
            pass
        else:
            self.fail("Problems setting an invalid set into a set array")

    def test_keys(self):
        """Check the keys for the array"""
        tmp=list(self.instance.A.keys())
        tmp.sort()
        self.assertEqual(tmp, ['A', 'C'])

    def test_len(self):
        """Check that a simple set of numeric elements has the right size"""
        try:
            len(self.instance.A)
        except TypeError:
            self.fail("fail test_len")
        else:
            pass

    def test_data(self):
        """Check that we can access the underlying set data"""
        try:
            self.instance.A.data()
        except:
            self.fail("Expected data() method to pass")

    def test_dim(self):
        """Check that a simple set has dimension zero for its indexing"""
        self.assertEqual( self.instance.A.dim(), 1)

    def test_clear(self):
        """Check the clear() method empties the set"""
        self.instance.A.clear()
        for key in self.instance.A:
            self.assertEqual( len(self.instance.A[key]), 0)

    def test_virtual(self):
        """Check if this is not a virtual set"""
        try:
            self.instance.A.virtual
        except:
            pass
        else:
            self.fail("Set arrays do not have a virtual data element")

    def test_check_values(self):
        """Check if the values added to this set are valid"""
        #
        # This should not throw an exception here
        #
        self.instance.A.check_values()

    def test_first(self):
        """Check that we can get the 'first' value in the set"""
        pass

    def test_removeValid(self):
        """Check that we can remove a valid set element"""
        pass

    def test_removeInvalid(self):
        """Check that we fail to remove an invalid set element"""
        pass

    def test_discardValid(self):
        """Check that we can discard a valid set element"""
        pass

    def test_discardInvalid(self):
        """Check that we fail to remove an invalid set element without an exception"""
        pass

    def test_iterator(self):
        """Check that we can iterate through the set"""
        tmp = 0
        for key in self.instance.A:
            tmp += len(self.instance.A[key])
        self.assertEqual( tmp, 8)

    def test_eq1(self):
        """ Various checks for set equality and inequality (1) """
        self.assertEqual(self.instance.A != self.instance.tmpset1, True)
        self.assertEqual(self.instance.tmpset1 != self.instance.A, True)
        self.assertEqual(self.instance.A == self.instance.tmpset1, False)
        self.assertEqual(self.instance.tmpset1 == self.instance.A, False)

    def test_eq2(self):
        """ Various checks for set equality and inequality (2) """
        self.assertEqual(self.instance.A == self.instance.tmpset2, False)
        self.assertEqual(self.instance.tmpset2 == self.instance.A, False)
        self.assertEqual(self.instance.A != self.instance.tmpset2, True)
        self.assertEqual(self.instance.tmpset2 != self.instance.A, True)

    def test_eq3(self):
        """ Various checks for set equality and inequality (3) """

        # Each test should be done with the arguments on each side to check
        # for commutativity

        # Self-equality
        self.assertEqual(self.instance.S == self.instance.S, True)
        self.assertEqual(self.instance.S != self.instance.S, False)

        # Equivalent members
        self.assertEqual(self.instance.S == self.instance.T, True)
        self.assertEqual(self.instance.T == self.instance.S, True)

        # Subset/superset nonequality
        self.assertEqual(self.instance.S != self.instance.R, True)
        self.assertEqual(self.instance.R != self.instance.S, True)

        # Manually initialized (Q_a) v. data file initialized (A["A"]) equality
        self.assertEqual(self.instance.A["A"] == self.instance.Q_a, True)
        self.assertEqual(self.instance.Q_a == self.instance.A["A"], True)

        # Manually initialized (Q_c) v. data file initialized (A["C"]) equality
        self.assertEqual(self.instance.A["C"] == self.instance.Q_c, True)
        self.assertEqual(self.instance.Q_c == self.instance.A["C"], True)

        # Comparison between Set and non-Set objects
        self.assertEqual(self.instance.A == 1.0, False)
        self.assertEqual(1.0 == self.instance.A, False)

        # Comparison between Set and non-Set objects
        self.assertEqual(self.instance.A != 1.0, True)
        self.assertEqual(1.0 != self.instance.A, True)

    def test_contains(self):
        """Various checks for contains() method"""
        tmp = self.e1 in self.instance.A
        self.assertEqual( tmp, False )

    def test_or(self):
        """Check that set union works"""
        try:
            self.instance.A | self.instance.tmpset3
        except TypeError:
            pass
        else:
            self.fail("fail test_or")

    def test_and(self):
        """Check that set intersection works"""
        try:
            self.instance.tmp = self.instance.A & self.instance.tmpset3
        except TypeError:
            pass
        else:
            self.fail("fail test_and")

    def test_xor(self):
        """Check that set exclusive or works"""
        try:
            self.instance.A ^ self.instance.tmpset3
        except TypeError:
            pass
        else:
            self.fail("fail test_xor")

    def test_diff(self):
        """Check that set difference works"""
        try:
            self.instance.A - self.instance.tmpset3
        except TypeError:
            pass
        else:
            self.fail("fail test_diff")

    def test_mul(self):
        """Check that set cross-product works"""
        try:
            self.instance.A * self.instance.tmpset3
        except TypeError:
            pass
        else:
            self.fail("fail test_mul")


class ArraySet2(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set Z := A C; set Y := 1 2 ; set A[A,1] := 1 3 5 7; set A[C,2] := 3 5 7 9; end;")
        OUTPUT.close()
        #
        # Create model instance
        #
        self.model.Z = Set()
        self.model.Y = Set()
        self.model.A = Set(self.model.Z,self.model.Y)
        #
        # Debugging
        #
        # Misc datasets
        #
        self.model.tmpset1 = Set()
        self.model.tmpset2 = Set()
        self.model.tmpset3 = Set()

        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.e1=('A1',1)

    def test_bounds(self):
        self.assertEqual( self.instance.A['A',1].bounds(), None)

    def test_getitem(self):
        """Check the access to items"""
        try:
            tmp=[]
            for val in self.instance.A['A',1]:
                tmp.append(val)
            tmp.sort()
        except:
            self.fail("Problems getting a valid subsetset from a set array")
        self.assertEqual( tmp, [1,3,5,7])

        try:
            tmp = self.instance.A['A',2]
        except:
            self.fail( "Problems getting a valid uninitialized subset "
                       "from a set array" )

        try:
            tmp = self.instance.A['A',3]
        except KeyError:
            pass
        else:
            self.fail("Problems getting an invalid set from a set array")

    def Xtest_setitem(self):
        """Check the access to items"""
        try:
            self.model.Y = Set(initialize=[1,2])
            self.model.Z = Set(initialize=['A','C'])
            self.model.A = Set(self.model.Z,self.model.Y,initialize={'A':[1]})
            self.instance = self.model.create_instance()
            tmp=[1,6,9]
            self.instance.A['A'] = tmp
            self.instance.A['C'] = tmp
        except:
            self.fail("Problems setting a valid set into a set array")
        try:
            self.instance.A['D'] = tmp
        except KeyError:
            pass
        else:
            self.fail("Problems setting an invalid set into a set array")

    def Xtest_keys(self):
        """Check the keys for the array"""
        tmp=self.instance.A.keys()
        tmp.sort()
        self.assertEqual(tmp, ['A', 'C'])

    def Xtest_len(self):
        """Check that a simple set of numeric elements has the right size"""
        try:
            len(self.instance.A)
        except TypeError:
            pass
        else:
            self.fail("fail test_len")

    def Xtest_data(self):
        """Check that we can access the underlying set data"""
        try:
            self.instance.A.data()
        except TypeError:
            pass
        else:
            self.fail("fail test_data")

    def Xtest_dim(self):
        """Check that a simple set has dimension zero for its indexing"""
        self.assertEqual( self.instance.A.dim(), 1)

    def Xtest_clear(self):
        """Check the clear() method empties the set"""
        self.instance.A.clear()
        for key in self.instance.A:
            self.assertEqual( len(self.instance.A[key]), 0)

    def Xtest_virtual(self):
        """Check if this is not a virtual set"""
        self.assertEqual( self.instance.A.virtual, False)

    def Xtest_check_values(self):
        """Check if the values added to this set are valid"""
        #
        # This should not throw an exception here
        #
        self.instance.A.check_values()

    def Xtest_first(self):
        """Check that we can get the 'first' value in the set"""
        pass

    def Xtest_removeValid(self):
        """Check that we can remove a valid set element"""
        pass

    def Xtest_removeInvalid(self):
        """Check that we fail to remove an invalid set element"""
        pass

    def Xtest_discardValid(self):
        """Check that we can discard a valid set element"""
        pass

    def Xtest_discardInvalid(self):
        """Check that we fail to remove an invalid set element without an exception"""
        pass

    def Xtest_iterator(self):
        """Check that we can iterate through the set"""
        tmp = 0
        for key in self.instance.A:
            tmp += len(self.instance.A[key])
        self.assertEqual( tmp, 8)

    def Xtest_eq1(self):
        """Various checks for set equality and inequality (1)"""
        try:
            self.assertEqual( self.instance.A == self.instance.tmpset1, True)
            self.assertEqual( self.instance.tmpset1 == self.instance.A, True)
            self.assertEqual( self.instance.A != self.instance.tmpset1, False)
            self.assertEqual( self.instance.tmpset1 != self.instance.A, False)
        except TypeError:
            pass
        else:
            self.fail("fail test_eq1")

    def Xtest_eq2(self):
        """Various checks for set equality and inequality (2)"""
        try:
            self.assertEqual( self.instance.A == self.instance.tmpset2, False)
            self.assertEqual( self.instance.tmpset2 == self.instance.A, False)
            self.assertEqual( self.instance.A != self.instance.tmpset2, True)
            self.assertEqual( self.instance.tmpset2 != self.instance.A, True)
        except TypeError:
            pass
        else:
            self.fail("fail test_eq2")

    def Xtest_contains(self):
        """Various checks for contains() method"""
        tmp = self.e1 in self.instance.A
        self.assertEqual( tmp, False )

    def Xtest_or(self):
        """Check that set union works"""
        try:
            self.instance.A | self.instance.tmpset3
        except TypeError:
            pass
        else:
            self.fail("fail test_or")

    def Xtest_and(self):
        """Check that set intersection works"""
        try:
            self.instance.tmp = self.instance.A & self.instance.tmpset3
        except TypeError:
            pass
        else:
            self.fail("fail test_and")

    def Xtest_xor(self):
        """Check that set exclusive or works"""
        try:
            self.instance.A ^ self.instance.tmpset3
        except TypeError:
            pass
        else:
            self.fail("fail test_xor")

    def Xtest_diff(self):
        """Check that set difference works"""
        try:
            self.instance.A - self.instance.tmpset3
        except TypeError:
            pass
        else:
            self.fail("fail test_diff")

    def Xtest_mul(self):
        """Check that set cross-product works"""
        try:
            self.instance.A * self.instance.tmpset3
        except TypeError:
            pass
        else:
            self.fail("fail test_mul")


class RealSetTests(SimpleSetA):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        x = RealSet()
        x.concrete=True
        self.model.A = x
        x.concrete=False
        #
        # Misc datasets
        #
        self.model.tmpset1 = Set(initialize=[1.1,3.1,5.1,7.1])
        self.model.tmpset2 = Set(initialize=[1.1,2.1,3.1,5.1,7.1])
        self.model.tmpset3 = Set(initialize=[2.1,3.1,5.1,7.1,9.1])

        y = RealSet()
        y.concrete=True
        self.model.setunion = y
        y.concrete=False
        self.model.setintersection = Set(initialize=[1.1,3.1,5.1,7.1])
        self.model.setxor = Set(initialize=[])
        self.model.setdiff = Set(initialize=[])
        self.model.setmul = None

        self.instance = self.model.create_instance()
        self.e1=1.1
        self.e2=2.1
        self.e3=3.1
        self.e4=4.1
        self.e5=5.1
        self.e6=6.1

    def tearDown(self):
        pass

    def test_bounds(self):
        self.assertEqual( self.instance.A.bounds(), (None,None))

    def test_len(self):
        """Check that the set has the right size"""
        try:
            len(self.instance.A)
        except ValueError:
            pass
        else:
            self.fail("test_len failure")

    def test_data(self):
        """Check that we can access the underlying set data"""
        try:
            self.instance.A.data()
        except TypeError:
            pass
        else:
            self.fail("test_data failure")

    def test_clear(self):
        """Check that the clear() method generates an exception"""
        self.assertRaises(TypeError, self.instance.A.clear)

    def test_virtual(self):
        """Check if this is not a virtual set"""
        self.assertEqual( self.instance.A.virtual, True)

    def test_discardValid(self):
        """Check that we fail to remove an invalid set element without an exception"""
        self.assertRaises(KeyError, self.instance.A.discard, self.e2)

    def test_discardInvalid(self):
        """Check that we fail to remove an invalid set element without an exception"""
        pass

    def test_removeValid(self):
        """Check that we can remove a valid set element"""
        self.assertRaises(KeyError, self.instance.A.remove, self.e3)

    def test_removeInvalid(self):
        pass

    def test_addInvalid(self):
        """Check that we get an error when adding invalid set elements"""
        pass

    def test_addValid(self):
        """Check that we can add valid set elements"""
        self.assertEqual( self.instance.A.domain, None)
        self.assertRaises(TypeError,self.instance.A.add,2)

    def test_iterator(self):
        """Check that we can iterate through the set"""
        try:
            for val in self.instance.A:
                tmp=val
        except TypeError:
            pass
        else:
            self.fail("test_iterator failure")

    def test_eq1(self):
        """Various checks for set equality and inequality (1)"""
        self.assertTrue(not(self.instance.A == self.instance.tmpset1))
        self.assertTrue(not(self.instance.tmpset1 == self.instance.A))
        self.assertTrue(self.instance.A != self.instance.tmpset1)
        self.assertTrue(self.instance.tmpset1 != self.instance.A)


    def test_eq2(self):
        """Various checks for set equality and inequality (2)"""
        self.assertTrue(not(self.instance.A == self.instance.tmpset2))
        self.assertTrue(not(self.instance.tmpset2 == self.instance.A))
        self.assertTrue(self.instance.A != self.instance.tmpset2)
        self.assertTrue(self.instance.tmpset2 != self.instance.A)

    def test_le1(self):
        """Various checks for set subset (1)"""
        try:
            self.instance.A < self.instance.tmpset1
            self.instance.A <= self.instance.tmpset1
            self.instance.A > self.instance.tmpset1
            self.instance.A >= self.instance.tmpset1
            self.instance.tmpset1 < self.instance.A
            self.instance.tmpset1 <= self.instance.A
            self.instance.tmpset1 > self.instance.A
            self.instance.tmpset1 >= self.instance.A
        except TypeError:
            pass
        else:
            self.fail("test_le1 failure")

    def test_le2(self):
        """Various checks for set subset (2)"""
        try:
            self.instance.A < self.instance.tmpset2
            self.instance.A <= self.instance.tmpset2
            self.instance.A > self.instance.tmpset2
            self.instance.A >= self.instance.tmpset2
            self.instance.tmpset2 < self.instance.A
            self.instance.tmpset2 <= self.instance.A
            self.instance.tmpset2 > self.instance.A
            self.instance.tmpset2 >= self.instance.A
        except TypeError:
            pass
        else:
            self.fail("test_le2 failure")

    def test_le3(self):
        """Various checks for set subset (3)"""
        try:
            self.instance.A < self.instance.tmpset3
            self.instance.A <= self.instance.tmpset3
            self.instance.A > self.instance.tmpset3
            self.instance.A >= self.instance.tmpset3
            self.instance.tmpset3 < self.instance.A
            self.instance.tmpset3 <= self.instance.A
            self.instance.tmpset3 > self.instance.A
            self.instance.tmpset3 >= self.instance.A
        except TypeError:
            pass
        else:
            self.fail("test_le3 failure")

    def test_contains(self):
        """Various checks for contains() method"""
        self.assertEqual( self.e1 in self.instance.A, True)
        self.assertEqual( self.e2 in self.instance.A, True)
        self.assertEqual( '2' in self.instance.A, False)

    def test_or(self):
        """Check that set union works"""
        try:
            self.instance.tmp = self.instance.A | self.instance.tmpset3
        except TypeError:
            pass
        else:
            self.fail("Operator __or__ should have failed.")

    def test_and(self):
        """Check that set intersection works"""
        try:
            self.instance.tmp = self.instance.A & self.instance.tmpset3
        except TypeError:
            pass
        else:
            self.fail("Operator __and__ should have failed.")

    def test_xor(self):
        """Check that set exclusive or works"""
        try:
            self.tmp = self.instance.A ^ self.instance.tmpset3
        except:
            pass
        else:
            self.fail("Operator __xor__ should have failed.")

    def test_diff(self):
        """Check that set difference works"""
        try:
            self.tmp = self.instance.A - self.instance.tmpset3
        except:
            pass
        else:
            self.fail("Operator __diff__ should have failed.")

    def test_mul(self):
        """Check that set cross-product works"""
        try:
            self.instance.tmp = self.instance.A * self.instance.tmpset3
        except:
            pass
        else:
            self.fail("Operator __mul__ should have failed.")


class IntegerSetTests(RealSetTests):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        x = IntegerSet()
        x.concrete=True
        self.model.A = x
        x.concrete=False
        #
        # Misc datasets
        #
        self.model.tmpset1 = Set(initialize=[1,3,5,7])
        self.model.tmpset2 = Set(initialize=[1,2,3,5,7])
        self.model.tmpset3 = Set(initialize=[2,3,5,7,9])

        y = IntegerSet()
        y.concrete=True
        self.model.setunion = y
        y.concrete=False
        self.model.setintersection = Set(initialize=[1,3,5,7])
        self.model.setxor = Set(initialize=[])
        self.model.setdiff = Set(initialize=[])
        self.model.setmul = None

        self.instance = self.model.create_instance()
        self.e1=1
        self.e2=2
        self.e3=3
        self.e4=4
        self.e5=5
        self.e6=6

    def test_bounds(self):
        self.assertEqual( self.instance.A.bounds(), (None,None))


class AnySetTests(RealSetTests):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        x = _AnySet()
        x.concrete=True
        self.model.A = x
        x.concrete=False
        #
        # Misc datasets
        #
        self.model.tmpset1 = Set(initialize=[1,'3',5,7])
        self.model.tmpset2 = Set(initialize=[1,2,'3',5,7])
        self.model.tmpset3 = Set(initialize=[2,'3',5,7,9])

        y = _AnySet()
        y.concrete=True
        self.model.setunion = y
        y.concrete=False
        self.model.setintersection = Set(initialize=[1,'3',5,7])
        self.model.setxor = Set(initialize=[])
        self.model.setdiff = Set(initialize=[])
        self.model.setmul = None

        self.instance = self.model.create_instance()
        self.e1=1
        self.e2=2
        self.e3='3'
        self.e4=4
        self.e5=5
        self.e6=6

    def test_bounds(self):
        self.assertEqual( self.instance.A.bounds(), None)

    def test_contains(self):
        """Various checks for contains() method"""
        self.assertEqual( self.e1 in self.instance.A, True)
        self.assertEqual( self.e2 in self.instance.A, True)
        self.assertEqual( '2' in self.instance.A, True)

    def test_None1(self):
        self.assertEqual( None in Any, False)

    def test_None2(self):
        self.assertEqual( None in AnyWithNone, True)

class SetArgs1(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)

    def test_initialize1(self):
        self.model.A = Set(initialize=[1,2,3,'A'])
        self.instance = self.model.create_instance()
        self.assertEqual(len(self.instance.A),4)

    def test_initialize2(self):
        self.model.A = Set(initialize=[(i,j) for i in range(0,3) for j in range(1,4) if (i+j)%2 == 0])
        self.instance = self.model.create_instance()
        self.assertEqual(len(self.instance.A),4)

    def test_initialize3(self):
        self.model.A = Set(initialize=((i,j) for i in range(0,3) for j in range(1,4) if (i+j)%2 == 0))
        self.instance = self.model.create_instance()
        self.assertEqual(len(self.instance.A),4)

    def test_initialize4(self):
        self.model.A = Set(initialize=range(0,4))
        def B_index(model):
            return (i for i in model.A if i%2 == 0)
        def B_init(model, i):
            return range(i,2+i)
        self.model.B = Set(B_index, initialize=B_init)
        self.instance = self.model.create_instance()
        #self.instance.pprint()
        self.assertEqual(self.instance.B[0].value,set([0,1]))
        self.assertEqual(self.instance.B[2].value,set([2,3]))
        self.assertEqual(list(sorted(self.instance.B.keys())),[0,2])

    def test_initialize5(self):
        self.model.A = Set(initialize=range(0,4))
        def B_index(model):
            for i in model.A:
                if i%2 == 0:
                    yield i
        def B_init(model, i):
            return range(i,2+i)
        self.model.B = Set(B_index, initialize=B_init)
        self.instance = self.model.create_instance()
        #self.instance.pprint()
        self.assertEqual(self.instance.B[0].value,set([0,1]))
        self.assertEqual(self.instance.B[2].value,set([2,3]))
        self.assertEqual(list(sorted(self.instance.B.keys())),[0,2])

    def test_initialize6(self):
        self.model.A = Set(initialize=range(0,4))
        def B_index(model):
            for i in model.A:
                if i%2 == 0:
                    yield i
        def B_init(model, i, j):
            k=i+j               # A dummy calculation
            if j:
                return range(i,2+i)
            return []
        self.model.B = Set(B_index, [True,False], initialize=B_init)
        self.instance = self.model.create_instance()
        #self.instance.pprint()
        self.assertEqual(set(self.instance.B.keys()),set([(0,True),(2,True),(0,False),(2,False)]))
        self.assertEqual(self.instance.B[0,True].value,set([0,1]))
        self.assertEqual(self.instance.B[2,True].value,set([2,3]))

    def test_initialize7(self):
        self.model.A = Set(initialize=range(0,3))
        @set_options(dimen=3)
        def B_index(model):
            return [(i,i+1,i*i) for i in model.A]
        def B_init(model, i, ii, iii, j):
            k=i+j               # A dummy calculation
            if j:
                return range(i,2+i)
            return []
        self.model.B = Set(B_index, [True,False], initialize=B_init)
        self.instance = self.model.create_instance()
        #self.instance.pprint()
        self.assertEqual(set(self.instance.B.keys()),set([(0,1,0,True),(1,2,1,True),(2,3,4,True),(0,1,0,False),(1,2,1,False),(2,3,4,False)]))
        self.assertEqual(self.instance.B[0,1,0,True].value,set([0,1]))
        self.assertEqual(self.instance.B[2,3,4,True].value,set([2,3]))

    def test_initialize8(self):
        self.model.A = Set(initialize=range(0,3))
        def B_index(model):
            return [(i,i+1,i*i) for i in model.A]
        def B_init(model, i, ii, iii, j):
            if j:
                return range(i,2+i)
            return []
        self.model.B = Set(B_index, [True,False], initialize=B_init)
        try:
            self.instance = self.model.create_instance()
            self.fail("Expected ValueError because B_index returns a tuple")
        except ValueError:
            pass

    def test_initialize9(self):
        self.model.A = Set(initialize=range(0,3))
        @set_options(domain=Integers)
        def B_index(model):
            return [i/2.0 for i in model.A]
        def B_init(model, i, j):
            if j:
                return range(int(i),int(2+i))
            return []
        self.model.B = Set(B_index, [True,False], initialize=B_init)
        try:
            self.instance = self.model.create_instance()
            self.fail("Expected ValueError because B_index returns invalid set values")
        except ValueError:
            pass

    def test_dimen1(self):
        #
        # Create model instance
        #
        self.model.A = Set(initialize=[1,2,3], dimen=1)
        self.instance = self.model.create_instance()
        #
        try:
            self.model.A = Set(initialize=[4,5,6], dimen=2)
            self.instance = self.model.create_instance()
        except ValueError:
            pass
        else:
            self.fail("test_dimen")
        #
        self.model.A = Set(initialize=[(1,2), (2,3), (3,4)], dimen=2)
        self.instance = self.model.create_instance()
        #
        try:
            self.model.A = Set(initialize=[(1,2), (2,3), (3,4)], dimen=1)
            self.instance = self.model.create_instance()
        except ValueError:
            pass
        else:
            self.fail("test_dimen")
        #
        def f(model):
            return [(1,1), (2,2), (3,3)]
        self.model.A = Set(initialize=f, dimen=2)
        self.instance = self.model.create_instance()
        #
        try:
            self.model.A = Set(initialize=f, dimen=3)
            self.instance = self.model.create_instance()
        except ValueError:
            pass
        else:
            self.fail("test_dimen")

    def test_dimen2(self):
        try:
            self.model.A = Set(initialize=[1,2,(3,4)])
            self.instance = self.model.create_instance()
        except ValueError:
            pass
        else:
            self.fail("test_dimen2")
        self.model.A = Set(dimen=None, initialize=[1,2,(3,4)])
        self.instance = self.model.create_instance()


    def test_rule(self):
        #
        # Create model instance
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; param n := 5; end;")
        OUTPUT.close()
        def tmp_init(model):
            ##model.n.pprint()
            ##print "HERE",model.n,value(model.n)
            return range(0,value(model.n))
        self.model.n = Param()
        self.model.A = Set(initialize=tmp_init)
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual(len(self.instance.A),5)

    def test_rule2(self):
        #
        # Create model instance
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; param n := 5; end;")
        OUTPUT.close()
        @simple_set_rule
        def tmp_init(model, z):
            if z>value(model.n) or z == 11:
                return None
            return z
        self.model.n = Param()
        self.model.A = Set(initialize=tmp_init)
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual(len(self.instance.A),5)

    def test_rule3(self):
        #
        # Create model instance
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; param n := 5; end;")
        OUTPUT.close()
        def tmp_init(model, z):
            if z>value(model.n) or z == 11:
                return Set.End
            return z
        self.model.n = Param()
        self.model.A = Set(initialize=tmp_init)
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual(len(self.instance.A),5)

    def test_within1(self):
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set A := 1 3 5 7.5; end;")
        OUTPUT.close()
        #
        # Create A with an error
        #
        self.model.A = Set(within=Integers)
        try:
            self.instance = self.model.create_instance(currdir+"setA.dat")
        except ValueError:
            pass
        else:
            self.fail("fail test_within1")

    def test_within2(self):
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set A := 1 3 5 7.5; end;")
        OUTPUT.close()
        #
        # Create A with an error
        #
        self.model.A = Set(within=Reals)
        try:
            self.instance = self.model.create_instance(currdir+"setA.dat")
        except ValueError:
            self.fail("fail test_within2")
        else:
            pass

    def test_validation1(self):
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set A := 1 3 5 7.5; end;")
        OUTPUT.close()
        #
        # Create A with an error
        #
        self.model.A = Set(validate=lambda model, x:x<6)
        try:
            self.instance = self.model.create_instance(currdir+"setA.dat")
        except ValueError:
            pass
        else:
            self.fail("fail test_validation1")

    def test_validation2(self):
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set A := 1 3 5 5.5; end;")
        OUTPUT.close()
        #
        # Create A with an error
        #
        self.model.A = Set(validate=lambda model, x:x<6)
        try:
            self.instance = self.model.create_instance(currdir+"setA.dat")
        except ValueError:
            self.fail("fail test_validation2")
        else:
            pass

    def test_other1(self):
        self.model.A = Set(initialize=[1,2,3,'A'], validate=lambda model, x:x in Integers)
        try:
            self.instance = self.model.create_instance()
        except ValueError:
            pass
        else:
            self.fail("fail test_other1")

    def test_other2(self):
        self.model.A = Set(initialize=[1,2,3,'A'], within=Integers)
        try:
            self.instance = self.model.create_instance()
        except ValueError:
            pass
        else:
            self.fail("fail test_other1")

    def test_other3(self):
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; param n := 5; end;")
        OUTPUT.close()
        def tmp_init(model):
            tmp=[]
            for i in range(0,value(model.n)):
                tmp.append(i/2.0)
            return tmp
        self.model.n = Param()
        self.model.A = Set(initialize=tmp_init, validate=lambda model, x:x in Integers)
        try:
            self.instance = self.model.create_instance(currdir+"setA.dat")
        except ValueError:
            pass
        else:
            self.fail("fail test_other1")

    def test_other4(self):
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; param n := 5; end;")
        OUTPUT.close()
        def tmp_init(model):
            tmp=[]
            for i in range(0,value(model.n)):
                tmp.append(i/2.0)
            return tmp
        self.model.n = Param()
        self.model.A = Set(initialize=tmp_init, within=Integers)
        try:
            self.instance = self.model.create_instance(currdir+"setA.dat")
        except ValueError:
            pass
        else:
            self.fail("fail test_other1")

    def tearDown(self):
        #
        # Remove Set 'A' data file
        #
        if os.path.exists(currdir+"setA.dat"):
            os.remove(currdir+"setA.dat")


class SetArgs2(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)

    def test_initialize(self):
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set Z := A C; set A[A] := 1 3 5 7; end;")
        OUTPUT.close()
        #
        # Create model instance
        #
        self.model.Z = Set()
        self.model.A = Set(self.model.Z, initialize={'A':[1,2,3,'A']})
        self.instance = self.model.create_instance()
        self.assertEqual(len(self.instance.A['A']),4)

    def test_dimen(self):
        #
        # Create model instance
        #
        self.model.Z = Set(initialize=[1,2])
        self.model.A = Set(self.model.Z, initialize=[1,2,3], dimen=1)
        self.instance = self.model.create_instance()
        try:
            self.model.A = Set(self.model.Z, initialize=[4,5,6], dimen=2)
            self.instance = self.model.create_instance()
        except ValueError:
            pass
        else:
            self.fail("test_dimen")
        self.model.A = Set(self.model.Z, initialize=[(1,2), (2,3), (3,4)], dimen=2)
        self.instance = self.model.create_instance()
        try:
            self.model.A = Set(self.model.Z, initialize=[(1,2), (2,3), (3,4)], dimen=1)
            self.instance = self.model.create_instance()
        except ValueError:
            pass
        else:
            self.fail("test_dimen")

    def test_rule(self):
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; param n := 5; set Z := A C; end;")
        OUTPUT.close()
        def tmp_init(model, i):
            return range(0,value(model.n))
        self.model.n = Param()
        self.model.Z = Set()
        self.model.A = Set(self.model.Z, initialize=tmp_init)
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual(len(self.instance.A['A']),5)

    def test_rule2(self):
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; param n := 5; set Z := A C; end;")
        OUTPUT.close()
        @simple_set_rule
        def tmp_rule2(model, z, i):
            if z>value(model.n):
                return None
            return z
        self.model.n = Param()
        self.model.Z = Set()
        self.model.A = Set(self.model.Z, initialize=tmp_rule2)
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual(len(self.instance.A['A']),5)

    def test_rule3(self):
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; param n := 5; set Z := A C; end;")
        OUTPUT.close()
        def tmp_rule2(model, z, i):
            if z>value(model.n):
                return Set.End
            return z
        self.model.n = Param()
        self.model.Z = Set()
        self.model.A = Set(self.model.Z, initialize=tmp_rule2)
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual(len(self.instance.A['A']),5)

    def test_within1(self):
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set Z := A C; set A[A] := 1 3 5 7.5; end;")
        OUTPUT.close()
        #
        # Create A with an error
        #
        self.model.Z = Set()
        self.model.A = Set(self.model.Z, within=Integers)
        try:
            self.instance = self.model.create_instance(currdir+"setA.dat")
        except ValueError:
            pass
        else:
            self.fail("fail test_within1")

    def test_within2(self):
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set Z := A C; set A[A] := 1 3 5 7.5; end;")
        OUTPUT.close()
        #
        # Create A with an error
        #
        self.model.Z = Set()
        self.model.A = Set(self.model.Z, within=Reals)
        try:
            self.instance = self.model.create_instance(currdir+"setA.dat")
        except ValueError:
            self.fail("fail test_within2")
        else:
            pass

    def test_validation1(self):
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set Z := A C; set A[A] := 1 3 5 7.5; end;")
        OUTPUT.close()
        #
        # Create A with an error
        #
        self.model.Z = Set()
        self.model.A = Set(self.model.Z, validate=lambda model, x:x<6)
        try:
            self.instance = self.model.create_instance(currdir+"setA.dat")
        except ValueError:
            pass
        else:
            self.fail("fail test_within1")

    def test_validation2(self):
        #
        # Create Set 'A' data file
        #
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set Z := A C; set A[A] := 1 3 5 5.5; end;")
        OUTPUT.close()
        #
        # Create A with an error
        #
        self.model.Z = Set()
        self.model.A = Set(self.model.Z, validate=lambda model, x:x<6)
        try:
            self.instance = self.model.create_instance(currdir+"setA.dat")
        except ValueError:
            self.fail("fail test_within2")
        else:
            pass

    def test_other1(self):
        self.model.Z = Set(initialize=['A'])
        self.model.A = Set(self.model.Z, initialize={'A':[1,2,3,'A']}, validate=lambda model, x:x in Integers)
        try:
            self.instance = self.model.create_instance()
        except ValueError:
            pass
        else:
            self.fail("fail test_other1")

    def test_other2(self):
        self.model.Z = Set(initialize=['A'])
        self.model.A = Set(self.model.Z, initialize={'A':[1,2,3,'A']}, within=Integers)
        try:
            self.instance = self.model.create_instance()
        except ValueError:
            pass
        else:
            self.fail("fail test_other1")

    def test_other3(self):
        def tmp_init(model, i):
            tmp=[]
            for i in range(0,value(model.n)):
                tmp.append(i/2.0)
            return tmp
        self.model.n = Param(initialize=5)
        self.model.Z = Set(initialize=['A'])
        self.model.A = Set(self.model.Z,initialize=tmp_init, validate=lambda model, x:x in Integers)
        try:
            self.instance = self.model.create_instance()
        except ValueError:
            pass
        else:
            self.fail("fail test_other1")

    def test_other4(self):
        def tmp_init(model, i):
            tmp=[]
            for i in range(0,value(model.n)):
                tmp.append(i/2.0)
            return tmp
        self.model.n = Param(initialize=5)
        self.model.Z = Set(initialize=['A'])
        self.model.A = Set(self.model.Z, initialize=tmp_init, within=Integers)
        self.model.B = Set(self.model.Z, initialize=tmp_init, within=Integers)
        try:
            self.instance = self.model.create_instance()
        except ValueError:
            pass
        else:
            self.fail("fail test_other1")

    def tearDown(self):
        #
        # Remove Set 'A' data file
        #
        if os.path.exists(currdir+"setA.dat"):
            os.remove(currdir+"setA.dat")


class Misc(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        #
        #
        self.model.A = Set(initialize=[1,2,3])
        self.model.B = Set(initialize=['a','b','c'])
        self.model.C = Set(initialize=[4,5,6])

    def tearDown(self):
        #
        # Remove Set 'A' data file
        #
        if os.path.exists(currdir+"setA.dat"):
            os.remove(currdir+"setA.dat")

    def test_cross_set(self):
        self.model.C = self.model.A * self.model.B
        self.instance = self.model.create_instance()
        self.assertEqual(len(self.instance.C),9)

    def test_tricross_set(self):
        self.model.D = self.model.A * self.model.B * self.model.C
        self.instance = self.model.create_instance()
        self.assertEqual(len(self.instance.D),27)

    def test_virtual_cross_set(self):
        self.model.C = self.model.A * self.model.B
        self.model.C.virtual = True
        self.instance = self.model.create_instance()
        self.assertEqual(len(self.instance.C),9)
        if not self.instance.C.value is None:
            self.assertEqual(len(self.instance.C.value),0)
        tmp=[]
        for item in self.instance.C:
            tmp.append(item)
        self.assertEqual(len(tmp),9)


class SetIO(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)

    def tearDown(self):
        #
        # Remove Set 'A' data file
        #
        if os.path.exists(currdir+"setA.dat"):
            os.remove(currdir+"setA.dat")

    def test_io1(self):
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set A := A1 A2 A3; end;")
        OUTPUT.close()
        self.model.A = Set()
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual( len(self.instance.A), 3)

    def test_io2(self):
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data; set B := 1 2 3 4; end;")
        OUTPUT.close()
        self.model.B = Set()
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual( len(self.instance.B), 4)

    def test_io3(self):
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data;\n")
        OUTPUT.write("set A := A1 A2 A3;\n")
        OUTPUT.write("set B := 1 2 3 4;\n")
        OUTPUT.write("set C := (A1,1) (A2,2) (A3,3);\n")
        OUTPUT.write("end;\n")
        OUTPUT.close()
        self.model.A = Set()
        self.model.B = Set()
        self.model.C = self.model.A * self.model.B
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual( len(self.instance.C), 12)

    def test_io4(self):
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data;\n")
        OUTPUT.write("set A := A1 A2 A3;\n")
        OUTPUT.write("set B := 1 2 3 4;\n")
        OUTPUT.write("set D := (A1,1) (A2,2) (A3,3);\n")
        OUTPUT.write("end;\n")
        OUTPUT.close()
        self.model.A = Set()
        self.model.B = Set()
        self.model.D = Set(within=self.model.A*self.model.B)
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual( len(self.instance.D), 3)

    def test_io5(self):
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write("data;\n")
        OUTPUT.write("set A := A1 A2 A3;\n")
        OUTPUT.write("set B := 1 2 3 4;\n")
        OUTPUT.write("set D : A1 A2 A3 :=\n")
        OUTPUT.write("    1   +  -  +\n")
        OUTPUT.write("    2   +  -  +\n")
        OUTPUT.write("    3   +  -  +\n")
        OUTPUT.write("    4   +  -  +;\n")
        OUTPUT.write("end;\n")
        OUTPUT.close()
        self.model.A = Set()
        self.model.B = Set()
        self.model.D = Set(within=self.model.A*self.model.B)
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual( len(self.instance.D), 8)

    def test_io6(self):
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write( "data;\n")
        OUTPUT.write( "set A := A1 A2 A3;\n")
        OUTPUT.write( "set B := 1 2 3 4;\n")
        OUTPUT.write( "set E :=\n")
        OUTPUT.write( "(A1,1,*) A1 A2\n")
        OUTPUT.write( "(A2,2,*) A2 A3\n")
        OUTPUT.write( "(A3,3,*) A1 A3 ;\n")
        OUTPUT.write( "end;\n")
        OUTPUT.close()
        self.model.A = Set()
        self.model.B = Set()
        self.model.E = Set(within=self.model.A*self.model.B*self.model.A)
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual( len(self.instance.E), 6)

    def test_io7(self):
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write( "data;\n")
        OUTPUT.write( "set A := A1 A2 A3;\n")
        OUTPUT.write( "set B := 1 2 3 4;\n")
        OUTPUT.write( "set F[A1] := 1 3 5;\n")
        OUTPUT.write( "set F[A2] := 2 4 6;\n")
        OUTPUT.write( "set F[A3] := 3 5 7;\n")
        OUTPUT.write( "end;\n")
        OUTPUT.close()
        self.model.A = Set()
        self.model.B = Set()
        self.model.F = Set(self.model.A)
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual( self.instance.F.dim(), 1)
        self.assertEqual( len(self.instance.F.keys()), 3)
        self.assertEqual( len(self.instance.F['A1']), 3)

    def test_io8(self):
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write( "data;\n" )
        OUTPUT.write( "set E :=\n" )
        OUTPUT.write( "(A1,1,*) A1 A2\n" )
        OUTPUT.write( "(*,2,*) A2 A3\n" )
        OUTPUT.write( "(A3,3,*) A1 A3 ;\n" )
        OUTPUT.write( "end;\n" )
        OUTPUT.close()
        self.model.E = Set(dimen=3)
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual( len(self.instance.E), 5)

    def test_io9(self):
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write( "data;\n" )
        OUTPUT.write( "set E :=\n" )
        OUTPUT.write( "(A1,1,A1) (A1,1,A2)\n" )
        OUTPUT.write( "(A2,2,A3)\n" )
        OUTPUT.write( "(A3,3,A1) (A3,3,A3) ;\n" )
        OUTPUT.write( "end;\n" )
        OUTPUT.close()
        self.model.E = Set(dimen=3)
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual( len(self.instance.E), 5)

    def test_io10(self):
        OUTPUT=open(currdir+"setA.dat","w")
        OUTPUT.write( "data;\n" )
        OUTPUT.write( "set A := 'A1 x' ' A2' \"A3\";\n" )
        OUTPUT.write( "set F['A1 x'] := 1 3 5;\n" )
        OUTPUT.write( "set F[\" A2\"] := 2 4 6;\n" )
        OUTPUT.write( "set F['A3'] := 3 5 7;\n" )
        OUTPUT.write( "end;\n" )
        OUTPUT.close()
        self.model.A = Set()
        self.model.F = Set(self.model.A)
        self.instance = self.model.create_instance(currdir+"setA.dat")
        self.assertEqual( self.instance.F.dim(), 1)
        self.assertEqual( len(self.instance.F.keys()), 3)
        self.assertEqual( len(self.instance.F['A1 x']), 3)


def init_fn(model):
    return []

def tmp_constructor(model, ctr, index):
    if ctr == 10:
        return None
    else:
        return ctr

class SetErrors(PyomoModel):

    def test_membership(self):
        self.assertEqual( 0 in Boolean, True)
        self.assertEqual( 1 in Boolean, True)
        self.assertEqual( True in Boolean, True)
        self.assertEqual( False in Boolean, True)
        self.assertEqual( 1.1 in Boolean, False)
        self.assertEqual( 2 in Boolean, False)

        self.assertEqual( 0 in Integers, True)
        self.assertEqual( 1 in Integers, True)
        self.assertEqual( True in Integers, True)
        self.assertEqual( False in Integers, True)
        self.assertEqual( 1.1 in Integers, False)
        self.assertEqual( 2 in Integers, True)

        self.assertEqual( 0 in Reals, True)
        self.assertEqual( 1 in Reals, True)
        self.assertEqual( True in Reals, True)
        self.assertEqual( False in Reals, True)
        self.assertEqual( 1.1 in Reals, True)
        self.assertEqual( 2 in Reals, True)

        self.assertEqual( 0 in Any, True)
        self.assertEqual( 1 in Any, True)
        self.assertEqual( True in Any, True)
        self.assertEqual( False in Any, True)
        self.assertEqual( 1.1 in Any, True)
        self.assertEqual( 2 in Any, True)

    @unittest.skipIf(not _has_numpy, "Numpy is not installed")
    def test_numpy_membership(self):

        self.assertEqual( numpy.int_(0) in Boolean, True)
        self.assertEqual( numpy.int_(1) in Boolean, True)
        self.assertEqual( numpy.bool_(True) in Boolean, True)
        self.assertEqual( numpy.bool_(False) in Boolean, True)
        self.assertEqual( numpy.float_(1.1) in Boolean, False)
        self.assertEqual( numpy.int_(2) in Boolean, False)

        self.assertEqual( numpy.int_(0) in Integers, True)
        self.assertEqual( numpy.int_(1) in Integers, True)
        # Numpy.bool_ is NOT a numeric type
        self.assertEqual( numpy.bool_(True) in Integers, False)
        self.assertEqual( numpy.bool_(False) in Integers, False)
        self.assertEqual( numpy.float_(1.1) in Integers, False)
        self.assertEqual( numpy.int_(2) in Integers, True)

        self.assertEqual( numpy.int_(0) in Reals, True)
        self.assertEqual( numpy.int_(1) in Reals, True)
        # Numpy.bool_ is NOT a numeric type
        self.assertEqual( numpy.bool_(True) in Reals, False)
        self.assertEqual( numpy.bool_(False) in Reals, False)
        self.assertEqual( numpy.float_(1.1) in Reals, True)
        self.assertEqual( numpy.int_(2) in Reals, True)

        self.assertEqual( numpy.int_(0) in Any, True)
        self.assertEqual( numpy.int_(1) in Any, True)
        self.assertEqual( numpy.bool_(True) in Any, True)
        self.assertEqual( numpy.bool_(False) in Any, True)
        self.assertEqual( numpy.float_(1.1) in Any, True)
        self.assertEqual( numpy.int_(2) in Any, True)

    def test_setargs1(self):
        try:
            a=Set()
            c=Set(a,foo=None)
            self.fail("test_setargs1 - expected error because of bad argument")
        except ValueError:
            pass

    def test_setargs2(self):
        try:
            a=Set()
            b=Set(a)
            c=Set(within=b, dimen=2)
            self.fail("test_setargs1 - expected error because of bad argument")
        except ValueError:
            pass
        a=Set()
        b=Set(a)
        c=Set(within=b, dimen=1)
        self.assertEqual(c.domain,b)
        c.domain = a
        self.assertEqual(c.domain,a)

    def test_setargs3(self):
        model = ConcreteModel()
        model.a=Set(dimen=1, initialize=(1,2))
        try:
            model.b=Set(dimen=2, initialize=(1,2))
            self.fail("test_setargs3 - expected error because dimen does not match set values")
        except ValueError:
            pass

    def test_setargs4(self):
        model = ConcreteModel()
        model.A = Set(initialize=[1])
        model.B = Set(model.A, initialize={1:[1]})
        try:
            model.C = Set(model.B)
            self.fail("test_setargs4 - expected error when passing in a set that is indexed")
        except TypeError:
            pass

    def test_verify(self):
        a=Set(initialize=[1,2,3])
        b=Set(within=a)
        try:
            b._verify(4)
            self.fail("test_verify - bad value was expected")
        except ValueError:
            pass
        #
        c=Set()
        try:
            c._verify( (1,2) )
            self.fail("test_verify - bad value was expected")
        except ValueError:
            pass
        #
        c=Set(dimen=2)
        try:
            c._verify( (1,2,3) )
            self.fail("test_verify - bad value was expected")
        except ValueError:
            pass

    def test_construct(self):
        a = Set(initialize={})
        try:
            a.construct()
            self.fail("test_construct - expected failure constructing with a dictionary")
        except ValueError:
            pass
        #
        a = Set(initialize=init_fn)
        try:
            a.construct()
            self.fail("test_construct - expected exception due to None model")
        except ValueError:
            pass

    def test_add(self):
        a=Set()
        a.add(1)
        a.add("a")
        try:
            a.add({})
            self.fail("test_add - expected type error because {} is unhashable")
        except:
            pass

    def test_getitem(self):
        a=Set(initialize=[1,2])
        try:
            a[0]
            self.fail("test_getitem - cannot index an unordered set")
        except ValueError:
            pass

    def test_eq(self):
        a=Set(dimen=1,name="a",initialize=[1,2])
        a.construct()
        b=Set(dimen=2)
        self.assertEqual(a==b,False)
        self.assertTrue(not a.__eq__(Boolean))
        self.assertTrue(not Boolean.__eq__(a))

    def test_neq(self):
        a=Set(dimen=1,initialize=[1,2])
        a.construct()
        b=Set(dimen=2)
        self.assertEqual(a!=b,True)
        self.assertTrue(a.__ne__(Boolean))
        self.assertTrue(Boolean.__ne__(a))

    def test_contains(self):
        a=Set(initialize=[1,3,5,7])
        a.construct()
        b=Set(initialize=[1,3])
        b.construct()
        self.assertEqual(b in a, True)
        self.assertEqual(a in b, False)
        self.assertEqual(1 in Integers, True)
        self.assertEqual(1 in NonNegativeIntegers, True)

    def test_subset(self):
        try:
            Integers in Reals
            self.fail("test_subset - expected TypeError")
        except TypeError:
            pass
        try:
            Integers.issubset(Reals)
            self.fail("test_subset - expected TypeError")
        except TypeError:
            pass
        try:
            a=Set(dimen=1)
            b=Set(dimen=2)
            a in b
            self.fail("test_subset - expected ValueError")
        except ValueError:
            pass

    def test_superset(self):
        try:
            Reals >= Integers
            self.fail("test_subset - expected TypeError")
        except TypeError:
            pass
        try:
            Integers.issubset(Reals)
            self.fail("test_subset - expected TypeError")
        except TypeError:
            pass
        a=Set(initialize=[1,3,5,7])
        a.construct()
        b=Set(initialize=[1,3])
        b.construct()
        self.assertEqual(Reals >= b, True)
        self.assertEqual(Reals >= [1,3,7], True)
        self.assertEqual(Reals >= [1,3,7,"a"], False)
        self.assertEqual(a >= b, True)

    def test_lt(self):
        try:
            Integers < Reals
            self.fail("test_subset - expected TypeError")
        except TypeError:
            pass
        a=Set(initialize=[1,3,5,7])
        a.construct()
        a < Reals
        b=Set(initialize=[1,3,5])
        b.construct()
        self.assertEqual(a<a,False)
        self.assertEqual(b<a,True)
        c=Set(initialize=[(1,2)])
        c.construct()
        try:
            a<c
            self.fail("test_subset - expected ValueError")
        except ValueError:
            pass

    def test_gt(self):
        a=Set(initialize=[1,3,5,7])
        a.construct()
        c=Set(initialize=[(1,2)])
        c.construct()
        try:
            a>c
            self.fail("test_subset - expected ValueError")
        except ValueError:
            pass

    def test_or(self):
        a=Set(initialize=[1,2,3])
        c=Set(initialize=[(1,2)])
        c.construct()
        try:
            Reals | Integers
            self.fail("test_or - expected TypeError")
        except TypeError:
            pass
        try:
            a | Integers
            self.fail("test_or - expected TypeError")
        except TypeError:
            pass
        try:
            a | c
            self.fail("test_or - expected ValueError")
        except ValueError:
            pass

    def test_and(self):
        a=Set(initialize=[1,2,3])
        c=Set(initialize=[(1,2)])
        c.construct()
        try:
            Reals & Integers
            self.fail("test_and - expected TypeError")
        except TypeError:
            pass
        try:
            a & Integers
            self.fail("test_and - expected TypeError")
        except TypeError:
            pass
        try:
            a & c
            self.fail("test_and - expected ValueError")
        except ValueError:
            pass

    def test_xor(self):
        a=Set(initialize=[1,2,3])
        c=Set(initialize=[(1,2)])
        c.construct()
        try:
            Reals ^ Integers
            self.fail("test_xor - expected TypeError")
        except TypeError:
            pass
        try:
            a ^ Integers
            self.fail("test_xor - expected TypeError")
        except TypeError:
            pass
        try:
            a ^ c
            self.fail("test_xor - expected ValueError")
        except ValueError:
            pass

    def test_sub(self):
        a=Set(initialize=[1,2,3])
        c=Set(initialize=[(1,2)])
        c.construct()
        try:
            Reals - Integers
            self.fail("test_sub - expected TypeError")
        except TypeError:
            pass
        try:
            a - Integers
            self.fail("test_sub - expected TypeError")
        except TypeError:
            pass
        try:
            a - c
            self.fail("test_sub - expected ValueError")
        except ValueError:
            pass

    def test_mul(self):
        a=Set(initialize=[1,2,3])
        c=Set(initialize=[(1,2)])
        c.construct()
        try:
            Reals * Integers
            self.fail("test_mul - expected TypeError")
        except TypeError:
            pass
        try:
            a * Integers
            self.fail("test_mul - expected TypeError")
        except TypeError:
            pass
        try:
            a * 1
            self.fail("test_mul - expected TypeError")
        except TypeError:
            pass
        b = a * c

    def test_arrayset_construct(self):
        a=Set(initialize=[1,2,3])
        a.construct()
        b=Set(a, initialize=tmp_constructor)
        try:
            b.construct({4:None})
            self.fail("test_arrayset_construct - expected KeyError")
        except KeyError:
            pass
        b._constructed=False
        try:
            b.construct()
            self.fail("test_arrayset_construct - expected ValueError")
        except ValueError:
            pass
        b=Set(a,a, initialize=tmp_constructor)
        for i in b:
            self.assertEqual(i in a, True)
        try:
            b.construct()
            self.fail("test_arrayset_construct - expected ValueError")
        except ValueError:
            pass

    def test_prodset(self):
        a=Set(initialize=[1,2])
        a.construct()
        b=Set(initialize=[6,7])
        b.construct()
        c=a*b
        c.construct()
        self.assertEqual((6,2) in c, False)
        c=pyomo.core.base.sets._SetProduct(a,b)
        c.virtual=True
        self.assertEqual((6,2) in c, False)
        self.assertEqual((1,7) in c, True)
        #c=pyomo.core.base.sets._SetProduct()
        #c.virtual=True
        #c.construct()
        c=pyomo.core.base.sets._SetProduct(a,b,initialize={(1,7):None,(2,6):None})
        c.construct()
        c=pyomo.core.base.sets._SetProduct(a,b,initialize=(1,7))
        c.construct()


def virt_constructor(model, y):
    return RealSet(validate=lambda model, x: x>y)


class ArraySetVirtual(unittest.TestCase):

    def test_construct(self):
        a=Set(initialize=[1,2,3])
        a.construct()
        b=Set(a, initialize=virt_constructor)
        #b.construct()

class NestedSetOperations(unittest.TestCase):

    def test_union(self):

        model = AbstractModel()
        s1 = set([1,2])
        model.s1 = Set(initialize=s1)
        s2 = set(['a','b'])
        model.s2 = Set(initialize=s2)
        s3 = set([None,True])
        model.s3 = Set(initialize=s3)

        model.union1 =    (model.s1 | (model.s2 | (model.s3 | (model.s3 | model.s2))))
        model.union2 =     model.s1 | (model.s2 | (model.s3 | (model.s3 | model.s2)))
        model.union3 = ((((model.s1 | model.s2) | model.s3) | model.s3) | model.s2)

        inst = model.create_instance()

        union = s1 | s2 | s3 | s3 | s2
        self.assertTrue(isinstance(inst.union1,
                                   pyomo.core.base.sets._SetUnion))
        self.assertEqual(inst.union1,
                         (s1 | (s2 | (s3 | (s3 | s2)))))
        self.assertTrue(isinstance(inst.union2,
                                   pyomo.core.base.sets._SetUnion))
        self.assertEqual(inst.union2,
                         s1 | (s2 | (s3 | (s3 | s2))))
        self.assertTrue(isinstance(inst.union3,
                                   pyomo.core.base.sets._SetUnion))
        self.assertEqual(inst.union3,
                         ((((s1 | s2) | s3) | s3) | s2))

    def test_intersection(self):

        model = AbstractModel()
        s1 = set([1,2])
        model.s1 = Set(initialize=s1)
        s2 = set(['a','b'])
        model.s2 = Set(initialize=s2)
        s3 = set([None,True])
        model.s3 = Set(initialize=s3)

        model.intersection1 = \
            (model.s1 & (model.s2 & (model.s3 & (model.s3 & model.s2))))
        model.intersection2 = \
            model.s1 & (model.s2 & (model.s3 & (model.s3 & model.s2)))
        model.intersection3 = \
            ((((model.s1 & model.s2) & model.s3) & model.s3) & model.s2)
        model.intersection4 = \
            model.s3 & model.s1 & model.s3

        inst = model.create_instance()

        self.assertTrue(isinstance(inst.intersection1,
                                   pyomo.core.base.sets._SetIntersection))
        self.assertEqual(sorted(inst.intersection1),
                         sorted((s1 & (s2 & (s3 & (s3 & s2))))))
        self.assertTrue(isinstance(inst.intersection2,
                                   pyomo.core.base.sets._SetIntersection))
        self.assertEqual(sorted(inst.intersection2),
                         sorted(s1 & (s2 & (s3 & (s3 & s2)))))
        self.assertTrue(isinstance(inst.intersection3,
                                   pyomo.core.base.sets._SetIntersection))
        self.assertEqual(sorted(inst.intersection3),
                         sorted(((((s1 & s2) & s3) & s3) & s2)))
        self.assertTrue(isinstance(inst.intersection4,
                                   pyomo.core.base.sets._SetIntersection))
        self.assertEqual(sorted(inst.intersection4),
                         sorted(s3 & s1 & s3))

    def test_difference(self):

        model = AbstractModel()
        s1 = set([1,2])
        model.s1 = Set(initialize=s1)
        s2 = set(['a','b'])
        model.s2 = Set(initialize=s2)
        s3 = set([None,True])
        model.s3 = Set(initialize=s3)

        model.difference1 = \
            (model.s1 - (model.s2 - (model.s3 - (model.s3 - model.s2))))
        model.difference2 = \
            model.s1 - (model.s2 - (model.s3 - (model.s3 - model.s2)))
        model.difference3 = \
            ((((model.s1 - model.s2) - model.s3) - model.s3) - model.s2)

        inst = model.create_instance()

        self.assertTrue(isinstance(inst.difference1,
                                   pyomo.core.base.sets._SetDifference))
        self.assertEqual(sorted(inst.difference1),
                         sorted((s1 - (s2 - (s3 - (s3 - s2))))))
        self.assertTrue(isinstance(inst.difference2,
                                   pyomo.core.base.sets._SetDifference))
        self.assertEqual(sorted(inst.difference2),
                         sorted(s1 - (s2 - (s3 - (s3 - s2)))))
        self.assertTrue(isinstance(inst.difference3,
                                   pyomo.core.base.sets._SetDifference))
        self.assertEqual(sorted(inst.difference3),
                         sorted(((((s1 - s2) - s3) - s3) - s2)))

    def test_symmetric_difference(self):

        model = AbstractModel()
        s1 = set([1,2])
        model.s1 = Set(initialize=s1)
        s2 = set([4,5])
        model.s2 = Set(initialize=s2)
        s3 = set([0,True])
        model.s3 = Set(initialize=s3)

        model.symdiff1 = \
            (model.s1 ^ (model.s2 ^ (model.s3 ^ (model.s3 ^ model.s2))))
        model.symdiff2 = \
            model.s1 ^ (model.s2 ^ (model.s3 ^ (model.s3 ^ model.s2)))
        model.symdiff3 = \
            ((((model.s1 ^ model.s2) ^ model.s3) ^ model.s3) ^ model.s2)
        model.symdiff4 = \
            model.s1 ^ model.s2 ^ model.s3

        inst = model.create_instance()

        self.assertTrue(isinstance(inst.symdiff1,
                                   pyomo.core.base.sets._SetSymmetricDifference))
        self.assertEqual(sorted(inst.symdiff1),
                         sorted((s1 ^ (s2 ^ (s3 ^ (s3 ^ s2))))))
        self.assertTrue(isinstance(inst.symdiff2,
                                   pyomo.core.base.sets._SetSymmetricDifference))
        self.assertEqual(sorted(inst.symdiff2),
                         sorted(s1 ^ (s2 ^ (s3 ^ (s3 ^ s2)))))
        self.assertTrue(isinstance(inst.symdiff3,
                                   pyomo.core.base.sets._SetSymmetricDifference))
        self.assertEqual(sorted(inst.symdiff3),
                         sorted(((((s1 ^ s2) ^ s3) ^ s3) ^ s2)))
        self.assertTrue(isinstance(inst.symdiff4,
                                   pyomo.core.base.sets._SetSymmetricDifference))
        self.assertEqual(sorted(inst.symdiff4),
                         sorted(s1 ^ s2 ^ s3))

    def test_product(self):

        model = AbstractModel()
        s1 = set([1,2])
        model.s1 = Set(initialize=s1)
        s2 = set([4,5])
        model.s2 = Set(initialize=s2)
        s3 = set([0,True])
        model.s3 = Set(initialize=s3)

        model.product1 = \
            (model.s1 * (model.s2 * (model.s3 * (model.s3 * model.s2))))
        model.product2 = \
            model.s1 * (model.s2 * (model.s3 * (model.s3 * model.s2)))
        model.product3 = \
            ((((model.s1 * model.s2) * model.s3) * model.s3) * model.s2)

        inst = model.create_instance()

        p = itertools.product

        self.assertTrue(isinstance(inst.product1,
                                   pyomo.core.base.sets._SetProduct))
        prod1 = set([pyutilib_misc_flatten_tuple(i) \
                     for i in set( p(s1,p(s2,p(s3,p(s3,s2)))) )])
        self.assertEqual(sorted(inst.product1),
                         sorted(prod1))
        self.assertTrue(isinstance(inst.product2,
                                   pyomo.core.base.sets._SetProduct))
        prod2 = set([pyutilib_misc_flatten_tuple(i) \
                     for i in  set( p(s1,p(s2,p(s3,p(s3,s2)))) )])
        self.assertEqual(sorted(inst.product2),
                         sorted(prod2))
        self.assertTrue(isinstance(inst.product3,
                                   pyomo.core.base.sets._SetProduct))
        prod3 = set([pyutilib_misc_flatten_tuple(i) \
                     for i in set( p(p(p(p(s1,s2),s3),s3),s2) )])
        self.assertEqual(sorted(inst.product3),
                         sorted(prod3))

if __name__ == "__main__":
    unittest.main()
