#!/bin/bash

# ProfileGPT Deployment Script
# Deploys both frontend and backend to production hosting

set -e

echo "🚀 Starting ProfileGPT Production Deployment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions for colored output
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check if required tools are installed
check_dependencies() {
    info "Checking dependencies..."

    if ! command -v git &> /dev/null; then
        error "Git is required but not installed"
        exit 1
    fi

    if ! command -v npm &> /dev/null; then
        error "npm is required but not installed"
        exit 1
    fi

    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
        exit 1
    fi

    success "All dependencies found"
}

# Install enhanced dependencies
install_backend_deps() {
    info "Installing enhanced backend dependencies..."
    cd backend

    # Install the enhanced requirements
    if python3 -m pip install -r requirements.txt; then
        success "Backend dependencies installed"
    else
        error "Failed to install backend dependencies"
        exit 1
    fi

    cd ..
}

install_frontend_deps() {
    info "Installing frontend dependencies..."
    cd frontend

    if npm ci; then
        success "Frontend dependencies installed"
    else
        error "Failed to install frontend dependencies"
        exit 1
    fi

    cd ..
}

# Test local functionality before deployment
test_local_setup() {
    info "Testing local setup..."

    # Test backend
    cd backend
    if python3 -c "import fastapi, uvicorn, sentence_transformers; print('Backend imports OK')"; then
        success "Backend dependencies working"
    else
        error "Backend import test failed"
        exit 1
    fi
    cd ..

    # Test frontend
    cd frontend
    if npm run build > /dev/null 2>&1; then
        success "Frontend builds successfully"
    else
        error "Frontend build failed"
        exit 1
    fi
    cd ..
}

# Deploy to Railway (Backend)
deploy_backend_railway() {
    info "Deploying backend to Railway..."

    if ! command -v railway &> /dev/null; then
        warning "Railway CLI not found. Install with: npm install -g @railway/cli"
        warning "Then run: railway login"
        warning "And manually deploy backend from /backend directory"
        return 1
    fi

    cd backend

    # Create or update railway.json if needed
    cat > railway.json << EOF
{
    "build": {
        "builder": "NIXPACKS"
    },
    "deploy": {
        "startCommand": "uvicorn main:app --host 0.0.0.0 --port \$PORT",
        "restartPolicyType": "ON_FAILURE"
    }
}
EOF

    # Create Procfile for Railway
    echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT --workers 1" > Procfile

    if railway deploy; then
        success "Backend deployed to Railway"
        BACKEND_URL=$(railway domain)
        success "Backend URL: $BACKEND_URL"
    else
        error "Railway deployment failed"
    fi

    cd ..
}

# Deploy to Vercel (Frontend)
deploy_frontend_vercel() {
    info "Deploying frontend to Vercel..."

    if ! command -v vercel &> /dev/null; then
        warning "Vercel CLI not found. Install with: npm install -g vercel"
        warning "Then run: vercel login"
        warning "And manually deploy frontend from /frontend directory"
        return 1
    fi

    cd frontend

    # Build the frontend
    if npm run build; then
        success "Frontend built successfully"
    else
        error "Frontend build failed"
        exit 1
    fi

    # Deploy to Vercel
    if vercel --prod; then
        success "Frontend deployed to Vercel"
    else
        error "Vercel deployment failed"
    fi

    cd ..
}

# Alternative deployment methods
deploy_backend_render() {
    info "Setting up Render deployment config..."

    cd backend

    # Create render.yaml
    cat > render.yaml << EOF
services:
  - type: web
    name: profilegpt-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port \$PORT --workers 1"
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: profilegpt-db
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
    autoDeploy: false

databases:
  - name: profilegpt-db
    databaseName: profilegpt
    user: profilegpt_user
EOF

    success "Render config created. Push to GitHub and connect to Render"
    cd ..
}

# Create Netlify config for frontend
deploy_frontend_netlify() {
    info "Setting up Netlify deployment config..."

    # Update netlify.toml with production settings
    cat > netlify.toml << EOF
[build]
  base = "frontend"
  publish = "frontend/out"
  command = "npm ci && npm run build"

[build.environment]
  NODE_VERSION = "20.9.0"
  NPM_VERSION = "10"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[context.production.environment]
  NEXT_PUBLIC_API_URL = "https://your-railway-backend.railway.app"

[context.deploy-preview.environment]
  NEXT_PUBLIC_API_URL = "https://your-railway-backend.railway.app"

[context.branch-deploy.environment]
  NEXT_PUBLIC_API_URL = "https://your-railway-backend.railway.app"
EOF

    success "Netlify config created. Connect GitHub repo to Netlify"
}

# Create production Docker configuration
create_docker_config() {
    info "Creating Docker production configuration..."

    # Backend Dockerfile
    cat > backend/Dockerfile.prod << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for document processing
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    software-properties-common \\
    git \\
    libmagic1 \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data and spacy models
RUN python -c "import nltk; nltk.download('punkt', quiet=True)"
RUN python -m spacy download en_core_web_sm --quiet

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
EOF

    # Frontend Dockerfile
    cat > frontend/Dockerfile.prod << EOF
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

    # Nginx config for frontend
    cat > frontend/nginx.conf << EOF
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html index.htm;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # Docker Compose for production
    cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/profilegpt
      - ENVIRONMENT=production
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./backend/uploads:/app/uploads
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=profilegpt
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
EOF

    success "Docker configuration created"
}

# Create comprehensive deployment guide
create_deployment_guide() {
    cat > DEPLOYMENT_GUIDE.md << EOF
# 🚀 ProfileGPT Production Deployment Guide

## Quick Deployment Options

### Option 1: Free Hosting (Recommended)
- **Frontend**: Vercel (Free tier: Unlimited deployments)
- **Backend**: Railway (Free tier: $5 credit/month)
- **Database**: Railway PostgreSQL (Included)
- **Total Cost**: FREE for small usage

### Option 2: Traditional Cloud
- **Frontend**: Netlify
- **Backend**: Render.com or Heroku
- **Database**: Supabase or AWS RDS

### Option 3: Self-Hosted Docker
- Use the provided docker-compose.prod.yml
- Suitable for VPS deployment

## Environment Variables Setup

### Backend (.env.production)
\`\`\`bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
OPENAI_API_KEY=your_openai_key_here
ENVIRONMENT=production
USE_LOCAL_EMBEDDINGS=true
ALLOWED_ORIGINS=["https://your-frontend.vercel.app"]
\`\`\`

### Frontend
\`\`\`bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
\`\`\`

## Manual Deployment Steps

### Deploy Backend to Railway:
1. \`npm install -g @railway/cli\`
2. \`railway login\`
3. \`cd backend && railway init\`
4. \`railway add\` (select PostgreSQL)
5. Set environment variables in Railway dashboard
6. \`railway deploy\`

### Deploy Frontend to Vercel:
1. \`npm install -g vercel\`
2. \`vercel login\`
3. \`cd frontend\`
4. Update NEXT_PUBLIC_API_URL in vercel dashboard
5. \`vercel --prod\`

## Testing Production Deployment

1. Visit your frontend URL
2. Try uploading a document
3. Test the chat interface
4. Verify API responses include citations

## Performance Optimization

- Enable Redis caching for faster responses
- Use OpenAI embeddings for better accuracy (requires API key)
- Configure CDN for faster file serving
- Set up monitoring with Langfuse

## Scaling Considerations

- **Railway**: Upgrade to Pro ($20/month) for more resources
- **Vercel**: Pro plan ($20/month) for team features
- **Database**: Scale PostgreSQL as needed
- **Caching**: Add Redis for session management

## Security Checklist

- [ ] Set strong SECRET_KEY
- [ ] Configure CORS properly
- [ ] Use HTTPS everywhere
- [ ] Secure database credentials
- [ ] Enable rate limiting
- [ ] Regular security updates

## Monitoring

- Railway: Built-in logs and metrics
- Vercel: Analytics and performance monitoring
- Custom: Add Langfuse for LLM tracing
- Health checks: /health endpoint

## Backup Strategy

- Database: Automated backups via Railway/Render
- Documents: Store in S3-compatible storage
- Code: GitHub repository
- Configuration: Environment variable backups

## Support

For deployment issues:
1. Check logs in hosting platform dashboards
2. Verify environment variables
3. Test API endpoints directly
4. Review this guide and README.md

Happy deploying! 🎉
EOF

    success "Deployment guide created: DEPLOYMENT_GUIDE.md"
}

# Main deployment flow
main() {
    echo "🎯 ProfileGPT Production Deployment"
    echo "===================================="

    check_dependencies

    echo ""
    info "Choose deployment option:"
    echo "1. Full automated deployment (Railway + Vercel)"
    echo "2. Create deployment configs only"
    echo "3. Install dependencies and test"
    echo "4. Docker setup for self-hosting"

    read -p "Enter choice (1-4): " choice

    case $choice in
        1)
            install_backend_deps
            install_frontend_deps
            test_local_setup
            deploy_backend_railway
            deploy_frontend_vercel
            ;;
        2)
            deploy_backend_render
            deploy_frontend_netlify
            create_docker_config
            create_deployment_guide
            ;;
        3)
            install_backend_deps
            install_frontend_deps
            test_local_setup
            success "Local setup tested successfully"
            ;;
        4)
            create_docker_config
            info "Docker configuration created. Run: docker-compose -f docker-compose.prod.yml up"
            ;;
        *)
            error "Invalid choice"
            exit 1
            ;;
    esac

    echo ""
    success "Deployment process completed!"
    echo ""
    info "Next steps:"
    echo "1. Set up your OpenAI API key for better AI responses"
    echo "2. Upload your personal documents via the /ingest endpoint"
    echo "3. Test the chat interface thoroughly"
    echo "4. Share your ProfileGPT with recruiters and colleagues"
    echo ""
    success "Your AI-powered portfolio is ready! 🎉"
}

# Run main function
main "$@"