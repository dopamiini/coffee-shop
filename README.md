## Setup

```bash
git clone https://github.com/<your-user>/<your-repo>.git
cd <your-repo>
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```
You will need the django and the cryptography module listed in requirements.txt.

## Comments
The app is a minimalistic online shop that sells brands of coffee. It should be fully functional and the navigation should be self-explanatory. For those with less coding experience, I recommend rerunning the seed file "python manage.py seed" after applying each fix. This is because some of the fixes hash and encrypt the plaintext data in the database. The seed file creates three default users: Alice has password 1, Bob has password 2, 
and admin has password admin.

Listing of the flaws covered:
1. (OWASP A01:2021) - Broken Access Control (CWE-639) - Authorization Bypass Through User-Controlled Key 
2. (OWASP A02:2021) - Cryptographic Failures (CWE-311) - Missing Encryption of Sensitive Data
3. (OWASP A03:2021) - Injection (CWE-89) - SQL Injection
4. (OWASP A07:2021) - Identification and Authentication Failures (CWE-256) - Plaintext Storage of Passwords
5. (OWASP A07:2021) - Identification and Authentication Failures (CWE-307) - Improper Restriction of Excessive Authentication Attempts
6. (OWA SP A07:2021) - Identification and Authentication Failures (CWE-521) - Weak Password Requirements
7. (OWASP A09:2021) - Security Logging and Monitoring Failures (CWE-778) - Insufficient Logging
