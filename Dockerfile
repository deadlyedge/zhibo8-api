FROM python:3.11-slim
LABEL maintainer="xdream oldlu <xdream@gmail.com>"

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 
COPY ./app /app/

# 
CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8001"]