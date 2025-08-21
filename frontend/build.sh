#!/bin/bash
set -e

echo "Starting build process..."

# Install dependencies
echo "Installing dependencies..."
npm install

# Check if expo is available
echo "Checking Expo CLI..."
npx expo --version

# Build the project
echo "Building project..."
npx expo export --platform web --output-dir web-build --clear

# Verify build output
echo "Verifying build output..."
ls -la web-build/
echo "Build completed successfully!"