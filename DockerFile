# 基础镜像
FROM python:3.12

# 设置工作目录
WORKDIR /app

# 复制代码到容器
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露容器的端口
EXPOSE 8000

# 设置环境变量
ENV DJANGO_SETTINGS_MODULE=main.settings_prod

# 启动应用
CMD ["daphne", "-p", "8000", "main.asgi:application"]
