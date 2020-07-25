from frozendict import frozendict
import numpy as np
from sympy import (
    Symbol,
    # symbols,
    Function,
    prod,
    sin,
    cos,
    pi,
    lambdify,
    simplify,
    factor,
    ImmutableMatrix,
    Expr
)
from sympy.physics.units import Quantity
from sympy.physics.units.systems import SI
from sympy.physics.units import (
    day,
    year,
    kilogram,
    gram
)
from CompartmentalSystems.smooth_reservoir_model import SmoothReservoirModel
from CompartmentalSystems.smooth_model_run import SmoothModelRun


from bgc_md2.described_quantities import (
    to_number
)

class NumericStartValues(frozendict):
    pass


# extending ndarray is special
# https://numpy.org/doc/stable/user/basics.subclassing.html
class NumericSimulationTimes(np.ndarray):
    def __new__(cls, input_array, info=None):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        # obj.info = info
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return
        #self.info = getattr(obj, 'info', None)
    


class NumericParameterization():
    # Note:
    # A parameterization implicitly refers to a unique specific
    # symbolic model: 
    #
    # 1.)   Obviously the keys of the par_dict and func_dict can
    #       only be substituted in a model with these symbols present
    # 2.)   Even if a symbolic model had the same free symbols
    #       these symbols aquire meaning from their use in the symbolic
    #       expressions.
    #
    #
    # An instance would naturally contain a referece to the model (self.model=).
    # This reference is omitted on purpose since the model might be given
    # only implicitly by variables defined in a model describing source.py
    def __init__(
        self,
        par_dict,
        func_dict
    ):
        self.par_dict = par_dict
        self.func_dict = func_dict


class QuantityParameterization(NumericParameterization):
    # If a numeric parameterization has some physical meanimg.
    # the purely numerical parameter values have implicit units.
    # Also purely numerical functions have to be interpreted in the
    # context of the units of their arguments and return value.
    #
    # Instead of seperately attaching units to
    # ALL parameters, function arguments and  return values and expressions
    # and letting sympy take care of the conversions,
    # we require the user to choose the units of
    # - start values and
    # - times
    # in a simulation using the paramterization.
    # Thus the user has to provide a numerical parameterization for the
    # WHOLE compartmental model to be consistent with these units.
    # Possibly parameters have to be converted manually by the user to work
    # for the units specified.
    # This  keeps the numerical computations several orders of magnitude faster
    # than fully automatic unit derivation in sympy and can be seen as a kind
    # of cached unit computation.

    def __init__(
        self,
        par_dict,
        func_dict,
        state_var_unit,
        time_unit
    ):
        super().__init__(
            par_dict,
            func_dict
        )
        self.state_var_unit = state_var_unit
        self.time_unit = time_unit


class QuantityParameterizedModel():
    def __init__(
        self,
        srm,
        parameterization
    ):
        self.srm                = srm
        self.parameterization   = parameterization


class QuantityModelRun():
    def __init__(
        self,
        qpm,
        start_values_quant,
        times_quant,
    ):
        self.qpm = qpm
        p = qpm.parameterization
        times_num=np.array([to_number(tv,p.time_unit) for tv in times_quant])
        start_values_num=np.array([to_number(sv,p.state_var_unit) for sv in start_values_quant])
        self.smr=SmoothModelRun(
            qpm.srm,
            p.par_dict,
            start_values_num,
            times_num,
            p.func_dict
        )


    def solve(self):
        # compute the solution with respect to the state_var_units given in 
        # the model parameterization
        sol_num = self.smr.solve()
       
        # the result is correct since it comes with unit 
        # and can be converted in any other unit.
        sol_quant=sol_num*self.qpm.parameterization.state_var_unit

        return sol_quant
        

# fixme: mm 03-12-2020
# At the moment the classes are just defined to provide
# the vocabulary for the computer signatures and model 
# descriptions.
# Ultimately the classes should have sensible constructors
# that check their arguments thoroughly to expose
# inadequate imput early in the process 
# part of this should be a dimensional analysis
# which requires that the model authors provide dimensions
# for there variables

class InFluxesBySymbol(frozendict):
    pass

class OutFluxesBySymbol(frozendict):
    pass

class InternalFluxesBySymbol(frozendict):
    pass

class TimeSymbol(Symbol):
    # should become a quantity with dimension time
    pass

class StateVariableTuple(tuple):
    pass

class InputTuple(tuple):
    pass

class CompartmentalMatrix(ImmutableMatrix):
    pass

# vegetation specific variables
class VegetationCarbonInputTuple(tuple):
    pass

class VegetationCarbonInputScalar(Expr):
    pass

class VegetationCarbonInputPartitioningTuple(tuple):
    pass

class VegetationCarbonStateVariableTuple(tuple):
    pass

class VegetationCarbonCompartmentalMatrix(ImmutableMatrix): #cycling matrix
    pass
class ParameterDict(frozendict):
    pass

