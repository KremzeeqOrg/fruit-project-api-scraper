FROM public.ecr.aws/lambda/python:3.11

RUN pip install pip --upgrade

RUN cat /etc/passwd
RUN echo ${LAMBDA_TASK_ROOT}
# Install shadow-utils to get useradd command
RUN yum update -y && yum install -y shadow-utils
RUN ls /usr/sbin/

# Ensure useradd is available and check its location
RUN command -v /usr/sbin/useradd
RUN /usr/sbin/useradd -m newuser
USER newuser

# Set the working directory to the Lambda task directoy for the newuser
WORKDIR ${LAMBDA_TASK_ROOT}/newuser

COPY --chown=newuser:newuser requirements.txt requirements.txt

# Install dependencies for Python app
RUN pip install --user --no-cache-dir -r requirements.txt

ENV PATH="${LAMBDA_TASK_ROOT}/newuser/.local/bin:${PATH}"

COPY --chown=newuser:newuser src/ .

CMD [ "handler.main" ]