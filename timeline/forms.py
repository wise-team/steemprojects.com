import re
from markdown import markdown

from django.core.exceptions import ValidationError
from django import forms
from django.forms import formset_factory, BaseFormSet, HiddenInput, CharField, BooleanField
from django.forms.formsets import (
    ManagementForm,
    TOTAL_FORM_COUNT,
    INITIAL_FORM_COUNT,
    MIN_NUM_FORM_COUNT,
    MAX_NUM_FORM_COUNT,
)
from django.forms.models import modelformset_factory
from django.forms.widgets import Select
from django.utils.functional import cached_property
from steem.account import Account
from steembase.exceptions import AccountDoesNotExistsException

from timeline.fields import TruncatingCharField
from timeline.models import TimelineEvent, TimelineEventInserterRulebook, TimelineEventInserterRule


class TimelineEventForm(forms.ModelForm):

    class Meta:
        model = TimelineEvent
        fields = ("date", "name", "url", "project",)
        field_classes = {
            'name': TruncatingCharField,
        }

    def __init__(self, project=None, *args, **kwargs):
        super(TimelineEventForm, self).__init__(*args, **kwargs)
        self.fields["project"].widget = forms.HiddenInput()
        self.fields["project"].initial = project and project.id
        self.fields["date"].widget.attrs = {"placeholder": "YYYY-MM-DD"}


BaseTimelineEventFormSet = modelformset_factory(
    TimelineEvent,
    fields=["date", "name", "url", "project"],
    form=TimelineEventForm,
    can_delete=True,
    extra=0,
)


class TimelineEventFormSet(BaseTimelineEventFormSet):

    def __init__(self, project=None, queryset=None, *args, **kwargs):
        self.project = project

        if queryset:
            queryset = queryset and queryset.order_by("date")

        super(TimelineEventFormSet, self).__init__(queryset=queryset, *args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super(TimelineEventFormSet, self).get_form_kwargs(*args, **kwargs)
        form_kwargs.update({
            "project": self.project,
        })
        return form_kwargs


class AttrChoiceWidget(Select):
    option_inherits_attrs = True
    service_class = None
    initial = None

    def get_service_class(self):
        if self.service_class is None:
            service_type = self.attrs.pop("service_type", None)
            if service_type:
                from timeline import services
                self.service_class = getattr(services, service_type)

        return self.service_class

    def get_initial(self):
        if self.initial is None:
            self.initial = self.attrs.pop("initial", None)

        return self.initial

    def create_option(self, name, value, label, selected, index, *args, **kwargs):
        form = re.findall(r'form-(.+)-type', name)[0]

        service_class = self.get_service_class()
        if service_class:
            req_rule_types = service_class.get_required_rule_types()

            initial = self.get_initial()
            if initial:
                if initial in req_rule_types:
                    if value == initial:
                        kwargs['attrs'] = {"selected": True}
                    else:
                        kwargs['attrs'] = {"disabled": True}
                else:
                    if value in req_rule_types:
                        kwargs['attrs'] = {"disabled": True}
            else:
                index = lambda elem, list_: list_.index(elem) if elem in list_ else -1

                if form in map(str, range(len(req_rule_types))):
                    if str(index(value, req_rule_types)) == form:
                        kwargs['attrs'] = {"selected": True}
                    else:
                        kwargs['attrs'] = {"disabled": True}
                else:
                    if value in req_rule_types:
                        kwargs['attrs'] = {"disabled": True}

        return super(AttrChoiceWidget, self).create_option(
            name, value, label, selected, index, *args, **kwargs
        )


class TimelineEventInserterRuleForm(forms.ModelForm):
    class Meta:
        model = TimelineEventInserterRule
        fields = '__all__'
        exclude = ('rulebook', )
        widgets = {
            'type': AttrChoiceWidget(),
        }

    def __init__(self, service_type, initial=None, *args, **kwargs):
        super(TimelineEventInserterRuleForm, self).__init__(initial=initial, *args, **kwargs)
        self.fields['type'].widget.attrs = {"service_type": service_type}
        if initial:
            self.fields['type'].widget.attrs['initial'] = initial["type"]
            from timeline import services
            self.service_class = getattr(services, service_type)
            if initial["type"] in self.service_class.get_required_rule_types():
                self.fields['type'].widget.attrs['required'] = True

        self.fields['type'].choices = [
            (k, v,)
            for k, v in self.fields['type'].choices
            if not service_type or
               not k or
               k in next(zip(*TimelineEventInserterRule.RULE_TYPES_PER_SERVICE[service_type]))
        ]

    def clean__rule_type__steem_author(self, argument):
        try:
            Account(argument)
        except AccountDoesNotExistsException as e:
            raise forms.ValidationError("Account does not exists")

    def clean(self):
        super().clean()

        rule_type = self.cleaned_data.get("type")
        argument = self.cleaned_data.get("argument")

        if rule_type == TimelineEventInserterRule.STEEM_AUTHOR_RULE:
            self.clean__rule_type__steem_author(argument)

        return self.cleaned_data


class TimelineManagementForm(ManagementForm):
    SERVICE_TYPE_FORM = 'SERVICE_TYPE'
    NOTIFY_FORM = 'NOTIFY'

    def __init__(self, *args, **kwargs):
        self.base_fields[self.SERVICE_TYPE_FORM] = CharField(widget=HiddenInput)
        self.base_fields[self.NOTIFY_FORM] = BooleanField(label="""
            Notify about new items added to timeline by this set of rules, by posting following comment bellow posts: 
        """, required=False)
        kwargs.setdefault('label_suffix', '')
        super(TimelineManagementForm, self).__init__(*args, **kwargs)

    def clean_service_type(self):
        service_type = self.cleaned_data.get(self.SERVICE_TYPE_FORM)
        if service_type not in TimelineEventInserterRulebook.service_types():
            raise ValidationError("Wrong service type")
        return service_type


class TimelineRuleBaseFormSet(BaseFormSet):
    @cached_property
    def management_form(self):
        """Returns the ManagementForm instance for this FormSet."""
        if self.is_bound:
            form = TimelineManagementForm(self.data, auto_id=self.auto_id, prefix=self.prefix)
            if not form.is_valid():
                raise ValidationError(
                    _('ManagementForm data is missing or has been tampered with'),
                    code='missing_management_form',
                )
        else:
            form = TimelineManagementForm(auto_id=self.auto_id, prefix=self.prefix, initial={
                TOTAL_FORM_COUNT: self.total_form_count(),
                INITIAL_FORM_COUNT: self.initial_form_count(),
                MIN_NUM_FORM_COUNT: self.min_num,
                MAX_NUM_FORM_COUNT: self.max_num,
                TimelineManagementForm.SERVICE_TYPE_FORM: self.service_type,
                TimelineManagementForm.NOTIFY_FORM: self.notify,
            })
            from timeline import services
            service_class = getattr(services, self.service_type)
            form.notification_example = markdown(service_class.get_notification_msg(self.project))
        return form


BaseTimelineEventInserterRuleFormSet = formset_factory(
    TimelineEventInserterRuleForm,
    formset=TimelineRuleBaseFormSet,
    extra=1,
    can_delete=True,
)


class TimelineEventInserterRuleFormSet(BaseTimelineEventInserterRuleFormSet):
    def __init__(self, project=None, service_type=None, notify=None, initial=None, data=None, *args, **kwargs):
        self.service_type = service_type
        self.notify = notify
        self.project = project

        if not service_type and "data" in kwargs:
            service_type = kwargs["data"].get('form-{}'.format(TimelineManagementForm.SERVICE_TYPE_FORM))

        if not initial and not data and service_type in TimelineEventInserterRulebook.service_types():
            from timeline import services
            service_class = getattr(services, service_type)
            initial = [
                {
                    'type': rule_type,
                    'argument': '',
                    'rulebook': None,
                }
                for rule_type in service_class.get_required_rule_types()
            ]
        super(TimelineEventInserterRuleFormSet, self).__init__(initial=initial, data=data, *args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super(TimelineEventInserterRuleFormSet, self).get_form_kwargs(*args, **kwargs)
        form_kwargs.update({"service_type": self.service_type})
        return form_kwargs

    def initial_form_count(self):
        if self.initial:
            return 0
        else:
            return BaseTimelineEventInserterRuleFormSet.initial_form_count(self)

    def total_form_count(self):
        if self.initial:
            count = len(self.initial) if self.initial else 0
            count += self.extra
            return count
        else:
            return BaseTimelineEventInserterRuleFormSet.total_form_count(self)


class TimelineEventInserterRulebookForm(forms.ModelForm):
    class Meta:
        model = TimelineEventInserterRulebook
        fields = ('service_type',)

    def __init__(self, choices=None, *args, **kwargs):
        super(TimelineEventInserterRulebookForm, self).__init__(*args, **kwargs)
        if choices:
            self.fields["service_type"].choices = choices
            self.fields["service_type"].widget.attrs['disabled'] = True
