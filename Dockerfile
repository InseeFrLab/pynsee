FROM python:3.9-slim-bullseye

RUN apt-get -y update && \
    apt-get -y install wget

# Install Miniconda
#RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
#    bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda && \
#    rm -f Miniconda3-latest-Linux-x86_64.sh

# Make conda command available
#ENV PATH="/miniconda/bin:${PATH}"

# Install mc
RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc && \
    chmod +x /usr/local/bin/mc

# Installation quarto
ENV QUARTO_VERSION="0.9.287"
RUN wget "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.deb"
RUN apt install "./quarto-${QUARTO_VERSION}-linux-amd64.deb"

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
COPY requirements-extra.txt .
COPY docs/requirements.txt /docs/requirements.txt 

RUN pip install -r requirements.txt
RUN pip install -r requirements-extra.txt
RUN pip install -r docs/requirements.txt 
RUN pip install pylint

# Copy project files on the Docker image
COPY ./pynsee /pynsee
COPY setup.py .
COPY pyproject.toml .
COPY README.rst .

RUN pip install . --use-feature=in-tree-build

# Make container listen on port 5000
EXPOSE 5000

# Make Python interpreter from "base" available
#ENV PATH="/miniconda/envs/testenv/bin:${PATH}"

ADD pynsee pynsee/

CMD ["pylint", "pynsee/download/__init__.py"]
