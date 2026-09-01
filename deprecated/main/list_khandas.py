filename = r'data\input\Samhita_with_Rishi_Devata_Chandas.txt'

with open(filename, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "खण्डः" in line:
        print(f"{i+1}: {line.strip()}")
