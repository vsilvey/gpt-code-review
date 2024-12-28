# Use a lightweight Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /github/workspace

# Copy dependency file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY . .

# Optionally add the src directory to PYTHONPATH (if needed for imports)
ENV PYTHONPATH="${PYTHONPATH}:/github/workspace/src"

# Set entry point and default command
ENTRYPOINT ["python"]
CMD ["src/main.py"]