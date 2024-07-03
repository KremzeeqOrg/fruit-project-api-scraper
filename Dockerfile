FROM public.ecr.aws/lambda/python:3.11

RUN pip install pip --upgrade

RUN cat /etc/passwd
RUN echo ${LAMBDA_TASK_ROOT}
RUN sudo apt-get update
RUN apt-get install adduser

RUN adduser -D newuser
USER newuser

# Set the working directory to the Lambda task root
WORKDIR ${LAMBDA_TASK_ROOT}/newuser

COPY --chown=newuser:newuser requirements.txt requirements.txt

# Install dependencies for Python app
RUN pip install --user --no-cache-dir -r requirements.txt

ENV PATH="${LAMBDA_TASK_ROOT}/newuser/.local/bin:${PATH}"

COPY --chown=newuser:newuser src/ .

CMD [ "handler.main" ]