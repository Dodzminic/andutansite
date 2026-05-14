🛡️ FILSYNC: Obsidian Sovereign Edition
FILSYNC is a high-end Identity Management System built with Django. Designed as a secure "Cyber-Terminal," it provides a sophisticated interface for managing user registries with advanced filtering, security protocols, and bulk administrative tools.

🚀 Key Features
Apex Obsidian UI: A custom-designed aesthetic featuring deep charcoal and cobalt color grading, glass-morphism panels, and high-visibility typography.

Sovereign Multi-Search: A real-time, live-scanning search engine that filters the database by Username, Email, or Gender Category simultaneously.

Sentinel Security Suite:

Live Identity Scanner: Real-time checks for Username and Email availability during registration to prevent database duplication.

Shield Verification: Dynamic visual feedback for password matching (Neon Verified vs. Mismatch alerts).

Bulk Command Center: An interactive action bar for mass-processing identities (Bulk Archive, Bulk Recovery, or Bulk Permanent Purge).

Sovereign Archive System: * Soft-Archive: Temporarily hide identities from the active directory.

Permanent Purge: Absolute removal of records from the database.

Recovery Portal: One-click restoration of archived identities.

🛠️ Tech Stack
Backend: Python 3.12 / Django 4.2.10

Database: MySQL (Local / PHPMyAdmin)

Frontend: HTML5, CSS3 (Glass-morphism), JavaScript (Fetch API / Live Scan)

UI Components: Bootstrap 5.3, Bootstrap Icons, SweetAlert2 (Apex Alerts)

📥 Installation & Setup
Clone the Repository:

Bash
git clone https://github.com/Dodzminic/andutansite.git
Install Requirements:

Bash
pip install django mysqlclient
Database Configuration:
Configure your MySQL settings in andutansite/settings.py.

Run Migrations:

Bash
python manage.py migrate
Initialize Terminal:

Bash
python manage.py runserver