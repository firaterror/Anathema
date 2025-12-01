import subprocess
import pyfiglet
import os
import json
import requests


WHATSAPP_TOKEN = "EAAPe4ZBzfP3sBQCcZAr1B0aPvugHbt2hgveJAw5OUx9vji4GL9NsuoD1ExXIiZAi7oSKQAgiZAkMZAooiYXuZBbhY1ogPQ6isGip1Hc29rAKFsvVlZCgbKwFZCv6TERkNsOUhtiR1tpHgTdwLqpEOgEixfCQ1lPIZCBhhZBTX0lqTdWgm0ZAxZA5epZBuDjxNtH71RAZDZD"
WHATSAPP_PHONE_ID = "867392246460915"
WHATSAPP_TO = "16138830217"

RED = "\033[31m"
RESET = "\033[0m"

banner = pyfiglet.figlet_format("Anathema", font="slant")
print(banner)
print("                     v1.0")

BASE = "/root/Anathema"
TOP_DOMAINS = f"{BASE}/top_domains.txt"
OUTPUT = f"{BASE}/getting_started.txt"
DNSX_OUT = f"{BASE}/dns_results.json"

def run_subfinder(domain):
    try:
        result = subprocess.run(
            ["subfinder", "-silent", "-d", domain],
            capture_output=True,
            text=True
        )
        subs = result.stdout.strip().split("\n")
        return [s for s in subs if s.strip()]
    except:
        return []

def run_dnsx(input_file, output_file):
    print(f"{RED}[+]{RESET} Running DNSx on {input_file}")
    os.system(f"dnsx -l {input_file} -json -silent > {output_file}")
    print(f"{RED}[+]{RESET} DNSx scan completed → {output_file}")

def parse_dnsx(json_file):
    print(f"{RED}[+]{RESET} Parsing DNSx results")

    resolved = []
    nxdomain = []
    cname_map = {}

    with open(json_file, "r") as f:
        for line in f:
            data = json.loads(line)

            domain = data.get("host")
            status = data.get("status_code")   # FIXED
            cname = data.get("cname", [])

            if status == "NXDOMAIN":
                nxdomain.append(domain)
            else:
                resolved.append(domain)

            if cname:
                cname_map[domain] = cname

    print(f"{RED}[+]{RESET} Resolved: {len(resolved)} | NXDOMAIN: {len(nxdomain)}")
    return resolved, nxdomain, cname_map

def run_nuclei(input_file):
    print(f"{RED}[+]{RESET} Running Nuclei takeover scan")
    nuclei_output = f"{BASE}/nuclei_results.json"
    os.system(f"nuclei -l {input_file} -t ~/nuclei-templates/http/takeovers/ -jsonl -silent -o {nuclei_output}")
    print(f"{RED}[+]{RESET} Nuclei scan completed → {nuclei_output}")
    return nuclei_output

def parse_nuclei_results(json_file):
    print(f"{RED}[+]{RESET} Parsing Nuclei results")
    vulnerabilities = []
    try:
        with open(json_file, "r") as f:
            for line in f:
                data = json.loads(line)
                vulnerabilities.append({
                    "host": data.get("host"),
                    "template": data.get("template-id"),
                    "matched": data.get("matched-at"),
                    "severity": data.get("info", {}).get("severity", "unknown")
                })
    except FileNotFoundError:
        print(f"{RED}[!]{RESET} No Nuclei results file found")
    
    print(f"{RED}[+]{RESET} Found {len(vulnerabilities)} vulnerable targets")
    return vulnerabilities





def send_whatsapp_alert():
    print(f"{RED}[+]{RESET} Sending WhatsApp notification")
    
    message = "Nuclei just ran!"
    
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": WHATSAPP_TO,
        "type": "text",
        "text": {"body": message}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    print(f"{RED}[DEBUG]{RESET} Response status: {response.status_code}")
    print(f"{RED}[DEBUG]{RESET} Response body: {response.text}")


def main():
    all_subs = set()  # FIXED — no global

    with open(TOP_DOMAINS, "r") as f:
        domains = [d.strip() for d in f if d.strip()]

    for d in domains:
        print(f"{RED}[+]{RESET} Running subfinder on: {d}")
        subs = run_subfinder(d)
        all_subs.update(subs)

    with open(OUTPUT, "w") as f:
        for sub in sorted(all_subs):
            f.write(sub + "\n")

    print(f"[+] Done. Saved {len(all_subs)} subdomains to {OUTPUT}")

    run_dnsx(OUTPUT, DNSX_OUT)

    resolved, nxdomain, cname_map = parse_dnsx(DNSX_OUT)
    scan_targets = set(nxdomain)
    scan_targets.update(cname_map.keys())
    targets_file = f"{BASE}/nuclei_targets.txt"
    with open(targets_file, "w") as f:
        for domain in sorted(scan_targets):
            f.write(domain + "\n")
    print(f"{RED}[+]{RESET} Scanning {len(scan_targets)} targets (NXDOMAIN + CNAME)")
    nuclei_output = run_nuclei(targets_file)
    vulnerabilities = parse_nuclei_results(nuclei_output)
    send_whatsapp_alert()

if __name__ == "__main__":
    main()
