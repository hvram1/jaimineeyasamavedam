import sys
import os

# Add local directory to path to find the module
sys.path.append(os.getcwd())

from Devanagari_standalone.working_baseline.renderPDF import escape_for_latex

print(f"Testing escape_for_latex with newline:")
result = escape_for_latex("\n")
print(f"Input: '\\n'")
print(f"Output: {repr(result)}")

expected = " "
if result == expected:
    print("SUCCESS: Newline mapped to space.")
else:
    print(f"FAILURE: Newline mapped to {repr(result)}")
