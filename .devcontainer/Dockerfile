FROM mcr.microsoft.com/devcontainers/python:3.12

USER root

RUN sudo apt-get update \
  && apt-get install -y --no-install-recommends \
  bash-completion \
  postgresql-common \
  && /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y \
  && apt-get install -y --no-install-recommends \
  postgresql-client \
  && rm -rf /var/lib/apt/lists/*

USER vscode

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pipx install poetry \
  && poetry completions bash >> ~/.bash_completion
