FROM python:3.9-slim-buster  

WORKDIR /app  

COPY requirements.txt requirements.txt 
RUN pip install -r requirements.txt  

COPY weather_api.py /app 

EXPOSE 5000  
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "weather_api:app"]
