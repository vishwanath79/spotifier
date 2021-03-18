# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1




WORKDIR /app
#ADD . /app

# Install pip requirements
#ADD requirements.txt .
RUN python -m pip install -r requirements.txt

# --------------- Configure Streamlit ---------------
RUN mkdir -p /root/.streamlit

RUN bash -c 'echo -e "\
	[server]\n\
	enableCORS = false\n\
	" > /root/.streamlit/config.toml'

EXPOSE 8501
COPY . /app



# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights

CMD ["streamlit", "run"]

CMD ["spotify_explorer.py"]



# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug

