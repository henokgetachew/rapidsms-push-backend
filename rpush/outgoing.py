from xml.sax.saxutils import escape
import urllib2
from django.template import loader, Context

from rapidsms.backends.base import BackendBase

outgoing_template_file_name = 'push-mobile-outgoing-template.xml'


class PushBackend(BackendBase):
    """
    A RapidSMS backend for PUSH SMS

    Example POST:

    RemoteNetwork=celtel-tz&IsReceipt=NO&BSDate-tomorrow=20101009&Local=*15522&ReceiveDate=2010-10-08%2016:46:22%20%2B0000&BSDate-today=20101008&ClientID=1243&MessageID=336876061&ChannelID=9840&ReceiptStatus=&ClientName=OnPoint%20-%20TZ&Prefix=JSI&MobileDevice=&BSDate-yesterday=20101007&Remote=%2B255785000017&MobileNetwork=celtel-tz&State=11&ServiceID=124328&Text=test%203&MobileNumber=%2B255785000017&NewSubscriber=NO&RegType=1&Subscriber=%2B255785000017&ServiceName=JSI%20Demo&Parsed=&BSDate-thisweek=20101004&ServiceEndDate=2010-10-30%2023:29:00%20%2B0300&Now=2010-10-08%2016:46:22%20%2B0000
    """

    def configure(self, sendsms_url, sendsms_params, **kwargs):
        self.sendsms_url = sendsms_url
        for key in ["channel", "service", "password"]:
            if key not in sendsms_params:
                raise ValueError("You are missing required config parameter: %s" % key)
        self.sendsms_params = sendsms_params

    def send(self, id_, text, identities, context={}):
        self.info('Sending message: %s' % text)
        self.info('identity: %s' % identities[0])

        params = {"text": escape(text),
                  "number": identities[0],
                 }
        params.update(self.sendsms_params)

        messaging_template = loader.get_template(outgoing_template_file_name)
        messaging_context = Context(params, True, None, None, None)

        payload = messaging_template.render(messaging_context)

        req = urllib2.Request(url=self.sendsms_url,
                              data=payload,
                              headers={'Content-Type': 'application/xml'})

        handle = urllib2.urlopen(req)
        resp = handle.read()
        self.debug("got push response: %s" % resp)
        return True
