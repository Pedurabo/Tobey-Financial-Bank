# Banking Management System - Deployment Guide

## 🚀 Production Deployment Steps

### 1. **Environment Setup**

#### Prerequisites
- Python 3.8+
- pip package manager
- Git (for version control)
- Web server (Nginx/Apache) - Optional
- SSL certificate - Recommended for production

#### Installation Steps
```bash
# Clone the repository
git clone <your-repo-url>
cd banking-management-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret-key
export DATABASE_URL=your-database-url
```

### 2. **Database Setup**

#### SQLite (Development)
```bash
# Database will be created automatically
python -c "from src.utils.database import init_db; init_db()"
```

#### PostgreSQL (Production)
```sql
-- Create database
CREATE DATABASE banking_system;

-- Create user
CREATE USER banking_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE banking_system TO banking_user;
```

### 3. **Configuration**

#### Environment Variables
Create `.env` file:
```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=postgresql://banking_user:secure_password@localhost/banking_system
DEBUG=False
HOST=0.0.0.0
PORT=5000
```

#### Security Configuration
- Change default passwords
- Enable HTTPS
- Configure firewall rules
- Set up logging

### 4. **Production Server Setup**

#### Using Gunicorn
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 webapp:app
```

#### Using uWSGI
```bash
# Install uWSGI
pip install uwsgi

# Create uwsgi.ini
[uwsgi]
module = webapp:app
master = true
processes = 4
socket = :5000
vacuum = true
die-on-term = true

# Run with uWSGI
uwsgi --ini uwsgi.ini
```

### 5. **Web Server Configuration (Nginx)**

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/static/files;
        expires 30d;
    }
}
```

### 6. **Systemd Service (Linux)**

#### Create service file
```bash
sudo nano /etc/systemd/system/banking-system.service
```

#### Service configuration
```ini
[Unit]
Description=Banking Management System
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/banking-system
Environment=PATH=/path/to/banking-system/venv/bin
ExecStart=/path/to/banking-system/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 webapp:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Enable and start service
```bash
sudo systemctl enable banking-system
sudo systemctl start banking-system
sudo systemctl status banking-system
```

### 7. **Monitoring & Logging**

#### Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
if not app.debug:
    file_handler = RotatingFileHandler('logs/banking_system.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Banking System startup')
```

#### Health Check Endpoint
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })
```

### 8. **Backup Strategy**

#### Database Backup
```bash
# PostgreSQL backup
pg_dump banking_system > backup_$(date +%Y%m%d_%H%M%S).sql

# SQLite backup
cp banking_system.db backup_$(date +%Y%m%d_%H%M%S).db
```

#### Automated Backup Script
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/banking-system"

mkdir -p $BACKUP_DIR
pg_dump banking_system > $BACKUP_DIR/backup_$DATE.sql

# Keep only last 30 days of backups
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

### 9. **Security Checklist**

- [ ] Change default passwords
- [ ] Enable HTTPS
- [ ] Configure firewall
- [ ] Set up SSL certificates
- [ ] Enable security headers
- [ ] Configure rate limiting
- [ ] Set up intrusion detection
- [ ] Regular security updates
- [ ] Database encryption
- [ ] Audit logging

### 10. **Performance Optimization**

#### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_loans_status ON loans(status);
```

#### Caching Strategy
```python
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})

# Cache frequently accessed data
@cache.memoize(timeout=300)
def get_customer_data(customer_id):
    # Database query here
    pass
```

### 11. **Testing Production Deployment**

#### Health Check
```bash
curl -f http://your-domain.com/health
```

#### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 http://your-domain.com/
```

### 12. **Rollback Plan**

#### Version Control
```bash
# Tag current version
git tag v1.0.0-production

# Rollback if needed
git checkout v1.0.0-production
sudo systemctl restart banking-system
```

#### Database Rollback
```bash
# Restore from backup
psql banking_system < backup_20240101_120000.sql
```

## 🎯 **Deployment Checklist**

- [ ] Environment setup complete
- [ ] Database configured
- [ ] Security settings applied
- [ ] SSL certificate installed
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Performance optimized
- [ ] Load testing completed
- [ ] Rollback plan ready
- [ ] Documentation updated

## 📞 **Support & Maintenance**

### Regular Maintenance Tasks
- Database backups (daily)
- Log rotation (weekly)
- Security updates (monthly)
- Performance monitoring (continuous)
- User training (as needed)

### Emergency Contacts
- System Administrator: admin@your-bank.com
- Database Administrator: dba@your-bank.com
- Security Team: security@your-bank.com

---

**🎉 Your Banking Management System is ready for production deployment!** 