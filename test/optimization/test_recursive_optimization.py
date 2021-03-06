# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2018, 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

""" Test Recursive Min Eigen Optimizer """

from test.optimization.common import QiskitOptimizationTestCase
from ddt import ddt, data

from qiskit import BasicAer
from qiskit.aqua.algorithms import NumPyMinimumEigensolver
from qiskit.aqua.algorithms import QAOA
from qiskit.aqua.components.optimizers import COBYLA

from qiskit.optimization.algorithms import (MinimumEigenOptimizer, CplexOptimizer,
                                            RecursiveMinimumEigenOptimizer)
from qiskit.optimization.problems import OptimizationProblem


@ddt
class TestRecursiveMinEigenOptimizer(QiskitOptimizationTestCase):
    """Recursive Min Eigen Optimizer Tests."""

    def setUp(self):
        super().setUp()

        self.resource_path = './test/optimization/resources/'

        # setup minimum eigen solvers
        self.min_eigen_solvers = {}

        # exact eigen solver
        self.min_eigen_solvers['exact'] = NumPyMinimumEigensolver()

        # QAOA
        optimizer = COBYLA()
        self.min_eigen_solvers['qaoa'] = QAOA(optimizer=optimizer)

    @data(
        ('exact', None, 'op_ip1.lp'),
        ('qaoa', 'statevector_simulator', 'op_ip1.lp'),
        ('qaoa', 'qasm_simulator', 'op_ip1.lp')
    )
    def test_recursive_min_eigen_optimizer(self, config):
        """ Min Eigen Optimizer Test """

        # unpack configuration
        min_eigen_solver_name, backend, filename = config

        # get minimum eigen solver
        min_eigen_solver = self.min_eigen_solvers[min_eigen_solver_name]
        if backend:
            min_eigen_solver.quantum_instance = BasicAer.get_backend(backend)
            if backend == 'qasm_simulator':
                min_eigen_solver.quantum_instance.run_config.shots = 10000

        min_eigen_optimizer = MinimumEigenOptimizer(min_eigen_solver)
        # construct minimum eigen optimizer
        recursive_min_eigen_optimizer = RecursiveMinimumEigenOptimizer(min_eigen_optimizer,
                                                                       min_num_vars=4)

        # load optimization problem
        problem = OptimizationProblem()
        problem.read(self.resource_path + filename)

        # solve problem with cplex
        cplex = CplexOptimizer()
        cplex_result = cplex.solve(problem)

        # solve problem
        result = recursive_min_eigen_optimizer.solve(problem)

        # analyze results
        self.assertAlmostEqual(cplex_result.fval, result.fval)
