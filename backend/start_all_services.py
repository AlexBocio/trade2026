"""
Bulk Service Migrator and Starter
Updates requirements.txt for Python 3.13 compatibility and starts all backend services
"""

import subprocess
import time
import os
from pathlib import Path

# Service configurations: (directory, port)
SERVICES = [
    ('factor_models', 5004),
    ('portfolio_optimizer', 5001),
    ('rl_trading', 5002),
    ('advanced_backtest', 5003),
    ('simulation_engine', 5005),
    ('fractional_diff', 5006),
    ('meta_labeling', 5007),
]

# Python 3.13 compatible requirements template
COMPATIBLE_REQUIREMENTS = """flask>=3.1.0
flask-cors>=5.0.0
numpy>=1.26.0
pandas>=2.2.0
scikit-learn>=1.5.0
requests>=2.32.0
"""

def update_requirements(service_dir):
    """Update requirements.txt to Python 3.13 compatible versions"""
    req_file = Path(service_dir) / 'requirements.txt'

    if req_file.exists():
        print(f"Updating requirements.txt for {service_dir.name}...")
        # Backup original
        backup = req_file.with_suffix('.txt.backup')
        if not backup.exists():
            req_file.rename(backup)

        # Write compatible requirements
        req_file.write_text(COMPATIBLE_REQUIREMENTS)
        print(f"  [OK] Updated {service_dir.name}/requirements.txt")
    else:
        print(f"  [WARN] No requirements.txt found for {service_dir.name}")

def install_dependencies(service_dir):
    """Install service dependencies"""
    print(f"Installing dependencies for {service_dir.name}...")
    result = subprocess.run(
        ['pip', 'install', '-r', 'requirements.txt'],
        cwd=service_dir,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"  [OK] Dependencies installed for {service_dir.name}")
        return True
    else:
        print(f"  [FAIL] Failed to install dependencies for {service_dir.name}")
        print(f"    Error: {result.stderr[:200]}")
        return False

def start_service(service_dir, port):
    """Start a service in background without visible console"""
    app_file = service_dir / 'app.py'

    if not app_file.exists():
        print(f"  [WARN] No app.py found for {service_dir.name}")
        return None

    print(f"Starting {service_dir.name} on port {port}...")

    # Create logs directory
    logs_dir = service_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)

    # Log file path
    log_file = logs_dir / f'{service_dir.name}.log'

    # Open log file for writing
    log_handle = open(log_file, 'w')

    # Start process silently (no console window)
    if os.name == 'nt':
        # Windows: use CREATE_NO_WINDOW flag
        process = subprocess.Popen(
            ['python', 'app.py'],
            cwd=service_dir,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            creationflags=0x08000000  # CREATE_NO_WINDOW
        )
    else:
        # Linux/Mac
        process = subprocess.Popen(
            ['python', 'app.py'],
            cwd=service_dir,
            stdout=log_handle,
            stderr=subprocess.STDOUT
        )

    print(f"  [OK] Started {service_dir.name} (PID: {process.pid}, Log: {log_file})")
    return process

def main():
    backend_dir = Path(__file__).parent
    print(f"Backend directory: {backend_dir}\n")

    started_services = []

    for service_name, port in SERVICES:
        service_dir = backend_dir / service_name

        if not service_dir.exists():
            print(f"[WARN] Service directory not found: {service_name}")
            continue

        print(f"\n{'='*60}")
        print(f"Processing {service_name} (port {port})")
        print(f"{'='*60}")

        # Update requirements.txt
        update_requirements(service_dir)

        # Install dependencies
        if not install_dependencies(service_dir):
            print(f"  [WARN] Skipping {service_name} due to dependency installation failure")
            continue

        # Start service
        process = start_service(service_dir, port)
        if process:
            started_services.append((service_name, port, process))

    print(f"\n{'='*60}")
    print(f"STARTUP SUMMARY")
    print(f"{'='*60}")
    print(f"Started {len(started_services)} services:\n")

    for service_name, port, process in started_services:
        print(f"  [OK] {service_name:20s} - Port {port} - PID {process.pid}")

    print(f"\n{'='*60}")
    print("Waiting 5 seconds for services to initialize...")
    print(f"{'='*60}")
    time.sleep(5)

    # Health check
    print("\nHealth Check:")
    import requests
    for service_name, port, _ in started_services:
        try:
            resp = requests.get(f"http://localhost:{port}/health", timeout=2)
            status = "[HEALTHY]" if resp.status_code == 200 else f"[{resp.status_code}]"
        except Exception as e:
            status = "[NOT RESPONDING]"

        print(f"  {status:20s} - {service_name} (port {port})")

if __name__ == "__main__":
    main()
