FROM python:3.11-slim
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# RUN apt-get update && apt-get install -y \
#     build-essential \ 
#     git \
#     curl \
#     && rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt .

# RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt && useradd -r -u 10001 tripmate-aws

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
