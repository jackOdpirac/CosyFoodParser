FROM joyzoursky/python-chromedriver:3.7

WORKDIR /usr/src/app

# install required Python libraries
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./server.py" ]