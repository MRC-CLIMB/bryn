from django.core.mail import send_mail as django_send_mail

from huey.contrib.djhuey import task


@task(retries=2, retry_delay=10)
def send_mail(*args, **kwargs):
    django_send_mail(*args, **kwargs)
