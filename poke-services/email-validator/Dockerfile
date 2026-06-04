FROM python:3.12-slim
WORKDIR /app
RUN pip install dnspython
COPY server.py .
EXPOSE 8781
CMD ["python3", "server.py"]
