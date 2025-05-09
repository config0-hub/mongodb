#!/bin/bash
# MongoDB 7.0 Installation Script for Ubuntu (using jammy repository)

# Function to check for root privileges
check_root() {
  if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root or with sudo privileges."
    exit 1
  fi
}

# Main installation function
install_mongodb() {
  # Update system packages
  echo "Updating system packages..."
  apt update || {
    echo "Error: Failed to update system packages."
    exit 1
  }

  # Install dependencies
  echo "Installing dependencies..."
  apt-get install -y gnupg curl || {
    echo "Error: Failed to install dependencies."
    exit 1
  }

  # Add MongoDB GPG key
  echo "Adding MongoDB GPG key..."
  curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor || {
    echo "Error: Failed to add MongoDB GPG key."
    exit 1
  }

  # Add MongoDB repository
  echo "Adding MongoDB repository..."
  echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
    tee /etc/apt/sources.list.d/mongodb-org-7.0.list || {
    echo "Error: Failed to add MongoDB repository."
    exit 1
  }

  # Update package lists
  echo "Updating package lists..."
  apt-get update || {
    echo "Error: Failed to update package lists after adding MongoDB repository."
    exit 1
  }

  # Install MongoDB
  echo "Installing MongoDB packages..."
  apt-get install -y mongodb-org || {
    echo "Error: Failed to install MongoDB packages."
    exit 1
  }

  # Start MongoDB service
  echo "Starting MongoDB service..."
  systemctl start mongod || {
    echo "Error: Failed to start MongoDB service."
    exit 1
  }
  
  # Enable MongoDB service to start on boot
  echo "Enabling MongoDB service to start on boot..."
  systemctl enable mongod || {
    echo "Error: Failed to enable MongoDB service."
    exit 1
  }

  # Verify installation
  echo "Verifying MongoDB installation..."
  mongod --version || {
    echo "Warning: MongoDB seems to be installed but the mongod command failed."
  }

  echo "MongoDB 7.0 installation completed successfully!"
  echo "MongoDB service status:"
  systemctl status mongod --no-pager
}

# Main execution
check_root
install_mongodb

exit 0