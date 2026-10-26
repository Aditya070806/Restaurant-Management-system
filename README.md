# Restaurant Management System

A Python and MySQL project that I'm developing to learn database integration, application design, and software development through practical experience.

**Status: Work in Progress 🚧**

This project will evolve as I learn new concepts and add features. The goal is to build a functional restaurant management system incrementally, improving its organization, reliability, and usability along the way.

## Current Development

The project currently contains Python modules for:

- **Restaurant:** Retrieving and displaying menu information from MySQL.
- **Customers:** Handling customer-related workflows.
- **Orders:** Implementing order-related functionality.

The application and its features are still under development.

## Tech Stack

- Python
- MySQL
- MySQL Connector/Python
- python-dotenv
- Git and GitHub

## Project Structure

```text
restaurant-management-system/
├── restaurant.py
├── customers.py
├── orders.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

The project structure may change as the application becomes more capable.

## Setup

### 1. Prerequisites

Install Python and MySQL. The application also requires a MySQL database with the tables expected by the current code.

### 2. Install dependencies

Clone the repository, enter the project directory, and install its dependencies:

```bash
pip install -r requirements.txt
```

Using a virtual environment is recommended.

### 3. Configure environment variables

Create a `.env` file based on `.env.example` and configure your MySQL connection details.

Never commit your actual `.env` file or database credentials.

### 4. Run the application

Start with:

```bash
python restaurant.py
```

The available functionality depends on the current development version and database setup.

## Development Goals

As the project evolves, I intend to work on:

- Improving customer and order workflows.
- Strengthening input validation and error handling.
- Making database operations more reliable.
- Improving the command-line interface.
- Organizing the application into clearer, maintainable components.
- Adding documentation and database setup instructions.
- Testing features and handling edge cases.
- Exploring more advanced Python and SQL concepts when appropriate.

These are development goals, not claims that the features are already implemented.

## Learning Objectives

Through this project, I'm learning how to:

- Connect Python programs to relational databases.
- Perform SQL operations from Python.
- Structure a multi-file application.
- Manage configuration securely.
- Debug and improve an existing codebase.
- Use Git and GitHub to track changes over time.

## Project Philosophy

Build incrementally. Test changes. Understand the code. Improve the design when the project needs it.

This repository documents both the application and my progress as a developer.

---

**Project status:** Actively developing and learning.