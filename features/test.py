import re

# Sample input string
input_string = "d/field 1 s/field 2 t/field 3"

# Define the regular expression pattern
pattern = r'([dts])/(.*?)\s*(?=[dts]/|\Z)'

# Use re.findall to extract the fields
fields = re.findall(pattern, input_string)

# Initialize dictionaries to store the extracted fields for each prefix
result = {'d': None, 't': None, 's': None}

# Loop through the extracted fields and store them in the result dictionary
for prefix, value in fields:
    result[prefix] = value

# Access the extracted fields
d_field = result['d']
t_field = result['t']
s_field = result['s']

# Print the extracted fields
print("d:", d_field)
print("t:", t_field)
print("s:", s_field)
