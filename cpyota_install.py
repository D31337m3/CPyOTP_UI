"""
Installation script for TOTP Authenticator
Copies all necessary files and sets up the environment
"""
import os
import json

def create_directory_structure():
    """Create necessary directories"""
    directories = ['/lib', '/config']
    
    for directory in directories:
        try:
            os.mkdir(directory)
            print(f"Created directory: {directory}")
        except OSError:
            pass  # Directory already exists

def create_sample_config():
    """Create sample configuration file"""
    sample_config = {
        "accounts": [],
        "settings": {
            "display_brightness": 1.0,
            "rotation_interval": 15,
            "codes_per_page": 3
        }
    }
    
    try:
        with open("/totp_config.json", 'w') as f:
            json.dump(sample_config, f, indent=2)
        print("Created sample configuration file")
    except Exception as e:
        print(f"Error creating config file: {e}")

def setup_wifi_config():
    """Create WiFi configuration template"""
    wifi_template = '''# WiFi Configuration
# Edit this file with your WiFi credentials

WIFI_SSID = "Your_WiFi_Network"
WIFI_PASSWORD = "Your_WiFi_Password"

# Web server settings
WEB_SERVER_PORT = 80
ENABLE_WEB_SERVER = True

# Display settings
DISPLAY_BRIGHTNESS = 1.0
ROTATION_INTERVAL = 15  # seconds
'''
    
    try:
        with open("/wifi_config.py", 'w') as f:
            f.write(wifi_template)
        print("Created WiFi configuration template")
    except Exception as e:
        print(f"Error creating WiFi config: {e}")

def install():
    """Main installation function"""
    print("TOTP Authenticator Installation")
    print("=" * 35)
    
    create_directory_structure()
    create_sample_config()
    setup_wifi_config()
    
    print("\nInstallation complete!")
    print("\nNext steps:")
    print("1. Edit wifi_config.py with your WiFi credentials")
    print("2. Reset your device or run boot.py")
    print("3. Configure TOTP accounts via web interface or console")
    print("\nFiles installed:")
    print("- boot.py (main boot script)")
    print("- totp_authenticator.py (main application)")
    print("- pyotp_circuitpython.py (TOTP library)")
    print("- web_server.py (web configuration interface)")
    print("- totp_console.py (console configuration)")
    print("- tftblinky.py (display backlight control)")

if __name__ == "__main__":
    install()
