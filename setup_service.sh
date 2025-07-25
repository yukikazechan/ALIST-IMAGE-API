#!/bin/bash
set -e

echo "--- Alist Image API systemd Service Setup ---"

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script with sudo."
  exit 1
fi

# Get current user and group
CURRENT_USER=$(logname)
CURRENT_GROUP=$(id -gn "$CURRENT_USER")

# Get the absolute path of the project directory
PROJECT_DIR=$(pwd)

# --- Force Rebuild Frontend ---
echo "Forcing a rebuild of the frontend to ensure it's up-to-date..."
cd frontend
npm run build
cd ..
echo "Frontend rebuild complete."

# Create the service file from the template
echo "Creating service file..."
sed -e "s|__USER__|$CURRENT_USER|g" \
    -e "s|__GROUP__|$CURRENT_GROUP|g" \
    -e "s|__WORKING_DIRECTORY__|$PROJECT_DIR|g" \
    alist-image-api.service.template > alist-image-api.service

# Move the service file to the systemd directory
echo "Installing service file to /etc/systemd/system/..."
mv alist-image-api.service /etc/systemd/system/alist-image-api.service

# --- Grant Permissions ---
echo "Granting ownership of the project directory to the service user..."
chown -R "$CURRENT_USER:$CURRENT_GROUP" "$PROJECT_DIR"
echo "Permissions granted."

# Stop the service if it's already running
if systemctl is-active --quiet alist-image-api.service; then
    echo "Stopping existing service..."
    systemctl stop alist-image-api.service
fi

# Reload systemd, enable and start the service
echo "Reloading systemd and starting the service..."
systemctl daemon-reload
systemctl enable alist-image-api.service
systemctl start alist-image-api.service

echo "--- Setup Complete! ---"
echo "The Alist Image API service is now running and will start automatically on boot."
echo "You can check its status with: sudo systemctl status alist-image-api.service"
echo "You can view its logs with: sudo journalctl -u alist-image-api.service -f"