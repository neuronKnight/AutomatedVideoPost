FROM python:3.10-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    xvfb \
    chromium \
    fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

# Install playwright
RUN pip install playwright && playwright install chromium

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 3032

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3032"]