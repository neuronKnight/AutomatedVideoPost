#!/bin/bash

# Setup script for Video Automation System
echo "Setting up Video Automation System..."

# Create necessary directories
mkdir -p data/n8n
mkdir -p data/certbot/conf
mkdir -p data/certbot/www
mkdir -p shared/media

# Set proper permissions
chmod -R 777 data
chmod -R 777 shared/media

# Clone repositories if they don't exist
if [ ! -d "lib/social-auto-upload" ]; then
  echo "Cloning social-auto-upload..."
  mkdir -p lib
  git clone https://github.com/dreammis/social-auto-upload.git lib/social-auto-upload
fi

if [ ! -d "MoneyPrinterTurbo" ]; then
  echo "Cloning MoneyPrinterTurbo..."
  git clone https://github.com/harry0703/MoneyPrinterTurbo.git
fi

# Copy configuration files
if [ ! -f "config/moneyprinter/config.toml" ]; then
  echo "Copying MoneyPrinterTurbo configuration..."
  mkdir -p config/moneyprinter
  cp MoneyPrinterTurbo/config.example.toml config/moneyprinter/config.toml
  echo "Please edit config/moneyprinter/config.toml with your API keys"
fi

echo "Setup completed! Use 'make dev' to start the development environment."
