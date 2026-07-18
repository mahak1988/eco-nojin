# W�2 ️ DEPRECATED: This launcher is legacy. Use "python apps/main.py" directly.
# See docs/DEPLOYMENT.md for production deployment.
# This file will be removed in a future release.
#
#!/usr/bin/env python3
"""
🚀 Econojin Smart Launcher v2.0
Fixed frontend startup issue + improved monitoring
"""
import subprocess
import sys
import time
import signal
import os
import json
from pathlib import Path
from datetime import datetime
import threading

# ==============================================================================
# Configuration
# ==============================================================================
ROOT = Path(__file__).parent.resolve()
CONFIG_FILE = ROOT / "econojin_config.json"

DEFAULT_CONFIG = {
    "backend": {
        "command": "uvicorn apps.main:app --reload --port 8000",
        "directory": str(ROOT),
        "port": 8000,
        "health_url": "http://localhost:8000/api/v1/health",
        "color": "emerald"
    },
    "frontend": {
        "command": "npx next dev -p 3001",
        "directory": str(ROOT / "apps" / "web"),
        "port": 3001,
        "health_url": "http://localhost:3001",
        "color": "blue"
    },
    "settings": {
        "auto_restart": True,
        "max_restarts": 3,
        "health_check_interval": 30,
        "log_to_file": False
    }
}

# ==============================================================================
# Color Output
# ==============================================================================
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    @staticmethod
    def get_color(name):
        colors = {
            "emerald": Colors.GREEN,
            "blue": Colors.BLUE,
            "red": Colors.RED,
            "yellow": Colors.YELLOW,
            "magenta": Colors.MAGENTA,
            "cyan": Colors.CYAN
        }
        return colors.get(name, Colors.RESET)

def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔════════════════════════════════════════════════════════════════╗
║                                                                                  ║
║   🌿 QDEPRECATED - Use `python apps/main.py` directly  🌿                  ║
║                                                                                   ║
║   Econojin Smart Launcher v2.0                                           ║
║                                                                                   ║
╚════════════════════════════════════════════════════════════════╝
{Colors.RESET}
"""
    print(banner)

def print_status(service: str, message: str, color: str = "cyan"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    color_code = Colors.get_color(color)
    print(f"{color_code}[{timestamp}] [{service}]{Colors.RESET} {message}")

# ==============================================================================
# Process Manager
# ==============================================================================
class ProcessManager:
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self.process = None
        self.is_running = False
        self.output_thread = None
        self.restart_count = 0
        self.max_restarts = config.get('max_restarts', 3)

    def start(self):
        """Start the process"""
        try:
            print_status(self.name, f"🛀 Starting: {self.config['command']}", self.config['color'])
            print_status(self.name, f"📁 Directory: {self.config['directory']}", "cyan")

            # Use cmd /c for Windows to properly handle arguments
            if os.name == 'nt':
                cmd = f'cmd /c "{self.config["command"]}"'
            else:
                cmd = self.config['command']

            self.process = subprocess.Popen(
                cmd,
                cwd=self.config['directory'],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )

            self.is_running = True
            self.restart_count = 0

            # Start output reader thread
            self.output_thread = threading.Thread(
                target=self._read_output,
                daemon=True
            )
            self.output_thread.start()

            print_status(self.name, f"✅ Started (PID: {self.process.pid})", "green")
            return True

        except Exception as e:
            print_status(self.name, f"❌ Failed to start: {e}", "red")
            return False

    def _read_output(self):
        """Read and display process output with color coding"""
        color_code = Colors.get_color(self.config['color'])
        try:
            for line in iter(self.process.stdout.readline, ''):
                if not line:
                    break
                line = line.rstrip()
                if not line:
                    continue

                # Colorize based on content
                if any(x in line.lower() for x in ["error", "exception", "failed", "❌"]):
                    print(f"{color_code}[{self.name}]{Colors.RED} {line}{Colors.RESET}")
                elif any(x in line.lower() for x in ["warning", "warn", "⚠️"]):
                    print(f"{color_code}[{self.name}]{Colors.YELLOW} {line}{Colors.RESET}")
                elif any(x in line.lower() for x in ["ready", "compiled", "started", "✅", "running"]):
                    print(f"{color_code}[{self.name}]{Colors.GREEN} {line}{Colors.RESET}")
                elif "GET" in line or "POST" in line:
                    print(f"{color_code}[{self.name}]{Colors.DIM} {line}{Colors.RESET}")
                else:
                    print(f"{color_code}[{self.name}]{Colors.RESET} {line}")
        except Exception as e:
            pass
        finally:
            self.is_running = False

    def stop(self):
        """Stop the process"""
        if self.process and self.is_running:
            print_status(self.name, "🛑 Stopping...", "yellow")
            try:
                # Try graceful termination first
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print_status(self.name, "⚠️  Force killing...", "yellow")
                    self.process.kill()
                    self.process.wait(timeout=2)

                self.is_running = False
                print_status(self.name, "✅ Stopped", "green")
            except Exception as e:
                print_status(self.name, f"⚠️  Stop error: {e}", "yellow")
                self.is_running = False

    def restart(self):
        """Restart the process"""
        print_status(self.name, "🔄 Restarting...", "yellow")
        self.stop()
        time.sleep(2)
        return self.start()

    def check_health(self):
        """Check if process is healthy"""
        if not self.process:
            return False

        if self.process.poll() is not None:
            self.is_running = False
            return False

        return True

    def get_pid(self):
        """Get process PID"""
        return self.process.pid if self.process else None

# ==============================================================================
# Main Launcher
# ==============================================================================
class EconojinLauncher:
    def __init__(self):
        self.config = self._load_config()
        self.backend = ProcessManager("Backend", self.config['backend'])
        self.frontend = ProcessManager("Frontend", self.config['frontend'])
        self.running = False

    def _load_config(self):
        """Load configuration from file or create default"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # Migrate old config if needed
                if "frontend" in config and "pnpm run dev -- -p" in config["frontend"].get("command", ""):
                    print_status("Config", "🔄 Migrating frontend command...", "yellow")
                    config["frontend"]["command"] = "npx next dev -p 3001"
                    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                    print_status("Config", "✅ Config migrated", "green")

                print_status("Config", "✅ Loaded from econojin_config.json", "green")
                return config
            except Exception as e:
                print_status("Config", f"⚠️  Error loading: {e}", "yellow")

        # Create default config
        print_status("Config", "📝 Creating default config...", "cyan")
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        print_status("Config", "✅ Created econojin_config.json", "green")
        return DEFAULT_CONFIG

    def start_all(self):
        """Start all services"""
        print_status("Launcher", "🛈 Starting all services...", "cyan")

        # Start backend first
        if not self.backend.start():
            print_status("Launcher", "❌ Backend failed to start", "red")
            return False

        # Wait for backend to be ready
        print_status("Launcher", "⏳ Waiting for backend to initialize...", "cyan")
        time.sleep(5)

        # Start frontend
        if not self.frontend.start():
            print_status("Launcher", "❌ Frontend failed to start", "red")
            self.backend.stop()
            return False

        self.running = True
        return True

    def stop_all(self):
        """Stop all services"""
        print_status("Launcher", "🛛 Stopping all services...", "cyan")
        self.frontend.stop()
        self.backend.stop()
        self.running = False

    def restart_all(self):
        """Restart all services"""
        print_status("Launcher", "🔄 Restarting all services...", "cyan")
        self.stop_all()
        time.sleep(2)
        self.start_all()

    def show_status(self):
        """Show status of all services"""
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}📊 Service Status{Colors.RESET}")
        print("=" * 70)

        backend_healthy = self.backend.check_health()
        frontend_healthy = self.frontend.check_health()

        backend_status = f"🟢 Running (PID: {self.backend.get_pid()})" if backend_healthy else "🔴 Stopped"
        frontend_status = f"🟢 Running (PID: {self.frontend.get_pid()})" if frontend_healthy else "🔴 Stopped"

        print(f"\n  Backend:  {backend_status}")
        print(f"            Port: {self.config['backend']['port']}")
        print(f"            URL:  {Colors.GREEN}http://localhost:{self.config['backend']['port']}{Colors.RESET}")
        print(f"            API:  {Colors.GREEN}http://localhost:{self.config['backend']['port']}/api/v1/health{Colors.RESET}")

        print(f"\n  Frontend: {frontend_status}")
        print(f"            Port: {self.config['frontend']['port']}")
        print(f"            URL:  {Colors.BLUE}http://localhost:{self.config['frontend']['port']}{Colors.RESET}")

        print("\n" + "=" * 70 + "\n")

    def open_urls(self):
        """Open URLs in browser"""
        import webbrowser
        print_status("Launcher", "🌐 Opening URLs in browser...", "cyan")
        time.sleep(1)
        webbrowser.open(f"http://localhost:{self.config['backend']['port']}/docs")
        time.sleep(1)
        webbrowser.open(f"http://localhost:{self.config['frontend']['port']}")

    def show_help(self):
        """Show available commands"""
        print(f"""
{Colors.BOLD}📋Available Commands:{Colors.RESET}

  {Colors.GREEN}status{Colors.RESET}      - Show status of all services
  {Colors.GREEN}restart{Colors.RESET}     - Restart all services
  {Colors.GREEN}backend{Colors.RESET}     - Restart backend only
  {Colors.GREEN}frontend{Colors.RESET}    - Restart frontend only
  {Colors.GREEN}open{Colors.RESET}        - Open URLs in browser
  {Colors.GREEN}logs{Colors.RESET}        - Show recent logs
  {Colors.GREEN}stop{Colors.RESET}        - Stop all services and exit
  {Colors.GREEN}help{Colors.RESET}        - Show this help message
  {Colors.GREEN}quit{Colors.RESET}        - Stop all services and exit

{Colors.BOLD}Shortcuts:{Colors.RESET}
  {Colors.YELLOW}s{Colors.RESET} = status  |  {Colors.YELLOW}r{Colors.RESET} = restart  |  {Colors.YELLOW}b{Colors.RESET} = backend  |  {Colors.YELLOW}f{Colors.RESET} = frontend
  {Colors.YELLOW}o{Colors.RESET} = open    |  {Colors.YELLOW}q{Colors.RESET} = quit

{Colors.BOLD}Press Ctrl+C to stop all services{Colors.RESET}
""")

    def run(self):
        """Main run loop"""
        print_banner()

        # Start all services
        if not self.start_all():
            print_status("Launcher", "❌ Failed to start services", "red")
            input("Press Enter to exit...")
            return 1

        # Show initial status
        time.sleep(3)
        self.show_status()
        self.show_help()

        # Setup signal handler
        def signal_handler(sig, frame):
            print_status("Launcher", "\n🛑 Shutdown signal received...", "yellow")
            self.stop_all()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # Command loop
        try:
            while self.running:
                try:
                    command = input(f"\n{Colors.CYAN}{Colors.BOLD}econojin>{Colors.RESET} ").strip().lower()

                    if command in ["status", "s"]:
                        self.show_status()
                    elif command in ["restart", "r"]:
                        self.restart_all()
                    elif command in ["backend", "b"]:
                        self.backend.restart()
                    elif command in ["frontend", "f"]:
                        self.frontend.restart()
                    elif command in ["open", "o"]:
                        self.open_urls()
                    elif command in ["logs", "l"]:
                        print_status("Launcher", "📜 Logs are displayed above in real-time", "cyan")
                    elif command in ["stop", "quit", "exit", "q"]:
                        break
                    elif command == "":
                        continue
                    else:
                        print_status("Launcher", f"❓ Unknown command: {command}", "yellow")
                        print("   Type 'help' for available commands")

                except KeyboardInterrupt:
                    break
                except EOFError:
                    break

        finally:
            self.stop_all()
            print_status("Launcher", "👋 Goodbye!🌿", "cyan")

        return 0

# ==============================================================================
# Entry Point
# ==============================================================================
if __name__ == "__main__:
    launcher = EconojinLauncher()
    sys.exit(launcher.run())