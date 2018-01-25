FROM python:2.7

WORKDIR /opt/

COPY ./app .
RUN pip install --no-cache-dir -r requirements.txt

ENV CONTAINER_SCALING_FILE=/var/lib/micado/alert-generator/scaling_policy.yaml 
ENV ALERTS_FILE_PATH=/etc/prometheus/
ENV AUTO_GENERATE_ALERT=True
ENV DEFAULT_SCALEUP=90
ENV DEFAULT_SCALEDOWN=30 
ENV PROMETHEUS=localhost

CMD [ "python", "./generator.py" ]