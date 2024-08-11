# Use the official Python image.
FROM python:3.10.12

# Set environment variables.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory.
WORKDIR /app

# Install dependencies.
COPY . /app/
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# Expose the port that the app runs on.
EXPOSE 8000

# Start the Django application.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
