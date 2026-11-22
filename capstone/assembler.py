"""
Hack Assembler - Nand to Tetris Capstone
Usage: python assembler.py Prog.asm      -> writes Prog.hack
"""
import sys

K = 41                  # <-- apna K (roll number ke last 2 digits) yaha likho
EXTRA = K % 3           # 0: symbols.txt | 1: error messages | 2: duplicate label warning

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}
DEST = {"": "000", "M": "001", "D": "010", "MD": "011",
        "A": "100", "AM": "101", "AD": "110", "AMD": "111"}
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}

SYMBOLS = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
           "SCREEN": 16384, "KBD": 24576}
for i in range(16):
    SYMBOLS["R%d" % i] = i


class AsmError(Exception):
    pass


def clean(line):
    """Comment aur spaces hatao."""
    line = line.split("//")[0]
    return "".join(line.split())


def encode_c(ins):
    dest, comp, jump = "", ins, ""
    if "=" in ins:
        dest, comp = ins.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)
    if dest not in DEST or comp not in COMP or jump not in JUMP:
        raise AsmError("invalid instruction")
    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def assemble(lines):
    symbols = dict(SYMBOLS)
    labels = {}
    errors = []
    warnings = []

    # ---------- First pass: labels ----------
    rom = 0
    for num, raw in enumerate(lines, 1):
        s = clean(raw)
        if not s:
            continue
        if s.startswith("("):
            if not s.endswith(")") or len(s) < 3:
                errors.append("Line %d: invalid label '%s'" % (num, s))
                continue
            name = s[1:-1]
            if name in labels:
                warnings.append("Warning line %d: label (%s) already defined" % (num, name))
            labels[name] = rom          # latest definition wins
            symbols[name] = rom
        else:
            rom += 1

    # ---------- Second pass: machine code ----------
    out = []
    next_var = 16
    variables = {}
    for num, raw in enumerate(lines, 1):
        s = clean(raw)
        if not s or s.startswith("("):
            continue
        try:
            if s[0] == "@":
                sym = s[1:]
                if sym == "":
                    raise AsmError("invalid instruction")
                if sym.isdigit():
                    val = int(sym)
                    if val > 32767:
                        raise AsmError("address too large")
                else:
                    if sym[0].isdigit():
                        raise AsmError("invalid symbol name")
                    if sym not in symbols:
                        symbols[sym] = next_var
                        variables[sym] = next_var
                        next_var += 1
                    val = symbols[sym]
                out.append(format(val, "016b"))
            else:
                out.append(encode_c(s))
        except AsmError as e:
            errors.append("Line %d: %s (%s)" % (num, e, raw.strip()))
    return out, labels, variables, errors, warnings


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".asm"):
        print("Usage: python assembler.py File.asm")
        sys.exit(1)
    path = sys.argv[1]
    with open(path) as f:
        lines = f.read().splitlines()

    out, labels, variables, errors, warnings = assemble(lines)

    # Feature 2 (K mod 3 == 2): duplicate label warning
    if EXTRA == 2:
        for w in warnings:
            print(w)

    # Feature 1 (K mod 3 == 1): clear error messages
    if errors:
        if EXTRA == 1:
            for e in errors:
                print(e)
        else:
            print("Assembly failed. Errors found.")
        sys.exit(1)

    hack = path[:-4] + ".hack"
    with open(hack, "w") as f:
        f.write("\n".join(out) + "\n")

    # Feature 0 (K mod 3 == 0): symbols.txt
    if EXTRA == 0:
        with open("symbols.txt", "w") as f:
            f.write("LABELS\n")
            for n, a in labels.items():
                f.write("%s = %d\n" % (n, a))
            f.write("VARIABLES\n")
            for n, a in variables.items():
                f.write("%s = %d\n" % (n, a))
    print("Done:", hack, "(%d instructions)" % len(out))


if __name__ == "__main__":
    main()
