# FitnessMaster 🏋️‍♂️

FitnessMaster is a comprehensive Gym Management System built with Django. It provides a robust platform for managing gym operations, trainers, customers, packages, and more.

## 🚀 Features

- **User Roles**: Admin, Trainer, and Customer dashboards.
- **Package Management**: Create and manage different gym membership packages.
- **Trainer Management**: track trainers and their specializations (Yoga, Gym, Zumba).
- **Diet & Exercise Plans**: Trainers can assign custom diet and workout plans to customers.
- **Payment Integration**: Supports Razorpay for online payments and cash payment tracking.
- **Notice Board**: Send notifications to all or specific groups of users via email.
- **Feedback System**: Gather customer ratings and messages.
- **Multilingual Support**: Supports both English and Hindi.
- **Equipment Tracking**: monitor gym equipment status and maintenance.

## 🛠️ Tech Stack

- **Backend**: Django (Python)
- **Database**: SQLite3 (default)
- **Frontend**: HTML, CSS, JavaScript
- **Payments**: Razorpay API
- **Environment**: python-dotenv

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dhyan2309/FITNESSMASTER.git
   cd FITNESSMASTER
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables**:
   Create a `.env` file in the root directory and add:
   ```env
   SECRET_KEY=your_secret_key
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   RAZORPAY_KEY_ID=your_key_id
   RAZORPAY_KEY_SECRET=your_key_secret
   ```

4. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start the server**:
   ```bash
   python manage.py runserver
   ```

## 📧 Contact

For any queries, please reach out to the project maintainer.
