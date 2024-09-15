# Fantasy-Football

## Setup Instructions
### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/fantasy-football.git
cd fantasy-football
```
### 2. Create and Activate a Virtual Environment
```
python -m venv venv
source venv/bin/activate  # For Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
Make sure you have pip installed, then run:
```
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a ```.env``` file in the inner project directory where settings.py file resides of your project to store sensitive settings such as secret keys, database configurations, etc.
Example .env:
```
DEBUG=True
SECRET_KEY=<your-secret-key>
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1
```

### 5. Apply and Run Migrations
```
python manage.py makemigrations
python manage.py migrate
```
### 6. Create a Superuser (Optional)
```
python manage.py createsuperuser
```

### 7. Run the Development Server
```
python manage.py runserver
```

### 8. Access the Application
Access the application via postman or curl on the following base url followed by endpoint:
```
http://127.0.0.1:8000/
```

## Docker Instructions (Optional)
If using Docker, follow these steps:

1. Build the Docker Image
```
docker-compose build
```
2. Run the Docker Container
```
docker-compose up
```

## Running Test Cases
To run the test cases of the project, use:
```
pytest
```
