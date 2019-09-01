FROM python:3.7-buster

WORKDIR /usr/src/app

ENV CHROME_HOST chrome:4444

# install required Python libraries and utility used to wait for chrome to start
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    git clone https://github.com/vishnubob/wait-for-it.git && chmod +x wait-for-it/wait-for-it.sh 

COPY . .

ENTRYPOINT [ "/bin/bash", "-c" ]

CMD ["./wait-for-it/wait-for-it.sh $CHROME_HOST --strict --timeout=10000 -- python server.py"]