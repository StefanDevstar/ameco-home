# Real Estate Lead Collector

This project is a Real Estate Lead Collector built using Python and MongoDB. It allows you to collect and manage leads for your real estate business.

## Features

- Lead collection: Collect leads by capturing information such as name, contact details, property preferences, etc.
- Database storage: Store the collected leads in a MongoDB database for easy retrieval and management.
- Search and filter: Search and filter leads based on various criteria such as location, budget, property type, etc.
- Export leads: Export leads to CSV or Excel format for further analysis or sharing with team members.

## Prerequisites

Before running the project, make sure you have the following installed:

- Python 3.x: [Download Python](https://www.python.org/downloads/)
- MongoDB: [Download MongoDB](https://www.mongodb.com/try/download/community)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/sprin-g-reen/real-estate-lead-collector.git
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Configure the MongoDB connection:

    - Open the `config.py` file.
    - Update the `MONGO_URI` variable with your MongoDB connection URI.

4. Configure Static:
    - Make sure property_data folder exisits

## Usage

1. Run the application:

    ```bash
    python3 app.py
    ```

2. Access the application in your web browser:

    ```
    http://localhost:5000
    ```

3. Start collecting leads by filling out the lead capture form.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
