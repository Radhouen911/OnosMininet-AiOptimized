FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    requests \
    flask \
    networkx \
    numpy

# Copy RAVEN controller code
COPY . /app

CMD ["python", "raven_controller.py"]
