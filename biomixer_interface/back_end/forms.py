from django import forms
from django.forms import formset_factory, BaseFormSet
from .models import *


# Labels for forms
class Labels:
    options = ['Support', 'Plasticizer', 'Binder', 'Preservative', 'Organic Waste']
    index = 0

    @property
    def get_label(self):
        current_index = self.index
        self.index += 1
        return self.options[current_index]


class MaterialForm (forms.Form):
    material = forms.ModelChoiceField(label='Material',
                                      required=True,
                                      widget=forms.Select(
                                          attrs={
                                              'class': 'col-3 mr-4 custom-select d-block',
                                              'placeholder': 'Choose Material'
                                          }),
                                      queryset=Material.objects.all())
    value = forms.IntegerField(required=True,
                               widget=forms.TextInput(
                                   attrs={
                                       'class': 'col-3 mr-4 form-control',
                                       'type': 'number', 'min': '0',
                                       'step': '0.1',
                                       'value': 0
                                    }))
    type = forms.ChoiceField(choices=Supply.Types.choices,
                             required=True,
                             widget=forms.Select(
                                 attrs={
                                     'class': 'col-3 mr-4 custom-select'
                                 }))
    # state = forms.TypedChoiceField(choices=formfields.State, initial='FIXED')




MaterialFormSet = formset_factory(MaterialForm, extra=5)
