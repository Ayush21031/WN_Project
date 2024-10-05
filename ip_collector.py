import csv
import socket
import dns.resolver
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os

def get_ip_addresses(domain):
    ipv4_addresses = []
    ipv6_addresses = []
    
    # IPv4 resolution
    try:
        answers = dns.resolver.resolve(domain, 'A')
        ipv4_addresses = [answer.to_text() for answer in answers]
    except Exception as e:
        print(f"IPv4 resolution failed for {domain}: {str(e)}")
        ipv4_addresses = ['Not found']
    
    # IPv6 resolution
    try:
        answers = dns.resolver.resolve(domain, 'AAAA')
        ipv6_addresses = [answer.to_text() for answer in answers]
    except Exception as e:
        print(f"IPv6 resolution failed for {domain}: {str(e)}")
        ipv6_addresses = ['Not found']
    
    return {
        'domain': domain,
        'ipv4_addresses': ipv4_addresses,
        'ipv6_addresses': ipv6_addresses
    }

def process_domains(input_file, output_file):
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return None
    
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        domains = df['Domain'].tolist()
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return None
    
    results = []
    
    # Use ThreadPoolExecutor for concurrent processing
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(get_ip_addresses, domain) for domain in domains]
        
        for future, domain in zip(futures, domains):
            try:
                result = future.result()
                category = df[df['Domain'] == domain]['Category'].iloc[0]
                region = df[df['Domain'] == domain]['Region'].iloc[0]
                
                results.append({
                    'Domain': domain,
                    'Category': category,
                    'Region': region,
                    'IPv4_Addresses': '; '.join(result['ipv4_addresses']),
                    'IPv6_Addresses': '; '.join(result['ipv6_addresses'])
                })
            except Exception as e:
                print(f"Error processing domain {domain}: {str(e)}")
                results.append({
                    'Domain': domain,
                    'Category': df[df['Domain'] == domain]['Category'].iloc[0],
                    'Region': df[df['Domain'] == domain]['Region'].iloc[0],
                    'IPv4_Addresses': 'Error',
                    'IPv6_Addresses': 'Error'
                })
    
    if not results:
        print("No results were generated.")
        return None
    
    # Convert results to DataFrame and save to CSV
    results_df = pd.DataFrame(results)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"{output_file}_{timestamp}.csv"
    results_df.to_csv(output_filename, index=False)
    print(f"Results saved to {output_filename}")
    
    return results_df

def main():
    input_file = 'website.csv'  # Make sure this matches your actual filename
    output_file = 'ip_addresses'
    
    print("Starting DNS resolution...")
    results_df = process_domains(input_file, output_file)
    
    if results_df is not None:
        # Print summary statistics
        total_domains = len(results_df)
        domains_with_ipv4 = results_df[results_df['IPv4_Addresses'] != 'Not found'].shape[0]
        domains_with_ipv6 = results_df[results_df['IPv6_Addresses'] != 'Not found'].shape[0]
        
        print(f"\nSummary:")
        print(f"Total domains processed: {total_domains}")
        print(f"Domains with IPv4: {domains_with_ipv4} ({domains_with_ipv4/total_domains*100:.2f}%)")
        print(f"Domains with IPv6: {domains_with_ipv6} ({domains_with_ipv6/total_domains*100:.2f}%)")
    else:
        print("Script execution failed.")

if __name__ == "__main__":
    main()