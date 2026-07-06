# 🌐 DNS Resolver

> A Python-based DNS Resolver application developed using Socket Programming. The project demonstrates how the Domain Name System (DNS) resolves hostnames into IP addresses while improving performance through a local caching mechanism with Time-To-Live (TTL) based cache expiration.

The application follows a client-server architecture and includes both Command Line (CLI) and Tkinter GUI clients for interacting with the DNS server.

---

## 📌 Features

- 🌐 Hostname to IP address resolution
- 🔗 Client-Server communication using TCP sockets
- ⚡ Local DNS cache for faster repeated lookups
- ⏳ TTL (Time-To-Live) based automatic cache expiration
- 📦 JSON-based communication between client and server
- 💻 Command Line Interface (CLI) client
- 🖥️ User-friendly GUI built with Tkinter
- 📊 Displays:
  - Hostname
  - IP Address
  - Cache Status (Hit/Miss)
  - TTL Value

---

## 🛠 Tech Stack

### Programming Language

- Python 3

### Networking

- TCP Socket Programming
- REST API

### GUI

- Tkinter

### Data Format

- JSON

### Tools

- Git
- GitHub
- VS Code

---

## 📂 Project Structure

```text
DNS-Resolver
│
├── dns_api_server.py
├── dns_cli_client_api.py
├── dns_gui_client_toggle.py
├── .gitignore
└── README.md
```

---

## ⚙️ How It Works

1. The DNS API server starts and listens for client requests.
2. The client sends a hostname (for example, `google.com`) to the server.
3. The server checks whether the hostname exists in the local DNS cache.
4. If the hostname is found and the TTL has not expired:
   - The cached IP address is returned immediately.
5. Otherwise:
   - The server resolves the hostname using the system DNS.
   - The resolved IP address is stored in the local cache with a TTL.
   - The result is returned to the client.
6. The CLI or GUI displays the hostname, resolved IP address, cache status, and remaining TTL.

---

## 🚀 Getting Started

### Clone the Repository

```bash
git clone https://github.com/Ishwari345/DNS-Resolver.git
```

Navigate to the project directory

```bash
cd DNS-Resolver
```

---

### Run the API Server

```bash
python dns_api_server.py
```

---

### Run the CLI Client

```bash
python dns_cli_client_api.py
```

---

### Run the GUI Client

```bash
python dns_gui_client_toggle.py
```

---

## 📷 Screenshots

> Add screenshots after testing the application.

- GUI Interface
- CLI Interface
- DNS Query Results
- Cache Hit / Miss Demonstration

---

## 🎯 Learning Outcomes

This project helped in understanding:

- Domain Name System (DNS)
- Client-Server Architecture
- TCP Socket Programming
- DNS Resolution
- DNS Caching
- Time-To-Live (TTL)
- JSON Data Exchange
- GUI Development using Tkinter

---

## 🔮 Future Enhancements

- IPv6 support
- Multi-client handling using threading
- DNS query logging
- Cache visualization within the GUI
- Enhanced error handling
- Configurable DNS server
- Cloud deployment

---

## 👩‍💻 Author

**Ishwari Bagewadi**

GitHub: https://github.com/Ishwari345

---

## 📚 References

- Python Socket Programming Documentation
- Python Tkinter Documentation
- RFC 1034 – Domain Names: Concepts and Facilities
- RFC 1035 – Domain Names: Implementation and Specification
- Computer Networks – Andrew S. Tanenbaum

---

## ⭐ If you found this project interesting...

Give this repository a ⭐ on GitHub!
