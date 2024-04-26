FROM postgres:latest

# Set environment variables
ENV POSTGRES_DB=mydatabase
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword

# Copy data and change ownership to the postgres user
COPY ./data /var/lib/postgresql/data
RUN chown -R postgres:postgres /var/lib/postgresql/data
RUN chmod -R 777 /var/lib/postgresql/data
