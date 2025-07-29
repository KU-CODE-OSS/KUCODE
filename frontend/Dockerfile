# Development Dockerfile for hot-reload  
FROM quay.io/fedora/fedora:38

# Install Node.js and npm
RUN dnf update -y && \
    dnf install -y nodejs npm && \
    dnf clean all

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install all dependencies (including dev dependencies)
RUN npm install

# Copy source code
COPY . .

# Expose port 5173 (Vite default)
EXPOSE 5173

# Start development server with host 0.0.0.0 to allow external access
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 