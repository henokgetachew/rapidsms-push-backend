from django import forms

class BaseHttpForm(forms.Form):

    def get_incoming_data(self):
        raise NotImplementedError()


class PushForm(BaseHttpForm):
    Text = forms.CharField()
    MobileNumber = forms.CharField()

    def get_incoming_data(self):
        return {'identity': self.cleaned_data['MobileNumber'],
                'text': self.cleaned_data['Text']}
