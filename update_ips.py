import sys
import socket
import ipaddress

# דומיינים דינמיים של YES / STINGTV לתרגום
DOMAINS = [
    "yes.co.il",
    "www.yes.co.il",
    "stingtv.co.il",
    "www.stingtv.co.il",
    "api.yes.co.il",
    "ott.yes.co.il",
    "cdnga.stingtv.co.il",
    "myco.co.il"
]

# טווחים קבועים (CIDR) הקיימים בפיירוול
STATIC_NETWORKS = [
    "185.86.204.0/22",
    "31.168.162.179/28"
]

OUTPUT_FILE = "yes_ips.txt"

def resolve_domains():
    print("[INFO] Starting resolution for YES / STINGTV...")
    valid_entries = set()
    socket.setdefaulttimeout(5)

    # 1. עיבוד ונרמול טווחי ה-IP הסטטיים
    for net_str in STATIC_NETWORKS:
        try:
            net_obj = ipaddress.ip_network(net_str, strict=False)
            if not (net_obj.is_private or net_obj.is_loopback or net_obj.is_unspecified):
                valid_entries.add(str(net_obj))
            else:
                print(f"[WARN] Ignored private static network: {net_str}", file=sys.stderr)
        except ValueError as e:
            print(f"[ERROR] Invalid static network {net_str}: {e}", file=sys.stderr)

    # 2. תרגום דינמי של הדומיינים ואימות IPv4 פומבי בלבד
    for domain in DOMAINS:
        try:
            results = socket.getaddrinfo(domain, None, socket.AF_INET)
            resolved_any = False
            for res in results:
                ip_str = res[4][0]
                try:
                    ip_obj = ipaddress.ip_address(ip_str)
                    if isinstance(ip_obj, ipaddress.IPv4Address):
                        if not (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_unspecified):
                            valid_entries.add(str(ip_obj))
                            resolved_any = True
                        else:
                            print(f"[WARN] Ignored private IP for {domain}: {ip_str}", file=sys.stderr)
                except ValueError:
                    continue
            if resolved_any:
                print(f"[SUCCESS] Resolved {domain}")
        except (socket.gaierror, socket.timeout) as e:
            print(f"[ERROR] Could not resolve {domain}: {e}", file=sys.stderr)

    # 3. מנגנון Fail-Safe: הגנה מפני קובץ ריק או כשל ב-DNS
    min_expected_entries = len(STATIC_NETWORKS) + 1
    if len(valid_entries) < min_expected_entries:
        print(f"[ERROR] Resolved only {len(valid_entries)} entries. Expected at least {min_expected_entries}.", file=sys.stderr)
        print(f"[ERROR] Aborting write to {OUTPUT_FILE} to protect Palo Alto EDL.", file=sys.stderr)
        sys.exit(1)

    # 4. שמירת הקובץ
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for entry in sorted(valid_entries):
            f.write(f"{entry}\n")

    print(f"[SUCCESS] Updated {OUTPUT_FILE} with {len(valid_entries)} entries.")

if __name__ == "__main__":
    resolve_domains()
