## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python (latest version)
- Node.js and npm

## Setup

To install this project, follow these steps:

### Backend Setup (Flask)

1. Clone the repository:
    ```bash
    git clone https://github.com/neptunerv/CS411_Project.git
    cd CS411_Project
    ```

2. Set up a virtual environment:
    ```bash
    cd server
    python -m venv venv
    ```

3. Activate the virtual environment:
    - On Windows:
      ```bash
      .\venv\Scripts\activate
      ```
    - On macOS and Linux:
      ```bash
      source venv/bin/activate
      ```

4. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Frontend Setup (React Vite)

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
