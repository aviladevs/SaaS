#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting deployment process..."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
fi

# Build the project
echo "🔨 Building the project..."
npm run build

# Export the static site
echo "📦 Exporting static site..."
npm run export

# Create a deployment package
echo "📦 Creating deployment package..."
DEPLOY_DIR="deploy"
OUTPUT_DIR="out"

# Create deployment directory if it doesn't exist
mkdir -p $DEPLOY_DIR

# Copy the built files to the deployment directory
cp -r $OUTPUT_DIR/* $DEPLOY_DIR/

# Create a simple Caddyfile for the subdomain
cat > $DEPLOY_DIR/Caddyfile << 'EOL'
clinica.aviladevops.com.br {
    root * /srv/clinica
    file_server
    encode gzip
    try_files {path} {path}/ /index.html
}
EOL

echo "✅ Build complete! Files are ready in the 'deploy' directory."
echo "
📋 Next steps:
1. Upload the contents of the 'deploy' directory to your server
2. Make sure the files are served from /srv/clinica on your server
3. Configure your web server (Nginx/Apache/Caddy) to point to this directory
4. Set up SSL certificates for HTTPS

For Caddy, you can use the included Caddyfile as a reference.
"

echo "🚀 Deployment preparation complete!"
