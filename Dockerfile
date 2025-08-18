# 1. Use the official Playwright image which includes all necessary system dependencies
# This image is based on Ubuntu 22.04 (Jammy) and includes Python
FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the requirements file and install our Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Install only the Playwright browser binaries (no system deps needed)
RUN playwright install

# 5. Copy the rest of the application code into the container
COPY . .

# 6. Expose the port the app runs on
EXPOSE 8000

# 7. Define the command to run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]