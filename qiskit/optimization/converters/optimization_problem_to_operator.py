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


from typing import Dict, Tuple

import numpy as np
from qiskit.quantum_info import Pauli

from qiskit.aqua.operators import WeightedPauliOperator
from qiskit.optimization import OptimizationProblem
from qiskit.optimization.utils import QiskitOptimizationError


class OptimizationProblemToOperator:
    """ Convert an optimization problem into a qubit operator.
    """

    def __init__(self):
        """ Constructor. Initialize the internal data structure. No args.
        """
        self._src = None
        self._q_d: Dict[int, int] = {}
        # e.g., self._q_d = {0: 0}

    def encode(self, op: OptimizationProblem) -> Tuple[WeightedPauliOperator, float]:
        """ Convert a problem into a qubit operator

        Args:
            op: The problem to be solved, that is an unconstrained problem with only binary variables.

        Returns:
            The qubit operator of the problem and the shift value.

        """

        self._src = op
        # if op has variables that are not binary, raise an error
        var_list = self._src.variables.get_types()
        if not all(var == 'B' for var in var_list):
            raise QiskitOptimizationError('The type of variable must be a binary variable.')

        # if constraints exist, raise an error
        linear_names = self._src.linear_constraints.get_names()
        if len(linear_names) > 0:
            raise QiskitOptimizationError('An constraint exists. '
                                          'The method supports only model with no constraints.')

        # TODO: check for quadratic constraints as well

        # assign variables of the model to qubits.
        _q_d = {}
        qubit_index = 0
        for name in self._src.variables.get_names():
            var_index = self._src.variables._varsgetindex[name]
            _q_d[var_index] = qubit_index
            qubit_index += 1

        # initialize Hamiltonian.
        num_nodes = len(_q_d)
        pauli_list = []
        shift = 0
        zero = np.zeros(num_nodes, dtype=np.bool)

        # set a sign corresponding to a maximized or minimized problem.
        # sign == 1 is for minimized problem. sign == -1 is for maximized problem.
        sense = self._src.objective.get_sense()

        # convert a constant part of the object function into Hamiltonian.
        shift += self._src.objective.get_offset() * sense

        # convert linear parts of the object function into Hamiltonian.
        for i, coef in self._src.objective.get_linear().items():
            z_p = np.zeros(num_nodes, dtype=np.bool)
            qubit_index = _q_d[i]
            weight = coef * sense / 2
            z_p[qubit_index] = True

            pauli_list.append([-weight, Pauli(z_p, zero)])
            shift += weight

        # convert quadratic parts of the object function into Hamiltonian.
        for i, vi in self._src.objective.get_quadratic().items():
            for j, coef in vi.items():
                if j < i:
                    continue
                qubit_index_1 = _q_d[i]
                qubit_index_2 = _q_d[j]
                if i == j:
                    coef = coef / 2
                weight = coef * sense / 4

                if qubit_index_1 == qubit_index_2:
                    shift += weight
                else:
                    z_p = np.zeros(num_nodes, dtype=np.bool)
                    z_p[qubit_index_1] = True
                    z_p[qubit_index_2] = True
                    pauli_list.append([weight, Pauli(z_p, zero)])

                z_p = np.zeros(num_nodes, dtype=np.bool)
                z_p[qubit_index_1] = True
                pauli_list.append([-weight, Pauli(z_p, zero)])

                z_p = np.zeros(num_nodes, dtype=np.bool)
                z_p[qubit_index_2] = True
                pauli_list.append([-weight, Pauli(z_p, zero)])

                shift += weight

        # Remove paulis whose coefficients are zeros.
        qubit_op = WeightedPauliOperator(paulis=pauli_list)

        return qubit_op, shift
