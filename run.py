#!/usr/bin/env python3
"""
Smart Attendance System - One-Click Launcher
Usage: python3 run.py
"""

import os
import sys
import time
import signal
import socket
import shutil
import subprocess
import webbrowser
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

# Colors for terminal output
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

processes = []

def check_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a specific TCP port is currently in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex((host, port)) == 0

def free_port(port: int, host: str = "127.0.0.1") -> bool:
    """Terminate any stale process holding the port to allow a clean start."""
    if not check_port_in_use(port, host):
        return True
    
    print(f"{YELLOW}[WARN] Port {port} is occupied by an existing process. Freeing port...{RESET}")
    if sys.platform != "win32":
        try:
            res = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
            pids = [int(p) for p in res.stdout.strip().split() if p.isdigit()]
            for pid in pids:
                if pid != os.getpid():
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except OSError:
                        pass
            time.sleep(0.8)
        except Exception as e:
            print(f"{YELLOW}[WARN] Could not automatically kill process on port {port}: {e}{RESET}")
    else:
        try:
            res = subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True, text=True)
            for line in res.stdout.strip().splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and parts[1].endswith(f":{port}"):
                    pid = parts[-1]
                    if pid.isdigit() and int(pid) != os.getpid():
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
            time.sleep(0.8)
        except Exception as e:
            print(f"{YELLOW}[WARN] Could not automatically kill process on port {port}: {e}{RESET}")

    if check_port_in_use(port, host):
        print(f"{RED}[ERROR] Port {port} could not be freed. Please close conflicting apps manually.{RESET}")
        return False
    else:
        print(f"{GREEN}✓ Port {port} is now free.{RESET}")
        return True

def find_python_executable():
    """Detect the appropriate Python executable with uvicorn available."""
    is_win = sys.platform == "win32"
    bin_name = "Scripts" if is_win else "bin"
    exe_name = "python.exe" if is_win else "python"

    # Candidate virtual environment locations (in priority order)
    candidate_envs = []
    
    # Active virtual environment
    if os.environ.get("VIRTUAL_ENV"):
        candidate_envs.append(Path(os.environ["VIRTUAL_ENV"]))

    # Standard workspace locations
    candidate_envs.extend([
        BACKEND_DIR / "venv",
        ROOT_DIR / ".venv",
        BACKEND_DIR / ".venv",
        ROOT_DIR / "venv",
    ])

    for env_path in candidate_envs:
        py_exe = env_path / bin_name / exe_name
        if py_exe.is_file():
            return str(py_exe)

    # Fallback: Check if current python has uvicorn installed
    try:
        res = subprocess.run([sys.executable, "-m", "uvicorn", "--version"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return sys.executable
    except Exception:
        pass

    # System uvicorn fallback
    uvicorn_in_path = shutil.which("uvicorn")
    if uvicorn_in_path:
        return uvicorn_in_path

    return None

def cleanup(sig=None, frame=None):
    """Gracefully terminate all background services and their child processes."""
    print(f"\n{YELLOW}Stopping services...{RESET}")
    for p in processes:
        if p.poll() is None:
            try:
                if sys.platform != "win32":
                    # Send SIGTERM to the entire process group
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                else:
                    p.terminate()
            except Exception:
                pass

    time.sleep(1)

    for p in processes:
        if p.poll() is None:
            try:
                if sys.platform != "win32":
                    os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                else:
                    p.kill()
            except Exception:
                pass

    print(f"{GREEN}All services stopped cleanly.{RESET}\n")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print(f"""
{CYAN}{BOLD}===========================================================
  🎓 Smart Attendance System - Single Command Launcher
==========================================================={RESET}
""")

    # 1. Verify and Find Python Environment
    python_cmd = find_python_executable()
    if not python_cmd:
        print(f"{RED}[ERROR] Python virtual environment with uvicorn not found!{RESET}")
        print("Please setup the backend virtual environment first:")
        print("  cd backend")
        print("  python3 -m venv venv")
        print("  source venv/bin/activate  # or venv\\Scripts\\activate on Windows")
        print("  pip install -r requirements.txt\n")
        sys.exit(1)

    # 2. Check and Free Ports
    if not free_port(8000):
        sys.exit(1)
    free_port(5173)

    # 3. Check Frontend node_modules
    node_modules_dir = FRONTEND_DIR / "node_modules"
    if not node_modules_dir.exists():
        print(f"{YELLOW}[INFO] frontend/node_modules not found. Installing npm dependencies...{RESET}")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        try:
            subprocess.run([npm_cmd, "install"], cwd=str(FRONTEND_DIR), check=True)
            print(f"{GREEN}✓ Frontend dependencies installed.{RESET}")
        except Exception as e:
            print(f"{RED}[ERROR] Failed to run 'npm install': {e}{RESET}")
            print("Please run 'npm install' inside the 'frontend' folder manually.\n")

    # 4. Start Backend
    print(f"{YELLOW}[1/2] Starting Backend (FastAPI)...{RESET}")
    if python_cmd.endswith("uvicorn") or python_cmd.endswith("uvicorn.exe"):
        backend_args = [python_cmd, "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    else:
        backend_args = [python_cmd, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]

    is_posix = sys.platform != "win32"
    backend_proc = subprocess.Popen(
        backend_args,
        cwd=str(BACKEND_DIR),
        env=os.environ.copy(),
        start_new_session=is_posix
    )
    backend_proc._name = "Backend (FastAPI)"
    processes.append(backend_proc)

    time.sleep(1.5)
    if backend_proc.poll() is not None:
        print(f"{RED}[ERROR] Backend failed to start (exit code {backend_proc.returncode}).{RESET}")
        cleanup()
        sys.exit(1)

    # 5. Start Frontend
    print(f"{YELLOW}[2/2] Starting Frontend (React/Vite)...{RESET}")
    npm_bin = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_args = [npm_bin, "run", "dev"]
    frontend_proc = subprocess.Popen(
        frontend_args,
        cwd=str(FRONTEND_DIR),
        env=os.environ.copy(),
        start_new_session=is_posix,
        shell=(sys.platform == "win32")
    )
    frontend_proc._name = "Frontend (React/Vite)"
    processes.append(frontend_proc)

    time.sleep(2)
    if frontend_proc.poll() is not None:
        print(f"{RED}[ERROR] Frontend failed to start (exit code {frontend_proc.returncode}).{RESET}")
        cleanup()
        sys.exit(1)

    print(f"""
{GREEN}{BOLD}===========================================================
  🚀 Both Services Are Running!
===========================================================
  🌐 Frontend:  http://127.0.0.1:5173
  ⚙️  Backend:   http://127.0.0.1:8000
  📚 API Docs:  http://127.0.0.1:8000/api/v1/docs

  🔑 Default Logins:
     • Admin:   admin / Admin@123
     • Faculty: dr.sharma / Faculty@123
-----------------------------------------------------------
  (Press Ctrl + C to stop all services)
==========================================================={RESET}
""")

    # Open browser automatically
    try:
        webbrowser.open("http://127.0.0.1:5173")
    except Exception:
        pass

    # Keep script running while child processes are alive
    try:
        while True:
            time.sleep(1)
            for p in processes:
                code = p.poll()
                if code is not None:
                    name = getattr(p, "_name", "A service")
                    if code != 0:
                        print(f"\n{RED}[WARN] {name} exited with code {code}.{RESET}")
                    cleanup()
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
