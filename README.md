# ⚡ TransitOps - Smart Transport Operations Platform

> A full-stack fleet management system built with Django, designed to streamline every aspect of transport operations from vehicle registration to real-time trip dispatch, maintenance workflows, fuel tracking, and analytics.

---

## 🚀 Features

### 🔐 Authentication and Role-Based Access Control
- Secure login/logout with session management
- Auto logout when browser is closed
- 4 distinct roles with different access levels:
  - **Fleet Manager** - Full access to everything
  - **Dispatcher** - Trips and dispatch management
  - **Safety Officer** - Driver compliance and license monitoring
  - **Financial Analyst** - Fuel, expenses, and cost analytics

### 🚛 Fleet Management
- Register vehicles with unique registration number validation
- Track vehicle type, load capacity, odometer, and acquisition cost
- Real-time status tracking: Available / On Trip / In Shop / Retired
- ROI calculation per vehicle (revenue vs operational cost)
- **Vehicle Document Management** - Upload RC Book, Insurance, PUC, Fitness Certificate and Route Permit with expiry tracking

### 🧑 Driver Management
- Complete driver profiles with license details and categories (LMV, HMV, HPMV, MGV)
- License expiry tracking with color-coded alerts
- Safety score visualization with progress bar
- **Email Reminders** - Send actual license expiry reminder emails via Gmail SMTP
- Bulk "Send All Reminders" with one click

### 🗺️ Trip Dispatch System
- Full trip lifecycle: Draft to Dispatched to Completed or Cancelled
- **9 Business Rule Validations:**
  - ❌ Retired/In Shop vehicles blocked from dispatch
  - ❌ Expired license drivers blocked
  - ❌ Suspended drivers blocked
  - ❌ Already On Trip vehicle/driver blocked
  - ❌ Cargo weight exceeding capacity blocked
  - ✅ Auto vehicle/driver status change on dispatch
  - ✅ Auto restore to Available on completion
  - ✅ Auto restore to Available on cancellation
  - ✅ Maintenance sets vehicle to In Shop automatically
- Live cargo capacity bar (green/amber/red)
- Trip timeline view with timestamps

### 🔧 Maintenance Workflow
- Multi-stage workflow: Pending to Approved to In Progress to Resolved or Rejected
- Priority levels: Low / Medium / High / Critical
- Auto vehicle status change to In Shop on approval
- Auto restore to Available on resolution

### ⛽ Fuel and Expense Tracking
- Log fuel fills with liters, cost, and odometer readings
- Track additional expenses: Toll, Parking, Fine, Maintenance, Other
- Summary cards showing total fuel cost, other expenses, and total operational cost
- CSV export for financial reporting

### 📊 Analytics Dashboard
- 5 KPI cards: Fleet utilization, Avg fuel efficiency, Revenue, Cost, Net Profit
- **6 Interactive Charts powered by Chart.js:**
  - Fleet Status Distribution (Doughnut)
  - Trip Status Distribution (Doughnut)
  - Fuel Efficiency by Vehicle (Bar)
  - Operational Cost by Vehicle (Bar)
  - Top Drivers by Trips Completed (Horizontal Bar)
  - Vehicle ROI (Bar)
- CSV export for full analytics report
- Print to PDF functionality

### 🎨 UI and UX
- 🌙 Dark mode toggle with localStorage persistence
- 🔍 Search, filter, and sort on all list pages
- 📥 CSV export on every module
- 🖨️ Print to PDF on vehicle detail and analytics pages
- ⚠️ Real-time alert banners for expired and expiring licenses and documents
- Role-based sidebar navigation
- Toast notifications for all actions
- Responsive design with Tailwind CSS

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Django 4.x |
| Database | SQLite |
| Frontend | HTML5, Tailwind CSS (CDN) |
| Charts | Chart.js |
| Icons | Tabler Icons |
| Email | Gmail SMTP via Django mail |
| Auth | Django custom user model |

---

## ⚙️ Setup and Installation

```bash
# 1. Clone the repository
git clone https://github.com/Agent-A345/transitops.git
cd transitops

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Run the server
python manage.py runserver
```

Open `http://127.0.0.1:8000` in your browser.

---

## 👥 User Roles and Access

| Feature | Fleet Manager | Dispatcher | Safety Officer | Financial Analyst |
|---|:---:|:---:|:---:|:---:|
| Dashboard | ✅ | ✅ | ✅ | ✅ |
| Fleet / Vehicles | ✅ | ❌ | ❌ | ❌ |
| Drivers | ✅ | ✅ | ✅ | ✅ |
| Trips | ✅ | ✅ | ❌ | ❌ |
| Maintenance | ✅ | ✅ | ❌ | ❌ |
| Fuel and Expenses | ✅ | ❌ | ❌ | ✅ |
| Analytics | ✅ | ✅ | ✅ | ✅ |

---

## 📁 Project Structure

```
transitops/
├── accounts/          # Custom user model, RBAC, decorators
├── vehicles/          # Vehicle CRUD, document management
├── drivers/           # Driver management, email reminders
├── trips/             # Trip dispatch system, business rules
├── maintenance/       # Maintenance workflow
├── fuel/              # Fuel logs and expense tracking
├── analytics/         # Charts, KPIs, reports
├── templates/         # All HTML templates
└── core/              # Settings, URLs
```

---

## 🏆 Built For

**Odoo Hackathon 2026**
> Solo entry by Atharva Pagar

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---
