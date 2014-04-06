from rpush.forms import PushForm
from lxml import etree
from django.http import QueryDict, HttpRequest, HttpResponse

from rapidsms.backends.http.views import BaseHttpBackendView
from rapidsms.router.celery import CeleryRouter 
from rapidsms.models import Backend
from rapidsms.messages import IncomingMessage

import logging
import datetime

logger=logging.getLogger(__name__)

class PushBackendView(BaseHttpBackendView):
    """ Backend view for handling inbound SMSes from Kannel """

    http_method_names = ['post']
    form_class = PushForm

    def form_valid(self, form):
        logger.debug('form is valid')

        incoming_data = form.get_incoming_data()
        backend, _ = Backend.objects.get_or_create(name=self.backend_name)
        connection, _ = backend.connection_set.get_or_create(identity=incoming_data['identity'], backend=backend)
        message = IncomingMessage([connection,], incoming_data['text'], datetime.datetime.now())

        router = CeleryRouter()
        response = router.receive_incoming(message)

        return HttpResponse('OK')


    def get_form_kwargs(self):
        xml = etree.fromstring(HttpRequest.read(self.request))

        kwargs = {
            'initial': self.get_initial(),
            'data': QueryDict('')
        }
        if self.request.method in ('POST', 'PUT'):
            needed_keys = ['MobileNumber', 'Text']
            post_args = []

            for element in xml:
                if element.attrib['name'] in needed_keys:
                    value = element.text or ''
                    post_args.append(element.attrib['name'] + '=' + value)

            kwargs['data'] = QueryDict('&'.join(post_args))

        return kwargs
