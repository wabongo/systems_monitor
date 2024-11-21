# EQA Franchise Monitor

A modern dashboard application for monitoring franchise systems metrics, services, and network status.

## Features

- Real-time system metrics monitoring (CPU, Memory, Disk Usage)
- Service status tracking
- Network performance metrics
- Dark/Light theme support
- Data export functionality
- Interactive graphs and visualizations

## Prerequisites

- Python 3.13 or higher
- pip (Python package installer)
- Git (optional, for version control)

## Installation

1. Clone or download the repository:
```bash
git clone <repository-url>
# or download and extract the ZIP file
```

2. Navigate to the project directory:
```bash
cd systems_monitor
```

3. Create and activate a virtual environment (recommended):
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

4. Install required dependencies:
```bash
pip install -r .\requirements.txt
```

## Configuration

1. Configure your settings in `config.yaml`:
   - Update server connections
   - Adjust monitoring intervals
   - Set threshold values

2. Make sure all required services are accessible from your network.

## Running the Application

1. Start the monitor:
```bash
python run.py
```

2. Access the dashboard:
   - Open your web browser
   - Navigate to `http://localhost:8050` (default port)

## Usage

1. Select a franchise from the dropdown menu
2. Monitor real-time metrics in three main sections:
   - System Metrics (CPU, Memory, Disk)
   - Service Status
   - Network Metrics

3. Use the theme toggle in the navbar to switch between light and dark modes
4. Export data using the export button when needed

## Troubleshooting

1. If the application fails to start:
   - Check if all dependencies are installed correctly
   - Verify the configuration in `config.yaml`
   - Ensure required ports are not in use

2. If metrics are not updating:
   - Check network connectivity
   - Verify service permissions
   - Review logs in the `logs` directory

## Project Structure

```
franchise_monitor/
├── app/                   # Main application directory
│   ├── assets/            # CSS and static files
│   ├── components/        # Reusable UI components
│   ├── layouts/           # Page layouts
│   └── callbacks/         # Dashboard interactivity
├── tests/                 # Test files
├── collector.py           # System metrics collector
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
└── run.py                 # Application entry point
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]
