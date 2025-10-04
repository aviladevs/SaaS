#!/bin/bash
# Quick Start Script for Monitoring & Observability Stack
# Ávila DevOps SaaS Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_success "Docker is installed"
    else
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose is installed"
    else
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if saas-network exists
    if docker network ls | grep -q saas-network; then
        print_success "saas-network exists"
    else
        print_warning "saas-network does not exist. Creating it..."
        docker network create saas-network
        print_success "saas-network created"
    fi
}

# Setup environment
setup_environment() {
    print_header "Setting Up Environment"
    
    if [ ! -f monitoring/.env ]; then
        print_info "Creating .env file from template..."
        cp monitoring/.env.example monitoring/.env
        print_success ".env file created"
        print_warning "Please update monitoring/.env with your actual configuration"
    else
        print_success ".env file already exists"
    fi
}

# Start monitoring stack
start_monitoring() {
    print_header "Starting Monitoring Stack"
    
    print_info "Starting services (this may take a few minutes)..."
    docker-compose -f docker-compose.monitoring.yml up -d
    
    print_success "Monitoring stack started!"
}

# Wait for services
wait_for_services() {
    print_header "Waiting for Services to Initialize"
    
    services=(
        "prometheus:9090"
        "grafana:3001"
        "elasticsearch:9200"
        "kibana:5601"
        "jaeger:16686"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r name port <<< "$service"
        print_info "Waiting for $name..."
        
        max_attempts=30
        attempt=0
        
        while [ $attempt -lt $max_attempts ]; do
            if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port" | grep -q "200\|302"; then
                print_success "$name is ready"
                break
            fi
            
            attempt=$((attempt + 1))
            if [ $attempt -eq $max_attempts ]; then
                print_warning "$name is taking longer than expected to start"
            fi
            sleep 2
        done
    done
}

# Display access information
show_access_info() {
    print_header "Access Information"
    
    echo ""
    echo -e "${GREEN}Monitoring services are now running!${NC}"
    echo ""
    echo -e "${BLUE}Dashboard URLs:${NC}"
    echo -e "  📊 Grafana:        ${GREEN}http://localhost:3001${NC}  (admin/admin)"
    echo -e "  📈 Prometheus:     ${GREEN}http://localhost:9090${NC}"
    echo -e "  🔔 AlertManager:   ${GREEN}http://localhost:9093${NC}"
    echo -e "  🔍 Kibana:         ${GREEN}http://localhost:5601${NC}"
    echo -e "  🔗 Jaeger:         ${GREEN}http://localhost:16686${NC}"
    echo -e "  🌺 Celery Flower:  ${GREEN}http://localhost:5555${NC}  (admin/admin)"
    echo ""
    echo -e "${BLUE}Metrics Exporters:${NC}"
    echo -e "  📊 Node Exporter:      ${GREEN}http://localhost:9100/metrics${NC}"
    echo -e "  🗄️  PostgreSQL Exporter: ${GREEN}http://localhost:9187/metrics${NC}"
    echo -e "  🔴 Redis Exporter:     ${GREEN}http://localhost:9121/metrics${NC}"
    echo -e "  📦 cAdvisor:          ${GREEN}http://localhost:8080${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Change default passwords in Grafana and Flower"
    echo "  2. Configure alert notifications in monitoring/.env"
    echo "  3. Integrate monitoring into your applications (see monitoring/INTEGRATION_GUIDE.md)"
    echo "  4. View pre-built dashboards in Grafana"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "  📖 Main README: monitoring/README.md"
    echo "  🔧 Integration Guide: monitoring/INTEGRATION_GUIDE.md"
    echo ""
    echo -e "${YELLOW}To stop monitoring:${NC}"
    echo "  docker-compose -f docker-compose.monitoring.yml down"
    echo ""
}

# Check service health
check_health() {
    print_header "Service Health Check"
    
    echo ""
    echo -e "${BLUE}Checking service health...${NC}"
    echo ""
    
    # Check Prometheus
    if curl -s http://localhost:9090/-/healthy | grep -q "Prometheus"; then
        print_success "Prometheus: Healthy"
    else
        print_error "Prometheus: Unhealthy"
    fi
    
    # Check Grafana
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/api/health | grep -q "200"; then
        print_success "Grafana: Healthy"
    else
        print_error "Grafana: Unhealthy"
    fi
    
    # Check Elasticsearch
    if curl -s http://localhost:9200/_cluster/health | grep -q "yellow\|green"; then
        print_success "Elasticsearch: Healthy"
    else
        print_error "Elasticsearch: Unhealthy"
    fi
    
    # Check Kibana
    if curl -s http://localhost:5601/api/status | grep -q "green"; then
        print_success "Kibana: Healthy"
    else
        print_warning "Kibana: Starting (this may take a few minutes)"
    fi
    
    echo ""
}

# Main function
main() {
    clear
    
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                           ║${NC}"
    echo -e "${BLUE}║    📊 Monitoring & Observability Stack Setup              ║${NC}"
    echo -e "${BLUE}║    Ávila DevOps SaaS Platform                            ║${NC}"
    echo -e "${BLUE}║                                                           ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    check_prerequisites
    setup_environment
    start_monitoring
    wait_for_services
    check_health
    show_access_info
}

# Handle script arguments
case "${1:-}" in
    start)
        start_monitoring
        ;;
    stop)
        print_info "Stopping monitoring stack..."
        docker-compose -f docker-compose.monitoring.yml down
        print_success "Monitoring stack stopped"
        ;;
    restart)
        print_info "Restarting monitoring stack..."
        docker-compose -f docker-compose.monitoring.yml restart
        print_success "Monitoring stack restarted"
        ;;
    status)
        docker-compose -f docker-compose.monitoring.yml ps
        ;;
    logs)
        docker-compose -f docker-compose.monitoring.yml logs -f "${2:-}"
        ;;
    health)
        check_health
        ;;
    *)
        main
        ;;
esac
