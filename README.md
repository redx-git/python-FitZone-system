# FitZone Gym Management System

A modular, file-based Python command-line management system designed for gym administration, class scheduling, membership tracking, and payment processing.

---

## Features by Role

### 1. System Administrator (`admin`)
* **Class Management:** Add, update, and remove fitness classes.
* **Trainer Management:** Register, update, and delete trainer profiles.
* **Data Inspection:** View full system logs and raw records for members, bookings, and payments.
* **Reporting:** Generate metrics on total registered members, class booking counts, and gross/net revenue.

### 2. Booking Officer (`booking`)
* **Member Registration:** Register new members with auto-generated IDs (`MB101...`).
* **Schedules & Class Capacity:** Browse active class listings.
* **Class Reservations:** Book member slots into fixed morning/afternoon shifts (`S1: 10:30–12:30`, `S2: 14:30–16:30`).
* **Booking Management:** Reschedule or cancel existing class reservations.

### 3. Accountant (`accountant`)
* **Payment Processing:** Record plan payments (`Basic: RM130`, `Standard: RM150`, `Premium: RM195`) with automated 8% SST calculation and auto-update member statuses to `Paid`.
* **Revenue Auditing:** Break down net income, SST tax liabilities, and grand total receipts.
* **Defaulter Tracking:** Generate unpaid membership reports matching active members against cleared transactions.
* **Package Analytics:** Analyze membership tier adoption rates and identify the most popular package.

### 4. Gym Member (`member`)
* **Class Viewing:** Inspect daily classes and assigned instructors.
* **Self-Service Booking:** Book or cancel personal gym session slots.
* **Member History:** View individual class schedules and itemized payment receipts.

---

## File Database Schema

Data is stored in pipe-delimited (`|`) plaintext files:

| File | Structure / Schema | Description |
| :--- | :--- | :--- |
| `staff.txt` | `Role|Email|Password` | User credentials for role verification |
| `members.txt` | `MemberID|FullName|PaymentStatus` | Registered member records |
| `classes.txt` | `ClassID|ClassName|TrainerName` | Class schedules and assignments |
| `trainers.txt` | `TrainerID|TrainerName` | Registered gym trainers |
| `bookings.txt` | `MemberID|ClassID|Day|Shift|TimeSlot` | Confirmed member class bookings |
| `payments.txt` | `PaymentID|MemberID|PlanName|TotalAmount|Date` | Transaction logs with SST |
| `log.txt` | Plaintext string per line | System audit trail with role timestamps |

---

## Getting Started

### Prerequisites
* Python 3.8+ installed on your system.

### Setup
1. Clone or download this repository to your local machine.
2. Ensure the working directory contains the main Python script.
3. Seed `staff.txt` with initial login credentials in the root directory:

```text
admin|admin@fitzone.com|admin123
booking|booking@fitzone.com|book123
accountant|accounts@fitzone.com|pay123
member|user@fitzone.com|user123