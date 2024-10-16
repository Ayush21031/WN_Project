import subprocess
a = ['nslookup', '-type=A', 'ameblo.jp']
nslookup_ipv4 = subprocess.run(a, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
print(nslookup_ipv4.stdout.decode('utf-8'))