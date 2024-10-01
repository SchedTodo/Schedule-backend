#!/bin/bash

# 激活 Conda 环境
source /home/azureuser/miniconda3/etc/profile.d/conda.sh
conda activate Schedule

docker compose -f docker-compose.yml down -v
docker compose -f docker-compose.yml up -d

export DJANGO_SETTINGS_MODULE=main.settings_prod

python manage.py makemigrations
python manage.py migrate
