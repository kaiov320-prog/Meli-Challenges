FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py demo.py ./
COPY tests ./tests
RUN mkdir -p /app/data
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "app.py"]
CMD ["--help"]
