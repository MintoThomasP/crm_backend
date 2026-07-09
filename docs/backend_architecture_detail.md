# Detailed Backend Architecture Documentation

This document provides a highly detailed walkthrough of the server-side Django architecture, its modular apps, models, serializers, views, and data handling processes.

---

## 1. Modular App Modules

### A. Accounting Module (`app_accounting/`)
Handles the financial general ledger database, double-entry ledgers, direct cash flows, expenses, claims, and manual journals.

#### 1. Data Models (`models.py`)
* **`Account`**:
  * Fields: `AccountId` (UUID/Primary), `Code` (unique account reference), `Name` (display name), `Type` (Asset, Liability, Equity, Revenue, Expense), `IsCashOrBank`.
* **`JournalEntry`**:
  * Fields: `JournalEntryId`, `Date` (transaction date), `ReferenceNumber` (unique batch ID), `Source` (e.g. manual, invoice, payment), `Narration`.
* **`JournalItem`**:
  * Fields: `JournalItemId`, `JournalEntryId` (foreign key to Entry), `AccountId` (foreign key to Account), `Debit` (decimal string), `Credit` (decimal string), `ClientId`.

#### 2. Serializers (`serializers.py`)
* **`AccountSerializer`**: Maps accounts for select lists.
* **`JournalEntrySerializer`**: Performs recursive parsing of transaction lines, ensuring that net debits minus net credits equal exactly zero before entry database persistence.

#### 3. Views & Logic (`views.py`)
* **`saveJournalEntry()` / `CreateJournalEntryApi()`**: 
  * Receives transaction splits payload.
  * Begins database transaction block.
  * Validates ledger integrity.
  * Updates related cash books when asset codes are impacted.

---

### B. Blog Module (`app_blog/`)
Serves as the database API layer for the frontend builder workspace.

#### 1. Data Models (`models.py`)
* **`CMSPage`**:
  * Fields: `id`, `title`, `slug` (unique indexing endpoint), `json_data` (visual canvas block tree configurations), `html_content` (pre-compiled HTML code ready for public rendering).
* **`Category`**:
  * Fields: `id`, `name`, `slug`, `parent_id` (foreign key to self), `description`.

#### 2. Views & Logic (`views.py`)
* **`getPageById()`**: Serves structured JSON configurations.
* **`updatePage()`**: Updates block configurations and compiles static web-page formats.

---

### C. Login & Security Module (`app_login/`)
Manages system authorization, user credential validation, and JWT token issuing.

#### 1. Data Models (`models.py`)
* **`Login`**:
  * Fields: `LoginId`, `EmailId`, `Password` (salted hash), `UserType` (reference to default role keys).
* **`LoginHistory`**:
  * Fields: `HistoryId`, `LoginId`, `IPAddress`, `Timestamp`.

#### 2. Views & Logic (`views.py`)
* **`loginApi()`**: 
  * Parses credential JSON payload.
  * Validates credentials against table records.
  * Creates authentication logs.
  * Generates web token response.

---

## 2. API Design & Middleware Utilities

### A. Automatic DB Retries (`@retry` decorator)
To prevent lockouts in concurrent execution spaces (e.g. general ledger debit updates), the system utilizes a retry decorator:

```python
def retry(retries=3, delay=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Executes db call.
            # Catches operational deadlocks and sleeps for 2 seconds before retrying up to 3 times.
```

### B. Serializer Schema Validations
REST endpoints rely heavily on Serializer constraint checking. For example, during direct expense postings (`app_accounting/views.py`), the request is parsed through `ExpenseSerializer`:
* Verifies `Debit Account Type` corresponds to "Expense".
* Verifies `Credit Account Type` is marked as `IsCashOrBank = True`.
* Ensures decimal values are valid positive numbers.
