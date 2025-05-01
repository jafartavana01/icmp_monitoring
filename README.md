# Network Monitor (ICMP)

A real-time network monitoring tool that uses ICMP (ping) to track the responsiveness of network hosts. Built with Flask and Chart.js.

![Network Monitor Screenshot](Screenshot%201404-02-12%20at%2000.32.17.png)

## Features

- Real-time ping monitoring of multiple hosts
- Interactive graphs showing response times
- Visual indication of timeouts (red background)
- Add and remove hosts dynamically
- Responsive web interface

## Requirements

- Python 3.x
- Flask
- ping3
- Flask-SocketIO

## Installation

1. Clone this repository:
```bash
git clone [your-repo-url]
cd icmp_monitoring
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`
3. Enter a hostname or IP address to start monitoring
4. To remove a host from monitoring, hover over its graph and click the "Remove" button

## License

MIT License