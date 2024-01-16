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