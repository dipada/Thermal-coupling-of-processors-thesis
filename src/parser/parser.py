import re
import sys

if len(sys.argv) != 2:
    print("Usage: python3 parser.py <input_file>")
    exit()

input_file = open(sys.argv[1], "r")
output_file = open("output.txt", "w")

# Regex that parse trace-cmd report output
regex = r'^.*?\[(\d+)\].*?(\d+\.\d+).*?19c, value (\w+)$'

for line in input_file:

    match = re.search(regex, line)

    # match with regex, write info on file
    
    if match:
        cpu_num = match.group(1)
        timestamp = match.group(2)
        temperature = match.group(3)  
        output_line = f"{cpu_num} - {timestamp} - {temperature}\n"
        output_file.write(output_line)

input_file.close()
output_file.close()