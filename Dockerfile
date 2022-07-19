FROM python:3-slim as requirements 

RUN pip3 install --no-cache-dir --upgrade poetry

COPY pyproject.toml poetry.lock ./ 
RUN poetry export -f requirements.txt --without-hashes -o /requirements.txt 

#​ Final app image 
FROM python:3-slim as app 

#​ Switching to non-root user appuser
RUN adduser appuser 
WORKDIR /home/appuser 
USER appuser:appuser 

#​ Install requirements 
COPY --from=requirements requirements.txt . 
RUN pip3 install --no-cache-dir --user -r requirements.txt

# Add the app code
COPY app.py /home/appuser/app.py

CMD ["python3", "app.py"]
