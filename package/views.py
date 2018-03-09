import importlib
import json
from datetime import timedelta, datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import mail_managers
from django.core.urlresolvers import reverse
from django.db.models import Q, Count, Case, When
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt


from grid.models import Grid
from package.forms import PackageForm, PackageExampleForm, DocumentationForm, ProjectImagesFormSet
from package.models import Category, Project, PackageExample, ProjectImage, TeamMembership
from package.repos import get_all_repos
from package.forms import TeamMembersFormSet
from profiles.models import Account, AccountType
from searchv2.builders import rebuild_project_search_index


def repo_data_for_js():
    repos = [handler.serialize() for handler in get_all_repos()]
    return json.dumps(repos)


def get_form_class(form_name):
    bits = form_name.split('.')
    form_module_name = '.'.join(bits[:-1])
    form_module = importlib.import_module(form_module_name)
    form_name = bits[-1]
    return getattr(form_module, form_name)


@login_required
def add_package(request, template_name="package/package_form.html"):

    if not request.user.profile.can_add_package:
        return HttpResponseForbidden("permission denied")

    new_package = Project()
    form = PackageForm(request.POST or None, instance=new_package)
    formset = TeamMembersFormSet(request.POST or None)

    if form.is_valid() and formset.is_valid():
        new_package = form.save()
        new_package.draft_added_by = request.user
        new_package.last_modified_by = request.user
        new_package.save()
        rebuild_project_search_index(new_package)
        #new_package.fetch_metadata()
        #new_package.fetch_commits()

        for inlineform in formset:
            if hasattr(inlineform, 'cleaned_data') and inlineform.cleaned_data:
                data = inlineform.cleaned_data

                account_type = AccountType.objects.get(name=data['account_type'])
                account, created = Account.objects.get_or_create(
                    account_type=account_type,
                    name=data['account_name']
                )

                membership = TeamMembership.objects.create(account=account, project=new_package, role=data['role'])
                membership.save()

        return HttpResponseRedirect(reverse("package", kwargs={"slug": new_package.slug}))

    return render(request, template_name, {
        "form": form,
        "formset": formset,
        "repo_data": repo_data_for_js(),
        "action": "add",
        })


@login_required
def edit_package(request, slug, template_name="package/package_form.html"):
    package = get_object_or_404(Project, slug=slug)
    if not request.user.profile.can_edit_package(package):
        return HttpResponseForbidden("permission denied")

    form = PackageForm(request.POST or None, instance=package)

    initial = [
        {
            'role': tm.role,
            'account_name': tm.account.name,
            'account_type': tm.account.type,
            'role_confirmed_by_account': tm.role_confirmed_by_account,
            'avatar_small': tm.account.avatar_small,
            'initialized': True,
        }
        for tm in package.teammembership_set.all()
    ]
    if request.POST:
        formset = TeamMembersFormSet(request.POST)
    else:
        formset = TeamMembersFormSet(initial=initial)

    formset.extra = 0

    if form.is_valid() and formset.is_valid():
        modified_package = form.save()
        modified_package.last_modified_by = request.user
        modified_package.save()
        rebuild_project_search_index(modified_package)

        for inlineform in formset:
            if hasattr(inlineform, 'cleaned_data') and inlineform.cleaned_data:
                data = inlineform.cleaned_data

                account_type = AccountType.objects.get(name=data['account_type'])

                if data['DELETE']:
                    account = Account.objects.get(account_type=account_type, name=data['account_name'])
                    membership = TeamMembership.objects.get(account=account, project=modified_package)
                    membership.delete()
                else:
                    account, __ = Account.objects.get_or_create(account_type=account_type, name=data['account_name'])
                    membership, __ = TeamMembership.objects.get_or_create(account=account, project=modified_package)
                    membership.role = data['role']
                    membership.save()

        if package.is_published:
            messages.add_message(request, messages.INFO, 'Project updated successfully')

        return HttpResponseRedirect(reverse("package", kwargs={"slug": modified_package.slug}))

    return render(request, template_name, {
        "form": form,
        "formset": formset,
        "package": package,
        "repo_data": repo_data_for_js(),
        "action": "Save",
    })


@login_required
def update_package(request, slug):

    package = get_object_or_404(Project, slug=slug)
    package.fetch_metadata()
    package.fetch_commits()
    package.last_fetched = timezone.now()
    messages.add_message(request, messages.INFO, 'Project updated successfully')

    return HttpResponseRedirect(reverse("package", kwargs={"slug": package.slug}))


@login_required
def project_approval(request, slug, action):

    project = get_object_or_404(Project, slug=slug)
    project.is_awaiting_approval = action == 'request'
    project.approval_request_datetime = datetime.now()

    project.save()

    if action == 'request':
        mail_managers(
            escape('New project added by @{} awaiting approval - {}'.format(
                project.draft_added_by.username,
                project.name
            )),
            'Project: {}'.format(request.build_absolute_uri(reverse('package', kwargs={'slug': project.slug})))
        )
    return HttpResponseRedirect(reverse("package", kwargs={"slug": project.slug}))


@login_required
def publish_project(request, slug):
    project = get_object_or_404(Project, slug=slug)
    try:
        project.publish(publisher=request.user)
        rebuild_project_search_index(project)
        messages.add_message(request, messages.INFO, 'Project is published!')
        return HttpResponseRedirect(reverse("package", kwargs={"slug": project.slug}))

    except PermissionError:
        return HttpResponseForbidden("permission denied")



@login_required
def edit_images(request, slug, template_name="package/images_form.html"):
    project = get_object_or_404(Project, slug=slug)
    if not request.user.profile.can_edit_package(project):
        return HttpResponseForbidden("permission denied")

    if request.POST:
        formset = ProjectImagesFormSet(data=request.POST, files=request.FILES, project=project,)
    else:
        formset = ProjectImagesFormSet(project=project, queryset=ProjectImage.objects.filter(project=project))

    if formset.is_valid():
        formset.save()

        messages.add_message(request, messages.INFO, 'Project updated successfully')
        return HttpResponseRedirect(reverse("package", kwargs={"slug": project.slug}))

    return render(request, template_name, {
        "formset": formset,
        "package": project,
        "action": "Save",
    })


@login_required
def add_example(request, slug, template_name="package/add_example.html"):

    package = get_object_or_404(Project, slug=slug)
    new_package_example = PackageExample()
    form = PackageExampleForm(request.POST or None, instance=new_package_example)

    if form.is_valid():
        package_example = PackageExample(package=package,
                title=request.POST["title"],
                url=request.POST["url"])
        package_example.save()
        return HttpResponseRedirect(reverse("package", kwargs={"slug": package_example.package.slug}))

    return render(request, template_name, {
        "form": form,
        "package": package
        })


@login_required
def edit_example(request, slug, id, template_name="package/edit_example.html"):

    package_example = get_object_or_404(PackageExample, id=id)
    form = PackageExampleForm(request.POST or None, instance=package_example)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse("package", kwargs={"slug": package_example.package.slug}))

    return render(request, template_name, {
        "form": form,
        "package": package_example.package
        })


def package_autocomplete(request):
    """
    Provides Package matching based on matches of the beginning
    """
    names = []
    q = request.GET.get("q", "")
    if q:
        names = (x.name for x in Project.objects.filter(name__istartswith=q))

    response = HttpResponse("\n".join(names))

    setattr(response, "djangologging.suppress_output", True)
    return response


def category(request, slug, template_name="package/package_grid.html"):
    category_ = get_object_or_404(Category, slug=slug)

    context = {
        'categories': [
            {
                "title_plural": category_.title_plural,
                "count": category_.project_set.published().count(),
                "description": category_.description,
                "packages": category_.project_set.published().select_related().annotate(usage_count=Count("usage"))
            }
        ]
    }

    return render(request, template_name, context)


def ajax_package_list(request, template_name="package/ajax_package_list.html"):
    q = request.GET.get("q", "")
    packages = []
    if q:
        _dash = "%s-%s" % (settings.PACKAGINATOR_SEARCH_PREFIX, q)
        _space = "%s %s" % (settings.PACKAGINATOR_SEARCH_PREFIX, q)
        _underscore = '%s_%s' % (settings.PACKAGINATOR_SEARCH_PREFIX, q)
        packages = Project.objects.filter(
                        Q(name__istartswith=q) |
                        Q(name__istartswith=_dash) |
                        Q(name__istartswith=_space) |
                        Q(name__istartswith=_underscore)
                    )

    packages_already_added_list = []
    grid_slug = request.GET.get("grid", "")
    if packages and grid_slug:
        grids = Grid.objects.filter(slug=grid_slug)
        if grids:
            grid = grids[0]
            packages_already_added_list = [x['slug'] for x in grid.packages.all().values('slug')]
            new_packages = tuple(packages.exclude(slug__in=packages_already_added_list))[:20]
            number_of_packages = len(new_packages)
            if number_of_packages < 20:
                try:
                    old_packages = packages.filter(slug__in=packages_already_added_list)[:20 - number_of_packages]
                except AssertionError:
                    old_packages = None

                if old_packages:
                    old_packages = tuple(old_packages)
                    packages = new_packages + old_packages
            else:
                packages = new_packages

    return render(request, template_name, {
        "packages": packages,
        'packages_already_added_list': packages_already_added_list,
        }
    )


@login_required
def usage(request, slug, action):
    success = False
    package = get_object_or_404(Project, slug=slug)

    # Update the current user's usage of the given package as specified by the
    # request.
    if package.usage.filter(username=request.user.username):
        if action.lower() == 'add':
            # The user is already using the package
            success = True
            change = 0
        else:
            # If the action was not add and the user has already specified
            # they are a use the package then remove their usage.
            package.usage.remove(request.user)
            success = True
            change = -1
    else:
        if action.lower() == 'lower':
            # The user is not using the package
            success = True
            change = 0
        else:
            # If the action was not lower and the user is not already using
            # the package then add their usage.
            package.usage.add(request.user)
            success = True
            change = 1

    # Invalidate the cache of this users's used_packages_list.
    if change == 1 or change == -1:
        cache_key = "sitewide_used_packages_list_%s" % request.user.pk
        cache.delete(cache_key)
        package.grid_clear_detail_template_cache()

    # Return an ajax-appropriate response if necessary
    if request.is_ajax():
        response = {'success': success}
        if success:
            response['change'] = change

        return HttpResponse(json.dumps(response))

    # Intelligently determine the URL to redirect the user to based on the
    # available information.
    next = request.GET.get('next') or request.META.get("HTTP_REFERER") or reverse("package", kwargs={"slug": package.slug})
    return HttpResponseRedirect(next)


def python3_list(request, template_name="package/python3_list.html"):
    packages = Project.objects.filter(version__supports_python3=True).distinct()
    packages = packages.order_by("-pypi_downloads", "-repo_watchers", "name")

    values = "category, category_id, commit, commit_list, created, added_by, added_by_id, documentation_url, dpotw, grid, gridpackage, id, last_fetched, last_modified_by, last_modified_by_id, modified, packageexample, participants, pypi_downloads, pypi_url, repo_description, repo_forks, repo_url, repo_watchers, slug, name, usage, version".split(',')
    values = [x.strip() for x in values]
    if request.GET.get('sort') and request.GET.get('sort') not in values:
        # Some people have cached older versions of this view
        request.GET = request.GET.copy()
        del request.GET['sort']

    return render(
        request,
        template_name, {
            "packages": packages
        }
    )


def package_list(request, template_name="package/package_grid.html"):
    context = {
        'categories': [
            {
                "title_plural": category.title_plural,
                "count": category.project_count,
                "description": category.description,
                "packages": category.project_set.published().order_by("-repo_watchers", "name")
            }
            for category in Category.objects.annotate(
                project_count=Count(Case(When(project__is_published=True, then=1)))
            )
        ]
    }

    return render(request, template_name, context)


def package_detail(request, slug, template_name="package/package.html"):

    package = get_object_or_404(Project, slug=slug)
    no_development = package.no_development
    try:
        if package.category == Category.objects.get(slug='projects'):
            # projects get a bye because they are a website
            pypi_ancient = False
            pypi_no_release = False
        else:
            pypi_ancient = package.pypi_ancient
            pypi_no_release = package.pypi_ancient is None
        warnings = no_development or pypi_ancient or pypi_no_release
    except Category.DoesNotExist:
        pypi_ancient = False
        pypi_no_release = False
        warnings = no_development

    if request.GET.get("message"):
        messages.add_message(request, messages.INFO, request.GET.get("message"))

    if package.is_draft:

        if package.is_awaiting_approval:
            messages.add_message(
                request,
                messages.INFO,
                'This project is waiting for approval.',
                extra_tags='data-stick'
            )
        else:
            messages.add_message(
                request,
                messages.WARNING,
                'Information about this project is not published yet. This is a draft!<br>' +
                'Add as much information about this project as you can. Add logo and some screenshots, add at least few timeline events.<br> ' +
                'When you will decide it is ready, submit a project for approval.',
                #' by <a href="https://google.com/">trusted users of SteemProjects</a>.'
                # 'Also, learn <a href="">how you can become a trusted user</a>.',
                extra_tags='draft data-stick'
            )

    proj_imgs = []
    if package.main_img:
        proj_imgs.append(package.main_img)
        proj_imgs.extend(ProjectImage.objects.exclude(pk=package.main_img.pk).filter(project=package).order_by('img'))
    else:
        proj_imgs.extend(ProjectImage.objects.filter(project=package).order_by('img'))

    all_github_accounts_of_teammambers = [
        ac.pk
        for profile in [ac.profile for ac in package.team_members.all() if ac.profile]
        for ac in profile.account_set.all() if ac.type == Account.TYPE_GITHUB
    ]

    can_edit_package = hasattr(request.user, "profile") and request.user.profile.can_edit_package(package)

    events_on_timeline = 5
    timeline_events = package.events.order_by('-date')
    timeline_axis_end = timeline_axis_start = None

    if timeline_events.count() > 0:
        timeline_end = timeline_events.first()
        timeline_start = timeline_events[events_on_timeline-1] if timeline_events.count() > events_on_timeline else timeline_events[0]
        timeline_axis_start = timeline_start.date - timedelta(30)
        timeline_axis_end = timeline_end.date + timedelta(30)

    return render(request, template_name,
            dict(
                package=package,
                timeline_events=timeline_events,
                timeline_axis_start=timeline_axis_start,
                timeline_axis_end=timeline_axis_end,
                project_imgs=[pi.img for pi in proj_imgs],
                pypi_ancient=pypi_ancient,
                no_development=no_development,
                pypi_no_release=pypi_no_release,
                warnings=warnings,
                latest_version=package.last_released(),
                repo=package.repo,
                not_team_contributors=package.contributors.exclude(pk__in=all_github_accounts_of_teammambers),
                can_edit_package=can_edit_package
            )
        )


def int_or_0(value):
    try:
        return int(value)
    except ValueError:
        return 0


@login_required
def post_data(request, slug):
    # if request.method == "POST":
        # try:
        #     # TODO Do this this with a form, really. Duh!
        #     package.repo_watchers = int_or_0(request.POST.get("repo_watchers"))
        #     package.repo_forks = int_or_0(request.POST.get("repo_forks"))
        #     package.repo_description = request.POST.get("repo_description")
        #     package.participants = request.POST.get('contributors')
        #     package.fetch_commits()  # also saves
        # except Exception as e:
        #     print e
    package = get_object_or_404(Project, slug=slug)
    package.fetch_pypi_data()
    package.repo.fetch_metadata(package)
    package.repo.fetch_commits(package)
    package.last_fetched = timezone.now()
    package.save()
    return HttpResponseRedirect(reverse("package", kwargs={"slug": package.slug}))


@login_required
def edit_documentation(request, slug, template_name="package/documentation_form.html"):
    package = get_object_or_404(Project, slug=slug)
    form = DocumentationForm(request.POST or None, instance=package)
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.INFO, 'Package documentation updated successfully')
        return redirect(package)
    return render(request, template_name,
            dict(
                package=package,
                form=form
            )
        )


@csrf_exempt
def github_webhook(request):
    if request.method == "POST":
        data = json.loads(request.POST['payload'])

        # Webhook Test
        if "zen" in data:
            return HttpResponse(data['hook_id'])

        repo_url = data['repository']['url']

        # service test
        if repo_url == "http://github.com/mojombo/grit":
            return HttpResponse("Service Test pass")

        package = get_object_or_404(Project, repo_url=repo_url)
        package.repo.fetch_commits(package)
        package.last_fetched = timezone.now()
        package.save()
    return HttpResponse()
