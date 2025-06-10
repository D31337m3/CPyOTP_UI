"""
CircuitPython TOTP Authenticator for ESP32-S3 with Display
Displays up to 3 TOTP codes with automatic rotation
"""
import time
import board
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
import json
import storage
import os
from tftblinky import TFTBlinky

# Import our custom TOTP library
try:
    from pyotp_circuitpython import TOTP, random_base32
except ImportError:
    print("Error: pyotp_circuitpython.py not found!")
    raise

class TOTPAuthenticator:
    def __init__(self):
        self.display = board.DISPLAY
        self.display_group = displayio.Group()
        self.display.show(self.display_group)
        
        # Display properties
        self.width = self.display.width
        self.height = self.display.height
        
        # TOTP configuration
        self.accounts = []
        self.current_page = 0
        self.codes_per_page = 3
        self.last_update = 0
        self.last_page_change = 0
        self.page_rotation_interval = 15  # seconds
        
        # Visual feedback
        self.blinky = TFTBlinky()
        
        # Load configuration
        self.load_config()
        
        # Setup display
        self.setup_display()
        
        print(f"TOTP Authenticator initialized with {len(self.accounts)} accounts")
        print(f"Display: {self.width}x{self.height}")
    
    def load_config(self):
        """Load TOTP accounts from configuration file"""
        config_file = "/totp_config.json"
        temp_file = "/totp_temp.json"
        
        # Check for temporary config file first (from web interface)
        if temp_file in os.listdir("/"):
            try:
                with open(temp_file, 'r') as f:
                    config = json.load(f)
                
                # Save to permanent config
                with open(config_file, 'w') as f:
                    json.dump(config, f)
                
                # Delete temporary file for security
                os.remove(temp_file)
                print("Configuration updated from web interface")
                
            except Exception as e:
                print(f"Error processing temp config: {e}")
        
        # Load main configuration
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            self.accounts = []
            for account_data in config.get('accounts', []):
                try:
                    totp = TOTP(
                        secret=account_data['secret'],
                        name=account_data.get('name', 'Unknown'),
                        issuer=account_data.get('issuer', ''),
                        digits=account_data.get('digits', 6),
                        interval=account_data.get('period', 30)
                    )
                    self.accounts.append({
                        'totp': totp,
                        'name': account_data.get('name', 'Unknown'),
                        'issuer': account_data.get('issuer', ''),
                        'color': account_data.get('color', 0xFFFFFF)
                    })
                except Exception as e:
                    print(f"Error loading account {account_data.get('name', 'Unknown')}: {e}")
                    
        except (OSError, ValueError) as e:
            print(f"No config file found or error loading: {e}")
            # Create default config
            self.create_default_config()
    
    def create_default_config(self):
        """Create a default configuration file"""
        default_config = {
            "accounts": [
                {
                    "name": "Demo Account",
                    "issuer": "Demo",
                    "secret": random_base32(32),
                    "digits": 6,
                    "period": 30,
                    "color": 0x00FF00
                }
            ]
        }
        
        try:
            with open("/totp_config.json", 'w') as f:
                json.dump(default_config, f)
            print("Created default configuration")
            self.load_config()
        except Exception as e:
            print(f"Error creating default config: {e}")
    
    def setup_display(self):
        """Setup the display layout"""
        # Clear display
        while len(self.display_group) > 0:
            self.display_group.pop()
        
        # Background
        background = Rect(0, 0, self.width, self.height, fill=0x000000)
        self.display_group.append(background)
        
        # Title bar
        title_bg = Rect(0, 0, self.width, 30, fill=0x333333)
        self.display_group.append(title_bg)
        
        title_text = label.Label(
            terminalio.FONT,
            text="TOTP Authenticator",
            color=0xFFFFFF,
            x=5,
            y=15
        )
        self.display_group.append(title_text)
        
        # Page indicator
        if len(self.accounts) > self.codes_per_page:
            total_pages = (len(self.accounts) + self.codes_per_page - 1) // self.codes_per_page
            page_text = label.Label(
                terminalio.FONT,
                text=f"{self.current_page + 1}/{total_pages}",
                color=0xFFFFFF,
                x=self.width - 40,
                y=15
            )
            self.display_group.append(page_text)
        
        # Account display areas
        self.setup_account_display()
    
    def setup_account_display(self):
        """Setup account display areas based on number of accounts"""
        if not self.accounts:
            no_accounts_text = label.Label(
                terminalio.FONT,
                text="No accounts configured\nUse console or web interface\nto add accounts",
                color=0xFF0000,
                x=10,
                y=60
            )
            self.display_group.append(no_accounts_text)
            return
        
        # Calculate accounts to show on current page
        start_idx = self.current_page * self.codes_per_page
        end_idx = min(start_idx + self.codes_per_page, len(self.accounts))
        current_accounts = self.accounts[start_idx:end_idx]
        
        # Calculate layout based on number of accounts
        num_accounts = len(current_accounts)
        if num_accounts == 1:
            self.display_single_account(current_accounts[0], 0)
        elif num_accounts == 2:
            self.display_two_accounts(current_accounts)
        else:  # 3 accounts
            self.display_three_accounts(current_accounts)
    
    def display_single_account(self, account, y_offset=40):
        """Display single account with large text"""
        y_pos = y_offset + 60
        
        # Issuer/Name
        name_text = f"{account['issuer']}: {account['name']}" if account['issuer'] else account['name']
        name_label = label.Label(
            terminalio.FONT,
            text=name_text[:25],  # Truncate if too long
            color=account['color'],
            x=10,
            y=y_pos
        )
        self.display_group.append(name_label)
        
        # TOTP Code (large)
        code = account['totp'].now()
        code_label = label.Label(
            terminalio.FONT,
            text=code,
            color=0xFFFFFF,
            x=10,
            y=y_pos + 30,
            scale=3
        )
        self.display_group.append(code_label)
        
        # Time remaining
        remaining = 30 - (int(time.time()) % 30)
        time_label = label.Label(
            terminalio.FONT,
            text=f"Expires in: {remaining}s",
            color=0x888888,
            x=10,
            y=y_pos + 70
        )
        self.display_group.append(time_label)
    
    def display_two_accounts(self, accounts):
        """Display two accounts with medium text"""
        for i, account in enumerate(accounts):
            y_pos = 50 + (i * 80)
            
            # Account separator
            if i > 0:
                separator = Rect(0, y_pos - 10, self.width, 1, fill=0x444444)
                self.display_group.append(separator)
            
            # Issuer/Name
            name_text = f"{account['issuer']}: {account['name']}" if account['issuer'] else account['name']
            name_label = label.Label(
                terminalio.FONT,
                text=name_text[:20],
                color=account['color'],
                x=5,
                y=y_pos + 10
            )
            self.display_group.append(name_label)
            
            # TOTP Code
            code = account['totp'].now()
            code_label = label.Label(
                terminalio.FONT,
                text=code,
                color=0xFFFFFF,
                x=5,
                y=y_pos + 35,
                scale=2
            )
            self.display_group.append(code_label)
    
    def display_three_accounts(self, accounts):
        """Display three accounts with compact text"""
        for i, account in enumerate(accounts):
            y_pos = 40 + (i * 60)
            
            # Account separator
            if i > 0:
                separator = Rect(0, y_pos - 5, self.width, 1, fill=0x444444)
                self.display_group.append(separator)
            
            # Issuer/Name
            name_text = f"{account['issuer']}: {account['name']}" if account['issuer'] else account['name']
            name_label = label.Label(
                terminalio.FONT,
                text=name_text[:18],
                color=account['color'],
                x=5,
                y=y_pos + 10
            )
            self.display_group.append(name_label)
            
            # TOTP Code
            code = account['totp'].now()
            code_label = label.Label(
                terminalio.FONT,
                text=code,
                color=0xFFFFFF,
                x=5,
                y=y_pos + 30,
                scale=1
            )
            self.display_group.append(code_label)
            
            # Time remaining (small)
            remaining = 30 - (int(time.time()) % 30)
            time_label = label.Label(
                terminalio.FONT,
                text=f"{remaining}s",
                color=0x666666,
                x=self.width - 25,
                y=y_pos + 30
            )
            self.display_group.append(time_label)
    
    def update_display(self):
        """Update the display with current TOTP codes"""
        current_time = time.time()
        
        # Check if we need to rotate pages
        if (len(self.accounts) > self.codes_per_page and 
            current_time - self.last_page_change >= self.page_rotation_interval):
            
            total_pages = (len(self.accounts) + self.codes_per_page - 1) // self.codes_per_page
            self.current_page = (self.current_page + 1) % total_pages
            self.last_page_change = current_time
            self.setup_display()
            return
        
        # Update codes every second
        if current_time - self.last_update >= 1:
            self.setup_display()
            self.last_update = current_time
            
            # Blink when codes refresh (every 30 seconds)
            if int(current_time) % 30 == 0:
                self.blinky.blink(count=1, on_time=0.1, off_time=0.1)
    
    def run(self):
        """Main application loop"""
        print("TOTP Authenticator running...")
        print("Use console commands or web interface to manage accounts")
        
        while True:
            try:
                self.update_display()
                time.sleep(0.1)
            except KeyboardInterrupt:
                print("Shutting down...")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(1)

# Main execution
if __name__ == "__main__":
    app = TOTPAuthenticator()
    app.run()
