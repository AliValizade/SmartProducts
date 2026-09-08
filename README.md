# 🛒 SmartProducts

A Django-based e-commerce application focused on product management, customer accounts, discounts, orders, reviews, and multilingual support.

The project demonstrates how a modern online store can be structured using **Django**, **PostgreSQL**, and a modular application architecture.

---

## 📌 Overview

SmartProducts is a web-based store application built with Django.

The project includes separate applications for user/account management and store functionality.

The current implementation focuses on core e-commerce concepts such as:

* User authentication and accounts
* Product management
* Product categories
* Product images
* Discounts
* Customers
* Customer addresses
* Orders
* Product reviews and ratings
* Persian language support
* Multilingual configuration

---

## ✨ Features

### 👤 User & Account Management

The `accounts` application provides user-related functionality and uses a custom Django user model.

The project also integrates **Django Allauth** for authentication.

The custom user model includes additional information such as:

* Phone number
* Address

---

### 📦 Product Management

The store application provides product-related models including:

* Products
* Categories
* Product images
* Discounts

Products contain information such as:

* Name
* Category
* Slug
* Description
* Price
* Inventory
* Active status
* Creation and modification dates
* Product images
* Discounts

---

### 🗂️ Categories

Products can be organized into categories.

Categories also support hierarchical relationships through parent/child relationships.

---

### 💰 Discounts

The project provides a dedicated discount model that can be associated with products.

---

### 👥 Customers

Customer information is separated from the authentication model and includes additional information such as:

* Phone number
* Birth date

Customer addresses include:

* Province
* City
* Street

---

### 🛍️ Orders

The project includes an order model containing information such as:

* Customer
* Payment status
* Customer information
* Address
* City
* Province
* Postal code
* Order notes
* Creation and modification timestamps

---

### ⭐ Product Ratings

Products support customer comments and star-based rating aggregation.

---

### 🌐 Multilingual Support

The project is configured for internationalization and includes:

* Persian (`fa`)
* English (`en`)

The default project language is configured as Persian.

The project also uses Django Rosetta for translation management.

---

## 🏗️ Architecture

The project follows Django's application-based architecture:

```text
SmartProducts/
│
├── accounts/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── store/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
└── .gitignore
```

---

## 🧩 Main Applications

| Application | Responsibility                                       |
| ----------- | ---------------------------------------------------- |
| `accounts`  | User and account management                          |
| `store`     | Products, customers, orders and store-related models |
| `config`    | Django project configuration                         |

---

## 🛠️ Technology Stack

### Backend

* Python
* Django 5.1

### Database

* PostgreSQL

### Authentication

* Django Authentication
* Django Allauth

### Forms & UI

* Django Crispy Forms
* Bootstrap integration

### Internationalization

* Django i18n
* Django Rosetta
* Persian / English support
* Jalali date support

### Development Tools

* Django Debug Toolbar
* Python Dotenv
* Environs

---

## 📋 Requirements

The project currently uses a pinned dependency list in `requirements.txt`.

Major dependencies include:

```text
Django 5.1.3
django-allauth
django-crispy-forms
django-debug-toolbar
django-jalali-date
django-rosetta
psycopg2
Pillow
python-dotenv
environs
```

For the complete dependency list, see:

```text
requirements.txt
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/AliValizade/SmartProducts.git
cd SmartProducts
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

The project reads sensitive configuration values from environment variables.

Create a `.env` file in the project root.

Example:

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True

DATABASE_NAME=smartproducts
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DJANGO_PORT=5432
```

> Never commit real credentials, passwords, or secret keys to the repository.

---

## 🗄️ Database Setup

The project is configured to use PostgreSQL.

After configuring the database and environment variables, run:

```bash
python manage.py migrate
```

Create an administrative user:

```bash
python manage.py createsuperuser
```

---

## ▶️ Running the Application

Start the Django development server:

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

---

## 🧪 Testing

The project contains Django test modules in the applications.

Run the test suite with:

```bash
python manage.py test
```

> Test coverage and automated CI are planned improvements for the project.

---

## 🔎 Project Highlights

SmartProducts demonstrates several practical Django development concepts:

* Custom user models
* Django application architecture
* Relational data modeling
* Product and inventory management
* Order management
* Authentication
* PostgreSQL integration
* Internationalization
* Persian localization
* Media handling
* Model relationships
* Django administration

---

## 🚀 Future Improvements

Potential improvements for future versions include:

* Shopping cart improvements
* Payment gateway integration
* Order tracking
* Advanced product search
* Product filtering
* REST API
* Automated testing and coverage
* CI/CD with GitHub Actions
* Improved responsive UI
* Containerized deployment with Docker
* Production deployment configuration
* Better documentation and screenshots

---

## 🎓 Learning Context

This project represents practical work with Django and demonstrates the implementation of an e-commerce application's core domain models and supporting infrastructure.

It is also part of the author's broader experience with Python and Django web application development.

---

## 👨‍💻 Author

**Ali Valizadeh**

Python Developer · Django · AI, NLP & Automation · University Instructor

GitHub:

https://github.com/AliValizade
