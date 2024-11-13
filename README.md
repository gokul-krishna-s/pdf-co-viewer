# PDF Co-Viewer

PDF Co-Viewer is a real-time collaborative PDF viewing application built with Python, Flask, and Socket.IO. It allows multiple users to view and navigate through a PDF document simultaneously, with one user acting as the admin/presenter.

## Features

- Real-time synchronization of PDF viewing across multiple users
- Admin/presenter control for navigating through the PDF
- User option to follow the admin's navigation or browse independently
- PDF upload functionality for the admin

## Technologies Used

- Python 3.8+
- Flask
- Flask-SocketIO
- PDF.js
- Socket.IO (client-side)

## Installation

1. Clone the repository:

`git clone https://github.com/yourusername/pdf-co-viewer.git
cd pdf-co-viewer`


2. Create a virtual environment and activate it:

`python -m venv venv
source venv/bin/activate # On Windows, use venv\Scripts\activate`


3. Install the required packages:

`pip install -r requirements.txt`


## Usage

1. Start the Flask application:

`python app.py`


2. Open a web browser and navigate to `http://localhost:5000`.

3. To create a new session:
- Enter a session name and click "Create Session"
- Upload a PDF file when prompted

4. To join an existing session:
- Select a session from the list
- Enter your name and click "Join Session"
- Wait for the admin to approve your join request

5. As an admin:
- Navigate through the PDF using the "Previous" and "Next" buttons
- Approve or reject join requests from users

6. As a user:
- Choose to follow the admin's navigation or browse independently using the "Follow Admin" checkbox
- Navigate through the PDF using the "Previous" and "Next" buttons when not following the admin