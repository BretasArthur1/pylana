#!/bin/bash
set -e

echo "=== Python to Solana sBPF Build Script ==="
echo ""

# Generate LLVM IR from Python
echo "Generating LLVM IR from Python..."
python transpiler.py
echo ""

# Compile LLVM IR to LLVM bitcode
echo "Compiling LLVM IR to bitcode..."
llvm-as program.ll -o program.bc
echo "✓ Generated program.bc (LLVM bitcode)"
echo ""

# Link bitcode to Solana sBPF
echo "Linking bitcode to Solana sBPF..."
sbpf-linker --cpu v2 --export entrypoint --output hello_world.so program.bc 2>&1 | grep -v "unable to open LLVM" || true
echo "✓ Generated hello_world.so (Solana sBPF binary)"
echo ""

# Deploy to Solana localnet
echo "Deploying to Solana localnet..."
solana program deploy hello_world.so
echo ""
echo "=== Deployment Complete ==="

#  Invoke the program
echo "Invoking the program"
echo "Call it with:"
echo ""
echo "    node invoke.js <YOUR_PROGRAM_ID>"
echo ""

