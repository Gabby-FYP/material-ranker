# Material Ranker

Material Ranker is a project designed to rank course materials based on various criteria. It provides a web interface for users to submit materials and retrieve rankings.

## Features

- Rank course materials based on various criteria.
- Submit and retrieve rankings through a web interface.

## Requirements

- Docker

## Setup and Installation

To set up the Material Ranker project using Docker, follow these steps:

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/material-ranker.git
cd material-ranker
```

### 2. Build the Docker Image

Build the Docker image using the provided `Dockerfile`:

```bash
docker compose build
```

### 3. Run the Docker Container

Run the Docker container using the built image:

```bash
docker compose up
```

This command will start the application and map port `8000` of the container to port `8000` on your host machine.

### 4. Access the Application

Once the container is running, you can access the web interface:

```
http://localhost:8000/
```

This will open the OpenAPI documentation where you can interact with the API.

## Database Migrations

To manage database migrations using Alembic, follow these steps:

### 1. Ensure Models are Imported

Make sure your models are imported in the Alembic environment file (`src/alembic/env.py`). This is necessary for Alembic to detect changes in the models.

### 2. Create a New Migration

Use the following command to autogenerate a new migration based on changes in your models:

```bash
alembic revision --autogenerate -m "<message>"
```

Replace `<message>` with a descriptive message for the migration.

### 3. Apply Migrations

To apply the latest migrations and update the database schema, run:

```bash
alembic upgrade head
```

### 4. Downgrade a Migration

If you need to revert a migration, use the following command:

```bash
alembic downgrade -1
```

This command will revert the last applied migration.

## Configuration

The application can be configured using environment variables. You can set these variables in a `.env` file or directly in the Docker command.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

