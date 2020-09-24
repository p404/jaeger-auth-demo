# -*- coding: utf-8 -*-
# pylint: disable=C0103

import os
import time 
import logging
import opentracing
from jaeger_client import Config
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Response, request 
from flask_opentracing import FlaskTracer

SLEEP_TIMER = os.environ['SLEEP_TIMER']
DATABASE_URI = os.environ['DATABASE_URI']
JAEGER_HOST = os.environ['JAEGER_REPORTING_HOST']
JAEGER_PORT = os.environ['JAEGER_REPORTING_PORT']
JAEGER_SVC_NAME = os.environ['JAEGER_SVC_NAME']

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)
engine = db.engine
Session = sessionmaker(bind=engine)

config = Config(
    config={
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'local_agent': {
            'reporting_host': JAEGER_HOST,
            'reporting_port': JAEGER_PORT,
        },
        'logging': True,
    },
    service_name=JAEGER_SVC_NAME,
)
opentracing_tracer = config.initialize_tracer()
tracer = FlaskTracer(opentracing_tracer)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)


@app.route('/auth', methods=['POST'])
@tracer.trace()
def login():
    if request.method == 'POST':
        logging.info("Request headers: {}".format(request.headers))

        span = tracer.get_span()
        payload = request.get_json()
        email = payload['email']
        password = payload['password']

        sp = opentracing_tracer.start_span('query', child_of=span)
        session = Session()
        user = session.query(Users).filter_by(email = email).first()
        time.sleep(int(SLEEP_TIMER))
        sp.finish()
        if user is None:
            return Response(status=404, mimetype='application/json')
        elif user.password == password:
            return Response(status=200, mimetype='application/json')
        else:
            return Response(status=401, mimetype='application/json')
   
if __name__ == "__main__":
    log_level = logging.DEBUG
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)
    app.run(debug=True, port=5001, host='0.0.0.0')
    opentracing_tracer.close()
