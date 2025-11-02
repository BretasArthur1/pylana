# Pylana - Python to Solana

Uses Python to generate Solana-compatible LLVM IR.

## What This Does

Generates LLVM IR using Python (llvmlite) → compiles to Solana sBPF → deploys to Solana.

The transpiler is hand-coded (not parsing arbitrary Python yet...), but it proves the concept works.

## LLVM IR (If you're curious)

LLVM IR (Intermediate Representation) is a low-level, strongly typed, and platform-independent assembly-like language used by the LLVM compiler framework to represent programs during compilation. It acts as a common representation layer between high-level source languages and machine code, enabling advanced optimization and code generation for multiple architectures.

## How to Use

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Build and deploy
chmod +x build.sh
./build.sh
```

You'll get a Program ID. Test it:

```bash
npm install # just for the first time
node invoke.js <YOUR_PROGRAM_ID>
```

You should see: `Program log: Hello World from Python!`

## Flow

```
transpiler.py (llvmlite)
    ↓ generates LLVM IR
program.ll
    ↓ llvm-as
program.bc (LLVM bitcode)
    ↓ sbpf-linker --cpu v3
hello_world.so (Solana program)
    ↓ solana deploy
Runs on-chain ✓
```

## Prerequisites

### Install Tools

```bash

# LLVM tools (macOS)
brew install llvm

# sbpf-linker (converts LLVM bitcode to Solana sBPF)
cargo install sbpf-linker

```

## Why this monstrosity works

Solana syscalls are function pointers at specific addresses. For example, `sol_log_` is at `0x207559bd`.

We use LLVM's `inttoptr` to cast that address to a function pointer:

```python
syscall_hash = ir.Constant(i64, 544561597)  # 0x207559bd
sol_log_ptr = builder.inttoptr(syscall_hash, func_ptr_type_ptr)
builder.call(sol_log_ptr, [string_ptr, message_len])
```

In the end we're just generating LLVM IR that Solana can understand, and then compiling it to sBPF with sbpf-linker.

## Resources

- [LLVM IR](https://llvm.org/docs/LangRef.html)
- [sbpf-linker](https://github.com/blueshift-gg/sbpf-linker)
- [llvmlite](https://llvmlite.readthedocs.io/en/latest/)

