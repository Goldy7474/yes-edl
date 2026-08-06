import socket

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
    "31.168.162.179/28"
]

def resolve_domains():
    ip_list = set()

    # הוספת הטווחים הסטטיים
    for net in STATIC_NETWORKS:
        ip_list.add(net)

    # תרגום דינמי של הדומיינים
    for domain in DOMAINS:
        try:
            results = socket.getaddrinfo(domain, None)
            for res in results:
                ip = res[4][0]
                # סינון כתובות IPv4 בלבד עבור EDL ב-PAN-OS
                if "." in ip:
                    ip_list.add(ip)
        except Exception as e:
            print(f"Error resolving {domain}: {e}")

    # שמירה לקובץ
    with open("yes_ips.txt", "w") as f:
        for ip in sorted(ip_list):
            f.write(f"{ip}\n")

if __name__ == "__main__":
    resolve_domains()
