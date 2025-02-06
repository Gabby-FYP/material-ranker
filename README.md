# Material Ranker

Material Ranker is a project designed to rank course materials based on various criteria. It provides an web-interface to interact with the ranking system, allowing users to submit materials and retrieve rankings.

## Features


## Requirements

- Docker

## Setup and Installation

To set up the Material Ranker project using Docker, follow these steps:

1. **Clone the Repository**

   First, clone the repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/material-ranker.git
   cd material-ranker
   ```

2. **Build the Docker Image**

   Build the Docker image using the provided `Dockerfile`:

   ```bash
   docker compose build
   ```

3. **Run the Docker Container**

   Run the Docker container using the built image:

   ```bash
   docker compose up
   ```

   This command will start the application and map port 8000 of the container to port 8000 on your host machine.

4. **Access the Application**

   Once the container is running, you can access the web interface:

   ```
   http://localhost:8000/
   ```

   This will open the OpenAPI documentation where you can interact with the API.

## Configuration

The application can be configured using environment variables. You can set these variables in a `.env` file or directly in the Docker command.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
