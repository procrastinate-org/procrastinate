FROM python:3

RUN pip install poetry

ARG UID=1000
ARG GID=1000
WORKDIR /src/
RUN chown -R $UID:$GID /src
USER $UID:$GID
ENV HOME="/src"

COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry install
ENTRYPOINT ["poetry", "run"]
CMD ["procrastinate", "worker"]
