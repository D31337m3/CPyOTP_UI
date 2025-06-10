 
 """
Console interface for TOTP Authenticator configuration
"""
import json
import os
from pyotp_circuitpython import TOTP, random_base32, base32_encode

class TOTPConsole:
    def __init__(self):
        self.config_file = "/totp_config.json"
        self.accounts = []
        self.load_config()
    
    def load_config(self):
        """Load existing configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            self.accounts = config.get('accounts', [])
        except:
            self.accounts = []
    
    def save_config(self):
        """Save configuration to file"""
        config = {"accounts": self.accounts}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
        print("Configuration saved!")
    
    def add_account(self):
        """Add a new TOTP account"""
        print("\n=== Add New TOTP Account ===")
        
        name = input("Account name: ").strip()
        if not name:
            print("Account name is required!")
            return
        
        issuer = input("Issuer (optional): ").strip()
        
        # Get secret
        print("\nSecret options:")
        print("1. Enter existing secret")
        print("2. Generate random secret")
        choice = input("Choice (1/2): ").strip()
        
        if choice == "2":
            secret = random_base32(32)
            print(f"Generated secret: {secret}")
        else:
            secret = input("Enter base32 secret: ").strip().upper()
            if not secret:
                print("Secret is required!")
                return
        
        # Optional parameters
        digits = input("Digits (default 6): ").strip()
        digits = int(digits) if digits.isdigit() else 6
        
        period = input("Period in seconds (default 30): ").strip()
        period = int(period) if period.isdigit() else 30
        
        # Color (hex)
        color_input = input("Display color (hex, default white): ").strip()
        if color_input.startswith('#'):
            color_input = color_input[1:]
        try:
            color = int(color_input, 16) if color_input else 0xFFFFFF
        except:
            color = 0xFFFFFF
       # Test the TOTP
        try:
            test_totp = TOTP(secret, digits=digits, interval=period)
            test_code = test_totp.now()
            print(f"\nTest TOTP code: {test_code}")
            
            # Generate QR code URI
            uri = test_totp.provisioning_uri(name=name, issuer_name=issuer)
            print(f"QR Code URI: {uri}")
            
        except Exception as e:
            print(f"Error testing TOTP: {e}")
            return
        
        # Confirm addition
        confirm = input("\nAdd this account? (y/N): ").strip().lower()
        if confirm == 'y':
            account = {
                "name": name,
                "issuer": issuer,
                "secret": secret,
                "digits": digits,
                "period": period,
                "color": color
            }
            self.accounts.append(account)
            self.save_config()
            print("Account added successfully!")
        else:
            print("Account not added.")
    
    def list_accounts(self):
        """List all configured accounts"""
        if not self.accounts:
            print("No accounts configured.")
            return
        
        print("\n=== Configured Accounts ===")
        for i, account in enumerate(self.accounts):
            print(f"{i+1}. {account['issuer']}: {account['name']}" if account['issuer'] 
                  else f"{i+1}. {account['name']}")
            
            # Generate current code
            try:
                totp = TOTP(account['secret'], digits=account['digits'], 
                           interval=account['period'])
                code = totp.now()
                print(f"   Current code: {code}")
            except Exception as e:
                print(f"   Error: {e}")
    
    def delete_account(self):
        """Delete an account"""
        if not self.accounts:
            print("No accounts to delete.")
            return
        
        self.list_accounts()
        try:
            index = int(input("\nEnter account number to delete: ")) - 1
            if 0 <= index < len(self.accounts):
                account = self.accounts[index]
                name = f"{account['issuer']}: {account['name']}" if account['issuer'] else account['name']
                
                confirm = input(f"Delete '{name}'? (y/N): ").strip().lower()
                if confirm == 'y':
                    self.accounts.pop(index)
                    self.save_config()
                    print("Account deleted!")
                else:
                    print("Account not deleted.")
            else:
                print("Invalid account number.")
        except ValueError:
            print("Invalid input.")
    
    def import_from_uri(self):
        """Import account from otpauth:// URI"""
        print("\n=== Import from URI ===")
        uri = input("Enter otpauth:// URI: ").strip()
        
        if not uri.startswith('otpauth://'):
            print("Invalid URI format. Must start with 'otpauth://'")
            return
        
        try:
            # Parse URI (simplified parser)
            if '?' not in uri:
                print("Invalid URI format.")
                return
            
            base_part, params_part = uri.split('?', 1)
            
            # Extract type and label
            if '//' not in base_part:
                print("Invalid URI format.")
                return
            
            type_label = base_part.split('//', 1)[1]
            if '/' not in type_label:
                print("Invalid URI format.")
                return
            
            otp_type, label = type_label.split('/', 1)
            
            # Parse label (issuer:account or just account)
            if ':' in label:
                issuer, name = label.split(':', 1)
                # URL decode
                issuer = issuer.replace('%20', ' ')
                name = name.replace('%20', ' ')
            else:
                issuer = ""
                name = label.replace('%20', ' ')
            
            # Parse parameters
            params = {}
            for param in params_part.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value.replace('%20', ' ')
            
            if 'secret' not in params:
                print("No secret found in URI.")
                return
            
            # Create account
            account = {
                "name": name,
                "issuer": issuer,
                "secret": params['secret'],
                "digits": int(params.get('digits', 6)),
                "period": int(params.get('period', 30)),
                "color": 0xFFFFFF
            }
            
            # Test the account
            totp = TOTP(account['secret'], digits=account['digits'], 
                       interval=account['period'])
            test_code = totp.now()
            
            print(f"Parsed account: {issuer}: {name}" if issuer else f"Parsed account: {name}")
            print(f"Test code: {test_code}")
            
            confirm = input("Import this account? (y/N): ").strip().lower()
            if confirm == 'y':
                self.accounts.append(account)
                self.save_config()
                print("Account imported successfully!")
            
        except Exception as e:
            print(f"Error parsing URI: {e}")
    
    def export_backup(self):
        """Export configuration as backup"""
        if not self.accounts:
            print("No accounts to export.")
            return
        
        backup_file = "/totp_backup.json"
        try:
            with open(backup_file, 'w') as f:
                json.dump({"accounts": self.accounts}, f, indent=2)
            print(f"Backup saved to {backup_file}")
            print("WARNING: This file contains secrets! Keep it secure.")
        except Exception as e:
            print(f"Error creating backup: {e}")
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "="*40)
        print("    TOTP Authenticator Console")
        print("="*40)
        print("1. Add account")
        print("2. List accounts")
        print("3. Delete account")
        print("4. Import from URI")
        print("5. Export backup")
        print("6. Generate random secret")
        print("7. Test TOTP code")
        print("0. Exit")
        print("="*40)
    
    def generate_secret(self):
        """Generate a random base32 secret"""
        length = input("Secret length (default 32): ").strip()
        length = int(length) if length.isdigit() else 32
        
        secret = random_base32(length)
        print(f"Generated secret: {secret}")
        print("Save this secret securely!")
    
    def test_totp(self):
        """Test a TOTP code"""
        secret = input("Enter secret: ").strip()
        if not secret:
            print("Secret is required!")
            return
        
        try:
            totp = TOTP(secret)
            code = totp.now()
            print(f"Current TOTP code: {code}")
            
            # Show next few codes
            import time
            current_time = int(time.time())
            for i in range(1, 4):
                future_time = current_time + (i * 30)
                future_code = totp.at(future_time)
                print(f"Code in {i*30}s: {future_code}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def run(self):
        """Main console loop"""
        print("TOTP Authenticator Console")
        print("Configure your TOTP accounts")
        
        while True:
            try:
                self.show_menu()
                choice = input("Enter choice: ").strip()
                
                if choice == '1':
                    self.add_account()
                elif choice == '2':
                    self.list_accounts()
                elif choice == '3':
                    self.delete_account()
                elif choice == '4':
                    self.import_from_uri()
                elif choice == '5':
                    self.export_backup()
                elif choice == '6':
                    self.generate_secret()
                elif choice == '7':
                    self.test_totp()
                elif choice == '0':
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    console = TOTPConsole()
    console.run()
