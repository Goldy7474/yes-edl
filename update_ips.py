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
    "185.86.204.0/22",      # מכסה את הטווחים 204.0/24, 205.0/24, 206.0/24, 207.0/24
    "31.168.162.179/28"     # הופך אוטומטית ל-31.168.162.176/28 התקין
]

OUTPUT_FILE = "yes_ips.txt"

def resolve_domains():
    valid_entries = set()

    # הגדרת Timeout של 5 שניות לכל שאילתת DNS
    socket.setdefaulttimeout(5)

    # 1. עיבוד ונרמול הרשתות הסטטיות
    for net_str in STATIC_NETWORKS:
        try:
            # strict=False מנרמל כתובת Host בתוך סאבנט לכתובת רשת חוקית
            net_obj = ipaddress.ip_network(net_str, strict=False)
            
            # סינון רשתות פרטיות או לא תקניות
            if not (net_obj.is_private or net_obj.is_loopback or net_obj.is_unspecified):
                valid_entries.add(str(net_obj))
            else:
                print(f"[WARN] Ignored private static network: {net_str}")
        except ValueError as e:
            print(f"[ERROR] Error processing network {net_str}: {e}")

    # 2. תרגום דינמי של הדומיינים ואימות תקינות ה-IP
    for domain in DOMAINS:
        try:
            results = socket.getaddrinfo(domain, None, socket.AF_INET) # סינון מראש ל-IPv4 בלבד
            for res in results:
                ip_str = res[4][0]
                try:
                    ip_obj = ipaddress.ip_address(ip_str)
                    
                    # אימות שהכתובת היא IPv4 פומבית ותקינה
                    if isinstance(ip_obj, ipaddress.IPv4Address):
                        if not (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_unspecified):
                            valid_entries.add(str(ip_obj))
                        else:
                            print(f"[WARN] Ignored private IP for {domain}: {ip_str}")
                except ValueError:
                    continue
        except Exception as e:
            print(f"[ERROR] Error resolving {domain}: {e}")

    # 3. מנגנון Fail-Safe: הגנה מפני קובץ ריק או תוצאה חלקית בגלל תקלת DNS
    # מצפים לפחות לטווחים הסטטיים + כתובות מהדומיינים
    min_expected = len(STATIC_NETWORKS) + 1
    if len(valid_entries) < min_expected:
        print(f"[CRITICAL] Only {len(valid_entries)} IPs/Networks resolved. Expected at least {min_expected}.")
        print("[CRITICAL] Aborting file write to protect Palo Alto EDL.")
        sys.exit(1) # הכשלת ה-Action כדי ש-GitHub לא יבצע Commit לקובץ פגום

    # 4. שמירה נקייה וממויינת לקובץ
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for entry in sorted(valid_entries):
            f.write(f"{entry}\n")
            
    print(f"[SUCCESS] Successfully updated {OUTPUT_FILE} with {len(valid_entries)} entries.")

if __name__ == "__main__":
    resolve_domains()
