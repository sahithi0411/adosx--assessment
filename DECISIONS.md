# Technical Decisions

## 1. Django REST Framework for the Backend

**Decision:** I used Django REST Framework to build the backend API.

**Reason:** It provides a structured way to create REST APIs and serialize data into JSON, which can be consumed by the React frontend.

**Alternative:** Flask.

## 2. SQLite as the Database

**Decision:** I selected SQLite for storing imported records.

**Reason:** It is lightweight, easy to configure, and sufficient for this assessment.

**Alternative:** PostgreSQL.

## 3. React.js for the Frontend

**Decision:** I used React.js to build the reconciliation dashboard.

**Reason:** React components and state management make it easier to display records, update filters, and sort data dynamically.

**Alternative:** Django templates.

## 4. Organization-Based Record Matching

**Decision:** I matched records using both organization ID and normalized record ID.

**Reason:** The same record reference should not be considered a match across different organizations. This also helps prevent cross-organization data from being treated as a valid match.

**Alternative:** Matching only by record ID.

## 5. Record Reference Normalization

**Decision:** I normalized record references before comparing them.

**Reason:** References may have different formats, such as `REC-1034`, `rec1034`, and ` REC - 1070 `. Normalization helps identify equivalent references.

**Alternative:** Direct string comparison.

## 6. Comparing System A Total Value With System B Value

**Decision:** I compared `SystemA.total_value` with `SystemB.value`.

**Reason:** I treated the total value in System A as the corresponding value to compare against System B.

**Alternative:** Comparing System B value with System A base value.

## 7. Separate Disagreement Categories

**Decision:** I represented missing records, orphan entries, duplicate entries, and value mismatches using separate reason codes.

**Reason:** This makes the results easier to filter, understand, test, and display in the dashboard. A duplicate entry can also have a value mismatch, so both reasons may be reported.

**Alternative:** Combining all disagreements into a single generic category.

## 8. Axios for API Communication

**Decision:** I used Axios to connect the React frontend with the Django backend.

**Reason:** It simplifies HTTP requests and response handling.

**Alternative:** The native Fetch API.