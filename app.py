    json_structure = {
        "remarks": acc.get('username', 'VIP-Server'),
        "log": {
            "loglevel": "warning"
        },
        "inbounds": [
            {
                "tag": "socks",
                "port": 10808,
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": True,
                    "userLevel": 8
                },
                "sniffing": {
                    "enabled": True,
                    "destOverride": ["http", "tls"],
                    "routeOnly": False
                }
            }
        ],
        "outbounds": [
            {
                "tag": "proxy",
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {
                            "address": acc.get('server_ip'),
                            "port": 443,
                            "users": [
                                {
                                    "id": acc.get('uuid'),
                                    "level": 8,
                                    "encryption": "none"
                                }
                            ]
                        }
                    ]
                },
                "streamSettings": {
                    "network": "ws",
                    "security": "tls",
                    "wsSettings": {
                        "path": "/vless",
                        "headers": {
                            "Host": acc.get('host')
                        }
                    },
                    "tlsSettings": {
                        "allowInsecure": True,
                        "serverName": acc.get('host'),
                        "show": False
                    }
                },
                "mux": {
                    "enabled": False,
                    "concurrency": -1,
                    "xudpConcurrency": 8,
                    "xudpProxyUDP443": ""
                }
            },
            {
                "tag": "direct",
                "protocol": "freedom",
                "settings": {
                    "domainStrategy": "UseIP"
                },
                "mux": {
                    "enabled": False,
                    "concurrency": 8,
                    "xudpConcurrency": 8,
                    "xudpProxyUDP443": ""
                }
            },
            {
                "tag": "block",
                "protocol": "blackhole",
                "settings": {
                    "response": {
                        "type": "http"
                    }
                },
                "mux": {
                    "enabled": False,
                    "concurrency": 8,
                    "xudpConcurrency": 8,
                    "xudpProxyUDP443": ""
                }
            }
        ],
        "dns": {
            "servers": ["1.1.1.1"],
            "hosts": {
                "domain:google.com": "8.8.8.8"
            }
        }
    }
