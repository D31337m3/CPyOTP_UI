"""
Boot script for TOTP Authenticator
Handles WiFi connection and service startup
"""
import wifi
import socketpool
import time
import board
import digitalio
import os

# Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
WEB_SERVER_PORT = 80
ENABLE_WEB_SERVER = True

def connect_wifi():
    """Connect to WiFi network"""
    print("Connecting to WiFi...")
    
    try:
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        print(f"Connected to WiFi: {wifi.radio.ipv4_address}")
        return True
    except Exception as e:
        print(f"WiFi connection failed: {e}")
        return False

def check_boot_mode():
    """Check if we should start in configuration mode"""
    # Check for configuration mode (e.g., button press during boot)
    try:
        # Assuming a button on pin IO0 (common boot button)
        if hasattr(board, 'IO0'):
            button = digitalio.DigitalInOut(board.IO0)
            button.direction = digitalio.Direction.INPUT
            button.pull = digitalio.Pull.UP
            
            if not button.value:  # Button pressed (active low)
                print("Boot button pressed - starting configuration mode")
                return "config"
    except:
        pass
    
    # Check if configuration exists
    if "/totp_config.json" not in os.listdir("/"):
        print("No configuration found - starting configuration mode")
        return "config"
    
    return "normal"

def main():
    """Main boot function"""
    print("TOTP Authenticator Boot")
    print("=" * 30)
    
    boot_mode = check_boot_mode()
    
    if boot_mode == "config":
        print("Starting in configuration mode...")
        
        if connect_wifi() and ENABLE_WEB_SERVER:
            print(f"Web interface available at: http://{wifi.radio.ipv4_address}")
            print("Configure your TOTP accounts via web browser")
            
            # Start web server for configuration
            from web_server import TOTPWebServer
            server = TOTPWebServer(WEB_SERVER_PORT)
            
            # Also start console interface in parallel
            print("Console interface also available via REPL")
            print("Import totp_console and run TOTPConsole().run()")
            
            # Run web server (blocking)
            server.run()
        else:
            print("WiFi not available - use console interface")
            print("Connect via REPL and run:")
            print(">>> from totp_console import TOTPConsole")
            print(">>> TOTPConsole().run()")
    
    else:
        print("Starting TOTP Authenticator...")
        
        # Optional: Connect to WiFi for time sync
        if WIFI_SSID and WIFI_PASSWORD:
            connect_wifi()
        
        # Start main TOTP application
        from totp_authenticator import TOTPAuthenticator
        app = TOTPAuthenticator()
        app.run()

if __name__ == "__main__":
    main()
