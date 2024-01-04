FROM python:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /frontend

COPY requirements.txt /frontend/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port
EXPOSE 8000
