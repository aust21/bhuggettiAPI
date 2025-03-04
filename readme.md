# bhuggetti (ba (like banana)-get + i)

The bhuggetti API allows people to submit interview questions, which will be used to help candidates prepare for interviews.

## Overview

This API allows contributors to:

- Submit new interview questions
- Update or delete existing questions
- Categorize questions by industry, difficulty, or job role
- Manage their submissions

## Features

- **User Authentication**: Secure login and authentication for contributors
- **Question Management**: CRUD (Create, Read, Update, Delete) operations on interview questions
- **Filtering & Sorting**: Retrieve questions based on categories, difficulty levels, and job roles
- **Admin Dashboard**: Manage user-submitted questions and moderate content

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive an access token
- `POST /auth/logout` - Logout a user

### API Endpoints

- Visit the API documentation [here](https://aust21.pythonanywhere.com/docs) to view the endpoints

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/aust21/bhuggettiAPI.git
   ```
2. Navigate to the project directory:
   ```sh
   cd bhuggettiAPI
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the application:
   ```sh
   flask run
   ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request to suggest improvements or report bugs.

## License

This project is licensed under the MIT License.
