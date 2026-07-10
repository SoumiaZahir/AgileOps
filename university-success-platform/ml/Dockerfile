FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt ./ 

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# السطر المعدل: إضافة تحديد المنفذ، السماح بالعمل كجذر، وتعطيل التوكن المعقد مؤقتاً لتجنب مشاكل الاتصال
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]