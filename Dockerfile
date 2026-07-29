FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

RUN useradd agent
USER agent

CMD ["python", "main.py"]