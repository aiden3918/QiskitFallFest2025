'''
Random Number Generator using locally-simulated quantum computing with Qiskit.
Python 3.x, probably best to run in a virtual environment

Required packages:
qiskit
qiskit_ibm_runtime
'''

from qiskit_ibm_runtime import QiskitRuntimeService

from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2 as Estimator
from qiskit.visualization import plot_histogram

import qiskit.quantum_info as qi
import math

# first-time initializations, if needed
'''
QiskitRuntimeService.save_account(
    token="<token here>",
    instance="<instance here>"
)
'''

service = QiskitRuntimeService()

# run single-qubit quantum circuit in succession and add up results
# returns -1 if something went wrong
def rng(start_inclusive = int, end_exclusive = int, max_attempts = int):
    # start check conditions
    if (start_inclusive >= end_exclusive):
        return -1
    if (start_inclusive < 0):
        return -1

    # calculate range and number of iterations/try needed
    num_range = end_exclusive - start_inclusive
    range_rng = 0
    n_iterations = int(math.ceil(math.log2(num_range)))

    # try to generate number for a maximum of max_attempts tries
    for j in range(0, int(max_attempts)):
        range_rng = 0
        # try to generate random number
        for i in range(0, int(n_iterations)):
            # quantum bits here
            # create a 1-qubit quantum circuit that represents a random digit (in binary) of the RNG
            qc = QuantumCircuit(1, 1)
            qc.h(0)
            psi = qi.Statevector(qc)
            counts = psi.sample_counts(shots = 1)
            # quantum ends here (4 lines bruh)
            # add measured state to nth digit if is 1 
            if '1' in counts:
                range_rng += math.pow(2, i)
            
        # if number generated is within the range, return
        if (range_rng < num_range):
            return int(start_inclusive + range_rng)
        # tries again if range computed > num_range given (due to math stuff)

    return -1

# test values
result = rng(0, 8, 64)
print(f'rng result: {result}')
result = rng(5, 20, 64)
print(f'rng result: {result}')
result = rng(500, 1000, 64)
print(f'rng result: {result}')
result = rng(0, 32, 64)
print(f'rng result: {result}')