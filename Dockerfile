FROM python:3.11.4-slim as installer

WORKDIR /app

COPY . /app/

RUN python -m venv /app/env

RUN . /app/env/bin/activate && \
python -m ensurepip --upgrade && \
python -m pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu  && \
python -m pip install --no-cache-dir -r /app/requirements.txt

FROM python:3.11.4-slim as final

WORKDIR /app

COPY --from=installer /app /app

EXPOSE 8501

ENV STREAMLIT_THEME_BASE dark
ENV STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR #3A475C
ENV STREAMLIT_THEME_BACKGROUND_COLOR #2d3748

RUN chown -R 2000:2000 /app
USER 2000:2000

CMD ["env/bin/streamlit", "run", "app.py"]