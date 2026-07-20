import os

path = r'c:\Users\DHYAN\Downloads\gym management (2)\gym management\gym management\_Project\_Project\gym\fitnessmaster\core\static\css\style.css'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We want to keep lines up to 384 (1-based index) and after 400
# Indices are 0-based
# Line 386 is index 385
# We want to remove from index 385 to 399
new_lines = lines[:385] + lines[400:]

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(new_lines)
