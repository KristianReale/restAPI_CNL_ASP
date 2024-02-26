# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

ARG PYTHON_VERSION=3.10.4
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \    
    git \
    coreutils
    

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN git clone https://github.com/streamlit/streamlit-example.git streamlit
RUN pip install -r streamlit/requirements.txt

ADD cnl2asp cnl2asp
ADD asp2cnl asp2cnl

# RUN python -m pip install --upgrade pip

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \    
    python -m pip install -r requirements.txt

RUN python -m pip install cnl2asp/.
RUN python -m pip install asp2cnl/.


# Copy the source code into the container.
COPY . .
RUN chmod -R 777 .

# Switch to the non-privileged user to run the application.
USER appuser

# Expose the port that the application listens on.
EXPOSE 5000
EXPOSE 8501

# Run the application.


#CMD nohup python app.py && 

ADD entrypoint.sh entrypoint.sh
#CMD nohup streamlit run "CNL ASP Solutions.py" --server.port=8501 --server.address=0.0.0.0 
ENTRYPOINT /app/entrypoint.sh
