FROM python:3.8

RUN apt-get update \
&& apt-get install unixodbc-dev -y \
&& apt-get clean

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]