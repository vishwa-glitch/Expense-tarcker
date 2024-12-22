# Expense Tracker API

## Overview
The Expense Tracker API is a backend application that allows users to manage their expenses effectively. It provides secure endpoints to create, update, retrieve, and filter expenses. Users can categorize expenses, track payments, and apply date-based filters to view expenses over specific time periods.
For more details about the project roadmap and features, visit [Expense Tracker API Roadmap](https://roadmap.sh/projects/expense-tracker-api).
---

## Features
- **User Authentication:** Secure authentication using JWT (JSON Web Tokens).
- **Expense Management:**
  - Create, update, retrieve, and delete expenses.
  - Categorize expenses and add descriptions.
  - Filter expenses by date ranges, such as the past week, month, or custom ranges.
- **Payment Tracking:**
  - Record payment methods such as cash, credit card, and digital wallets.
- **Validation:**
  - Ensures expenses have positive amounts.
  - Prevents future-dated expenses.
- **Secure API:** All endpoints are protected and accessible only to authenticated users.

---

## Installation

### Prerequisites
- Python 3.8+
- Django 4+
- Django REST Framework
- Django REST Framework Simple JWT

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/vishwa-glitch/Expense-tracker.git
   cd Expense-tracker
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Apply migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

5. Access the application at `http://127.0.0.1:8000/`.

---

## API Endpoints

### Authentication
- **Obtain Token:**
  - `POST /api/token/`
  - Request body: `{ "username": "<username>", "password": "<password>" }`

- **Refresh Token:**
  - `POST /api/token/refresh/`
  - Request body: `{ "refresh": "<refresh_token>" }`

### Expense Management
- **Retrieve Expenses:**
  - `GET /api/expenses/`
  - Query parameters:
    - `filter`: `past_week`, `past_month`, `last_3_months`, or `custom`.
    - `start_date` and `end_date`: Required for `custom` filter.

- **Create Expense:**
  - `POST /api/expenses/`
  - Request body:
    ```json
    {
      "category": "FOOD",
      "amount": 50.00,
      "date": "2024-12-01",
      "description": "Lunch at a restaurant",
      "payment_methods": "CASH"
    }
    ```

- **Update Expense:**
  - `PUT /api/expenses/{id}/`
  - Request body: Similar to create expense.

- **Delete Expense:**
  - `DELETE /api/expenses/{id}/`

---

## Models

### Expenses
| Field            | Type           | Description                          |
|------------------|----------------|--------------------------------------|
| `user`           | ForeignKey     | Authenticated user who owns expense |
| `amount`         | DecimalField   | Expense amount                      |
| `category`       | CharField      | Expense category                    |
| `description`    | CharField      | Optional expense description         |
| `date`           | DateField      | Date of the expense                 |
| `payment_methods`| CharField      | Payment method used                 |

---

## Validation Rules
- Amount must be greater than zero.
- Date must not be in the future.
- Both category and payment method are required.

---

## Filtering
- **Past Week:** Filters expenses from the past 7 days.
- **Past Month:** Filters expenses from the past 30 days.
- **Last 3 Months:** Filters expenses from the past 90 days.
- **Custom Date Range:** Specify `start_date` and `end_date` query parameters.

---

## Contributing
Feel free to fork the repository and submit pull requests. Contributions are always welcome.

---

## License
This project is licensed under the MIT License.

---

## Contact
For any issues or queries, please reach out to [vishwa12550@gmail.com](mailto:vishwa12550@gmail.com).

