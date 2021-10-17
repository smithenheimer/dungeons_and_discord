FROM python:3
WORKDIR /usr/src/app
COPY . .

RUN pip3 install python-dotenv
RUN pip3 install psycopg2-binary
RUN pip3 install discord
RUN pip3 install sqlalchemy
RUN pip3 install pandas
RUN pip3 install loguru

CMD ["dd_bot.py"]
ENTRYPOINT ["python3"]

