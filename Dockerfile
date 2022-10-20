FROM python:3
RUN mkdir -p /opt/procrastinate/procrastinate
WORKDIR /opt/procrastinate
COPY pyproject.toml README.rst /opt/procrastinate/
COPY procrastinate/ /opt/procrastinate/procrastinate/
RUN pip install -e /opt/procrastinate[aiopg]
CMD ["procrastinate", "worker"]
