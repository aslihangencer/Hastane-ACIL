# 🏥 Hospital ER Automation System (PRO Edition)

![Hospital ERP Banner](https://img.shields.io/badge/Meditech-Style-blue?style=for-the-badge&logo=meditech)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30-FF4B4B?style=for-the-badge&logo=streamlit)
![SQL Server](https://img.shields.io/badge/SQL_Server-Enterprise-CC2927?style=for-the-badge&logo=microsoft-sql-server)

A production-ready, medical-grade Emergency Department (ED) ERP system built with a modular CQRS-inspired architecture. This system provides a professional user interface based on Meditech/Epic aesthetics, rule-based triage scoring, and real-time bed management.

## ✨ Key Features

- **🚀 Enterprise App Shell**: Sticky navigation, role-based sidebars, and real-time notification hub.
- **⚡ Smart Triage Engine**: Rule-based medical scoring system with symptom-weight analysis.
- **📊 Advanced Analytics**: Interactive dashboards for hourly patient density and triage distribution.
- **🛏 Live Bed Grid**: Visual heatmap of room/bed occupancy with color-coded status.
- **🕒 Real Flow Tracking**: Automated state machine (Registered -> Triaged -> Treated -> Discharged).
- **🛡 SQL Safe Mode**: Dynamic schema introspection to prevent runtime column mismatches.
- **📜 Medical Audit Log**: Masked sensitive data scrubbing and comprehensive activity tracking.

## 🏗 Architecture

The system follows a clean, modular architecture:

- `core/`: Connectivity (Stitch), Security (Auth/Session), and UI Constants.
- `services/`: Business logic (Triage, Discharge, Analytics, Notifications).
- `data/`: CQRS separated Read and Write repositories.
- `ui/`: Premium components and role-specific pages.

## 🛠 Installation

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd Acil_Servis_App
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**:
   - Ensure SQL Server is running.
   - Run the provided schema scripts (if any) or ensure `HastaneAcilServis` database exists.
   - Configure connection in `core/config.py` or `.env`.

4. **Run Application**:
   ```bash
   streamlit run app.py
   ```

## 🔒 Security

- Role-Based Access Control (Admin, Doctor, Nurse).
- Session idle timeout (15 mins).
- TC Identity Number masking in logs.
- SQL Injection protection via parameterized queries.

---
© 2026 Meditech Style ERP Systems | Built for Clinical Excellence
