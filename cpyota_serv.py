"""
Minimal web server for TOTP configuration
Serves the web interface and handles configuration uploads
"""
import socket
import json
import os
import gc
from micropython import const

# HTML content (minified version of the web interface)
HTML_CONTENT = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>TOTP Config</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial,sans-serif;background:#667eea;padding:20px}.container{max-width:600px;margin:0 auto;background:white;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,0.2)}.header{background:#2c3e50;color:white;padding:20px;text-align:center}.content{padding:20px}.form-group{margin-bottom:15px}label{display:block;margin-bottom:5px;font-weight:600}input,select{width:100%;padding:10px;border:2px solid #ddd;border-radius:6px}.btn{background:#667eea;color:white;border:none;padding:12px 24px;border-radius:6px;cursor:pointer;margin:5px}.btn:hover{background:#5a67d8}.btn-danger{background:#e53e3e}.account-item{background:#f7fafc;border:1px solid #e2e8f0;border-radius:6px;padding:15px;margin:10px 0;display:flex;justify-content:space-between;align-items:center}.status{padding:10px;border-radius:6px;margin:15px 0;display:none}.status.success{background:#c6f6d5;color:#22543d}.status.error{background:#fed7d7;color:#742a2a}.hidden{display:none}</style></head><body><div class="container"><div class="header"><h1>🔐 TOTP Authenticator</h1><p>Configure your ESP32-S3</p></div><div class="content"><div id="status" class="status"></div><form id="addAccountForm"><h3>Add Account</h3><div class="form-group"><label>Name *</label><input type="text" id="accountName" required></div><div class="form-group"><label>Issuer</label><input type="text" id="issuer"></div><div class="form-group"><label>Secret *</label><input type="text" id="secret" required><button type="button" class="btn" onclick="generateSecret()">Generate</button></div><div class="form-group"><label>Digits</label><select id="digits"><option value="6">6</option><option value="8">8</option></select></div><div class="form-group"><label>Period</label><select id="period"><option value="30">30s</option><option value="60">60s</option></select></div><button type="submit" class="btn">Add Account</button></form><div><h3>Accounts</h3><div id="accountsList"></div></div><div style="text-align:center;margin-top:20px"><button class="btn" onclick="uploadConfig()">Upload to Device</button><button class="btn btn-danger" onclick="clearAll()">Clear All</button></div></div></div><script>let accounts=[];document.getElementById('addAccountForm').addEventListener('submit',function(e){e.preventDefault();addAccount()});function showStatus(msg,type='success'){const s=document.getElementById('status');s.textContent=msg;s.className=`status ${type}`;s.style.display='block';setTimeout(()=>s.style.display='none',5000)}function generateSecret(){const chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';let secret='';for(let i=0;i<32;i++)secret+=chars.charAt(Math.floor(Math.random()*chars.length));document.getElementById('secret').value=secret;showStatus('Secret generated!')}function addAccount(){const name=document.getElementById('accountName').value.trim();const issuer=document.getElementById('issuer').value.trim();const secret=document.getElementById('secret').value.trim().toUpperCase();const digits=parseInt(document.getElementById('digits').value);const period=parseInt(document.getElementById('period').value);if(!name||!secret){showStatus('Name and secret required!','error');return}if(!/^[A-Z2-7]+=*$/.test(secret)){showStatus('Invalid base32 secret!','error');return}accounts.push({name,issuer,secret,digits,period,color:0xFFFFFF});updateAccountsList();document.getElementById('addAccountForm').reset();showStatus('Account added!')}function updateAccountsList(){const container=document.getElementById('accountsList');if(accounts.length===0){container.innerHTML='<p>No accounts</p>';return}container.innerHTML=accounts.map((acc,i)=>`<div class="account-item"><div><div><strong>${acc.name}</strong></div>${acc.issuer?`<div><small>${acc.issuer}</small></div>`:
''}<div><small>${acc.digits} digits, ${acc.period}s</small></div></div><button class="btn btn-danger" onclick="removeAccount(${i})">Remove</button></div>`).join('')}function removeAccount(i){if(confirm('Remove account?')){accounts.splice(i,1);updateAccountsList();showStatus('Account removed!')}}function clearAll(){if(confirm('Clear all accounts?')){accounts=[];updateAccountsList();showStatus('All cleared!')}}async function uploadConfig(){if(accounts.length===0){showStatus('No accounts to upload!','error');return}try{const response=await fetch('/upload_config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({accounts})});if(response.ok){showStatus('Uploaded successfully!');}else{throw new Error('Upload failed')}}catch(error){showStatus('Upload error: '+error.message,'error')}}updateAccountsList();</script></body></html>"""

class TOTPWebServer:
    def __init__(self, port=80):
        self.port = port
        self.socket = None
        self.running = False
    
    def start(self):
        """Start the web server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('', self.port))
            self.socket.listen(1)
            self.running = True
            print(f"Web server started on port {self.port}")
            return True
        except Exception as e:
            print(f"Failed to start web server: {e}")
            return False
    
    def stop(self):
        """Stop the web server"""
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
        print("Web server stopped")
    
    def handle_request(self, client_socket):
        """Handle incoming HTTP request"""
        try:
            # Receive request
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                return
            
            # Parse request line
            lines = request.split('\n')
            if not lines:
                return
            
            request_line = lines[0].strip()
            method, path, _ = request_line.split(' ', 2)
            
            print(f"Request: {method} {path}")
            
            if method == 'GET' and path == '/':
                # Serve main page
                self.send_response(client_socket, 200, HTML_CONTENT, 'text/html')
                
            elif method == 'POST' and path == '/upload_config':
                # Handle configuration upload
                self.handle_config_upload(client_socket, request)
                
            elif method == 'GET' and path == '/status':
                # Device status
                self.send_json_response(client_socket, 200, {
                    'status': 'ok',
                    'free_memory': gc.mem_free(),
                    'accounts_configured': self.count_accounts()
                })
                
            else:
                # 404 Not Found
                self.send_response(client_socket, 404, "Not Found", 'text/plain')
                
        except Exception as e:
            print(f"Error handling request: {e}")
            self.send_response(client_socket, 500, "Internal Server Error", 'text/plain')
        
        finally:
            client_socket.close()
    
    def handle_config_upload(self, client_socket, request):
        """Handle TOTP configuration upload"""
        try:
            # Extract JSON data from POST request
            if '\r\n\r\n' in request:
                _, body = request.split('\r\n\r\n', 1)
            else:
                body = ""
            
            if not body:
                self.send_json_response(client_socket, 400, {'error': 'No data received'})
                return
            
            # Parse JSON
            try:
                config_data = json.loads(body)
            except ValueError as e:
                self.send_json_response(client_socket, 400, {'error': 'Invalid JSON'})
                return
            
            # Validate configuration
            if 'accounts' not in config_data or not isinstance(config_data['accounts'], list):
                self.send_json_response(client_socket, 400, {'error': 'Invalid configuration format'})
                return
            
            # Save configuration to temporary file
            temp_file = "/totp_temp.json"
            try:
                with open(temp_file, 'w') as f:
                    json.dump(config_data, f)
                
                self.send_json_response(client_socket, 200, {
                    'status': 'success',
                    'message': 'Configuration uploaded successfully',
                    'accounts_count': len(config_data['accounts'])
                })
                
                print(f"Configuration uploaded: {len(config_data['accounts'])} accounts")
                
            except Exception as e:
                self.send_json_response(client_socket, 500, {'error': f'Failed to save configuration: {e}'})
                
        except Exception as e:
            print(f"Error in config upload: {e}")
            self.send_json_response(client_socket, 500, {'error': 'Internal server error'})
    
    def send_response(self, client_socket, status_code, content, content_type):
        """Send HTTP response"""
        status_text = {
            200: 'OK',
            400: 'Bad Request',
            404: 'Not Found',
            500: 'Internal Server Error'
        }.get(status_code, 'Unknown')
        
        response = f"HTTP/1.1 {status_code} {status_text}\r\n"
        response += f"Content-Type: {content_type}\r\n"
        response += f"Content-Length: {len(content)}\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        response += content
        
        client_socket.send(response.encode('utf-8'))
    
    def send_json_response(self, client_socket, status_code, data):
        """Send JSON response"""
        json_content = json.dumps(data)
        self.send_response(client_socket, status_code, json_content, 'application/json')
    
    def count_accounts(self):
        """Count configured accounts"""
        try:
            with open("/totp_config.json", 'r') as f:
                config = json.load(f)
            return len(config.get('accounts', []))
        except:
            return 0
    
    def run(self):
        """Main server loop"""
        if not self.start():
            return
        
        print("Web server running. Connect to configure TOTP accounts.")
        
        try:
            while self.running:
                try:
                    client_socket, addr = self.socket.accept()
                    print(f"Connection from {addr}")
                    self.handle_request(client_socket)
                    gc.collect()  # Clean up memory
                    
                except OSError as e:
                    if self.running:  # Only print error if we're supposed to be running
                        print(f"Socket error: {e}")
                        break
                        
        except KeyboardInterrupt:
            print("Server interrupted")
        finally:
            self.stop()

# Standalone web server for configuration
if __name__ == "__main__":
    server = TOTPWebServer()
    server.run()
