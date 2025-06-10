# CPy TOTP Authenticator User front END  (CpyOTP_UI)

A comprehensive TOTP (Time-based One-Time Password) authenticator system for ESP32-S3 microcontrollers with display support. This project provides a secure, offline 2FA solution with both display interface and web-based management.

## Overview

This TOTP authenticator displays up to 3 authentication codes simultaneously with automatic page rotation for multiple accounts. It features a clean display interface, web-based account management, and secure local storage of TOTP secrets.

## Core Components

### CPyOTP Library Integration

This project relies on the **[CPyOTP library](https://github.com/d31337m3/cpyotp)** as its foundation for TOTP functionality:

- **Role**: CPyOTP provides the core TOTP/HOTP implementation optimized for CircuitPython
- **Functionality**: 
  - RFC 6238 compliant TOTP generation
  - HMAC-SHA1 cryptographic operations
  - Base32 secret key handling
  - Customizable time intervals and code lengths
- **Integration**: The main authenticator imports and utilizes CPyOTP's `TOTP` class and utilities
- **Why CPyOTP**: Specifically designed for microcontroller constraints with efficient memory usage and CircuitPython compatibility

### CPYOTP_UI Files

The **CPYOTP_UI** components provide the user interface layer:

#### Main Display Interface ('cpyotp_main.py')
- **Primary Role**: Main application controller and display manager
- **Features**:
  - Multi-account TOTP code display (1-3 codes per page)
  - Automatic page rotation for accounts beyond display capacity
  - Real-time code updates with expiration timers
  - Responsive layout adaptation based on account count
  - Visual feedback with LED blinking on code refresh

#### Web Management Interface
- **Role**: Browser-based account configuration and management
- **Features**:
  - Add/remove TOTP accounts via web form
  - QR code scanning support for easy account setup
  - Secure secret key input and validation
  - Account customization (colors, names, issuers)
  - Real-time preview of generated codes

#### Configuration Management
- **Role**: Secure storage and retrieval of TOTP account data
- **Features**:
  - JSON-based configuration with encryption support
  - Automatic backup and recovery mechanisms
  - Temporary file handling for web interface updates
  - Default configuration generation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CPYOTP_UI Layer                          │
├─────────────────────────────────────────────────────────────┤
│  Display Interface  │  Web Interface  │  Config Manager     │
│  - Code Display     │  - Account Mgmt │  - JSON Storage     │
│  - Page Rotation    │  - QR Scanning  │  - Security         │
│  - Visual Feedback  │  - Validation   │  - Backup/Recovery  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     CPyOTP Library                          │
├─────────────────────────────────────────────────────────────┤
│  - TOTP/HOTP Generation    │  - HMAC-SHA1 Crypto           │
│  - RFC 6238 Compliance     │  - Base32 Encoding/Decoding   │
│  - Time Synchronization    │  - Memory Optimization        │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### Display Capabilities
- **Adaptive Layout**: Automatically adjusts display layout based on number of accounts (1-3 per page)
- **Large Text Mode**: Single account displays with large, easy-to-read codes
- **Compact Mode**: Three accounts with essential information and countdown timers
- **Page Rotation**: Automatic cycling through multiple pages of accounts
- **Visual Indicators**: Page numbers, expiration timers, and status feedback

### Security Features
- **Offline Operation**: No internet connection required after initial setup
- **Local Storage**: TOTP secrets stored securely on device
- **Temporary File Cleanup**: Automatic deletion of sensitive temporary files
- **Memory Protection**: Efficient memory usage to prevent data leakage

### Management Features
- **Web Interface**: Easy account management through built-in web server
- **QR Code Support**: Direct import from authenticator QR codes
- **Bulk Operations**: Add/remove multiple accounts efficiently
- **Configuration Backup**: JSON-based configuration with backup support

## Hardware Requirements

- ESP32-S3 microcontroller
- TFT display (compatible with CircuitPython displayio)
- Optional: LED for visual feedback
- MicroSD card (recommended for configuration backup)

## Dependencies

- **CPyOTP**: Core TOTP functionality
- **CircuitPython**: Base runtime environment
- **displayio**: Display management
- **adafruit_display_text**: Text rendering
- **adafruit_display_shapes**: UI elements

## Usage

1. **Initial Setup**: Flash CircuitPython and copy all files to the device
2. **Configuration**: Use web interface or console to add TOTP accounts
3. **Operation**: Device automatically displays rotating TOTP codes
4. **Management**: Access web interface for account modifications

## Security Considerations

- Store device in secure location when not in use
- Regularly backup configuration to secure storage
- Use strong, unique secrets for each account
- Monitor for unauthorized access attempts via web interface

## Contributing

This project builds upon the excellent work of the CPyOTP library. Contributions should maintain compatibility with the CPyOTP API and follow CircuitPython best practices.
## Installation

### Prerequisites
- ESP32-S3 board with CircuitPython 8.0+ installed
- TFT display connected via SPI
- Computer with USB connection to ESP32-S3

### Step-by-Step Installation

1. **Install CircuitPython Libraries**
   ```bash
   # Download required libraries to /lib folder on CIRCUITPY drive
   ```
   Required libraries:
   - `adafruit_display_text`   -Only needed if hardware supports display output
   - `adafruit_display_shapes` -If not found CpyOTP_UI will just forward app launch to Console version.
   - `adafruit_requests` (for web interface)
   - `adafruit_connection_manager`

2. **Install CPyOTP Library**
   ```bash
   # Clone CPyOTP repository
   git clone https://github.com/d31337m3/cpyotp.git
   ```
   or Copy cpyotp.py` from CPyOTP to your CircuitPython device's root directory.

3. **Deploy CPYOTP_UI Files**
   Copy all CPYOTP_UI files to your CircuitPython device "/" or "/lib" directory:
   -/cpyotp_main.py        - Main authenticator app , run this fie to start manually.
   -/cpyotp_serv.py        - Web interface server
   -/cpyotp_install.py        - Simple installer for creating required directory structure etc (mostly for future use with next release)
   -/cpyotp_console.py     - Console Interface for Usage and Configuration directly from the REPL prompt etc, no display needed to run this program.

4. **Hardware Setup**
   Connect your TFT display according to your board's pinout configuration.

## Configuration

### Adding Accounts via Web Interface

1. **Connect to Device WiFi**
   - Device creates AP: `TOTP-Authenticator`
   - Connect with password: `totp2024`

2. **Access Web Interface**
   - Open browser to: `http://192.168.4.1`
   - Navigate to "Add Account" section

3. **Add Account Methods**:
   
   **Method 1: QR Code Scanning**
   - Use phone camera to scan service's QR code
   - Copy the `otpauth://` URL
   - Paste into web interface

   **Method 2: Manual Entry**
   - Service Name: `Google`
   - Account: `user@gmail.com`
   - Secret Key: `JBSWY3DPEHPK3PXP` (from service)
   - Digits: `6` (usually 6)
   - Period: `30` (seconds)

### Adding Accounts via Console

```python
# Connect to CircuitPython REPL
import json

# Load existing config
with open('/totp_config.json', 'r') as f:
    config = json.load(f)

# Add new account
new_account = {
    "name": "GitHub",
    "issuer": "GitHub",
    "secret": "YOUR_SECRET_KEY_HERE",
    "digits": 6,
    "period": 30,
    "color": 0x00FF00
}

config['accounts'].append(new_account)

# Save updated config
with open('/totp_config.json', 'w') as f:
    json.dump(config, f)
```

### Configuration File Format

```json
{
  "accounts": [
    {
      "name": "Google Account",
      "issuer": "Google",
      "secret": "JBSWY3DPEHPK3PXP",
      "digits": 6,
      "period": 30,
      "color": 16711680
    },
    {
      "name": "GitHub",
      "issuer": "GitHub", 
      "secret": "ANOTHER_SECRET_KEY",
      "digits": 6,
      "period": 30,
      "color": 65280
    }
  ],
  "settings": {
    "page_rotation_interval": 15,
    "display_brightness": 80,
    "wifi_enabled": true
  }
}
```

## Display Modes

### Single Account Mode
- **Layout**: Large text display
- **Features**: 
  - 3x scaled TOTP code
  - Full service name display
  - Large countdown timer
  - Maximum readability

### Dual Account Mode  
- **Layout**: Two accounts vertically stacked
- **Features**:
  - 2x scaled TOTP codes
  - Service names truncated to 20 chars
  - Visual separators between accounts

### Triple Account Mode
- **Layout**: Three accounts in compact view
- **Features**:
  - Standard size TOTP codes
  - Service names truncated to 18 chars
  - Small countdown timers on right
  - Horizontal separators

### Page Rotation
- **Automatic**: Pages rotate every 15 seconds (configurable)
- **Manual**: Press button to advance pages (if hardware button connected)
- **Indicator**: Page numbers shown in top-right corner

## API Reference

### TOTPAuthenticator Class

```python
class TOTPAuthenticator:
    def __init__(self):
        """Initialize authenticator with display and configuration"""
        
    def load_config(self):
        """Load TOTP accounts from JSON configuration"""
        
    def add_account(self, name, issuer, secret, digits=6, period=30, color=0xFFFFFF):
        """Add new TOTP account"""
        
    def remove_account(self, name):
        """Remove TOTP account by name"""
        
    def update_display(self):
        """Refresh display with current codes"""
        
    def run(self):
        """Main application loop"""
```

### CPyOTP Integration

```python
from cpyotp import TOTP, random_base32

# Create TOTP instance
totp = TOTP(
    secret="JBSWY3DPEHPK3PXP",
    name="My Account",
    issuer="Service Provider",
    digits=6,
    interval=30
)

# Generate current code
current_code = totp.now()

# Generate code for specific time
code_at_time = totp.at(timestamp)

# Verify code
is_valid = totp.verify(user_code)
```

## Troubleshooting

### Common Issues

**Display Not Working**
- Check SPI connections
- Verify display driver compatibility
- Ensure sufficient power supply

**No Accounts Showing**
- Check `/totp_config.json` exists
- Verify JSON syntax is valid
- Check secret key format (Base32)

**Incorrect Codes**
- Verify device time is accurate
- Check secret key matches service
- Confirm digits and period settings

**Web Interface Not Accessible**
- Check WiFi connection
- Verify IP address (usually 192.168.4.1)
- Ensure web server is running

### Debug Mode

Enable debug output by modifying the main script:

```python
# Add at top of file
DEBUG = True

def debug_print(message):
    if DEBUG:
        print(f"[DEBUG] {message}")
```

### Log Files

Check CircuitPython console output for error messages:
- Connection issues
- Configuration errors  
- Display problems
- TOTP generation errors

## Performance Optimization

### Memory Management
- Limit number of accounts (recommended: 12 max)
- Use shorter account names when possible
- Regular garbage collection in main loop

### Display Optimization
- Reduce update frequency for battery operation
- Use monospace fonts for consistent layout
- Minimize color changes to reduce flicker

### Power Saving
- Implement sleep mode between updates.
- Reduce display brightness. 
- Disable WiFi when not needed - wifi is only needed breifly during boot to sync rtc, and for WebUI Config.

## Security Best Practices

### Device Security
- Change default WiFi password
- Disable web interface when not needed
- Use secure physical storage
- Regular firmware updates

### Account Management
- Use unique secrets for each service
- Regularly audit configured accounts
- Remove unused accounts promptly
- Backup configuration securely

### Network Security
- Use device on trusted networks only (partly why no WiFi configuration ui is provided, Wifi is setup manually prior to install via settings.toml)
- Monitor for unauthorized access
- Consider VPN for remote management
- Disable unnecessary network services

## Contributing

### Development Setup
1. Fork the repository
2. Set up CircuitPython development environment
3. Install CPyOTP library
4. Create feature branch
5. Test on actual hardware
6. Submit pull request

### Code Standards
- Follow CircuitPython conventions
- Maintain CPyOTP API compatibility
- Include comprehensive error handling
- Add documentation for new features
- Test with multiple account configurations

### Testing
- Test with various account counts (1-12)
- Verify display layouts on different screen sizes
- Test web interface on multiple browsers
- Validate TOTP code accuracy against reference implementations

## License

This project builds upon CPyOTP library. Please refer to individual component licenses:
- CPyOTP: [License](https://github.com/d31337m3/cpyotp/blob/main/LICENSE)
- CPYOTP_UI: [Your License Here]
- CircuitPython Libraries: MIT License

## Acknowledgments

- **CPyOTP Library**: Core TOTP implementation by d31337m3
- **Adafruit**: CircuitPython libraries and hardware support
- **CircuitPython Community**: Documentation and examples
- **RFC 6238**: TOTP standard specification

## Support

For issues related to:
- **CPyOTP Library**: Report to [CPyOTP GitHub](https://github.com/d31337m3/cpyotp/issues)
- **CPYOTP_UI**: Report to this project's issue tracker
- **CircuitPython**: Check [CircuitPython Documentation](https://docs.circuitpython.org/)

## Changelog

### v1.0.0
- Initial release with CPyOTP integration
- Multi-account display support
- Web interface for account management
- Automatic page rotation
- Configurable display layouts

======================================================================================================

## Advanced Configuration

### Custom Display Themes

Create custom color schemes by modifying the configuration:

```json
{
  "themes": {
    "dark": {
      "background": 0x000000,
      "text": 0xFFFFFF,
      "accent": 0x00FF00,
      "separator": 0x444444
    },
    "light": {
      "background": 0xFFFFFF,
      "text": 0x000000,
      "accent": 0x0066CC,
      "separator": 0xCCCCCC
    },
    "cyberpunk": {
      "background": 0x0D1117,
      "text": 0x00FF41,
      "accent": 0xFF0080,
      "separator": 0x30363D
    }
  },
  "active_theme": "dark"
}
```

### Time Zone Configuration

For accurate TOTP generation across time zones:

```python
# In configuration file
{
  "timezone": {
    "offset_hours": -5,  # EST offset from UTC
    "dst_enabled": true,
    "dst_start": "2024-03-10",
    "dst_end": "2024-11-03"
  }
}
```

### Hardware Button Integration

Add physical buttons for navigation:

```python
import digitalio

class TOTPAuthenticator:
    def __init__(self):
        # ... existing code ...
        
        # Setup buttons
        self.next_button = digitalio.DigitalInOut(board.GP15)
        self.next_button.direction = digitalio.Direction.INPUT
        self.next_button.pull = digitalio.Pull.UP
        
        self.select_button = digitalio.DigitalInOut(board.GP14)
        self.select_button.direction = digitalio.Direction.INPUT
        self.select_button.pull = digitalio.Pull.UP
    
    def check_buttons(self):
        """Handle button presses"""
        if not self.next_button.value:  # Button pressed (active low)
            self.next_page()
            time.sleep(0.3)  # Debounce
```

### Network Configuration

#### WiFi Station Mode
Connect to existing WiFi network:

```python
import wifi
import socketpool

# Connect to WiFi
wifi.radio.connect("YOUR_SSID", "YOUR_PASSWORD")
print(f"Connected to WiFi: {wifi.radio.ipv4_address}")

# Enable NTP time synchronization
import rtc
import adafruit_ntp

pool = socketpool.SocketPool(wifi.radio)
ntp = adafruit_ntp.NTP(pool, tz_offset=0)
rtc.RTC().datetime = ntp.datetime
```

#### Access Point Mode
Create standalone WiFi network:

```python
import wifi

# Create access point
wifi.radio.start_ap("TOTP-Device", "secure_password_2024")
print(f"AP created: {wifi.radio.ipv4_address_ap}")
```

### Backup and Restore

#### Automatic Backup
```python
import time
import json

class BackupManager:
    def __init__(self, backup_interval=3600):  # 1 hour
        self.backup_interval = backup_interval
        self.last_backup = 0
    
    def create_backup(self):
        """Create timestamped backup"""
        timestamp = int(time.time())
        backup_filename = f"/backups/totp_backup_{timestamp}.json"
        
        try:
            with open("/totp_config.json", "r") as source:
                config = json.load(source)
            
            with open(backup_filename, "w") as backup:
                json.dump(config, backup)
                
            print(f"Backup created: {backup_filename}")
            
        except Exception as e:
            print(f"Backup failed: {e}")
    
    def restore_backup(self, backup_filename):
        """Restore from backup file"""
        try:
            with open(backup_filename, "r") as backup:
                config = json.load(backup)
            
            with open("/totp_config.json", "w") as target:
                json.dump(config, target)
                
            print(f"Restored from: {backup_filename}")
            return True
            
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
```

#### Manual Export/Import
```bash
# Export configuration (via REPL)
import json
with open('/totp_config.json', 'r') as f:
    config = json.load(f)
print(json.dumps(config, indent=2))

# Import configuration
config_data = '''{"accounts": [...]}'''
import json
config = json.loads(config_data)
with open('/totp_config.json', 'w') as f:
    json.dump(config, f)
```

## Performance Monitoring

### Memory Usage Tracking
```python
import gc

class PerformanceMonitor:
    def __init__(self):
        self.memory_samples = []
    
    def log_memory(self):
        """Log current memory usage"""
        gc.collect()
        free_memory = gc.mem_free()
        allocated_memory = gc.mem_alloc()
        
        self.memory_samples.append({
            'timestamp': time.time(),
            'free': free_memory,
            'allocated': allocated_memory
        })
        
        # Keep only last 100 samples
        if len(self.memory_samples) > 100:
            self.memory_samples.pop(0)
    
    def get_memory_stats(self):
        """Get memory usage statistics"""
        if not self.memory_samples:
            return None
            
        recent = self.memory_samples[-10:]  # Last 10 samples
        avg_free = sum(s['free'] for s in recent) / len(recent)
        avg_allocated = sum(s['allocated'] for s in recent) / len(recent)
        
        return {
            'average_free': avg_free,
            'average_allocated': avg_allocated,
            'total_samples': len(self.memory_samples)
        }
```

### Display Performance
```python
import time

class DisplayMetrics:
    def __init__(self):
        self.frame_times = []
        self.last_frame_time = time.time()
    
    def start_frame(self):
        """Mark start of display update"""
        self.frame_start = time.time()
    
    def end_frame(self):
        """Mark end of display update and calculate metrics"""
        frame_time = time.time() - self.frame_start
        self.frame_times.append(frame_time)
        
        # Keep only last 50 frame times
        if len(self.frame_times) > 50:
            self.frame_times.pop(0)
    
    def get_fps(self):
        """Calculate average FPS"""
        if len(self.frame_times) < 2:
            return 0
            
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0
```

## Integration Examples

### Home Assistant Integration
```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: "TOTP Device Status"
    resource: "http://192.168.1.100/api/status"
    method: GET
    value_template: "{{ value_json.status }}"
    json_attributes:
      - account_count
      - current_page
      - memory_free
      - uptime

automation:
  - alias: "TOTP Device Low Memory Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.totp_device_status
      attribute: memory_free
      below: 10000
    action:
      service: notify.mobile_app
      data:
        message: "TOTP device memory low: {{ state_attr('sensor.totp_device_status', 'memory_free') }} bytes"
```

### MQTT Integration
```python
import adafruit_minimqtt.adafruit_minimqtt as MQTT

class MQTTManager:
    def __init__(self, broker, port=1883):
        self.mqtt_client = MQTT.MQTT(
            broker=broker,
            port=port,
            client_id="totp-authenticator"
        )
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")
        client.subscribe("totp/command")
    
    def on_message(self, client, topic, message):
        """Handle incoming MQTT messages"""
        if topic == "totp/command":
            if message == "next_page":
                self.authenticator.next_page()
            elif message == "refresh":
                self.authenticator.setup_display()
    
    def publish_status(self, status_data):
        """Publish device status"""
        self.mqtt_client.publish("totp/status", json.dumps(status_data))
```

### REST API Endpoints

```python
# Web server endpoints for external integration
@app.route('/api/status', methods=['GET'])
def get_status():
    return {
        'status': 'online',
        'account_count': len(authenticator.accounts),
        'current_page': authenticator.current_page,
        'memory_free': gc.mem_free(),
        'uptime': time.time() - start_time
    }

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Return account list (without secrets)"""
    accounts = []
    for account in authenticator.accounts:
        accounts.append({
            'name': account['name'],
            'issuer': account['issuer'],
            'digits': account['totp'].digits,
            'period': account['totp'].interval
        })
    return {'accounts': accounts}

@app.route('/api/generate/<account_name>', methods=['GET'])
def generate_code(account_name):
    """Generate TOTP code for specific account"""
    for account in authenticator.accounts:
        if account['name'] == account_name:
            return {
                'account': account_name,
                'code': account['totp'].now(),
                'expires_in': 30 - (int(time.time()) % 30)
            }
    return {'error': 'Account not found'}, 404
```

## Deployment Strategies

### Production Deployment
```bash
# 1. Prepare device
# Flash CircuitPython 8.x
# Install required libraries

# 2. Deploy application
cp -r cpyotp_ui/* /Volumes/CIRCUITPY/
cp pyotp_circuitpython.py /Volumes/CIRCUITPY/

# 3. Configure for production
# Disable debug mode
# Set secure WiFi credentials
# Configure backup schedule
```

### Development Environment
```bash
# Setup development environment
git clone https://github.com/your-repo/cpyotp-ui.git
cd cpyotp-ui

# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run tests
python -m pytest tests/

# Deploy to device
./deploy.sh /Volumes/CIRCUITPY
```

### Continuous Integration
```yaml
# .github/workflows/test.yml
name: Test CPYOTP UI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install circuitpython-stubs
        pip install -r requirements-test.txt
    
    - name: Run syntax checks
      run: |
        python -m py_compile *.py
        
    - name: Run unit tests
      run: |
        python -m pytest tests/ -v
```

## Future Roadmap

### Planned Features
- [ ] **Encrypted Storage**: AES encryption for configuration files
- [ ] **Biometric Authentication**: Fingerprint sensor integration
- [ ] **Bluetooth Sync**: Mobile app synchronization
- [ ] **Voice Alerts**: Audio feedback for code expiration
- [ ] **Multi-Language**: Internationalization support
- [ ] **Cloud Backup**: Secure cloud configuration backup
- [ ] **Hardware Security**: TPM/secure element integration

### Version 2.0 Goals
- Enhanced security with hardware encryption
- Mobile companion app
- Advanced analytics and usage tracking
- Enterprise management features
- Multi-device synchronization

### Community Contributions
We welcome contributions in the following areas:
- Additional display drivers
- New authentication methods (HOTP, Steam Guard)
- Mobile applications
- Documentation improvements
- Testing and bug reports

---

**Project Status**: Active Development  
**Current Version**: 1.0.0  
**Last Updated**: 2024  
**Maintainer**: D31337m3 / Devin Ranger 

For the latest updates and documentation, visit our [GitHub repository](https://github.com/d31337m3/cpyotp_ui).
