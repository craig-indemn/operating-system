#!/usr/bin/env bash

# =============================================================================
# Indemn Local Development Helper
# =============================================================================
# NOTE: Requires bash 4.0+ for associative arrays
# On macOS: brew install bash
# =============================================================================

# Check bash version (need 4.0+ for associative arrays)
if ((BASH_VERSINFO[0] < 4)); then
    echo "Error: This script requires bash 4.0 or later"
    echo "Your version: $BASH_VERSION"
    echo ""
    echo "On macOS, install newer bash with:"
    echo "  brew install bash"
    echo ""
    echo "Then run this script with:"
    echo "  /opt/homebrew/bin/bash ./local-dev.sh <command>"
    echo "  # or"
    echo "  /usr/local/bin/bash ./local-dev.sh <command>"
    exit 1
fi
# Usage:
#   ./local-dev.sh status                    - Check which services are running
#   ./local-dev.sh validate --env=dev        - Validate environment (no start)
#   ./local-dev.sh start <service> --env=dev - Start a specific service
#   ./local-dev.sh start minimal --env=dev   - Start minimal set (bot + evals)
#   ./local-dev.sh start platform --env=dev  - Start platform development set
#   ./local-dev.sh start chat --env=dev      - Start full chat stack
#   ./local-dev.sh start all --env=dev       - Start all services
#   ./local-dev.sh stop <port>               - Stop service on a port
#   ./local-dev.sh stop all                  - Stop all services
#   ./local-dev.sh logs <service>            - Tail logs for a service
#   ./local-dev.sh logs combined             - Combined logs from all services
# =============================================================================

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INDEMN_ENV=""  # Will be set by --env flag

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# =============================================================================
# ENVIRONMENT LOADING
# =============================================================================

parse_env_flag() {
    for arg in "$@"; do
        case $arg in
            --env=*)
                INDEMN_ENV="${arg#*=}"
                ;;
        esac
    done
}

load_environment() {
    local env=$1
    local env_file="$REPO_DIR/.env.${env}"

    if [[ -z "$env" ]]; then
        echo -e "${RED}Error: No environment specified${NC}"
        echo "Usage: ./local-dev.sh <command> --env=dev|prod"
        echo ""
        echo "First, create your environment file:"
        echo "  cp .env.template .env.dev"
        echo "  # Edit .env.dev with your values"
        return 1
    fi

    if [[ ! -f "$env_file" ]]; then
        echo -e "${RED}Error: Environment file not found: $env_file${NC}"
        echo ""
        echo "To create it:"
        echo "  cp .env.template .env.${env}"
        echo "  # Edit .env.${env} with your values"
        return 1
    fi

    echo -e "${BLUE}Loading environment: ${BOLD}$env${NC}"

    # Export all variables from the env file
    set -a
    source "$env_file"
    set +a

    export INDEMN_ENV="$env"
    echo -e "${GREEN}✓ Environment loaded${NC}"
    return 0
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

validate_mongodb() {
    echo -e "${CYAN}Validating MongoDB connection...${NC}"

    # Try different variable names used across services
    local uri="${MONGODB_URI:-${MONGO_URL:-${DATABASE_URI:-}}}"

    if [[ -z "$uri" ]]; then
        echo -e "${RED}✗ MongoDB URI not configured${NC}"
        echo "  Set MONGODB_URI, MONGO_URL, or DATABASE_URI in .env.${INDEMN_ENV}"
        return 1
    fi

    # Mask password for display
    local masked=$(echo "$uri" | sed -E 's|://([^:]+):([^@]+)@|://\1:***@|')
    echo "  URI: $masked"

    # Check if mongosh is available
    if command -v mongosh &> /dev/null; then
        if mongosh "$uri" --eval "db.runCommand({ping:1})" --quiet 2>/dev/null | grep -q '"ok" : 1\|"ok": 1'; then
            echo -e "${GREEN}✓ MongoDB connected${NC}"
            return 0
        else
            echo -e "${RED}✗ MongoDB connection failed${NC}"
            echo "  Check MONGODB_URI in .env.${INDEMN_ENV} points to Atlas cluster"
            echo "  Copy credentials from: cat bot-service/.env | grep MONGO"
            return 1
        fi
    elif command -v mongo &> /dev/null; then
        if mongo "$uri" --eval "db.runCommand({ping:1})" --quiet 2>/dev/null | grep -q '"ok" : 1\|"ok": 1'; then
            echo -e "${GREEN}✓ MongoDB connected${NC}"
            return 0
        else
            echo -e "${RED}✗ MongoDB connection failed${NC}"
            return 1
        fi
    else
        # Try Python as fallback
        if command -v python3 &> /dev/null; then
            if python3 -c "
from pymongo import MongoClient
import sys
try:
    client = MongoClient('$uri', serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    sys.exit(0)
except Exception as e:
    sys.exit(1)
" 2>/dev/null; then
                echo -e "${GREEN}✓ MongoDB connected${NC}"
                return 0
            else
                echo -e "${RED}✗ MongoDB connection failed${NC}"
                return 1
            fi
        else
            echo -e "${YELLOW}⚠ Cannot verify MongoDB (no mongosh/mongo/python3 found)${NC}"
            echo "  Install mongosh: brew install mongosh"
            return 0  # Don't fail, just warn
        fi
    fi
}

validate_redis() {
    echo -e "${CYAN}Validating Redis connection...${NC}"

    local host="${REDIS_HOST:-localhost}"
    local port="${REDIS_PORT:-6379}"
    local pass="${REDIS_PASSWORD:-}"

    echo "  Host: $host:$port"

    # Check if redis-cli is available
    if command -v redis-cli &> /dev/null; then
        local auth_args=""
        if [[ -n "$pass" ]]; then
            auth_args="-a $pass"
        fi

        if redis-cli -h "$host" -p "$port" $auth_args PING 2>/dev/null | grep -q "PONG"; then
            echo -e "${GREEN}✓ Redis connected${NC}"
            return 0
        else
            echo -e "${RED}✗ Redis connection failed${NC}"
            echo "  Check REDIS_HOST, REDIS_PORT, REDIS_PASSWORD in .env.${INDEMN_ENV}"
            echo "  Copy credentials from: cat bot-service/.env | grep REDIS"
            return 1
        fi
    else
        # Try netcat to at least check port is open
        if command -v nc &> /dev/null; then
            if nc -z "$host" "$port" 2>/dev/null; then
                echo -e "${GREEN}✓ Redis port open (install redis-cli for full validation)${NC}"
                return 0
            else
                echo -e "${RED}✗ Redis port not reachable${NC}"
                return 1
            fi
        else
            echo -e "${YELLOW}⚠ Cannot verify Redis (no redis-cli or nc found)${NC}"
            return 0
        fi
    fi
}

validate_rabbitmq() {
    echo -e "${CYAN}Validating RabbitMQ connection...${NC}"

    local url="${RABBITMQ_CONNECT_URL:-${CLOUDAMQP_URL:-amqp://localhost:5672}}"

    # Extract host and port from URL
    local host=$(echo "$url" | sed -E 's|amqps?://([^:@]+:)?([^:@]+@)?([^:/]+).*|\3|')
    local port=$(echo "$url" | sed -E 's|.*:([0-9]+)/?.*|\1|')
    [[ "$port" == "$url" ]] && port="5672"

    echo "  Host: $host:$port"

    # Check if port is reachable
    if command -v nc &> /dev/null; then
        if nc -z "$host" "$port" 2>/dev/null; then
            echo -e "${GREEN}✓ RabbitMQ port reachable${NC}"
            return 0
        else
            echo -e "${RED}✗ RabbitMQ not reachable${NC}"
            echo "  Check RABBITMQ_CONNECT_URL in .env.${INDEMN_ENV}"
            echo "  Copy credentials from: cat bot-service/.env | grep RABBITMQ"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ Cannot verify RabbitMQ (nc not found)${NC}"
        return 0
    fi
}

validate_api_keys() {
    echo -e "${CYAN}Validating API keys...${NC}"
    local errors=0

    # Required keys
    if [[ -z "${OPENAI_API_KEY:-}" ]]; then
        echo -e "${RED}✗ OPENAI_API_KEY not set (required)${NC}"
        ((errors++))
    elif [[ "${OPENAI_API_KEY}" == "sk-your-"* || "${OPENAI_API_KEY}" == "sk-..." ]]; then
        echo -e "${RED}✗ OPENAI_API_KEY is placeholder value${NC}"
        ((errors++))
    else
        echo -e "${GREEN}✓ OPENAI_API_KEY set${NC}"
    fi

    if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
        echo -e "${YELLOW}⚠ ANTHROPIC_API_KEY not set (optional but recommended)${NC}"
    elif [[ "${ANTHROPIC_API_KEY}" == "sk-ant-your-"* ]]; then
        echo -e "${YELLOW}⚠ ANTHROPIC_API_KEY is placeholder value${NC}"
    else
        echo -e "${GREEN}✓ ANTHROPIC_API_KEY set${NC}"
    fi

    # LangSmith (required for evaluations)
    if [[ -z "${LANGSMITH_API_KEY:-}${LANGCHAIN_API_KEY:-}" ]]; then
        echo -e "${YELLOW}⚠ LANGSMITH_API_KEY not set (required for evaluations, tracing disabled)${NC}"
    else
        echo -e "${GREEN}✓ LANGSMITH_API_KEY set${NC}"
    fi

    # Pinecone (required for KB features)
    if [[ -z "${PINECONE_API_KEY:-}" ]]; then
        echo -e "${YELLOW}⚠ PINECONE_API_KEY not set (KB features limited)${NC}"
    else
        echo -e "${GREEN}✓ PINECONE_API_KEY set${NC}"
    fi

    if [[ $errors -gt 0 ]]; then
        return 1
    fi
    return 0
}

validate_ports() {
    local services=("$@")
    echo -e "${CYAN}Checking port availability...${NC}"
    local errors=0

    if [[ ${#services[@]} -eq 0 ]]; then
        # Check all service ports
        for name in "${!SERVICES[@]}"; do
            IFS=':' read -r port dir cmd <<< "${SERVICES[$name]}"
            if check_port $port; then
                local pid=$(get_pid_on_port $port)
                echo -e "${YELLOW}⚠ Port $port in use (PID: $pid) - needed for $name${NC}"
                ((errors++))
            fi
        done
    else
        # Check only specified services
        for name in "${services[@]}"; do
            if [[ -n "${SERVICES[$name]:-}" ]]; then
                IFS=':' read -r port dir cmd <<< "${SERVICES[$name]}"
                if check_port $port; then
                    local pid=$(get_pid_on_port $port)
                    echo -e "${YELLOW}⚠ Port $port in use (PID: $pid) - needed for $name${NC}"
                    ((errors++))
                fi
            fi
        done
    fi

    if [[ $errors -eq 0 ]]; then
        echo -e "${GREEN}✓ All required ports available${NC}"
        return 0
    else
        echo -e "${RED}✗ $errors port(s) already in use${NC}"
        echo "  Use './local-dev.sh stop <port>' to free them"
        return 1
    fi
}

validate_all() {
    local services=("$@")
    local errors=0

    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}              ENVIRONMENT VALIDATION: ${BOLD}$INDEMN_ENV${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""

    # MongoDB (required)
    if ! validate_mongodb; then
        ((errors++))
    fi
    echo ""

    # Redis (required for some services)
    if ! validate_redis; then
        ((errors++))
    fi
    echo ""

    # RabbitMQ (required for chat flow)
    if ! validate_rabbitmq; then
        ((errors++))
    fi
    echo ""

    # API Keys
    if ! validate_api_keys; then
        ((errors++))
    fi
    echo ""

    # Port availability
    if ! validate_ports "${services[@]}"; then
        ((errors++))
    fi
    echo ""

    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    if [[ $errors -eq 0 ]]; then
        echo -e "${GREEN}${BOLD}✓ All validations passed${NC}"
        return 0
    else
        echo -e "${RED}${BOLD}✗ $errors validation(s) failed${NC}"
        echo "  Fix the issues above before starting services"
        return 1
    fi
}

# =============================================================================
# DIRECTORY RESOLUTION
# =============================================================================
# Repos may be cloned with org names or legacy names. Auto-detect which exists.
# Format: "primary_name:fallback_name" — checks primary first, then fallback.

declare -A DIR_ALIASES=(
    ["indemn-platform-v2"]="copilot-dashboard-react"
    ["indemn-observability"]="Indemn-observatory"
)

resolve_dir() {
    local name=$1
    # Direct match
    if [[ -d "$REPO_DIR/$name" ]]; then
        echo "$name"
        return 0
    fi
    # Check alias (primary → fallback)
    if [[ -n "${DIR_ALIASES[$name]:-}" ]]; then
        local alt="${DIR_ALIASES[$name]}"
        if [[ -d "$REPO_DIR/$alt" ]]; then
            echo "$alt"
            return 0
        fi
    fi
    # Check reverse alias (fallback → primary)
    for primary in "${!DIR_ALIASES[@]}"; do
        if [[ "${DIR_ALIASES[$primary]}" == "$name" ]] && [[ -d "$REPO_DIR/$primary" ]]; then
            echo "$primary"
            return 0
        fi
    done
    # Not found — return original name (will fail later with clear error)
    echo "$name"
    return 1
}

# =============================================================================
# SERVICE DEFINITIONS
# =============================================================================

# Resolve directory names for services with aliases
_platform_dir=$(resolve_dir "indemn-platform-v2")
_observatory_dir=$(resolve_dir "indemn-observability")

# Service definitions: name:port:directory:command
declare -A SERVICES=(
    ["bot-service"]="8001:bot-service:uv run python app.py"
    ["evaluations"]="8002:evaluations:uv run uvicorn indemn_evals.api.main:app --port 8002 --reload"
    ["evaluations-ui"]="5174:evaluations/ui:npm run dev -- --port 5174"
    ["platform-v2"]="8003:${_platform_dir}:uv run uvicorn indemn_platform.api.main:app --port 8003 --reload"
    ["platform-v2-ui"]="5173:${_platform_dir}/ui:npm run dev -- --port 5173"
    ["observability"]="8004:${_observatory_dir}:source venv/bin/activate && uvicorn src.observatory.api.main:app --port 8004 --reload"
    ["observability-ui"]="5175:${_observatory_dir}/frontend:npm run dev -- --port 5175"
    ["copilot-server"]="3000:copilot-server:npm start"
    ["copilot-dashboard"]="4500:copilot-dashboard:npm start"
    ["middleware"]="8000:middleware-socket-service:npm start"
    ["copilot-sync"]="5555:copilot-sync-service:npm start"
    ["kb-service"]="8080:kb-service:uv run python app.py"
    ["conversation-service"]="9090:conversation-service:uv run python app.py"
    ["voice-service"]="9192:voice-service:npm start"
    ["point-of-sale"]="3002:point-of-sale:npm run dev -- --port 3002"
)

# Infrastructure services
declare -A INFRA=(
    ["mongodb"]="27017"
    ["redis"]="6379"
    ["rabbitmq"]="5672"
)

# Service groups
MINIMAL_SERVICES=("bot-service" "evaluations" "evaluations-ui")
PLATFORM_SERVICES=("bot-service" "platform-v2" "platform-v2-ui" "evaluations")
CHAT_SERVICES=("bot-service" "middleware" "copilot-server" "conversation-service" "point-of-sale")
ANALYTICS_SERVICES=("observability" "observability-ui")

check_port() {
    local port=$1
    if lsof -i :$port -sTCP:LISTEN > /dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

get_pid_on_port() {
    lsof -i :$1 -sTCP:LISTEN -t 2>/dev/null | head -1
}

print_status() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                    INDEMN LOCAL DEV STATUS                     ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""

    # Infrastructure
    echo -e "${YELLOW}Infrastructure:${NC}"
    printf "  %-20s %-8s %s\n" "SERVICE" "PORT" "STATUS"
    echo "  ────────────────────────────────────────────"
    for name in "${!INFRA[@]}"; do
        port=${INFRA[$name]}
        if check_port $port; then
            printf "  %-20s %-8s ${GREEN}● Running${NC}\n" "$name" "$port"
        else
            printf "  %-20s %-8s ${RED}○ Stopped${NC}\n" "$name" "$port"
        fi
    done

    echo ""
    echo -e "${YELLOW}Application Services:${NC}"
    printf "  %-20s %-8s %s\n" "SERVICE" "PORT" "STATUS"
    echo "  ────────────────────────────────────────────"

    for name in "${!SERVICES[@]}"; do
        IFS=':' read -r port dir cmd <<< "${SERVICES[$name]}"
        if check_port $port; then
            pid=$(get_pid_on_port $port)
            printf "  %-20s %-8s ${GREEN}● Running (PID: %s)${NC}\n" "$name" "$port" "$pid"
        else
            printf "  %-20s %-8s ${RED}○ Stopped${NC}\n" "$name" "$port"
        fi
    done
    echo ""
}

start_service() {
    local name=$1

    if [[ -z "${SERVICES[$name]:-}" ]]; then
        echo -e "${RED}Unknown service: $name${NC}"
        echo "Available services:"
        for svc in "${!SERVICES[@]}"; do
            echo "  - $svc"
        done
        return 1
    fi

    IFS=':' read -r port dir cmd <<< "${SERVICES[$name]}"

    if check_port $port; then
        echo -e "${YELLOW}Service $name is already running on port $port${NC}"
        return 0
    fi

    local full_dir="$REPO_DIR/$dir"
    if [[ ! -d "$full_dir" ]]; then
        echo -e "${RED}Directory not found: $full_dir${NC}"
        return 1
    fi

    echo -e "${BLUE}Starting $name on port $port...${NC}"
    echo -e "${BLUE}Directory: $full_dir${NC}"
    echo -e "${BLUE}Command: $cmd${NC}"
    echo ""

    # Create log directory
    mkdir -p "$REPO_DIR/.logs"
    local logfile="$REPO_DIR/.logs/$name.log"

    # Start the service in background
    cd "$full_dir"
    nohup bash -c "$cmd" > "$logfile" 2>&1 &
    local pid=$!

    # Record PID
    echo "$pid" > "$REPO_DIR/.logs/$name.pid"

    echo -e "${GREEN}Started $name (PID: $pid)${NC}"
    echo -e "Logs: $logfile"

    cd "$REPO_DIR"

    # Wait for health check if requested
    if [[ "${WAIT_FOR_HEALTH:-true}" == "true" ]]; then
        wait_for_health "$name" "$port"
    fi
}

wait_for_health() {
    local name=$1
    local port=$2
    local timeout=${3:-30}
    local health_url="http://localhost:$port/health"

    echo -ne "  Waiting for service..."

    local elapsed=0
    local interval=2
    local port_opened=false

    while (( elapsed < timeout )); do
        # Phase 1: Wait for port to open (service starts listening)
        if ! $port_opened; then
            if check_port $port; then
                port_opened=true
                echo -ne " port open, checking health..."
            else
                sleep $interval
                ((elapsed += interval))
                echo -ne "."
                continue
            fi
        fi

        # Phase 2: Port was open - check if it's still open (service might have crashed)
        if ! check_port $port; then
            echo -e " ${RED}✗ Service died${NC}"
            echo "  Check logs: tail -50 .logs/$name.log"
            return 1
        fi

        # Phase 3: Try health endpoint
        if curl -sf "$health_url" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓ Healthy${NC}"
            return 0
        fi

        # Also try root endpoint (some services use / for health)
        if curl -sf "http://localhost:$port/" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓ Responding${NC}"
            return 0
        fi

        sleep $interval
        ((elapsed += interval))
        echo -ne "."
    done

    # If port opened but no health response, service might still be initializing
    if $port_opened; then
        echo -e " ${YELLOW}⚠ Running but health check timeout${NC}"
    else
        echo -e " ${RED}✗ Port never opened${NC}"
        echo "  Check logs: tail -50 .logs/$name.log"
        return 1
    fi
    return 0  # Don't fail, just warn
}

show_health_summary() {
    local services=("$@")

    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                      STARTUP SUMMARY                           ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""

    local healthy=0
    local unhealthy=0

    for name in "${services[@]}"; do
        if [[ -z "${SERVICES[$name]:-}" ]]; then
            continue
        fi
        IFS=':' read -r port dir cmd <<< "${SERVICES[$name]}"

        if check_port $port; then
            # Check health endpoint
            if curl -sf "http://localhost:$port/health" > /dev/null 2>&1 || \
               curl -sf "http://localhost:$port/" > /dev/null 2>&1; then
                printf "  ${GREEN}●${NC} %-20s http://localhost:%s\n" "$name" "$port"
                ((healthy++))
            else
                printf "  ${YELLOW}◐${NC} %-20s http://localhost:%s (starting)\n" "$name" "$port"
            fi
        else
            printf "  ${RED}○${NC} %-20s Failed to start\n" "$name"
            ((unhealthy++))
        fi
    done

    echo ""
    if [[ $unhealthy -eq 0 ]]; then
        echo -e "${GREEN}${BOLD}All $healthy service(s) started successfully${NC}"
    else
        echo -e "${YELLOW}${BOLD}$healthy healthy, $unhealthy failed${NC}"
    fi
    echo ""
    echo "Commands:"
    echo "  ./local-dev.sh status     - Check all services"
    echo "  ./local-dev.sh logs <svc> - View service logs"
    echo "  ./local-dev.sh stop all   - Stop everything"
    echo ""
}

# Service startup tiers (for dependency ordering)
declare -A SERVICE_TIERS=(
    # Tier 0: No service dependencies
    ["copilot-server"]=0
    ["observability"]=0
    # Tier 1: Depends on copilot-server
    ["middleware"]=1
    ["copilot-sync"]=1
    # Tier 2: Depends on middleware
    ["bot-service"]=2
    ["kb-service"]=2
    # Tier 3: Depends on bot-service
    ["evaluations"]=3
    ["platform-v2"]=3
    ["conversation-service"]=3
    # Tier 4: Frontends
    ["evaluations-ui"]=4
    ["platform-v2-ui"]=4
    ["observability-ui"]=4
    ["copilot-dashboard"]=4
    ["point-of-sale"]=4
    # Tier 5: Optional
    ["voice-service"]=5
)

get_service_tier() {
    local name=$1
    echo "${SERVICE_TIERS[$name]:-5}"
}

start_group() {
    local group=$1
    local services=()

    case $group in
        minimal)
            services=("${MINIMAL_SERVICES[@]}")
            echo -e "${BLUE}Starting minimal development set...${NC}"
            ;;
        platform)
            services=("${PLATFORM_SERVICES[@]}")
            echo -e "${BLUE}Starting platform development set...${NC}"
            ;;
        chat)
            services=("${CHAT_SERVICES[@]}")
            echo -e "${BLUE}Starting full chat stack...${NC}"
            ;;
        analytics)
            services=("${ANALYTICS_SERVICES[@]}")
            echo -e "${BLUE}Starting analytics set...${NC}"
            ;;
        *)
            echo -e "${RED}Unknown group: $group${NC}"
            echo "Available groups: minimal, platform, chat, analytics"
            return 1
            ;;
    esac

    echo ""

    # Sort services by tier for proper dependency ordering
    local sorted_services=()
    for tier in 0 1 2 3 4 5; do
        for svc in "${services[@]}"; do
            if [[ "$(get_service_tier "$svc")" == "$tier" ]]; then
                sorted_services+=("$svc")
            fi
        done
    done

    # Start services in tier order
    local current_tier=-1
    for svc in "${sorted_services[@]}"; do
        local tier=$(get_service_tier "$svc")
        if [[ $tier -ne $current_tier ]]; then
            current_tier=$tier
            echo -e "${CYAN}── Tier $tier ──${NC}"
        fi
        start_service "$svc"
        echo ""
    done

    # Show health summary
    show_health_summary "${services[@]}"
}

stop_service() {
    local port=$1

    if ! check_port $port; then
        echo -e "${YELLOW}No service running on port $port${NC}"
        return 0
    fi

    local pid=$(get_pid_on_port $port)
    echo -e "${BLUE}Stopping service on port $port (PID: $pid)...${NC}"
    kill $pid 2>/dev/null
    sleep 1

    if check_port $port; then
        echo -e "${YELLOW}Service still running, sending SIGKILL...${NC}"
        kill -9 $pid 2>/dev/null
    fi

    echo -e "${GREEN}Stopped${NC}"
}

stop_all_services() {
    echo -e "${BLUE}Stopping all Indemn services...${NC}"
    echo ""

    local stopped=0
    for name in "${!SERVICES[@]}"; do
        IFS=':' read -r port dir cmd <<< "${SERVICES[$name]}"
        if check_port $port; then
            local pid=$(get_pid_on_port $port)
            echo -e "Stopping ${BOLD}$name${NC} on port $port (PID: $pid)..."
            kill $pid 2>/dev/null
            ((stopped++))
        fi
    done

    sleep 2

    # Force kill any remaining
    for name in "${!SERVICES[@]}"; do
        IFS=':' read -r port dir cmd <<< "${SERVICES[$name]}"
        if check_port $port; then
            local pid=$(get_pid_on_port $port)
            echo -e "${YELLOW}Force stopping $name...${NC}"
            kill -9 $pid 2>/dev/null
        fi
    done

    if [[ $stopped -eq 0 ]]; then
        echo -e "${YELLOW}No services were running${NC}"
    else
        echo ""
        echo -e "${GREEN}Stopped $stopped service(s)${NC}"
    fi
}

show_logs() {
    local name=$1

    if [[ "$name" == "combined" ]]; then
        show_combined_logs
        return
    fi

    local logfile="$REPO_DIR/.logs/$name.log"

    if [[ ! -f "$logfile" ]]; then
        echo -e "${RED}No log file found for $name${NC}"
        echo "Available logs:"
        ls -1 "$REPO_DIR/.logs/"*.log 2>/dev/null | xargs -n1 basename 2>/dev/null | sed 's/.log$//'
        return 1
    fi

    echo -e "${BLUE}Tailing logs for $name (Ctrl+C to stop)...${NC}"
    tail -f "$logfile"
}

show_combined_logs() {
    local log_dir="$REPO_DIR/.logs"

    if [[ ! -d "$log_dir" ]] || [[ -z "$(ls -A "$log_dir"/*.log 2>/dev/null)" ]]; then
        echo -e "${RED}No log files found in $log_dir${NC}"
        return 1
    fi

    echo -e "${BLUE}Combined logs from all services (Ctrl+C to stop)...${NC}"
    echo ""

    # Use tail with color-coded prefixes
    # This uses a simple approach with tail -f and awk for coloring
    tail -f "$log_dir"/*.log 2>/dev/null | awk '
        /==>.*<==/ {
            # Extract filename from tail header
            gsub(/==> /, "", $0)
            gsub(/ <==/, "", $0)
            gsub(/.*\//, "", $0)
            gsub(/\.log/, "", $0)
            current_file = $0
            next
        }
        {
            # Color codes
            if (current_file ~ /bot-service/) color = "\033[0;32m"
            else if (current_file ~ /platform/) color = "\033[0;34m"
            else if (current_file ~ /evaluations/) color = "\033[0;35m"
            else if (current_file ~ /observability/) color = "\033[0;36m"
            else if (current_file ~ /middleware/) color = "\033[0;33m"
            else if (current_file ~ /copilot/) color = "\033[0;31m"
            else color = "\033[0;37m"

            printf "%s[%-20s]\033[0m %s\n", color, current_file, $0
        }
    '
}

start_interactive() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                 INDEMN LOCAL DEV - INTERACTIVE                 ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Choose a service group to start:"
    echo ""
    echo "  1) minimal   - bot-service + evaluations (agent development)"
    echo "  2) platform  - platform-v2 + bot-service (agent builder)"
    echo "  3) chat      - full chat stack (end-to-end chat testing)"
    echo "  4) analytics - observability stack"
    echo "  5) custom    - select individual services"
    echo ""
    read -p "Enter choice [1-5]: " choice

    case $choice in
        1) start_group "minimal" ;;
        2) start_group "platform" ;;
        3) start_group "chat" ;;
        4) start_group "analytics" ;;
        5)
            echo ""
            echo "Available services:"
            local i=1
            local svc_array=()
            for svc in "${!SERVICES[@]}"; do
                echo "  $i) $svc"
                svc_array+=("$svc")
                ((i++))
            done
            echo ""
            read -p "Enter service numbers (comma-separated): " selections
            IFS=',' read -ra nums <<< "$selections"
            for num in "${nums[@]}"; do
                num=$(echo "$num" | tr -d ' ')
                if [[ $num =~ ^[0-9]+$ ]] && (( num > 0 && num <= ${#svc_array[@]} )); then
                    start_service "${svc_array[$((num-1))]}"
                    sleep 2
                fi
            done
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            ;;
    esac
}

print_help() {
    echo ""
    echo -e "${BLUE}${BOLD}Indemn Local Development Helper${NC}"
    echo ""
    echo -e "${BOLD}Usage:${NC}"
    echo "  ./local-dev.sh setup                     - Install dependencies (run once)"
    echo "  ./local-dev.sh status                    - Check service status"
    echo "  ./local-dev.sh validate --env=dev        - Validate environment only"
    echo "  ./local-dev.sh start <target> --env=dev  - Start with validation"
    echo "  ./local-dev.sh stop <port|all>           - Stop service(s)"
    echo "  ./local-dev.sh logs <service|combined>   - View logs"
    echo ""
    echo -e "${BOLD}First Time Setup:${NC}"
    echo "  1. ./local-dev.sh setup                  # Install Node dependencies"
    echo "  2. cp .env.template .env.dev             # Create environment file"
    echo "  3. Edit .env.dev with your credentials"
    echo "  4. ./local-dev.sh start minimal --env=dev"
    echo ""
    echo -e "${BOLD}Environment:${NC}"
    echo "  --env=dev    Load .env.dev (development)"
    echo "  --env=prod   Load .env.prod (production data)"
    echo ""
    echo -e "${BOLD}Service Groups:${NC}"
    echo "  minimal   - bot-service, evaluations, evaluations-ui"
    echo "  platform  - bot-service, platform-v2, platform-v2-ui, evaluations"
    echo "  chat      - bot-service, middleware, copilot-server, conversation-service, point-of-sale"
    echo "  analytics - observability, observability-ui"
    echo "  all       - All services (use with caution)"
    echo ""
    echo -e "${BOLD}Individual Services:${NC}"
    for svc in "${!SERVICES[@]}"; do
        IFS=':' read -r port dir cmd <<< "${SERVICES[$svc]}"
        printf "  %-20s (port %s)\n" "$svc" "$port"
    done | sort
    echo ""
    echo -e "${BOLD}Examples:${NC}"
    echo "  ./local-dev.sh start minimal --env=dev   # Start bot + evals with dev config"
    echo "  ./local-dev.sh validate --env=prod       # Check prod connectivity"
    echo "  ./local-dev.sh logs combined             # Watch all service logs"
    echo "  ./local-dev.sh stop all                  # Stop everything"
    echo ""
}

# =============================================================================
# SETUP FUNCTIONS
# =============================================================================

# Node.js services that need npm install (resolves directory aliases)
NODE_SERVICES=(
    "copilot-server"
    "copilot-dashboard"
    "middleware-socket-service"
    "copilot-sync-service"
    "voice-service"
    "point-of-sale"
    "${_platform_dir}/ui"
    "${_observatory_dir}/frontend"
)

setup_dependencies() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}              INSTALLING DEPENDENCIES                          ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""

    local success=0
    local failed=0

    # Node.js services
    echo -e "${CYAN}Installing Node.js dependencies...${NC}"
    echo ""
    for dir in "${NODE_SERVICES[@]}"; do
        local full_path="$REPO_DIR/$dir"
        local display_name="${dir##*/}"  # Show last path component
        [[ "$display_name" == "$dir" ]] && display_name="$dir"
        if [[ -d "$full_path" ]] && [[ -f "$full_path/package.json" ]]; then
            echo -ne "  Installing ${BOLD}$dir${NC}..."
            if (cd "$full_path" && npm install --silent 2>/dev/null); then
                echo -e " ${GREEN}✓${NC}"
                ((success++))
            else
                echo -e " ${RED}✗${NC}"
                ((failed++))
            fi
        else
            echo -e "  ${YELLOW}Skipping $dir (not found)${NC}"
        fi
    done

    echo ""

    # Fix sharp module for Apple Silicon (copilot-server needs this)
    if [[ "$(uname -m)" == "arm64" ]] && [[ -d "$REPO_DIR/copilot-server" ]]; then
        echo -e "${CYAN}Fixing platform-specific modules...${NC}"
        echo -ne "  Rebuilding ${BOLD}sharp${NC} for Apple Silicon..."
        if (cd "$REPO_DIR/copilot-server" && npm install --os=darwin --cpu=arm64 sharp --silent 2>/dev/null); then
            echo -e " ${GREEN}✓${NC}"
        else
            echo -e " ${YELLOW}⚠ (may need manual fix)${NC}"
        fi
    fi

    echo ""

    # Python services with uv (optional - uv run handles this automatically)
    echo -e "${CYAN}Python services use 'uv run' which auto-installs dependencies.${NC}"
    echo ""

    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    if [[ $failed -eq 0 ]]; then
        echo -e "${GREEN}${BOLD}✓ Setup complete ($success packages installed)${NC}"
    else
        echo -e "${YELLOW}${BOLD}Setup finished: $success succeeded, $failed failed${NC}"
    fi
    echo ""
    echo "Next steps:"
    echo "  1. Create environment file: cp .env.template .env.dev"
    echo "  2. Fill in credentials (see template comments)"
    echo "  3. Start services: ./local-dev.sh start minimal --env=dev"
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================

# Parse --env flag from all arguments
parse_env_flag "$@"

case "${1:-}" in
    setup)
        setup_dependencies
        ;;

    status)
        print_status
        ;;

    validate)
        if [[ -z "$INDEMN_ENV" ]]; then
            echo -e "${RED}Please specify environment: --env=dev or --env=prod${NC}"
            exit 1
        fi
        if ! load_environment "$INDEMN_ENV"; then
            exit 1
        fi
        validate_all
        exit $?
        ;;

    start)
        if [[ -z "${2:-}" ]]; then
            echo -e "${RED}Please specify a service or group to start${NC}"
            print_help
            exit 1
        fi

        # Require environment for start
        if [[ -z "$INDEMN_ENV" ]]; then
            echo -e "${RED}Please specify environment: --env=dev or --env=prod${NC}"
            echo ""
            echo "Example: ./local-dev.sh start $2 --env=dev"
            exit 1
        fi

        # Load and validate environment
        if ! load_environment "$INDEMN_ENV"; then
            exit 1
        fi

        # Determine services to validate/start
        target_services=()
        case "$2" in
            minimal)
                target_services=("${MINIMAL_SERVICES[@]}")
                ;;
            platform)
                target_services=("${PLATFORM_SERVICES[@]}")
                ;;
            chat)
                target_services=("${CHAT_SERVICES[@]}")
                ;;
            analytics)
                target_services=("${ANALYTICS_SERVICES[@]}")
                ;;
            all)
                for svc in "${!SERVICES[@]}"; do
                    target_services+=("$svc")
                done
                ;;
            *)
                target_services=("$2")
                ;;
        esac

        # Run validation
        echo ""
        if ! validate_all "${target_services[@]}"; then
            echo ""
            read -p "Validation failed. Continue anyway? [y/N]: " confirm
            if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
                echo "Aborted."
                exit 1
            fi
        fi
        echo ""

        # Start services
        case "$2" in
            minimal|platform|chat|analytics)
                start_group "$2"
                ;;
            all)
                echo -e "${BLUE}Starting all services...${NC}"
                for svc in "${!SERVICES[@]}"; do
                    start_service "$svc"
                    sleep 2
                done
                ;;
            *)
                start_service "$2"
                ;;
        esac
        ;;

    stop)
        if [[ -z "${2:-}" ]]; then
            echo -e "${RED}Please specify a port or 'all'${NC}"
            exit 1
        fi
        if [[ "$2" == "all" ]]; then
            stop_all_services
        else
            stop_service "$2"
        fi
        ;;

    logs)
        if [[ -z "${2:-}" ]]; then
            echo -e "${RED}Please specify a service name or 'combined'${NC}"
            echo "Available: combined, or any of:"
            ls -1 "$REPO_DIR/.logs/"*.log 2>/dev/null | xargs -n1 basename 2>/dev/null | sed 's/.log$//' | sort
            exit 1
        fi
        show_logs "$2"
        ;;

    help|--help|-h)
        print_help
        ;;

    "")
        start_interactive
        ;;

    *)
        echo -e "${RED}Unknown command: $1${NC}"
        print_help
        exit 1
        ;;
esac
