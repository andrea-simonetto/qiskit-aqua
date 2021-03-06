
# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""The CPLEX optimizer wrapped to be used within Qiskit Optimization.

Examples:
    >>> problem = OptimizationProblem()
    >>> # specify problem here
    >>> optimizer = CplexOptimizer()
    >>> result = optimizer.solve(problem)
"""

from typing import Optional
from cplex import ParameterSet
from cplex.exceptions import CplexSolverError

from .optimization_algorithm import OptimizationAlgorithm
from ..utils.qiskit_optimization_error import QiskitOptimizationError
from ..results.optimization_result import OptimizationResult
from ..problems.optimization_problem import OptimizationProblem


class CplexOptimizer(OptimizationAlgorithm):
    """The CPLEX optimizer wrapped to be used within the Qiskit Optimization.

    This class provides a wrapper for ``cplex.Cplex`` (https://pypi.org/project/cplex/)
    to be used within Qiskit Optimization.

    TODO: The arguments for ``Cplex`` are passed via the constructor.
    """

    def __init__(self, parameter_set: Optional[ParameterSet] = None) -> None:
        """Initializes the CplexOptimizer.

        TODO: This initializer takes the algorithmic parameters of CPLEX and stores them for later
            use when ``solve()`` is invoked.

        Args:
            parameter_set: The CPLEX parameter set
        """
        self._parameter_set = parameter_set

    @property
    def parameter_set(self) -> Optional[ParameterSet]:
        """Returns the parameter set.
        Returns the algorithmic parameters for CPLEX.
        Returns:
            The CPLEX parameter set.
        """
        return self._parameter_set

    @parameter_set.setter
    def parameter_set(self, parameter_set: Optional[ParameterSet]):
        """Set the parameter set.
        Args:
            parameter_set: The new parameter set.
        """
        self._parameter_set = parameter_set

    def is_compatible(self, problem: OptimizationProblem) -> Optional[str]:
        """Checks whether a given problem can be solved with this optimizer.

        Returns ``True`` since CPLEX accepts all problems that can be modeled using the
        ``OptimizationProblem``. CPLEX may throw an exception in case the problem is determined
        to be non-convex. This case could be addressed by setting CPLEX parameters accordingly.

        Args:
            problem: The optization problem to check compatibility.

        Returns:
            Returns ``None`` if the problem is compatible and else a string with the error message.
        """
        return None

    def solve(self, problem: OptimizationProblem) -> OptimizationResult:
        """Tries to solves the given problem using the optimizer.

        Runs the optimizer to try to solve the optimization problem. If problem is not convex,
        this optimizer may raise an exception due to incompatibility, depending on the settings.

        Args:
            problem: The problem to be solved.

        Returns:
            The result of the optimizer applied to the problem.

        Raises:
            QiskitOptimizationError: If the problem is incompatible with the optimizer.
        """

        # convert to CPLEX problem
        cplex = problem.to_cplex()

        # set parameters
        # TODO: need to find a good way to set the parameters

        # solve problem
        try:
            cplex.solve()
        except CplexSolverError:
            raise QiskitOptimizationError('Non convex/symmetric matrix.')

        # process results
        sol = cplex.solution

        # create results
        result = OptimizationResult(sol.get_values(), sol.get_objective_value(), sol)

        # return solution
        return result
