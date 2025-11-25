'''
A demonstration of the BB84 quantum encryption done locally through Alice, Bob, and Eve

Required packages:
qiskit
qiskit_ibm_runtime
qiskit_aer
'''

from qiskit_ibm_runtime import QiskitRuntimeService

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2 as Estimator
from qiskit.visualization import plot_histogram
from qiskit_aer import Aer
from qiskit_aer import AerSimulator

import qiskit.quantum_info as qi
import math
import random
import matplotlib

# first-time initializations, if needed
'''
QiskitRuntimeService.save_account(
    token="<token here>",
    instance="<instance here>"
)
'''

service = QiskitRuntimeService()

# simulation for generating a pad in which
# pad can only be on zeroes or ones
def check_connection_bb84(pad_length = int, is_eve_eavesdropping = bool, error_threshold = float):

    alice_bases = list()
    bob_bases = list()

    # generate random message from alice and alice and bob's respective bases
    alice_message = list()
    bob_message = list()

    qc = QuantumCircuit(pad_length, pad_length)

    # create random message from alice and decide on random bases for both
    for i in range(0, pad_length):
        alice_message.append(random.randint(0, 1)) 

        alice_bases.append("X" if random.randint(0, 1) == 0 else "H")
        bob_bases.append("X" if random.randint(0, 1) == 0 else "H") 

    print("Alice's message")
    print(alice_message)

    # encrypt message
    for n in range(pad_length):
        if alice_message[n] == 0:
            if alice_bases[n] == "H":
                qc.h(n)
        if alice_message[n] == 1:
            qc.x(n)
            if alice_bases[n] == "H":
                qc.h(n)

    # if eve is eavesdropping, it will be between when alice and bob apply their bases (chronological order)
    if (is_eve_eavesdropping):
        eve_bases = list()

        for n in range(pad_length):
            # eve guesses a base and measures
            eve_bases.append("X" if random.randint(0, 1) == 0 else "H")
            
            if (eve_bases[n] == "H"):
                qc.h(n)
            qc.measure(n, n)
        qc.measure_all()

        # transpile with AerSimulator (copy bob)
        simulator = AerSimulator()
        qc = transpile(qc, simulator)

        # run
        result = simulator.run(qc).result()
        counts = result.get_counts(qc)
        # print("counts")
        # print(counts)

        # get information
        keys = counts.keys()
        key = list(keys)[0]
        eve_measurements = list(key)
        eve_message = list()
        for n in range(pad_length):
            eve_message.append(int(eve_measurements[n]))

        # reverse order because bob's message is measured in reverse for some reason?
        eve_message_reversed = eve_message[::-1]

        # eve prepares new quantum circuit and state, mimicking alice with guessed values
        qc = QuantumCircuit(pad_length, pad_length)

        for n in range(pad_length):
            if eve_message_reversed[n] == 0:
                if eve_bases[n] == "H":
                    qc.h(n)
            if eve_message_reversed[n] == 1:
                qc.x(n)
                if eve_bases[n] == "H":
                    qc.h(n)

    # add bob's bases
    for l in range(pad_length):
        if bob_bases[l] == "H":
            qc.h(l)
        # else:
        #     qc.x(l)
        qc.measure(l, l)

    print("Alice and bob's bases, respectively")
    print(alice_bases)
    print(bob_bases)

    meas_qc = qc.copy()
    meas_qc.measure_all()

    # transpile with AerSimulator
    simulator = AerSimulator()
    qc = transpile(qc, simulator)

    # run
    result = simulator.run(qc).result()
    counts = result.get_counts(qc)
    # print("counts")
    # print(counts)

    # get information
    keys = counts.keys()
    key = list(keys)[0]
    bob_measurements = list(key)
    for n in range(pad_length):
        bob_message.append(int(bob_measurements[n]))
 
    # reverse order because bob's message is measured in reverse for some reason?
    bob_message_reversed = bob_message[::-1]
 
    print("Bob's message")
    print(bob_message)

    # get matching bases (not relevant to algorithm, good for visualization purposes)
    matching_bases = list()
    new_pad = list()
    for l in range(0, pad_length):
        if alice_bases[l] == bob_bases[l]:
            matching_bases.append(alice_bases[l])
            new_pad.append(alice_bases[l])
        else:
            matching_bases.append("0")

    print("Matching bases")
    print(matching_bases)

    # bob shares his bases and bits with alice to check whether or not there is an eavesdropper
    # if no eavesdropper, no problem
    # if there is, bob is sharing a "corrupted" string that is of no use publicly
    alice_good_bits = list()
    bob_good_bits = list()
    num_good_bits = 0
    for m in range(pad_length):
        # Check whether bases matched.
        if alice_bases[m] == bob_bases[m]:
            alice_good_bits.append(int(alice_message[m]))
            bob_good_bits.append(bob_message_reversed[m])
            # If bits match when bases matched, increase count of matching bits
            if int(alice_message[m]) == int(bob_message_reversed[m]):
                num_good_bits += 1
    
    print("Alice and bob's good base bits, respectively")
    print(alice_good_bits)
    print(bob_good_bits)
    accuracy = float(num_good_bits) / (float)(len(alice_good_bits))
    print("accuracy = ", accuracy)
    print("error = ", 1.0 - accuracy)
    
    if (accuracy < error_threshold):
        print("Accuracy is below error threshold. Check that connection is secure or try again.")
    else:
        print("Accuracy is at or below threshold. Connection is valid.")

    return None

check_connection_bb84(20, False, 0.9)
check_connection_bb84(20, True, 0.9)