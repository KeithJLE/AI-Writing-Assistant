FROM node:24-bookworm-slim

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json .

# Install dependencies
RUN npm install

# Don't copy application code in development - volume mount handles this
# COPY . .

# Expose port
EXPOSE 5173

# Command to run the application with polling for file changes (Windows compatibility)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
