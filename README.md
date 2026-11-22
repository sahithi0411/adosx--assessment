# DealerOS Reconciliation Dashboard

## 1. Project Overview

DealerOS Reconciliation is a full-stack application that compares records from two different systems, System A and System B.

The application identifies disagreements between the systems and displays them in a dashboard.

The main goal is to help users identify missing records, duplicate entries, orphan records, and value mismatches.

## 2. Technologies Used

**Backend**
- Python
- Django
- Django REST Framework
- SQLite

**Frontend**
- React.js
- JavaScript
- HTML
- CSS
- Axios
- Lucide React

## 3. Project Structure

```text
adosx-assessment/
│
├── backend/
│   ├── config/
│   ├── reconciliation/
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── index.html
│
├── data/
│   ├── locations.csv
│   ├── system_a.csv
│   └── system_b.csv
│
├── README.md
└── DECISIONS.md
```

## 4. Features Implemented

- Imported CSV data from System A, System B, and Locations.
- Normalized record references to support different reference formats.
- Compared records using organization and record identifiers.
- Identified missing records in System B.
- Identified orphan entries in System B.
- Identified duplicate entries in System B.
- Identified value mismatches between the systems.
- Created a REST API to return disagreement records.
- Developed a React dashboard to display disagreements.
- Added filters based on disagreement reason.
- Added sorting based on System A value.
- Added currency formatting using Indian Rupees.
- Added summary cards and icons.

## 5. How to Run the Project

### Backend Setup

Open a terminal and navigate to the backend folder.

```powershell
cd backend
```

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Apply migrations:

```powershell
python manage.py migrate
```

Import the CSV data:

```powershell
python manage.py import_csv --data-dir ..\data
```

Start the Django server:

```powershell
python manage.py runserver
```

Backend API:

http://127.0.0.1:8000/api/disagreements/

### Frontend Setup

Open another terminal and navigate to the frontend folder.

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the React development server:

```powershell
npm run dev
```

Open:

http://localhost:5173/

## 6. Running Tests

Navigate to the backend folder and execute:

```powershell
python manage.py test reconciliation
```

The tests cover the four disagreement types:
- Missing in System B
- Orphan in System B
- Duplicate entries in System B
- Value mismatch

## 7. What I Built

I implemented the Django backend, CSV import functionality, reconciliation logic, REST API, and React dashboard.

The dashboard provides summary information, disagreement filtering, value sorting, and a detailed comparison table.

## 8. What Is Not Implemented

- User authentication and authorization.
- A frontend interface for uploading CSV files.
- Advanced handling and display of every possible invalid CSV row.
- Production deployment and production database configuration.

## 9. How I Worked With an AI Agent

I used an AI assistant as a development guide while building the application.

I worked step by step, asked for explanations of unfamiliar concepts, reviewed suggested code, and ran commands and tests to verify the implementation.

I made the final changes in my local project and checked the application through the browser and backend terminal.

## 10. AI Agent Mistakes

One issue during development was that the initial frontend styling retained default Vite CSS, which prevented the intended dashboard design from appearing correctly. I corrected the CSS and verified the updated dashboard in the browser.

## 11. Least Confident Part

I am least confident about handling all possible dirty CSV data cases, especially invalid references and rows with missing or unparseable values.

## 12. What I Would Improve With One Extra Day

I would improve CSV validation and error handling so that every source row is preserved, including rows with invalid or unknown location references.

I would also improve tenant-specific data access, add more edge-case tests, and improve the dashboard further.