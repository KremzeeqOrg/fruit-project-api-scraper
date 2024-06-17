FROM public.ecr.aws/lambda/python:3.10

#COPY requirements.txt ./
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install dependencies for Python app
RUN pip install --no-cache-dir -r requirements.txt

#COPY src/* .
COPY src/* ${LAMBDA_TASK_ROOT}

CMD [ "handler.main" ]