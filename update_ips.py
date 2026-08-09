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

def resolve_domains():
    valid_entries = set()

    # 1. עיבוד ונרמול הרשתות הסטטיות
    for net_str in STATIC_NETWORKS:
        try:
            # strict=False מנרמל כתובת Host בתוך סאבנט לכתובת רשת חוקית
            net_obj = ipaddress.ip_network(net_str, strict=False)
            valid_entries.add(str(net_obj))
        except ValueError as e:
            print(f"Error processing network {net_str}: {e}")

    # 2. תרגום דינמי של הדומיינים ואימות תקינות ה-IP
    for domain in DOMAINS:
        try:
            results = socket.getaddrinfo(domain, None)
            for res in results:
                ip_str = res[4][0]
                try:
                    # אימות שהכתובת היא IPv4 תקינה
                    ip_obj = ipaddress.ip_address(ip_str)
                    if isinstance(ip_obj, ipaddress.IPv4Address):
                        valid_entries.add(str(ip_obj))
                except ValueError:
                    continue
        except Exception as e:
            print(f"Error resolving {domain}: {e}")

    # 3. שמירה לקובץ
    with open("yes_ips.txt", "w") as f:
        for entry in sorted(valid_entries):
            f.write(f"{entry}\n")

if __name__ == "__main__":
    resolve_domains()
