# Step 1: Use an official Python runtime as a parent image
FROM python:3.12-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container at /app
COPY . /app

# Step 4: Install any needed dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Expose the port the app runs on (if your API uses port 5000, change it accordingly)
EXPOSE 5000

# Step 6: Define environment variable to use the correct environment (optional)
# ENV FLASK_ENV=production

# Step 7: Run app.py when the container launches
CMD ["python", "app.py"]

