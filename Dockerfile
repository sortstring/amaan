# Base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Set the working directory in the container to /app
WORKDIR /app

COPY ./requirements.txt /tmp/requirements.txt

# Create a virtual environment and install dependencies
# Set the user to use when running this image
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp

# Add the contents in the app directory into the container at /app
COPY ./app /app

# Set the path to the virtual environment
ENV PATH="/py/bin:$PATH"
