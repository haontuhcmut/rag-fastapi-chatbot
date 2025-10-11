FROM python:3.13

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python packages with retry mechaism
RUN pip install --no-cache-dir -r requirements.txt || \
    (echo "Retrying in 5 seconds..." && sleep 5 && pip install --no-cache-dir -r requirements.txt) || \
    (echo "Retrying in 10 seconds..." && sleep 10 && pip install --no-cache-dir -r requirements.txt)

# Install python packages cache
RUN pip install "huggingface_hub[cli]" transformers

# Copy entrypoint script frist
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Copy the rest of the application
COPY . .

## Create uploads directory
#RUN mkdir -p uploads
#RUN mkdir -p models

# Set Python path and environment
ENV PYTHONPATH=/app
ENV ENVIRONMENT=development

# Run the application
ENTRYPOINT ["./entrypoint.sh"]






