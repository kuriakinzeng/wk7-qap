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
from ape import accounts, project
import random


# Check if all points are on curve
def is_on_curve_G1(pt):
    if pt == None:
        return True
    x, y = pt
    return y**2 - x**3 == 3

def generate_proof(x, y):

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

    out = 3 * x * x * y + 5 * x * y - x- 2*y + 3  # out = 3x^2y + 5xy - x - 2y + 3
    v1 = 3*x*x 
    v2 = v1 * y 
    w = np.array([1, out, x, y, v1, v2]) % p

    # -- Method 1 -- 
    # We probably need to multiply L to s1 in mod p because s1 is done using a library, but we're manually doing this. 
    # Alternatively we should be able to do Lw and then multiply them to G1, G2 accordingly, which is Method 2
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
    For reference this is how Ls1 looks like 
    Ls1 = [
        (4503322228978077916651710446042370109107355802721800704639343137502100212473, 6132642251294427119375180147349983541569387941788025780665104001559216576968), 
        (17108685722251241369314020928988529881027530433467445791267465866135602972753, 20666112440056908034039013737427066139426903072479162670940363761207457724060), 
        (1368015179489954701390400359078579693043519447331113978918064868415326638035, 9918110051302171585080402603319702774565515993150576347155970296011118125764)
        ]
    '''

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
    Rs2_str = [[[repr(el.coeffs[0]), repr(el.coeffs[1])] for el in pair] for pair in Rs2]
    Os1_str = [[repr(el) for el in pair] for pair in Os1]

    return (Ls1_str, Rs2_str, Os1_str)

# Call verifier with Ls1, Rs2, Os1 as inputs
def test_verifier(accounts):
    x = random.randint(1,1000)
    y = random.randint(1,1000)
    L, R, O = generate_proof(x, y)

    account = accounts[0]
    contract = account.deploy(project.R1CSVerifier)
    result = contract.verify(L, R, O, sender=account)
    print('result if error', result.decode_logs())
    assert result

# WIP
# result = contract.verifyOne(Ls1_str[0])
# result = contract.verifyOneList(Ls1_str)
# result = contract._verify_row(Ls1_str[0], Rs2_str[0], Os1_str[0], sender=account)
