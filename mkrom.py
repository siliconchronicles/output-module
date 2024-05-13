from enum import Enum
from pathlib import Path


class Config:
    # bits follow sequence dp-a-b-c-d-e-f-g (g is the least-significant)
    FONT = {
        "0": 0b1111110,
        "1": 0b0110000,
        "2": 0b1101101,
        "3": 0b1111001,
        "4": 0b0110011,
        "5": 0b1011011,
        "6": 0b1011111,
        "7": 0b1110000,
        "8": 0b1111111,
        "9": 0b1110011,
        "a": 0b1110111,
        "b": 0b0011111,
        "c": 0b1001110,
        "d": 0b0111101,
        "e": 0b1001111,
        "f": 0b1000111,
        "-": 0b0000001,
        " ": 0,
    }

    BITS = 8
    DIGITS = 4
    ROM_SIZE = 2**13
    ROM_LAYOUT = "pgfabcde"
    ORIGIN = "pabcdefg"[::-1]  # Reverse, so .index() gives us bit positions


def shuffle(value: int, ordering: str = Config.ROM_LAYOUT) -> int:
    result = 0
    for segment in ordering:
        result <<= 1
        pos = Config.ORIGIN.index(segment)
        mask = 1 << pos
        result += (value & mask) != 0
    return result


class Mode(Enum):
    UNSIGNED_DECIMAL = 0
    SIGNED_DECIMAL = 1
    HEX = 2
    SIGNED_HEX = 3


def generate_text(value: int, mode: Mode) -> str:
    if mode not in (Mode.SIGNED_DECIMAL, Mode.SIGNED_HEX):
        value = value % (2**Config.BITS)
    if mode in (Mode.HEX, Mode.SIGNED_HEX):
        if value >= 0:
            text = "%02x" % value
        else:
            text = "%03x" % value  # Extra width for sign
    else:
        text = str(value)
    assert len(text) <= Config.DIGITS
    return text.rjust(Config.DIGITS)


if __name__ == "__main__":
    output = bytearray(2**Config.BITS * Config.DIGITS * len(Mode))
    for value in range(-(2 ** (Config.BITS - 1)), 2 ** (Config.BITS - 1)):
        for mode in Mode:
            text = generate_text(value, mode)
            assert len(text) == Config.DIGITS
            for idx, ch in enumerate(text):
                addr = value % (2**Config.BITS)
                addr |= (idx + mode.value * Config.DIGITS) << Config.BITS
                output[addr] = shuffle(Config.FONT[ch])
    # Pad with dashes:
    output += bytearray([shuffle(Config.FONT["-"])] * (Config.ROM_SIZE - len(output)))
    Path("output.bin").write_bytes(output)
