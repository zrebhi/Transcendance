FROM python:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /game

COPY requirements.txt /game/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port
EXPOSE 8000
