# Laboratory Management System

A desktop application for managing laboratory resources, built with Python, Tkinter, and SQLite. Developed as part of the BIT Semester 02 project at the University of Moratuwa.

## Features

| Module | Description |
|--------|-------------|
| **User Management** | Admin-only user registration, role-based access (Student, Staff, Admin) |
| **Equipment Management** | Add, update, delete, and search laboratory equipment |
| **Category Management** | Admin-only management of equipment categories (stored in database) |
| **Equipment Borrowing** | Issue equipment to students, track returns, detect damage |
| **Laboratory Booking** | Students request lab time with time picker, staff approve/reject |
| **Maintenance Tracking** | Report damaged equipment, track repair completion |
| **Reports & Export** | Generate date-range reports with PDF export |

## Architecture

The system uses a **bundle/microservice architecture**. Each feature is a self-contained bundle that can be added or removed independently.

```
university_lab_management/
├── main.py                     # Entry point
├── setup.py                    # One-command setup script
├── requirements.txt            # Python dependencies
├── core/                       # Core framework
│   ├── app.py                  # Application controller
│   ├── auth.py                 # Password hashing (SHA-256)
│   ├── base_bundle.py          # Bundle interface class
│   ├── bundle_manager.py       # Auto-discovery & dependency resolution
│   ├── database.py             # SQLite connection manager
│   ├── date_picker.py          # Custom calendar date picker widget
│   ├── time_picker.py          # Custom hour/minute time picker widget
│   ├── logger.py               # Logging configuration
│   ├── theme.py                # Material Design colour theme (clam)
│   └── validators.py           # Input validation functions
├── bundles/                    # Feature bundles (add/remove as needed)
│   ├── user_management/        # User CRUD & authentication
│   ├── equipment/              # Equipment, laboratory & category management
│   ├── borrowing/              # Equipment borrowing & returns
│   ├── booking/                # Laboratory booking system
│   ├── maintenance/            # Maintenance tracking
│   └── reports/                # Report generation & PDF export
├── logs/                       # Application logs (auto-created)
└── laboratory.db               # SQLite database (auto-created)
```

### Adding a New Bundle

1. Create a new folder in `bundles/` (e.g., `bundles/my_feature/`)
2. Add three files:
   - `__init__.py` - Subclass `BaseBundle`, define tables, indexes, seed data, and tabs
   - `models.py` - Data access functions
   - `views.py` - Tkinter UI frames
3. The bundle is auto-discovered on the next application startup

### Removing a Bundle

Delete its folder from `bundles/`. The application will continue running without it.

## Database

SQLite database with 7 tables, all using UUID primary keys:

| Table | Description |
|-------|-------------|
| Users | User accounts with email-based authentication, CreatedAt timestamp |
| Category | Equipment categories (managed by Admin), CreatedAt timestamp |
| Laboratory | Lab rooms and locations |
| Equipment | Lab equipment linked to laboratories and categories |
| Borrowing | Equipment borrowing and return records |
| Booking | Laboratory booking requests and approvals |
| Maintenance | Equipment maintenance and repair tracking |

All tables are sorted by date in descending order (newest first) - using CreatedAt, PurchaseDate, BorrowDate, BookingDate, or ReportedDate as appropriate.

## UI Components

### Custom Widgets

- **DatePicker** - Calendar dialog for selecting dates (no external dependencies)
- **TimePicker** - Hour/minute spinbox picker with 5-minute increments

### Colour-Coded Buttons

All buttons follow a Material Design colour scheme for intuitive action recognition:

| Colour | Actions |
|--------|---------|
| Green | Add, Approve, Submit, Issue, Export, Login |
| Red | Delete, Reject, Logout |
| Blue | Update, Search, Generate, Refresh |
| Orange | Reset Password, Report Damage, Return Equipment |
| Grey | Clear, Show All |

Buttons brighten on hover for visual feedback.

### Live Data Refresh

All tabs automatically refresh their data when switched to. Dropdown lists (students, equipment, categories) reload from the database each time they are opened, ensuring newly added records appear immediately.

### Safety Features

- Logged-in admin cannot delete their own account
- Equipment with active borrowings cannot be deleted
- Users with active borrowings cannot be deleted
- Categories in use by equipment cannot be deleted
- Booking slots are checked for overlaps before submission

## Prerequisites

- **Python 3.8+**
- **tkinter** (usually included with Python; see platform-specific notes below)

### Platform-Specific tkinter Installation

| Platform | Command |
|----------|---------|
| macOS (Homebrew) | `brew install python-tk@3.13` (match your Python version) |
| Ubuntu/Debian | `sudo apt-get install python3-tk` |
| Fedora/RHEL | `sudo dnf install python3-tkinter` |
| Windows | Included by default (ensure tcl/tk is checked during Python install) |

## Installation & Setup

### Option 1: Automated Setup (Recommended)

```bash
cd university_lab_management
python3 setup.py
```

This will:
1. Create a virtual environment (`venv/`)
2. Install all dependencies (`fpdf2`, `Pillow`)
3. Verify tkinter availability

### Option 2: Manual Setup

```bash
cd university_lab_management
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

## Running the Application

```bash
cd university_lab_management
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
python main.py
```

## Default Login Credentials

| Email | Password | Role |
|-------|----------|------|
| admin@uom.lk | admin123 | Admin |
| john.smith@uom.lk | staff123 | Staff |
| sarah.j@uom.lk | staff456 | Staff |
| david.b@students.uom.lk | student123 | Student |
| emma.w@students.uom.lk | student456 | Student |

## User Roles

| Role | Access |
|------|--------|
| **Admin** | Full access + user management + category management |
| **Staff** | Equipment management, borrowing, booking approvals, maintenance, reports |
| **Student** | Equipment search, lab booking requests, view booking status |

### Admin-Only Features

- Register, update, and delete user accounts (cannot delete own account)
- Manage equipment categories (add, update, delete)
- All staff features

## Logging

Application logs are written to `logs/app.log` with automatic rotation (5 MB max, 3 backups). Logs include user actions, database operations, and error details.

## Technologies

- **Python 3** - Core language
- **Tkinter** - GUI framework (clam theme for cross-platform colour support)
- **SQLite** - Embedded database with UUID primary keys
- **fpdf2** - PDF report generation
- **Pillow** - Image processing support
- **Material Design** - UI colour palette and theming
