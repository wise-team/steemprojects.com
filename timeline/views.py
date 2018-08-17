from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from package.models import Project
from timeline.models import TimelineEvent, TimelineEventInserterRulebook, TimelineEventInserterRule
from timeline.forms import (
    TimelineEventFormSet,
    TimelineEventInserterRulebookForm,
    TimelineEventInserterRuleFormSet,
    TimelineManagementForm,
)


@login_required
def edit_timeline(request, slug, template_name="timeline/timeline_form.html"):
    project = get_object_or_404(Project, slug=slug)
    if not request.user.profile.can_edit_package(project):
        return HttpResponseForbidden("permission denied")

    if request.POST:
        formset = TimelineEventFormSet(data=request.POST, project=project,)
    else:
        formset = TimelineEventFormSet(project=project, queryset=TimelineEvent.objects.filter(project=project))

    if formset.is_valid():
        formset.save()

        messages.add_message(request, messages.INFO, 'Project updated successfully')
        return HttpResponseRedirect(reverse("package", kwargs={"slug": project.slug}))

    rulesets = TimelineEventInserterRulebook.objects.filter(project=project)

    return render(request, template_name, {
        "formset": formset,
        "package": project,
        "rulesets": rulesets,
        "action": "Save",
    })


@login_required
def add_ruleset(request, slug, template_name="timeline/ruleset_form.html"):
    project = get_object_or_404(Project, slug=slug)
    if not request.user.profile.can_edit_package(project):
        return HttpResponseForbidden("permission denied")

    rule_formsets = []

    if request.POST:
        rule_formset = TimelineEventInserterRuleFormSet(project=project, data=request.POST)
        if rule_formset.is_valid():
            ruleset = TimelineEventInserterRulebook.objects.create(
                project=project,
                service_type=rule_formset.management_form.cleaned_data[TimelineManagementForm.SERVICE_TYPE_FORM],
                notify=rule_formset.management_form.cleaned_data[TimelineManagementForm.NOTIFY_FORM],
            )

            for inlineform in rule_formset:
                if hasattr(inlineform, 'cleaned_data') and inlineform.cleaned_data and not inlineform.cleaned_data['DELETE']:
                    data = inlineform.cleaned_data

                    TimelineEventInserterRule.objects.create(
                        type=data['type'],
                        argument=data['argument'],
                        rulebook=ruleset
                    )

            messages.add_message(request, messages.INFO, 'New RuleSet "{}" updated successfully'.format(ruleset.name))
            return HttpResponseRedirect(reverse("edit_timeline", kwargs={"slug": project.slug}))
        else:
            rule_formsets.append(rule_formset)
            rulebook_form = TimelineEventInserterRulebookForm(
                initial={"service_type": rule_formset.management_form.cleaned_data[TimelineManagementForm.SERVICE_TYPE_FORM]}
            )

    else:
        rule_formsets.extend([
            TimelineEventInserterRuleFormSet(project=project, service_type=service_type)
            for service_type in TimelineEventInserterRulebook.service_types()
        ])

        rulebook_form = TimelineEventInserterRulebookForm()

    return render(request, template_name, {
        "package": project,
        "rulebook_form": rulebook_form,
        "rule_formsets": rule_formsets,
    })


@login_required
def edit_ruleset(request, slug, ruleset_id, template_name="timeline/ruleset_form.html"):
    project = get_object_or_404(Project, slug=slug)
    if not request.user.profile.can_edit_package(project):
        return HttpResponseForbidden("permission denied")

    ruleset = get_object_or_404(TimelineEventInserterRulebook, id=ruleset_id)

    rule_formsets = []

    if request.POST:
        rule_formset = TimelineEventInserterRuleFormSet(project=project, data=request.POST)
        if rule_formset.is_valid():
            ruleset.notify = rule_formset.management_form.cleaned_data[TimelineManagementForm.NOTIFY_FORM]
            ruleset.rules.all().delete()

            for inlineform in rule_formset:
                if hasattr(inlineform, 'cleaned_data') and inlineform.cleaned_data and not inlineform.cleaned_data['DELETE']:
                    data = inlineform.cleaned_data

                    TimelineEventInserterRule.objects.create(
                        type=data['type'],
                        argument=data['argument'],
                        rulebook=ruleset
                    )

            ruleset.save()
            messages.add_message(request, messages.INFO, 'New RuleSet "{}" updated successfully'.format(ruleset.name))
            return HttpResponseRedirect(reverse("edit_timeline", kwargs={"slug": project.slug}))
        else:
            rule_formsets.append(rule_formset)

    else:

        for service_type in TimelineEventInserterRulebook.service_types():

            kwargs = {
                "service_type": service_type,
                "project": project,
                "notify": ruleset.notify,
            }
            if service_type == ruleset.service_type:
                kwargs["initial"] = [
                    {"type": rule.type, "argument": rule.argument}
                    for rule in TimelineEventInserterRule.objects.filter(rulebook=ruleset)
                ]

            rule_formsets.append(TimelineEventInserterRuleFormSet(**kwargs))

    rulebook_form = TimelineEventInserterRulebookForm(
        initial={"service_type": ruleset.service_type}
    )

    return render(request, template_name, {
        "package": project,
        "rulebook_form": rulebook_form,
        "rule_formsets": rule_formsets,
    })


@login_required
def delete_ruleset(request, slug, ruleset_id):
    project = get_object_or_404(Project, slug=slug)
    ruleset = get_object_or_404(TimelineEventInserterRulebook, id=ruleset_id)

    name = ruleset.name
    ruleset.delete()

    messages.add_message(
        request,
        messages.INFO,
        'Ruleset "{}" has been deleted'.format(name)
    )

    # Intelligently determine the URL to redirect the user to based on the
    # available information.
    next = request.GET.get('next') or request.META.get("HTTP_REFERER") or reverse("package", kwargs={"slug": project.slug})
    return HttpResponseRedirect(next)


