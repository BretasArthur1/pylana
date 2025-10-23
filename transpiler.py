"""
Python to LLVM IR Transpiler for Solana sBPF
Generates Solana-compatible LLVM IR using Python
We're doomed.
"""

import llvmlite.ir as ir
import llvmlite.binding as llvm

def create_solana_program():
    module = ir.Module(name="solana_program")
    module.triple = "bpf"
    
    # In LLVM IR, the i64 = 64 bit integer 
    i8 = ir.IntType(8)
    i64 = ir.IntType(64)
    i8_ptr = i8.as_pointer()
    void = ir.VoidType()
    
    # Create the entrypoint function with proper attributes
    # Signature: uint64_t entrypoint(uint8_t *input)
    entrypoint_type = ir.FunctionType(i64, [i8_ptr])
    entrypoint_func = ir.Function(module, entrypoint_type, name="entrypoint")
    
    # Set function attributes required by solana
    entrypoint_func.linkage = 'external'
    entrypoint_func.attributes.add('noinline')
    
    block = entrypoint_func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    
    # Create string literal for convenience...
    message = "Hello World from Python!\x00"  # null-terminated
    message_bytes = bytearray(message.encode('utf-8'))
    
    # Create global string constant 
    c_message = ir.Constant(ir.ArrayType(i8, len(message_bytes)), message_bytes)
    global_message = ir.GlobalVariable(module, c_message.type, name="python_message")
    global_message.linkage = 'internal'
    global_message.global_constant = True
    global_message.initializer = c_message
    global_message.align = 1  # Important for BPF alignment
    
    # Message length (excluding null terminator) to pass to sol_log_
    message_len = ir.Constant(i64, len(message) - 1)
    
    # 0x207559bd = 544561597 in decimal aka sol_log_ syscall hash
    syscall_hash = ir.Constant(i64, 544561597)
    
    # Cast the hash to a function pointer: void (*)(i8*, i64)
    func_ptr_type = ir.FunctionType(void, [i8_ptr, i64])
    func_ptr_type_ptr = func_ptr_type.as_pointer()
    
    # Cast syscall hash to function pointer using inttoptr
    sol_log_ptr = builder.inttoptr(syscall_hash, func_ptr_type_ptr)
    
    # Get pointer to string constant - cast the array to i8* (pointer to bytes)
    string_ptr = builder.bitcast(global_message, i8_ptr)
    
    # Call the function pointer: sol_log_(message, length)
    builder.call(sol_log_ptr, [string_ptr, message_len])
    
    # Return 0 (success)
    builder.ret(ir.Constant(i64, 0))
    
    return module

def main(): 
    module = create_solana_program()
    
    llvm_module = llvm.parse_assembly(str(module))
    llvm_module.verify()
    
    ir_code = str(module)
    with open('program.ll', 'w') as f:
        f.write(ir_code)
    
    print("✓ Generated LLVM IR: program.ll")
    print("\nGenerated IR:")
    print("-" * 60)
    print(ir_code)
    print("-" * 60)

if __name__ == "__main__":
    main()
