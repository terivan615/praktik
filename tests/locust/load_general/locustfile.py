# locustfile.py
from locust import HttpUser, task, between, events
import random
import requests
from datetime import datetime, timedelta

# ========================================
# CONFIGURATION (from your HTML)
# ========================================
NOCODB_CONFIG = {
    "base_url": "https://app.nocodb.com",
    "workspace_id": "p2zp5kay2ja7qli",
    "table_id": "mpqzfhxx5kmz9tv",
    "api_token": "b4EJZcJpb4lP-_fbGm8Nlf-30qRoAZuVI3eRSlmk",
}

API_ENDPOINT = f"/api/v2/tables/{NOCODB_CONFIG['table_id']}/records"

# ========================================
# DIVERSE TEST DATA
# ========================================

# Realistic device names
DEVICES = [
    "Laptop-Dell-5420", "Laptop-HP-850", "Laptop-Lenovo-T480",
    "PC-Accounting-01", "PC-HR-02", "PC-Manager-03",
    "Printer-HP-LaserJet-01", "Printer-Canon-MF-02",
    "Monitor-Samsung-27-01", "Monitor-Dell-24-02",
    "iPhone-13-Pro", "iPhone-12", "Samsung-Galaxy-S22",
    "iPad-Pro-11", "iPad-Air",
    "MacBook-Pro-16", "MacBook-Air-M2", "iMac-27",
    "Server-File-01", "Server-DB-02", "Server-Web-03",
    "Router-Cisco-01", "Switch-Netgear-02",
    "Scanner-Epson-01", "Webcam-Logitech-C920",
    "Keyboard-Wireless-01", "Mouse-Logitech-MX",
    "Docking-Station-01", "USB-Hub-02",
    "Projector-Epson-01", "TV-Samsung-55-Conference"
]

# Realistic problem descriptions
PROBLEM_DESCRIPTIONS = {
    "bug": [
        "System crashes when opening large Excel files (>50MB)",
        "Blue screen appears after Windows update",
        "Application freezes during file save operation",
        "Error 0x80070005 when trying to install software",
        "Network disconnects every 30 minutes",
        "Printer prints garbage characters",
        "Screen flickering on external monitor",
        "USB ports not recognizing devices",
        "WiFi connection drops frequently",
        "Outlook not syncing emails",
        "Cannot access network drive Z:",
        "Audio stops working after sleep mode",
        "Keyboard shortcuts not responding",
        "Mouse cursor disappears randomly",
        "Browser crashes when opening multiple tabs"
    ],
    "feature": [
        "Request to install Adobe Photoshop for design work",
        "Need access to VPN for remote work",
        "Request dual monitor setup for productivity",
        "Need software license for AutoCAD",
        "Request upgrade to 16GB RAM",
        "Need access to shared calendar",
        "Request installation of Python and VS Code",
        "Need new email signature template",
        "Request access to project management tool",
        "Need backup solution for local files"
    ],
    "question": [
        "How to connect to company VPN from home?",
        "What is the procedure for software installation?",
        "How to set up email on mobile device?",
        "Where to find network printer drivers?",
        "How to request new hardware?",
        "What is the backup schedule?",
        "How to share large files with clients?",
        "Where to download approved software?",
        "How to reset password?",
        "What antivirus is approved for use?"
    ],
    "task": [
        "Install Windows 11 on new laptop",
        "Configure email account for new employee",
        "Replace old monitor with new 27 inch",
        "Update antivirus definitions",
        "Clean up disk space on PC-HR-02",
        "Install printer drivers for new device",
        "Configure VPN access for remote user",
        "Replace keyboard and mouse set",
        "Upgrade RAM from 8GB to 16GB",
        "Setup dual boot Windows/Linux"
    ]
}

# Realistic assignees
ASSIGNEES = [
    "ivanov", "petrov", "sidorov", "kozlov", "novikov",
    "smirnov", "kuznetsov", "popov", "vasiliev", "mikhailov",
    "tech_support_1", "tech_support_2", "admin", "helpdesk"
]

# Realistic priorities distribution
PRIORITIES = ["critical", "high", "normal", "low"]
PRIORITY_WEIGHTS = [0.05, 0.15, 0.60, 0.20]  # Realistic distribution

TYPES = ["bug", "feature", "question", "task"]
TYPE_WEIGHTS = [0.35, 0.15, 0.20, 0.30]

STATUSES = ["backlog", "inProgress", "review", "done"]
STATUS_WEIGHTS = [0.40, 0.30, 0.15, 0.15]


def generate_realistic_ticket():
    """Generate realistic ticket data with variety"""
    
    ticket_type = random.choices(TYPES, weights=TYPE_WEIGHTS, k=1)[0]
    priority = random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS, k=1)[0]
    
    # Generate realistic ticket ID
    ticket_id = f"T{random.randint(1000, 99999)}"
    
    # Get problem description based on type
    descriptions = PROBLEM_DESCRIPTIONS[ticket_type]
    description = random.choice(descriptions)
    
    # Add some variation to description
    if random.random() > 0.7:
        description += f". Urgency: {random.choice(['High', 'Medium', 'Low'])}"
    if random.random() > 0.8:
        description += f". Reported by: {random.choice(ASSIGNEES)}"
    
    # Select device
    device = random.choice(DEVICES)
    
    # Select assignee (sometimes unassigned)
    if random.random() > 0.2:
        assignee = random.choice(ASSIGNEES)
    else:
        assignee = ""
    
    # Status based on type
    if ticket_type == "question":
        status = random.choices(["done", "inProgress"], weights=[0.7, 0.3], k=1)[0]
    else:
        status = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]
    
    # Blocked status (rare)
    blocked = random.random() < 0.1
    
    return {
        "ticketId": ticket_id,
        "title": description[:80],  # Truncate if too long
        "type": ticket_type,
        "priority": priority,
        "assignee": assignee,
        "device": device,
        "description": description,
        "blocked": blocked,
        "status": status
    }


# ========================================
# LOCUST USERS
# ========================================

class WebsiteUser(HttpUser):
    """User who visits the website and creates tickets"""
    wait_time = between(3, 10)
    
    @task(3)
    def load_website(self):
        """Load main website page"""
        with self.client.get("/", name="GET / (website)", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed: {response.status_code}")
    
    @task(1)
    def create_ticket(self):
        """Create ticket via NocoDB API"""
        ticket_data = generate_realistic_ticket()
        
        try:
            response = requests.post(
                f"{NOCODB_CONFIG['base_url']}{API_ENDPOINT}",
                json=ticket_data,
                headers={
                    "xc-token": NOCODB_CONFIG["api_token"],
                    "Content-Type": "application/json"
                },
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                print(f"[OK] Created ticket: {ticket_data['ticketId']} - {ticket_data['title'][:50]}")
            else:
                print(f"[ERROR] {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"[NETWORK ERROR] {e}")


class ApiTestUser(HttpUser):
    """Separate class for testing only NocoDB API"""
    host = NOCODB_CONFIG["base_url"]
    wait_time = between(5, 15)
    
    @task(3)
    def create_ticket_api(self):
        """POST - Create ticket"""
        ticket_data = generate_realistic_ticket()
        
        with self.client.post(
            API_ENDPOINT,
            json=ticket_data,
            headers={
                "xc-token": NOCODB_CONFIG["api_token"],
                "Content-Type": "application/json"
            },
            name="POST /records (create)",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def list_tickets_api(self):
        """GET - List tickets"""
        limit = random.choice([10, 20, 50, 100])
        
        with self.client.get(
            f"{API_ENDPOINT}?limit={limit}",
            headers={
                "xc-token": NOCODB_CONFIG["api_token"]
            },
            name="GET /records (list)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def update_ticket_api(self):
        """PATCH - Update ticket status"""
        record_id = random.randint(1, 5000)
        new_status = random.choice(STATUSES)
        
        payload = [{
            "Id": record_id,
            "status": new_status
        }]
        
        with self.client.patch(
            API_ENDPOINT,
            json=payload,
            headers={
                "xc-token": NOCODB_CONFIG["api_token"],
                "Content-Type": "application/json"
            },
            name="PATCH /records (update)",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def search_tickets(self):
        """Search/filter tickets"""
        search_terms = ["printer", "laptop", "network", "email", "error", "install"]
        term = random.choice(search_terms)
        
        with self.client.get(
            f"{API_ENDPOINT}?limit=20&where=(title,~,{term})",
            headers={
                "xc-token": NOCODB_CONFIG["api_token"]
            },
            name="GET /records (search)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")


# ========================================
# EVENT HANDLERS
# ========================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=" * 70)
    print("LOAD TEST STARTING")
    print("=" * 70)
    print(f"Website: {environment.host}")
    print(f"NocoDB API: {NOCODB_CONFIG['base_url']}")
    print(f"Table ID: {NOCODB_CONFIG['table_id']}")
    print(f"Workspace: {NOCODB_CONFIG['workspace_id']}")
    print("=" * 70)
    print("Available user classes:")
    print("  - WebsiteUser: website load + ticket creation")
    print("  - ApiTestUser: API only (POST/GET/PATCH/SEARCH)")
    print("=" * 70)


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Log problematic requests"""
    if exception:
        print(f"[ERROR] {name} | {exception}")
    elif response_time > 3000:
        print(f"[SLOW] {name} | {response_time:.0f}ms")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("=" * 70)
    print("LOAD TEST COMPLETED")
    print("=" * 70)