FROM python:3.6-slim
LABEL maintainer="ManojManivannan"

###### Copy python package
COPY . /home/

WORKDIR /home/

###### Install the python packages
RUN apt-get update && apt-get install -y gcc libgeos-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install --no-cache-dir wheel
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir etc/basemap-master.zip
RUN rm -f etc/basemap-master.zip

EXPOSE 8501
CMD ["python","home/app/main.py"]
