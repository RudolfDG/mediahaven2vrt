FROM python:3.6
EXPOSE 8080

RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup

WORKDIR /app

COPY --chown=appuser:appgroup . .

RUN pip install -r requirements.txt --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple --trusted-host do-prd-mvn-01.do.viaa.be

USER appuser
CMD [ "uwsgi", "-i", "uwsgi.ini"]
