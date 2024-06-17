FROM public.ecr.aws/lambda/python:3.10

# Set the working directory to the Lambda task root
WORKDIR ${LAMBDA_TASK_ROOT}

#COPY requirements.txt ./
COPY requirements.txt .

# Install dependencies for Python app
RUN pip install --no-cache-dir -r requirements.txt

#COPY src/* .
COPY src/* .

CMD [ "handler.main" ]