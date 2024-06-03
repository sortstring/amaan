# Amaan

## Getting Started

Follow these steps to set up and run the Amaan application:

### Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/sortstring/amaan.git
cd amaan
```

### Build the Docker Containers

Build the Docker containers using Docker Compose:

```bash
docker compose build
```

### Start the Docker Containers

Start the Docker containers in detached mode:

```bash
docker compose up -d
```

### View Logs

To view the logs of the web container, use the following command:

```bash
docker compose logs web -f
```

---