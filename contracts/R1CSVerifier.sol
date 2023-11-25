// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity ^0.8.10;

contract R1CSVerifier {

    event Log1(ECPoint pt);
    event Log2(ECPoint2 pt2);
    event LogInt(uint256 num);
    event LogStr(string msg);

    struct ECPoint {
        uint256 x;
        uint256 y;
    }

    struct ECPoint2 {
        uint256[2] x;
        uint256[2] y;
    }

    uint256 constant FIELD_MOD = 21888242871839275222246405745257275088696311157297823662689037894645226208583;

    function neg(ECPoint memory pt) internal pure returns (ECPoint memory) {
        if (pt.x == 0 && pt.y == 0)
            return pt;
        else
            return ECPoint(pt.x, (FIELD_MOD - pt.y) % FIELD_MOD);
    }

    // This function should verify 0 = -ls1 * rs2 + os1 * G2 where ls1, rs2, os1 are the elements of the respective matrices
    // TODO: Convert this to private later
    function _verify_row(ECPoint memory ls1, ECPoint2 memory rs2, ECPoint memory os1) public returns (bool) {
        ECPoint2 memory G2 = ECPoint2(
            [   
                10857046999023057135944570762232829481370756359578518086990519993285655852781, 
                11559732032986387107991004021392285783925812861821192530917403151452391805634
            ],
            [
                8495653923123431417604973247489272438418190587263600148770280649306958101930, 
                4082367875863433681332203403145435568316851327593401208105741076214120093531
            ]
        );

        ECPoint memory Negls1 = neg(ls1);

        uint256[12] memory points = [
            Negls1.x,
            Negls1.y,
            rs2.x[1],
            rs2.x[0],
            rs2.y[1],
            rs2.y[0],
            os1.x,
            os1.y,
            G2.x[1],
            G2.x[0],
            G2.y[1],
            G2.y[0]
        ];

        bool success;

        assembly {
            success := staticcall(gas(), 0x08, points, mul(12, 0x20), points, 0x20)
        }

        if (success) {
            return true;
        }

        return false;
    }
    
    function verify(ECPoint[] memory Ls1, ECPoint2[] memory Rs2, ECPoint[] memory Os1) public returns (bool) {
        // TODO: Check the if the inputs are valid before proceeding
        bool success;
        for (uint256 i = 0; i < Ls1.length; i++) {
            success = _verify_row(Ls1[i], Rs2[i], Os1[i]);
            if (!success) {
                emit LogStr("failed!!");
                return false;
            }
        }
        emit LogStr("success!!");
        return true;
    }
}

// --- WIP ---
// These work
// function verifyOnePair(ECPoint memory Ls1) public view returns (bool) {
//     return true;
// }

// function verifyOneList(ECPoint[] memory Ls1) public view returns (ECPoint memory) {
//     return Ls1[0];
// }