# 🧾Thoth API

A Python API built with **FastAPI** to read and extract data from Receipts.

## 💻 Prerequisites

To run this project, you only need to have **Python** installed on your computer.

* [Download Python (3.8+)](https://www.python.org/downloads/)

---

## ⚙️ Setup & Installation

Follow these steps to set up your local environment.

### 1. Create a Virtual Environment

The virtual environment isolates the project dependencies from your system.

**On Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate

```

**On Linux or Mac:**

```bash
python3 -m venv .venv
source .venv/bin/activate

```

### 2. Install Dependencies

Run the command below to install FastAPI, Uvicorn (the server), and the library for handling file uploads:

```bash
pip install fastapi uvicorn python-multipart

```

---

## ▶️ How to Run

With the virtual environment activated and dependencies installed, start the server using the following command:

```bash
uvicorn app.main:app --reload

```

* **`app.main:app`**: Points to the `app` object inside the `app/main.py` file.
* **`--reload`**: Makes the server restart automatically whenever you change the code (useful for development).

### 📍 Access the API

Once the server is running, open your browser and go to:

👉 **http://localhost:8000/docs**

This will open the interactive Swagger UI where you can test your endpoints.
