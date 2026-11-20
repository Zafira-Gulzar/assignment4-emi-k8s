# Use an official slim/alpine base image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install only production dependencies
RUN npm install --omit=dev

# Copy the rest of the application code
COPY . .

# Set the user to non-root (node user is built-in in Node.js images)
USER node

# Expose the application port
EXPOSE 8080

# Start the application
CMD ["node", "server.js"]
