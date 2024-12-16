FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    libfreetype6-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./app /code/app

EXPOSE 5020

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5020"]
