# Schedule-backend


User
Schedule
Settings

### 修改 model
```bash
python manage.py makemigrations
python manage.py migrate
```

### 建立超級使用者
```bash
python manage.py createsuperuser
```

### 建立新的 app
```bash
python manage.py startapp app_name
```

### 运行
```bash
python manage.py runserver
daphne -p 8000 main.asgi:application
```

### 测试
```bash
python manage.py test
```

### 部署
#### 数据库
```bash
sudo bash scripts/initilize.sh
```

#### 配置 Nginx
/etc/nginx/sites-available/schedule
```nginx
server {
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Cookie $http_cookie;
        proxy_cookie_path / /;
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```
用 certbot 配置 https

```bash
sudo nginx -t  # 检查配置文件
sudo systemctl restart nginx
```

#### 启动服务
/etc/systemd/system/schedule.service
```systemd
[Unit]
Description=Schedule
After=network.target

[Service]
User=azureuser
Group=sudo
WorkingDirectory=/home/azureuser/Schedule-backend/
ExecStart=/home/azureuser/Schedule-backend/scripts/start.sh
Environment="DJANGO_SETTINGS_MODULE=main.settings_prod"

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start schedule
sudo systemctl enable schedule  # 开机启动
sudo systemctl status schedule  # 查看状态
sudo systemctl stop schedule  # 停止
sudo systemctl restart schedule  # 重启
sudo journalctl -u schedule  # 查看日志
```

