#!/bin/bash

rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-available/default

# Write the environment variable to the key.pem file
echo "$PRIVATE_KEY" > /etc/nginx/certs/key.pem

# Ensure the correct permissions are set for the key file
chmod 600 /etc/nginx/certs/key.pem

# Start Nginx
nginx -g 'daemon off;'
