# Zscaler API call for websites categories
# 2023-01-06
# Muten

import csv
import requests
import time

debug = False

# Set the input and output filenames and the Zscaler info filename
input_filename = 'URLS.txt'
output_filename = 'output.csv'
zscaler_filename = 'zscaler-infos.txt'

# Set the chunk size for the API calls
chunk_size = 100

# Set the rate limit for the API calls
#Rate Limit (1/SECOND) exceeded
rate_limit = 1.1

# Read the input file
if debug:
    print(f" Read the input file")

with open(input_filename, 'r') as file:
    # Read the lines in the file
    if debug:
        print(f" Read the lines in the file")

    lines = file.readlines()

# Remove the newline characters from the lines
lines = [line.strip() for line in lines]

# Split the lines into chunks of the specified size
if debug:
    print(f" Split the lines into chunks of the specified size")

url_chunks = [lines[i:i+chunk_size] for i in range(0, len(lines), chunk_size)]

# Load the Zscaler info from the file
if debug:
    print(f" Load the Zscaler info from the file")

with open(zscaler_filename, 'r') as file:
    # Read the lines in the file
    if debug:
        print(f" Read the lines in the file")

    lines = file.readlines()

# Extract the host, login, password, role and API key from the lines
if debug:
    print(f" Extract the host, login, password, role and API key from the lines")

host = lines[0].split(':')[1].strip()
login = lines[1].split(':')[1].strip()
password = lines[2].split(':')[1].strip()
role = lines[3].split(':')[1].strip()
api_key = lines[4].split(':')[1].strip()

if debug:
    print(f"Host: {host}")
    print(f"login: {login}")
    print(f"password: {password}")
    print(f"role: {role}")
    print(f"api_key: {api_key}")

# Obfuscate the API key with the current timestamp
if debug:
    print(f" Obfuscate the API key with the current timestamp")

timestamp = str(int(time.time() * 1000))
n = timestamp[-6:]
r = str(int(n) >> 1).zfill(6)
obfuscated_key = ""
for i in range(0, len(n), 1):
    obfuscated_key += api_key[int(n[i])]
for j in range(0, len(r), 1):
    obfuscated_key += api_key[int(r[j])+2]

if debug:
    print("Timestamp:", n, "\tKey", obfuscated_key)

# Authenticate with the API
if debug:
    print(f" Authenticate with the API")

headers = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache'
}

if debug:
    print("headers:", headers)

data = {
    'apiKey': obfuscated_key,
    'username': login,
    'password': password,
    'timestamp': timestamp
}

if debug:
    print("data:", data)
    print(f'https://{host}/api/v1/authenticatedSession')

r = requests.post(f'https://{host}/api/v1/authenticatedSession', headers=headers, json=data)

if debug:
    print("Response authent:", r)

# Check that the request was successful
if debug:
    print(f" Check that the request was successful")

if r.status_code != 200:
    print(f"Erreur {r.status_code} lors de l'authentification")
    print("Response authent:", r)
    exit()

# Extract the JSESSIONID from the response
if debug:
    print(f" Extract the JSESSIONID from the response")

jsessionid = r.cookies['JSESSIONID']

if debug:
    print("jsessionid:", jsessionid)

# Set the headers for the API calls
if debug:
    print(f" Set the headers for the API calls")

headers = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
    'Cookie': f'JSESSIONID={jsessionid}'
}

# Initialize the list of results
if debug:
    print(f" Initialize the list of results")

results = []

# Loop over the URL chunks
if debug:
    print(f" Loop over the URL chunks")

for i, url_chunk in enumerate(url_chunks):
    # Delay for the rate limit
    time.sleep(rate_limit)

    print(f" Call #", i)
    if debug:
        print("headers:", headers)

    # Set the data for the API call
    if debug:
        print(f" Set the data for the API call")

    data = url_chunk

    if debug:
        print("data:", data)

    # Call the API
    if debug:
        print(f" Call the API")

    r = requests.post(f'https://{host}/api/v1/urlLookup', headers=headers, json=data)

    if debug:
        print(f'https://{host}/api/v1/urlLookup')
        print("Response API:", r)

    # Check that the request was successful
    if debug:
        print(f" Check that the request was successful")

    if r.status_code != 200:
        print(f"Erreur {r.status_code} lors de l'appel API")
        print(r.content)
        exit()

    # Get the response data
    if debug:
        print(f" Get the response data")

    chunk_results = r.json()

    if debug:
        print("chunk_results:", chunk_results)
        print(f" Get the response data")

    # Append the results to the list
    if debug:
        print(f" Append the results to the list")

    results += chunk_results

# Open the output file
if debug:
    print(f" Open the output file")

with open(output_filename, 'w', newline='') as file:
    # Create a CSV writer
    if debug:
        print(f" Create a CSV writer")

    writer = csv.writer(file, delimiter=';')

    # Write the header row
    if debug:
        print(f" Write the header row")

    writer.writerow(['Numéro', 'URL', 'Catégories'])

    # Write the data rows
    if debug:
        print(f" Write the data rows")

    for i, result in enumerate(results):
        categories = ', '.join(result['urlClassifications'])
        writer.writerow([i+1, result['url'], categories])

# Log out of the API
if debug:
    print(f" Log out of the API")

r = requests.delete(f'https://{host}/api/v1/authenticatedSession', cookies={'JSESSIONID': jsessionid})

# Check that the request was successful
if debug:
    print(f" Check that the request was successful")

if r.status_code != 200:
    print(f"Erreur {r.status_code} lors de la déconnexion")
    print("Response déco:", r)

print("Done!")
