#!/usr/bin/env python3
import sys
import time

print("=== TEST SCRIPT STARTING ===", flush=True)
print("Python version:", sys.version, flush=True)
print("Sleeping for 60 seconds...", flush=True)

for i in range(60):
    print(f"Still alive... {i+1}/60", flush=True)
    time.sleep(1)

print("Test complete!", flush=True)
