# type: ignore

# flake8:noqa E501  Ignore long lines, some test cases are just inherently long

from typing import Iterable, Type
import io
from remerkleable.complex import Container, Vector, List
from remerkleable.basic import boolean, bit, byte, uint8, uint16, uint32, uint64, uint128, uint256
from remerkleable.bitfields import Bitvector, Bitlist
from remerkleable.byte_arrays import ByteVector, ByteList
from remerkleable.core import View, ObjType
from remerkleable.union import Union
from hashlib import sha256

import json

import pytest


def bytes_hash(data: bytes):
    return sha256(data).digest()


class SingleFieldTestStruct(Container):
    A: byte


class SmallTestStruct(Container):
    A: uint16
    B: uint16


class FixedTestStruct(Container):
    A: uint8
    B: uint64
    C: uint32


class VarTestStruct(Container):
    A: uint16
    B: List[uint16, 1024]
    C: uint8


class ComplexTestStruct(Container):
    A: uint16
    B: List[uint16, 128]
    C: uint8
    D: List[byte, 256]
    E: VarTestStruct
    F: Vector[FixedTestStruct, 4]
    G: Vector[VarTestStruct, 2]


sig_test_data = [0 for i in range(96)]
for k, v in {0: 1, 32: 2, 64: 3, 95: 0xff}.items():
    sig_test_data[k] = v


def chunk(hex: str) -> str:
    return (hex + ("00" * 32))[:64]  # just pad on the right, to 32 bytes (64 hex chars)


def h(a: str, b: str) -> str:
    return bytes_hash(bytes.fromhex(a) + bytes.fromhex(b)).hex()


# zero hashes, as strings, for
zero_hashes = [chunk("")]
for layer in range(1, 32):
    zero_hashes.append(h(zero_hashes[layer - 1], zero_hashes[layer - 1]))


def merge(a: str, branch: Iterable[str]) -> str:
    """
    Merge (out on left, branch on right) leaf a with branch items, branch is from bottom to top.
    """
    out = a
    for b in branch:
        out = h(out, b)
    return out


test_data = [
   
    ("complexTestStruct", ComplexTestStruct,
     ComplexTestStruct(
         A=0xaabb,
         B=List[uint16, 128](0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112,
0x112),
         C=10,
         D=List[byte, 256](1, 2),
         E=VarTestStruct(A=0xabcd, B=List[uint16, 1024](1, 2, 3), C=0xff),
         F=Vector[FixedTestStruct, 4](
             FixedTestStruct(A=0xcc, B=0x4242424242424242, C=0x13371337),
             FixedTestStruct(A=0xdd, B=0x3333333333333333, C=0xabcdabcd),
             FixedTestStruct(A=0xee, B=0x4444444444444444, C=0x00112233),
             FixedTestStruct(A=0xff, B=0x5555555555555555, C=0x44556677)),
         G=Vector[VarTestStruct, 2](
             VarTestStruct(A=0xdead, B=List[uint16, 1024](1, 2, 3), C=0x11),
             VarTestStruct(A=0xbeef, B=List[uint16, 1024](4, 5, 6), C=0x22)),
     ),
     "bbaa"
     "47000000"  # offset of B, []uint16
     "ff"
     "4b000000"  # offset of foobar
     "51000000"  # offset of E
     "cc424242424242424237133713"
     "dd3333333333333333cdabcdab"
     "ee444444444444444433221100"
     "ff555555555555555577665544"
     "5e000000"  # pointer to G
     "22114433"  # contents of B
     "666f6f626172"  # foobar
     "cdab07000000ff010002000300"  # contents of E
     "08000000" "15000000"  # [start G]: local offsets of [2]varTestStruct
     "adde0700000011010002000300"
     "efbe0700000022040005000600",
     h(
         h(
             h(  # A and B
                 chunk("bbaa"),
                 h(merge(chunk("22114433"), zero_hashes[0:3]), chunk("02000000"))  # 2*128/32 = 8 chunks
             ),
             h(  # C and D
                 chunk("ff"),
                 h(merge(chunk("666f6f626172"), zero_hashes[0:3]), chunk("06000000"))  # 256/32 = 8 chunks
             )
         ),
         h(
             h(  # E and F
                 h(h(chunk("cdab"), h(merge(chunk("010002000300"), zero_hashes[0:6]), chunk("03000000"))),
                   h(chunk("ff"), chunk(""))),
                 h(
                     h(
                         h(h(chunk("cc"), chunk("4242424242424242")), h(chunk("37133713"), chunk(""))),
                         h(h(chunk("dd"), chunk("3333333333333333")), h(chunk("cdabcdab"), chunk(""))),
                     ),
                     h(
                         h(h(chunk("ee"), chunk("4444444444444444")), h(chunk("33221100"), chunk(""))),
                         h(h(chunk("ff"), chunk("5555555555555555")), h(chunk("77665544"), chunk(""))),
                     ),
                 )
             ),
             h(  # G and padding
                 h(
                     h(h(chunk("adde"), h(merge(chunk("010002000300"), zero_hashes[0:6]), chunk("03000000"))),
                       h(chunk("11"), chunk(""))),
                     h(h(chunk("efbe"), h(merge(chunk("040005000600"), zero_hashes[0:6]), chunk("03000000"))),
                       h(chunk("22"), chunk(""))),
                 ),
                 chunk("")
             )
         )
     ), {
        'A': 0xaabb,
        'B': [0x1122, 0x3344],
        'C': 0xff,
        'D': list(b"foobar"),
        'E': {'A': 0xabcd, 'B': [1, 2, 3], 'C': 0xff},
        'F': (
            {'A': 0xcc, 'B': 0x4242424242424242, 'C': 0x13371337},
            {'A': 0xdd, 'B': 0x3333333333333333, 'C': 0xabcdabcd},
            {'A': 0xee, 'B': 0x4444444444444444, 'C': 0x00112233},
            {'A': 0xff, 'B': 0x5555555555555555, 'C': 0x44556677},
        ),
        'G': (
            {'A': 0xdead, 'B': [1, 2, 3], 'C': 0x11},
            {'A': 0xbeef, 'B': [4, 5, 6], 'C': 0x22},
        ),
     })
]




@pytest.mark.parametrize("name, typ, value, serialized, root, obj", test_data)
def test_encode_bytes(name: str, typ: Type[View], value: View, serialized: str, root: str, obj: ObjType):
    print(value)
    encoded = value.encode_bytes()
    int_values = [x for x in encoded]
            
    print(int_values)
     
    #assert encoded.hex() == serialized

