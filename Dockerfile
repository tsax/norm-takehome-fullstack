# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /norm-fullstack

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install uvicorn

# Ollama configuration (connects to host machine's Ollama service)
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434
ENV LLM_MODEL=llama3
ENV EMBED_MODEL=nomic-embed-text

# Copy the content of the local src directory to the working directory
COPY ./app /norm-fullstack/app
COPY ./docs /norm-fullstack/docs

# Command to run on container start
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]