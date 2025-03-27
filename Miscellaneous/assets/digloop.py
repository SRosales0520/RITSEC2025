import subprocess
import re
import time

# DNS query and extract TXT records and NSEC information
def get_txt_and_nsec_record(domain):
    command = ["dig", "+dnssec", domain, "ANY"]
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Regex pattern to extract the TXT record starting with RS{
    pattern_txt = r'"RS\{[^}]*\}"'
    matches_txt = re.findall(pattern_txt, result.stdout)
    
    # Regex pattern to extract the next domain from NSEC records
    pattern_nsec = r'NSEC\s+(\S+)'
    matches_nsec = re.findall(pattern_nsec, result.stdout)
    
    return matches_txt, matches_nsec

# keep querying based on NSEC records and automatically pick up the next domain
def get_all_flags(start_domain, output_file, max_retries=5, wait_time=2):
    all_flags = []
    current_domain = start_domain
    visited_domains = set()  # keeps track of domains already visited
    
    while current_domain:
        # if already visited, stop to avoid infinite loop
        if current_domain in visited_domains:
            print(f"Already visited {current_domain}, stopping to avoid infinite loop.")
            break
        visited_domains.add(current_domain)

        retries = 0
        flags = []
        nsec_domains = []

        # get flags and NSEC records, retry if NSEC records not found
        while retries < max_retries:
            flags, nsec_domains = get_txt_and_nsec_record(current_domain)
            
            # if found, break retry loop
            if nsec_domains:
                break
            else:
                retries += 1
                print(f"Waiting for NSEC records for {current_domain}... (Attempt {retries}/{max_retries})")
                time.sleep(wait_time)  # Wait before retrying
        
        if retries == max_retries:
            print(f"Failed to find NSEC records for {current_domain} after {max_retries} attempts. Stopping.")
            break

        # Print flags found in current domain
        if flags:
            print(f"Found flags for {current_domain}: {', '.join(flags)}")
            all_flags.extend(flags)
            
            # log to fragments file
            with open(output_file, 'a') as file:
                for flag in flags:
                    file.write(f"{flag}\n")
        else:
            print(f"No flags found for {current_domain}.")
        
        # If NSEC records point to another domain, continu
        if nsec_domains:
            current_domain = nsec_domains[0]
            print(f"Moving to next domain: {current_domain}")
        else:
            print("No more NSEC records found, ending loop.")
            break 
    
    return all_flags

# first domain found
start_domain = "0018q6.linksnsec.stellasec.com"
output_file = "fragments.txt"  # Output file for flags

with open(output_file, 'w') as file:
    file.write("Flags collected from DNS queries:\n")

all_flags = get_all_flags(start_domain, output_file)

print("\nAll flags collected:")
for flag in all_flags:
    print(flag)
