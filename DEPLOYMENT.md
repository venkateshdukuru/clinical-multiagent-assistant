# 🚀 Production Deployment Guide

This guide covers deploying the Medical AI Multi-Agent System to a production environment (Ubuntu EC2 or similar Linux server).

## Prerequisites

- Ubuntu 20.04+ server
- Python 3.10+
- Domain name (optional, for SSL)
- SSH access to server

## Server Setup

### 1. Initial Server Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install Nginx
sudo apt install nginx -y

# Install certbot for SSL (optional)
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Create Application User

```bash
# Create dedicated user
sudo useradd -m -s /bin/bash medicalai
sudo su - medicalai
```

### 3. Deploy Application

```bash
# Clone/upload your application
cd /home/medicalai
# Upload your medical_ai folder here

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
cd medical_ai
pip install -r requirements.txt

# Configure environment
nano .env
# Add your OPENAI_API_KEY and other settings
```

### 4. Create Systemd Service

Create `/etc/systemd/system/medicalai.service`:

```ini
[Unit]
Description=Medical AI Multi-Agent System
After=network.target

[Service]
Type=simple
User=medicalai
WorkingDirectory=/home/medicalai/medical_ai
Environment="PATH=/home/medicalai/venv/bin"
ExecStart=/home/medicalai/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable medicalai
sudo systemctl start medicalai
sudo systemctl status medicalai
```

### 5. Configure Nginx Reverse Proxy

Create `/etc/nginx/sites-available/medicalai`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    client_max_body_size 10M;  # Allow PDF uploads up to 10MB

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/medicalai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Configure SSL (Optional but Recommended)

```bash
sudo certbot --nginx -d your-domain.com
```

Follow the prompts to set up HTTPS.

## Environment Configuration

Production `.env` file:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-production-key
MODEL_NAME=gpt-4o

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
APP_RELOAD=false  # Important: disable reload in production

# Logging
LOG_LEVEL=WARNING
```

## Monitoring and Maintenance

### View Logs

```bash
# Application logs
sudo journalctl -u medicalai -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Service

```bash
sudo systemctl restart medicalai
```

### Update Application

```bash
sudo su - medicalai
cd medical_ai
source venv/bin/activate
git pull  # or upload new files
pip install -r requirements.txt
exit
sudo systemctl restart medicalai
```

## Performance Tuning

### Increase Workers

Edit `/etc/systemd/system/medicalai.service`:

```ini
ExecStart=/home/medicalai/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 8
```

Restart: `sudo systemctl daemon-reload && sudo systemctl restart medicalai`

### Optimize Nginx

Add to nginx config:

```nginx
# Enable gzip compression
gzip on;
gzip_vary on;
gzip_min_length 10240;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

# Add caching headers
add_header Cache-Control "public, max-age=3600";
```

## Security Best Practices

### 1. Firewall Configuration

```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 2. Secure Environment Variables

```bash
# Set proper permissions
chmod 600 /home/medicalai/medical_ai/.env
chown medicalai:medicalai /home/medicalai/medical_ai/.env
```

### 3. Rate Limiting (Optional)

Add to Nginx config:

```nginx
limit_req_zone $binary_remote_addr zone=medical_ai:10m rate=10r/s;

location / {
    limit_req zone=medical_ai burst=20;
    # ... rest of config
}
```

### 4. CORS Configuration

Update [app/main.py](app/main.py) for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Backup and Recovery

### Backup Critical Files

```bash
# Backup environment files
cp /home/medicalai/medical_ai/.env /backup/location/

# Backup application (if not using git)
tar -czf medical_ai_backup.tar.gz /home/medicalai/medical_ai/
```

## Health Monitoring

Set up a cron job to monitor health:

```bash
# Add to crontab
*/5 * * * * curl -f http://localhost:8000/health || systemctl restart medicalai
```

## Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u medicalai -n 50

# Check if port is in use
sudo netstat -tulpn | grep 8000

# Verify Python environment
sudo su - medicalai
cd medical_ai
source venv/bin/activate
python -m app.main
```

### High memory usage

```bash
# Monitor resources
htop

# Reduce workers if needed
# Edit /etc/systemd/system/medicalai.service
# Change --workers value
```

### Slow response times

1. Check OpenAI API latency
2. Increase worker count
3. Enable caching (if applicable)
4. Monitor server resources

## Cost Optimization

### OpenAI API Usage

- Monitor API usage in OpenAI dashboard
- Set usage limits and alerts
- Consider caching repeated analyses
- Use streaming for long responses (if needed)

### Server Resources

- Start with t2.medium or t3.medium on AWS
- Monitor CPU/Memory usage
- Scale vertically if needed
- Consider load balancing for high traffic

## Production Checklist

- [ ] SSL/HTTPS configured
- [ ] Environment variables secured
- [ ] Firewall configured
- [ ] Systemd service running
- [ ] Nginx reverse proxy configured
- [ ] Logging enabled
- [ ] Health monitoring set up
- [ ] Backups configured
- [ ] CORS properly configured
- [ ] Rate limiting enabled (if needed)
- [ ] Domain configured
- [ ] Error alerts configured

---

## Support

For production issues, check:
1. Application logs: `sudo journalctl -u medicalai`
2. Nginx logs: `/var/log/nginx/`
3. System resources: `htop` or `top`
4. OpenAI API status: https://status.openai.com/

---

**Production deployment requires careful configuration and monitoring. Always test thoroughly before deploying to production.**
