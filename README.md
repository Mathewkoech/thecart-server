# Portfolio Project

## Description

This portfolio project is a comprehensive web application featuring a robust backend built with Django. It showcases my skills in backend development and includes functionalities like user authentication, product management, cart functionality, and order processing.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [License](#license)
- [Contact](#contact)

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL
- Django 5.0

### Backend Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/Mathewkoech/thecart-server.git
    cd thecart-server
    ```

2. Create and activate a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install backend dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:

    Create a `.env` file in the root directory and add the necessary environment variables. For example:

    ```env
    SECRET_KEY=your_secret_key
    DATABASE_URL=your_database_url
    DEBUG=True
    ```

5. Apply database migrations:

    ```bash
    python manage.py migrate
    ```

6. Run the development server:

    ```bash
    python manage.py runserver
    ```

## Features

- **User Authentication**: Secure login and registration using Django Allauth.
- **Product Management**: Admin interface for managing products, including details like images, descriptions, and pricing.
- **Cart Functionality**: Users can add products to their cart and manage quantities.
- **Order Processing**: Users can place orders and view order history.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

If you have any questions or feedback, feel free to reach out to me at [mathewkoech55@gmail.com](mailto:mathewkoech55@gmail.com).

## Authors

mathekoech55@gmail.com
debaycisse@gmail.com
