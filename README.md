# 🐾 PetPal — Shelter Records & Adoption Manager

PetPal is a full-stack web application designed to help small animal shelters manage animal records and adoption applications in one centralized, easy-to-use platform.

Shelters can list animals with photos, track adoption applications, and approve or deny requests through a secure admin dashboard. Public users can browse adoptable animals and apply online.

---

## ✨ Features

### Public
- Homepage with site overview and live stats
- Browse adoptable animals
- View individual animal detail pages with images
- Submit adoption applications online

### Admin (Secure)
- Admin login with session-based authentication
- View all adoption applications
- Approve, deny, or reset application status
- Protected admin routes

### System
- Image uploads for animals
- SQLite database with SQLAlchemy ORM
- Clean Git workflow with `main` and `develop` branches

---

## 🧱 Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite (via SQLAlchemy)
- **Authentication:** Flask sessions (admin login)
- **Frontend:** Flask templates (HTML, CSS, JavaScript)
- **Image Storage:** Local uploads (development)
- **Version Control:** Git & GitHub

---

### 1️⃣ Clone the repository
```bash
git clone <https://github.com/JBrij/petpal-shelter-manager>
cd petpal
```
### 2️⃣ Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set environment variables (Windows)
```bash
set FLASK_APP=app
set FLASK_ENV=development
```

### 5️⃣ Run the app
```bash
flask run
```

The site will be available at:
http://127.0.0.1:5000/

## Testing
This project includes a pytest test suite covering:
- Public routes
- Animal API
- Adoption application validation
- Admin-only route protection

Run tests locally:
```bash
pytest
```

### 📜 License
This project is for educational purposes.
