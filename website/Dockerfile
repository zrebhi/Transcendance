FROM python:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /website

COPY requirements.txt /website/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000
