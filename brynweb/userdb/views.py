from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, authenticate, login as auth_login)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.contrib.auth.decorators import user_passes_test

from .forms import CustomUserCreationForm, TeamForm, InvitationForm
from .models import (Institution, Team, TeamMember, Invitation, UserProfile,
                     Region)


def register(request):
    if request.method == 'POST':
        userform = CustomUserCreationForm(request.POST)
        teamform = TeamForm(request.POST)

        if userform.is_valid() and teamform.is_valid():
            user = userform.save()

            profile = UserProfile()
            profile.current_region = Region.objects.get(name='warwick')
            profile.send_validation_link(user)

            # add team
            team = teamform.save(commit=False)
            team.creator = user
            team.verified = False
            team.default_region = Region.objects.get(name='warwick')
            team.save()

            # add team member
            member = TeamMember()
            member.team = team
            member.user = user
            member.is_admin = True
            member.save()

            messages.success(
                request,
                "Thank you for registering. Your request will be approved by "
                "an administrator and you will receive an email with further "
                "instructions")

            # notify admins
            team.new_registration_admin_email()

            return HttpResponseRedirect(reverse('home:home'))
    else:
        userform = CustomUserCreationForm()
        teamform = TeamForm()

    return render(request, 'userdb/register.html',
                  {'userform': userform,
                   'teamform': teamform})


@login_required
def invite(request):
    if request.method == 'POST':
        form = InvitationForm(request.user, request.POST)
        if form.is_valid():
            if Invitation.objects.filter(email=form.cleaned_data['email'],
                                         to_team=form.cleaned_data['to_team']):
                messages.error(request,
                               "User has already been invited to this team.")
            else:
                invitation = form.save(commit=False)
                invitation.send_invitation(request.user)

                messages.success(request, 'Invitation sent.')
    else:
        messages.error(request, 'No information supplied for invitation')
    return HttpResponseRedirect(reverse('home:home'))


def institution_typeahead(request):
    q = request.GET.get('q', '')
    if q:
        matches = (Institution.objects
                   .filter(name__icontains=q)
                   .values_list('name', flat=True)[:10])
    else:
        matches = Institution.objects.all().values_list('name', flat=True)
    data = list(matches)
    return JsonResponse(data, safe=False)


def accept_invite(request, uuid):
    i = get_object_or_404(Invitation, uuid=uuid)
    if request.method == 'POST':
        userform = CustomUserCreationForm(request.POST)
        if userform.is_valid():
            user = userform.save()

            # add user profile
            profile = UserProfile()
            profile.user = user
            profile.current_region = Region.objects.get(name='warwick')
            profile.email_validated = True
            profile.save()

            # add team member
            member = TeamMember()
            member.team = i.to_team
            member.user = user
            member.is_admin = False
            member.save()

            i.accepted = True
            i.save()

            messages.success(
                request,
                "Congratulations you are now a member of %s. "
                "Please log-in to get started." % (member.team))
            return HttpResponseRedirect(reverse('home:home'))
        else:
            messages.error(request, 'Invalid values supplied for form.')
    else:
        i = Invitation.objects.get(uuid=uuid)
        if i.accepted:
            messages.error(request,
                           "This invitation has already been claimed!")
            return HttpResponseRedirect(reverse('home:home'))

        userform = CustomUserCreationForm()
        userform.initial['email'] = i.email

    return render(request, 'userdb/user-register.html', {'form': userform})


def validate_email(request, uuid):
    profile = get_object_or_404(UserProfile, validation_link=uuid)
    profile.email_validated = True
    profile.save()
    messages.success(
        request,
        "Thank you for confirming your email address, "
        "you can now log-in to get started.")
    return HttpResponseRedirect(reverse('home:home'))


@user_passes_test(lambda u: u.is_superuser)
def active_users(request):
    recordset = TeamMember.objects.filter(team__verified=True)
    txt = "\n".join(["%s\t%s\t%s\t%s\t%s" % (u.user.first_name, u.user.last_name, u.user.email, u.team.institution, u.team.name) for u in recordset])
    return HttpResponse(txt, content_type='text/plain')

