## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python (latest version)
- Node.js and npm

## Setup

To install this project, follow these steps:

### Backend Setup (Flask)

1. Clone the repository:
    ```bash
    git clone https://github.com/justin9668/Attendance-App.git
    cd Attendance-App
    ```

2. Set up a virtual environment:
    ```bash
    cd server
    python3 -m venv venv
    ```

3. Activate the virtual environment:
    - On macOS and Linux:
      ```bash
      source venv/bin/activate
      ```
    - On Windows:
      ```bash
      .\venv\Scripts\activate
      ```

4. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

5. Create a `.env` file in the `server` directory and add the following environmental variables:
    ```
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    SECRET_KEY=your_secret_key
    DATABASE_URL=your_database_url
    GOOGLE_API_KEY=your_google_api_key
    ```

## Frontend Setup (React Vite)

1. Navigate to the frontend directory:
    ```bash
    cd client
    ```

2. Install NPM packages:
    ```bash
    npm install
    ```

## Running the Application

To run the application, follow these steps:

### Backend

1. Ensure your virtual environment is activated and navigate to the directory containing `main.py`.
2. Run the Flask application:
    ```bash
    python3 main.py
    ```

### Frontend

1. Navigate to the frontend directory.
2. Start the Vite server:
    ```bash
    npm run dev
    ```

The React application will be available at `http://localhost:5173`, and the Flask API at `http://127.0.0.1:5000`.

## Building the Project

To build the project for production:

### Backend

Flask does not need a build process. Just ensure all configurations are set for production.

### Frontend

1. Navigate to the frontend directory.
2. Build the React application:
    ```bash
    npm run build
    ```

This will create a `dist` folder containing your production-ready frontend.
