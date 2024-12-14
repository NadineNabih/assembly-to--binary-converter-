class Assembler:
    def __init__(self):
        self.symbol_table = {}
        self.location_counter = 0
        self.opcode_table = {
            "AND": "000",
            "ADD": "001",
            "LDA": "010",
            "STA": "011",
            "BUN": "100",
            "BSA": "101",
            "ISZ": "110",
            "CLA": "7800",
            "CLE": "7400",
            "CMA": "7200",
            "CIR": "7080",
            "CIL": "7040",
            "INC": "7020",
            "SPA": "7010",
            "SNA": "7008",
            "SZA": "7004",
            "SZE": "7002",
            "HLT": "7001",
            "INP": "F800",
            "OUT": "F400",
            "SKI": "F200",
            "SKO": "F100",
            "ION": "F080",
            "IOF": "F040",
        }
        self.binary_output = []

    def first_pass(self, assembly_code):
        """
        First pass to construct the symbol table.
        """
        self.location_counter = 0
        for line in assembly_code:
            line = line.strip()
            if not line or line.startswith("/"):
                continue  # Skip comments and empty lines

            tokens = line.split()

            # Check if the line has a label
            if tokens[0].endswith(","):
                label = tokens[0][:-1]
                self.symbol_table[label] = self.location_counter
                tokens = tokens[1:]  # Remove the label

            # Handle pseudo-instructions like ORG
            if tokens[0] == "ORG":
                self.location_counter = int(tokens[1], 16)
            elif tokens[0] == "END":
                break
            else:
                self.location_counter += 1

    def second_pass(self, assembly_code):
        """
        Second pass to translate assembly into binary.
        """
        self.location_counter = 0
        for line in assembly_code:
            line = line.strip()
            if not line or line.startswith("/"):
                continue
    
            tokens = line.split()
    
            # Skip labels in this pass
            if tokens[0].endswith(","):
                tokens = tokens[1:]
    
            if tokens[0] == "ORG":
                self.location_counter = int(tokens[1], 16)
            elif tokens[0] == "END":
                break
            elif tokens[0] in self.opcode_table:
                opcode = self.opcode_table[tokens[0]]
    
                if len(opcode) == 3:  # Memory-reference instruction
                    label = tokens[1].strip(",") if len(tokens) > 1 else None
                    address = self.symbol_table.get(label, 0)  # Default to 0 if label is None
    
                    address_binary = f"{address:012b}"
                    is_indirect = len(tokens) > 2 and tokens[-1] == "I"
    
                    # Combine opcode and address with the indirect bit
                    indirect_bit = "1" if is_indirect else "0"
                    binary_instruction = f"{indirect_bit}{opcode}{address_binary}"
    
                    print(f"Processing MRI: {tokens[0]} {label or ''} {'I' if is_indirect else ''}")
                    print(f"Opcode: {opcode}, Address: {address_binary}, Indirect Bit: {indirect_bit}, Instruction: {binary_instruction}")
    
                elif len(opcode) == 4:  # Non-MRI instruction
                    binary_instruction = f"{int(opcode, 16):016b}"
                    print(f"Processing Non-MRI: {tokens[0]}, Instruction: {binary_instruction}")
                else:
                    raise ValueError(f"Invalid opcode format for instruction: {tokens[0]}")
    
                self.binary_output.append((self.location_counter, binary_instruction))
                self.location_counter += 1
            elif tokens[0] in ["DEC", "HEX"]:
                # Handle constants
                value = int(tokens[1], 10 if tokens[0] == "DEC" else 16)
                if value < 0:  # Handle negative numbers
                    value = (1 << 16) + value
                self.binary_output.append((self.location_counter, f"{value:016b}"))
                print(f"Processing constant: {tokens[0]} {tokens[1]}, Value: {value:016b}")
                self.location_counter += 1

    def assemble(self, assembly_code):
        self.first_pass(assembly_code)
        print("Symbol Table after First Pass:")
        for symbol, address in self.symbol_table.items():
            print(f"{symbol}: {address:03X}")

        self.second_pass(assembly_code)
        return self.binary_output

    def print_output(self):
        """
        Print the Symbol Table and Machine Code in the desired format.
        """
        print("Symbol Table:")
        for symbol, address in self.symbol_table.items():
            print(f"{symbol}: {address:03X}")

        print("\nMachine Code:")
        for location, binary in self.binary_output:
            print(f"{location:03X}: {binary}")

# Example usage:
assembly_code = [
    "ORG 100",
    "LDA SUB",
    "CMA",
    "INC",
    "ADD MIN",
    "STA DIF",
    "HLT",
    "MIN, DEC 83",
    "SUB, DEC -23",
    "DIF, HEX 0",
    "END",
]

assembler = Assembler()
binary_output = assembler.assemble(assembly_code)
assembler.print_output()
