# Selenium'un resmi Chrome base image'ini kullan
FROM selenium/standalone-chrome:latest

# Root olarak çalış (paket yüklemek için)
USER root

# Python ve pip kur
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini oluştur
WORKDIR /app

# Requirements dosyasını kopyala ve bağımlılıkları yükle
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Test dosyalarını kopyala
COPY features/ ./features/
COPY pages/ ./pages/
COPY utilities/ ./utilities/
COPY configuration.properties .
COPY behave.ini .

# Reports klasörünü oluştur
RUN mkdir -p reports/allure-results

# Make /app directory writable for output files
RUN chmod -R 777 /app

# Selenium user'a geri dön
USER seluser

# Chrome'un headless modda çalışması için environment variables
ENV DISPLAY=:99

# Testleri çalıştırmak için varsayılan komut
CMD ["behave", "-f", "allure_behave.formatter:AllureFormatter", "-o", "reports/allure-results"]
