# Hermius

##### *Currently a WIP. Expect bugs and errors to be present.
Hermius is a secure and anonymous chatroom service that allows users to communicate without revealing their identity. Users can choose to chat anonymously or create an account for additional features. All messages are end-to-end encrypted, ensuring that only encrypted messages are stored in the database.

## Features

- **Anonymous Chat**: Join chatrooms without creating an account.
- **Account Management**: Create an account for additional features like modifying account details.
- **End-to-End Encryption**: Messages are encrypted before being stored in the database.
- **Real-time Communication**: Powered by Flask and Socket.IO for real-time messaging.
- **User Profiles**: View and modify user profiles.
- **Room Management**: Create and join chatrooms with unique codes.

## Technologies Used

- **Backend**: Flask, SQLite
- **Frontend**: HTML, CSS (TailwindCSS), JavaScript
- **Real-time Communication**: Socket.IO

## Setup Instructions

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/TheRevanite/Hermius.git
    cd Hermius
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up the Database**:
    The database will be automatically set up when you run the application for the first time.

4. **Run the Application**:
    ```bash
    python app.py
    ```

5. **Access the Application**:
    Open your web browser and navigate to `http://localhost:5000`.

## File Structure

- **app.py**: Main application file containing routes and Socket.IO event handlers.
- **lib.py**: Contains encryption and decryption functions.
- **templates/**: Directory containing HTML templates for different pages.
- **static/**: Directory for static files like CSS and JavaScript.

## Encryption Details

Hermius currently uses a simple Caesar cipher for encrypting messages. In the future, we plan to implement more secure encryption methods like AES-256 and RSA.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.
