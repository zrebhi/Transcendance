# Dockerfile for Nginx Service
FROM nginx:latest

# Remove default Nginx configuration files
RUN rm /etc/nginx/conf.d/default.conf
RUN rm /etc/nginx/nginx.conf

# Copy custom Nginx configuration files from the host
COPY ./default.conf /etc/nginx/conf.d/
COPY ./nginx.conf /etc/nginx/
COPY ./certs /etc/nginx/certs
