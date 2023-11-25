'''
### Prover step (Python)
1. Use an example equation such as `out = 3x^2y + 5xy - x - 2y + 3` from Q3
2. Compute the `L`, `R`, `O`, and `w` as per last homework.
3. Encrypt `w` as `s1` and `s2` by multiplying `w` with `G1` and `G2` respectively.
4. Compute `Ls1`, `Rs2` and `Os1`.
5. Send `Ls1`, `Rs2`, `Os1` to the verifier contract.
'''

import numpy as np
from py_ecc.bn128 import G1, G2, multiply, curve_order, pairing, eq
from py_ecc.fields import (
    bn128_FQ as FQ,
    bn128_FQ2 as FQ2
)
from ape import accounts, project

p = curve_order

# We steal the L, R, O and w from Q3
L = np.array([[0,0,3,0,0,0],
               [0,0,0,0,1,0],
               [0,0,1,0,0,0]]) % p

R = np.array([[0,0,1,0,0,0],
               [0,0,0,1,0,0],
               [0,0,0,5,0,0]]) % p

O = np.array([[0,0,0,0,1,0],
               [0,0,0,0,0,1],
               [-3,1,1,2,0,-1]]) % p

x = 2  #TODO: Make this random later
y = 3 
out = 3 * x * x * y + 5 * x * y - x- 2*y + 3  # out = 3x^2y + 5xy - x - 2y + 3
v1 = 3*x*x 
v2 = v1 * y 
w = np.array([1, out, x, y, v1, v2]) % p

# -- Method 1 -- 
# We probably need to multiply L to s1 in mod p because s1 is done using a library, but we're manually doing this. 
# Alternatively we should be able to do Lw and then multiply them to G1, G2 accordingly
# s1 = np.array([multiply(G1, el) for el in w])
# s2 = np.array([multiply(G2, el) for el in w])

# Ls1 = L.dot(s1) 
# Rs2 = R.dot(s2)
# Os1 = O.dot(s1)

# -- Method 2 -- 
Lw = L.dot(w) % p 
Rw = R.dot(w) % p
Ow = O.dot(w) % p 

# Check if the equation adds up
assert np.all(np.equal((Lw * Rw) % p, Ow)), "Lw * Rw != Ow"

Ls1 = [multiply(G1, el) for el in Lw]
Rs2 = [multiply(G2, el) for el in Rw]
Os1 = [multiply(G1, el) for el in Ow]

''' 
Ls1 = [
    [4104045538469864104171201077235739079130558341993341936754194605245979914105 7866087282067239532994802064701833235000236822153905378778872993388128168709]
    [17108685722251241369314020928988529881027530433467445791267465866135602972753 20666112440056908034039013737427066139426903072479162670940363761207457724060]
    [1368015179489954701390400359078579693043519447331113978918064868415326638035 9918110051302171585080402603319702774565515993150576347155970296011118125764]
    ]

New:
Ls1 = [
    (4503322228978077916651710446042370109107355802721800704639343137502100212473, 6132642251294427119375180147349983541569387941788025780665104001559216576968), 
    (17108685722251241369314020928988529881027530433467445791267465866135602972753, 20666112440056908034039013737427066139426903072479162670940363761207457724060), 
    (1368015179489954701390400359078579693043519447331113978918064868415326638035, 9918110051302171585080402603319702774565515993150576347155970296011118125764)
    ]
'''

# Check if all points are on curve
def is_on_curve_G1(pt):
    if pt == None:
        return True
    x, y = pt
    return y**2 - x**3 == 3
assert np.all([is_on_curve_G1(pt) for pt in Ls1]), "Not all Ls1 is on curve"
assert np.all([is_on_curve_G1(pt) for pt in Os1]), "Not all Os1 is on curve"
# assert (np.all([is_on_curve_G2(pt) for pt in Rs2])) 
# TODO: no idea how to do this yet, but it's not critical right now

# # Comment out as pairing takes a while to run
# # Check the pairing first
# for i in range(len(Ls1)):
#     a = pairing(Rs2[i], Ls1[i]) 
#     b = pairing(G2, Os1[i])
#     assert eq(a, b), "Some pairing failed"

# Convert the big numbers into strings so that they can be passed to Solidity
Ls1_str = [[repr(el) for el in pair] for pair in Ls1]
Os1_str = [[repr(el) for el in pair] for pair in Os1]
Rs2_str = [[[repr(el.coeffs[0]), repr(el.coeffs[1])] for el in pair] for pair in Rs2]

# Call verifier with Ls1, Rs2, Os1 as inputs
def test_verifier(accounts):
    account = accounts[0]
    contract = account.deploy(project.R1CSVerifier)
    result = contract._verify_row(Ls1_str[0], Rs2_str[0], Os1_str[0])
    # result = contract.verify(Ls1_str, Rs2_str, Os1_str)
    print('result if error', result)
    print("Ls1: ", Ls1_str[0])
    print("Rs2: ", Rs2_str[0])
    print("Os1: ", Os1_str[0])
    assert result


# # WIP
# # result = contract.verifyOne(Ls1_str[0])
# # result = contract.verifyOneList(Ls1_str)


# def test_verifier(accounts):
#     account = accounts[0]
#     contract = account.deploy(project.R1CSVerifier)
#     tx = contract._verify_row(Ls1_str[0], Rs2_str[0], Os1_str[0])
#     print(tx)
#     # tx = contract.verify(Ls1_str, Rs2_str, Os1_str, sender=account)
#     # logs = tx.decode_logs()
#     # for log in logs:
#         # print(log.value)  # This will print the value logged in the event
#     assert False