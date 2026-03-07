import csv
import json
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, TemplateView, CreateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone

from .models import Family
from webpush import send_user_notification


class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser


class UserCreateView(SuperuserRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'family/user_form.html'
    success_url = reverse_lazy('family:list')

    def form_valid(self, form):
        # Additional logic if needed (e.g. setting some default flags)
        return super().form_valid(form)


class UserListView(SuperuserRequiredMixin, ListView):
    model = User
    template_name = 'family/user_list.html'
    context_object_name = 'users'
    ordering = ['-date_joined']


class UserDeleteView(SuperuserRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy('family:user_list')

    def delete(self, request, *args, **kwargs):
        user_to_del = self.get_object()
        if user_to_del.is_superuser and User.objects.filter(is_superuser=True).count() <= 1:
            messages.error(request, "Cannot delete the only superuser.")
            return redirect('family:user_list')
        messages.success(request, f"User {user_to_del.username} deleted.")
        return super().delete(request, *args, **kwargs)


class SendPushNotificationView(SuperuserRequiredMixin, View):
    """Allow superusers to broadcast custom push notifications."""
    template_name = 'family/send_notification.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()
        link = request.POST.get('link', '').strip() or '/'

        if not title or not message:
            messages.error(request, "ക്രോസ് ചെയ്യാത്ത ശീർഷകവും സന്ദേശവും നൽകുക.")
            return render(request, self.template_name, {
                'title_val': title,
                'message_val': message,
                'link_val': link
            })

        payload = {
            "head": title,
            "body": message,
            "url": link
        }

        count = 0
        # Broadcast to all users (alternatively, targeted users)
        for user in User.objects.all():
            try:
                send_user_notification(user=user, payload=payload, ttl=3600)
                count += 1
            except Exception:
                pass

        messages.success(request, f"വിജകരമായി {count} ഉപയോക്താക്കൾക്ക് അറിയിപ്പ് അയച്ചു.")
        return redirect('family:user_list')


# ── CSV helpers ───────────────────────────────────────────────────────────────

CSV_TOP_FIELDS = [
    'പഞ്ചായത്ത്', 'വാർഡ്', 'ഫോം നമ്പർ', 'ഗൃഹനാഥന്റെ പേര്',
    'മൊബൈൽ നമ്പർ', 'മൊബൈൽ നമ്പർ 2', 'ഉപ്പയുടെ പേര്', 'ഉമ്മയുടെ പേര്', 'ഭാര്യയുടെ പേര്',
]

CSV_HEADERS = (
    ['id', 'created_at']
    + CSV_TOP_FIELDS
    + ['മക്കൾ എണ്ണം', 'സഹോദരിമാർ എണ്ണം', 'മക്കളുടെ വിവരം', 'സഹോദരിമാരുടെ വിവരങ്ങൾ']
)


def _children_summary(children):
    parts = []
    for c in children:
        relation = c.get('ബന്ധം', '')
        name = c.get('പേര്', '')
        mobile = c.get('മൊബൈൽ നമ്പർ', '')
        mobile2 = c.get('മൊബൈൽ നമ്പർ 2', '')
        wife = c.get('ഭാര്യയുടെ പേര്', '')
        wife_mobile = c.get('ഭാര്യയുടെ മൊബൈൽ', '')
        kids = c.get('കുട്ടികൾ', {})
        above5 = kids.get('5 വയസിനു മുകളിൽ', 0)
        below5 = kids.get('5 വയസിനു താഴെ', 0)
        part = f"{relation}: {name}"
        if mobile:
            part += f" | {mobile}"
        if mobile2:
            part += f" | {mobile2}"
        if wife:
            part += f" | ഭാര്യ: {wife}"
            if wife_mobile:
                part += f" ({wife_mobile})"
        part += f" | കുട്ടികൾ: {above5}+{below5}"
        parts.append(part)
    return ' ; '.join(parts)


def _sisters_summary(sisters):
    parts = []
    for s in sisters:
        name = s.get('സഹോദരിയുടെ പേര്', '')
        mobile = s.get('മൊബൈൽ നമ്പർ', '')
        mobile2 = s.get('മൊബൈൽ നമ്പർ 2', '')
        kids = s.get('കുട്ടികൾ', {})
        above5 = kids.get('5 വയസിനു മുകളിൽ', 0)
        below5 = kids.get('5 വയസിനു താഴെ', 0)
        part = f"{name}"
        if mobile:
            part += f" | {mobile}"
        if mobile2:
            part += f" | {mobile2}"
        part += f" | കുട്ടികൾ: {above5}+{below5}"
        parts.append(part)
    return ' ; '.join(parts)


def _mask_mobile_value(value):
    if not value:
        return value
    val_str = str(value)
    if len(val_str) <= 4:
        return value
    return '*' * (len(val_str) - 4) + val_str[-4:]


def _mask_family_data(data):
    """Deep copy and mask all mobile numbers in the family data dict."""
    import copy
    masked_data = copy.deepcopy(data)
    
    # Root level
    if 'മൊബൈൽ നമ്പർ' in masked_data:
        masked_data['മൊബൈൽ നമ്പർ'] = _mask_mobile_value(masked_data['മൊബൈൽ നമ്പർ'])
    if 'മൊബൈൽ നമ്പർ 2' in masked_data:
        masked_data['മൊബൈൽ നമ്പർ 2'] = _mask_mobile_value(masked_data['മൊബൈൽ നമ്പർ 2'])
        
    # Children
    for child in masked_data.get('മക്കളുടെ വിവരം', []):
        if 'മൊബൈൽ നമ്പർ' in child:
            child['മൊബൈൽ നമ്പർ'] = _mask_mobile_value(child['മൊബൈൽ നമ്പർ'])
        if 'മൊബൈൽ നമ്പർ 2' in child:
            child['മൊബൈൽ നമ്പർ 2'] = _mask_mobile_value(child['മൊബൈൽ നമ്പർ 2'])
        if 'ഭാര്യയുടെ മൊബൈൽ' in child:
            child['ഭാര്യയുടെ മൊബൈൽ'] = _mask_mobile_value(child['ഭാര്യയുടെ മൊബൈൽ'])
            
    # Sisters
    sisters_key = 'സഹോദരിമാരുടെ വിവരങ്ങൾ'
    for k in masked_data.keys():
        if k.strip() == sisters_key:
            for sister in masked_data[k]:
                if 'മൊബൈൽ നമ്പർ' in sister:
                    sister['മൊബൈൽ നമ്പർ'] = _mask_mobile_value(sister['മൊബൈൽ നമ്പർ'])
                if 'മൊബൈൽ നമ്പർ 2' in sister:
                    sister['മൊബൈൽ നമ്പർ 2'] = _mask_mobile_value(sister['മൊബൈൽ നമ്പർ 2'])
            break
            
    return masked_data


def _family_to_csv_row(family):
    data = family.family_json
    children = data.get('മക്കളുടെ വിവരം', [])
    sisters = data.get('സഹോദരിമാരുടെ വിവരങ്ങൾ', [])
    return (
        [family.pk, family.created_at.strftime('%Y-%m-%d %H:%M')]
        + [data.get(f, '') for f in CSV_TOP_FIELDS]
        + [len(children), len(sisters), _children_summary(children), _sisters_summary(sisters)]
    )



class FamilyListView(ListView):
    """Display all family submissions in a table."""
    model = Family
    template_name = 'family/list.html'
    context_object_name = 'families'
    paginate_by = 20

    def get_queryset(self):
        qs = Family.objects.all().order_by('-created_at')
        q = self.request.GET.get('q', '').strip()

        if q:
            if q.isdigit():
                # Search by Form Number
                qs = qs.filter(**{"family_json__ഫോം നമ്പർ__icontains": q})
            else:
                # Search by Name
                qs = qs.filter(**{"family_json__ഗൃഹനാഥന്റെ പേര്__icontains": q})
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class FamilyDetailView(DetailView):
    """Show the full stored JSON for a single family submission."""
    model = Family
    template_name = 'family/detail.html'
    context_object_name = 'family'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pretty_json'] = json.dumps(
            self.object.family_json,
            ensure_ascii=False,
            indent=2
        )
        return context


def _parse_family_form(data):
    """Parse POST data into (family_json dict, errors list)."""
    errors = []
    panchayath  = data.get('panchayath', '').strip()
    ward        = data.get('ward', '').strip()
    form_number = data.get('form_number', '').strip()
    head_name   = data.get('head_name', '').strip()
    mobile      = data.get('mobile', '').strip()
    mobile2     = data.get('mobile2', '').strip()
    father_name = data.get('father_name', '').strip()
    mother_name = data.get('mother_name', '').strip()
    wife_name   = data.get('wife_name', '').strip()

    if not panchayath:  errors.append('പഞ്ചായത്ത് നൽകുക.')
    if not ward:        errors.append('വാർഡ് നൽകുക.')
    if not form_number: errors.append('ഫോം നമ്പർ നൽകുക.')
    if not head_name:   errors.append('ഗൃഹനാഥന്റെ പേര് നൽകുക.')
    if mobile and (not mobile.isdigit() or len(mobile) < 10):
        errors.append('മൊബൈൽ നമ്പർ 1 10 അക്കം ആയിരിക്കണം.')
    if mobile2 and (not mobile2.isdigit() or len(mobile2) < 10):
        errors.append('മൊബൈൽ നമ്പർ 2 10 അക്കം ആയിരിക്കണം.')

    children_list = []
    child_relations    = data.getlist('child_relation')
    child_names        = data.getlist('child_name')
    child_mobiles      = data.getlist('child_mobile')
    child_mobiles2     = data.getlist('child_mobile2')
    child_wife_names   = data.getlist('child_wife_name')
    child_wife_mobiles = data.getlist('child_wife_mobile')
    child_above5       = data.getlist('child_above5')
    child_below5       = data.getlist('child_below5')
    for i in range(len(child_relations)):
        relation = child_relations[i].strip() if i < len(child_relations) else ''
        if not relation:
            continue
        name          = child_names[i].strip()     if i < len(child_names)     else ''
        child_mobile  = child_mobiles[i].strip()   if i < len(child_mobiles)   else ''
        child_mobile2 = child_mobiles2[i].strip()  if i < len(child_mobiles2)  else ''
        try:  above5 = int(child_above5[i]) if i < len(child_above5) and child_above5[i] else 0
        except (ValueError, TypeError): above5 = 0
        try:  below5 = int(child_below5[i]) if i < len(child_below5) and child_below5[i] else 0
        except (ValueError, TypeError): below5 = 0
        if above5 < 0 or below5 < 0:
            errors.append(f'കുട്ടികളുടെ എണ്ണം 0-ൽ കുറയരുത് (entry {i+1}).')
            continue
        entry = {'ബന്ധം': relation, 'പേര്': name,
                 'മൊബൈൽ നമ്പർ': child_mobile, 'മൊബൈൽ നമ്പർ 2': child_mobile2,
                 'കുട്ടികൾ': {'5 വയസിനു മുകളിൽ': above5, '5 വയസിനു താഴെ': below5}}
        if relation == 'മകൻ':
            entry['ഭാര്യയുടെ പേര്'] = child_wife_names[i].strip() if i < len(child_wife_names) else ''
            entry['ഭാര്യയുടെ മൊബൈൽ'] = child_wife_mobiles[i].strip() if i < len(child_wife_mobiles) else ''
        children_list.append(entry)

    sisters_list = []
    sister_names    = data.getlist('sister_name')
    sister_mobiles  = data.getlist('sister_mobile')
    sister_mobiles2 = data.getlist('sister_mobile2')
    sister_above5   = data.getlist('sister_above5')
    sister_below5   = data.getlist('sister_below5')
    for i in range(len(sister_names)):
        name = sister_names[i].strip() if i < len(sister_names) else ''
        if not name:
            continue
        sister_mobile  = sister_mobiles[i].strip()  if i < len(sister_mobiles)  else ''
        sister_mobile2 = sister_mobiles2[i].strip() if i < len(sister_mobiles2) else ''
        try:  above5 = int(sister_above5[i]) if i < len(sister_above5) and sister_above5[i] else 0
        except (ValueError, TypeError): above5 = 0
        try:  below5 = int(sister_below5[i]) if i < len(sister_below5) and sister_below5[i] else 0
        except (ValueError, TypeError): below5 = 0
        if above5 < 0 or below5 < 0:
            errors.append(f'സഹോദരിയുടെ കുട്ടികളുടെ എണ്ണം 0-ൽ കുറയരുത് (entry {i+1}).')
            continue
        sisters_list.append({'സഹോദരിയുടെ പേര്': name,
                              'മൊബൈൽ നമ്പർ': sister_mobile, 'മൊബൈൽ നമ്പർ 2': sister_mobile2,
                              'കുട്ടികൾ': {'5 വയസിനു മുകളിൽ': above5, '5 വയസിനു താഴെ': below5}})

    family_json = {
        'പഞ്ചായത്ത്': panchayath, 'വാർഡ്': ward, 'ഫോം നമ്പർ': form_number,
        'ഗൃഹനാഥന്റെ പേര്': head_name, 'മൊബൈൽ നമ്പർ': mobile,
        'മൊബൈൽ നമ്പർ 2': mobile2,
        'ഉപ്പയുടെ പേര്': father_name, 'ഉമ്മയുടെ പേര്': mother_name,
        'ഭാര്യയുടെ പേര്': wife_name,
        'മക്കളുടെ വിവരം': children_list,
        'സഹോദരിമാരുടെ വിവരങ്ങൾ': sisters_list,
    }
    return family_json, errors


class FamilyCreateView(SuperuserRequiredMixin, View):
    """Handle GET (show form) and POST (parse + save) for family data entry."""

    template_name = 'family/form.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        """Parse POST data; if valid, create Family; else re-render with errors."""
        family_json, errors = _parse_family_form(request.POST)

        if errors:
            # Reconstruct basic fields for repopulation
            post_data = {
                'panchayath':  request.POST.get('panchayath', ''),
                'ward':        request.POST.get('ward', ''),
                'form_number': request.POST.get('form_number', ''),
                'head_name':   request.POST.get('head_name', ''),
                'mobile':      request.POST.get('mobile', ''),
                'mobile2':     request.POST.get('mobile2', ''),
                'father_name': request.POST.get('father_name', ''),
                'mother_name': request.POST.get('mother_name', ''),
                'wife_name':   request.POST.get('wife_name', ''),
            }
            return render(request, self.template_name, {
                'errors': errors,
                'post': post_data,
                'prefill_json': json.dumps({
                    'children': family_json.get('മക്കളുടെ വിവരം', []),
                    'sisters':  family_json.get('സഹോദരിമാരുടെ വിവരങ്ങൾ', []),
                }, ensure_ascii=False),
            })

        # Save record
        photo = request.FILES.get('photo')
        family = Family.objects.create(family_json=family_json, photo=photo)

        # Trigger Push Notification to Admins
        payload = {
            "head": "പുതിയ കുടുംബ ഡേറ്റ",
            "body": f"{family_json.get('ഗൃഹനാഥന്റെ പേര്')} - ഫോം #{family_json.get('ഫോം നമ്പർ')} ചേർത്തു.",
            "url": reverse('family:detail', kwargs={'pk': family.pk})
        }
        for admin in User.objects.filter(is_superuser=True):
            try:
                send_user_notification(user=admin, payload=payload, ttl=1000)
            except Exception:
                pass

        messages.success(request, 'പുതിയ കുടുംബ ഡേറ്റ വിജയകരമായി ചേർത്തു.')
        return redirect('family:detail', pk=family.pk)


class FamilyEditView(SuperuserRequiredMixin, View):
    """Show the pre-populated edit form (GET) and save updates (POST)."""

    template_name = 'family/form.html'

    def get(self, request, pk):
        family = get_object_or_404(Family, pk=pk)
        d = family.family_json
        # Build a POST-compatible dict so template's {{ post.field }} works
        initial = {
            'panchayath':   d.get('പഞ്ചായത്ത്', ''),
            'ward':         d.get('വാർഡ്', ''),
            'form_number':  d.get('ഫോം നമ്പർ', ''),
            'head_name':    d.get('ഗൃഹനാഥന്റെ പേര്', ''),
            'mobile':       d.get('മൊബൈൽ നമ്പർ', ''),
            'mobile2':      d.get('മൊബൈൽ നമ്പർ 2', ''),
            'father_name':  d.get('ഉപ്പയുടെ പേര്', ''),
            'mother_name':  d.get('ഉമ്മയുടെ പേര്', ''),
            'wife_name':    d.get('ഭാര്യയുടെ പേര്', ''),
        }
        return render(request, self.template_name, {
            'post':         initial,
            'edit_pk':      pk,
            'prefill_json': json.dumps({
                'children': d.get('മക്കളുടെ വിവരം', []),
                'sisters':  d.get('സഹോദരിമാരുടെ വിവരങ്ങൾ', []),
            }, ensure_ascii=False),
        })

    def post(self, request, pk):
        """Reuse the same parse logic; update the existing record."""
        family = get_object_or_404(Family, pk=pk)
        # Delegate parsing to a shared helper (defined below)
        family_json, errors = _parse_family_form(request.POST)
        if errors:
            d = family.family_json
            initial = {
                'panchayath':  request.POST.get('panchayath', d.get('പഞ്ചായത്ത്', '')),
                'ward':        request.POST.get('ward',        d.get('വാർഡ്', '')),
                'form_number': request.POST.get('form_number', d.get('ഫോം നമ്പർ', '')),
                'head_name':   request.POST.get('head_name',   d.get('ഗൃഹനാഥന്റെ പേര്', '')),
                'mobile':      request.POST.get('mobile',      d.get('മൊബൈൽ നമ്പർ', '')),
                'mobile2':     request.POST.get('mobile2',     d.get('മൊബൈൽ നമ്പർ 2', '')),
                'father_name': request.POST.get('father_name', d.get('ഉപ്പയുടെ പേര്', '')),
                'mother_name': request.POST.get('mother_name', d.get('ഉമ്മയുടെ പേര്', '')),
                'wife_name':   request.POST.get('wife_name',   d.get('ഭാര്യയുടെ പേര്', '')),
            }
            return render(request, self.template_name, {
                'errors': errors, 'post': initial, 'edit_pk': pk,
                'prefill_json': json.dumps({
                    'children': family_json.get('മക്കളുടെ വിവരം', []),
                    'sisters':  family_json.get('സഹോദരിമാരുടെ വിവരങ്ങൾ', []),
                }, ensure_ascii=False),
            })
        family.family_json = family_json
        if 'photo' in request.FILES:
            family.photo = request.FILES['photo']
        family.save()
        messages.success(request, 'ഫോം ഡാറ്റ അപ്ഡേറ്റ് ചെയ്തു.')
        return redirect('family:detail', pk=family.pk)


class LandingView(TemplateView):
    """Refined landing page for the Pakkada application."""
    template_name = 'family/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_families'] = Family.objects.count()
        return context


class SuccessView(TemplateView):
    template_name = 'family/success.html'


# ── Export views ──────────────────────────────────────────────────────────────

class ExportAllJSON(SuperuserRequiredMixin, View):
    """Export ALL family records as a single JSON file."""

    def get(self, request):
        families = Family.objects.all().order_by('id')
        payload = []
        for fam in families:
            payload.append({
                'id': fam.pk,
                'created_at': fam.created_at.strftime('%Y-%m-%d %H:%M'),
                'data': fam.family_json,
            })
        content = json.dumps(payload, ensure_ascii=False, indent=2)
        response = HttpResponse(content, content_type='application/json; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="families_all.json"'
        return response


class ExportAllCSV(SuperuserRequiredMixin, View):
    """Export ALL family records as a flat CSV file."""

    def get(self, request):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="families_all.csv"'
        response.write('\ufeff')  # UTF-8 BOM for Excel compatibility
        writer = csv.writer(response)
        writer.writerow(CSV_HEADERS)
        for fam in Family.objects.all().order_by('id'):
            writer.writerow(_family_to_csv_row(fam))
        return response


class ExportSingleJSON(SuperuserRequiredMixin, View):
    """Export a single Family record as JSON."""

    def get(self, request, pk):
        family = get_object_or_404(Family, pk=pk)
        payload = {
            'id': family.pk,
            'created_at': family.created_at.strftime('%Y-%m-%d %H:%M'),
            'data': family.family_json,
        }
        content = json.dumps(payload, ensure_ascii=False, indent=2)
        response = HttpResponse(content, content_type='application/json; charset=utf-8')
        fname = f"family_{family.pk}.json"
        response['Content-Disposition'] = f'attachment; filename="{fname}"'
        return response


class ExportSingleCSV(SuperuserRequiredMixin, View):
    """Export a single Family record as CSV."""

    def get(self, request, pk):
        family = get_object_or_404(Family, pk=pk)
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        fname = f"family_{family.pk}.csv"
        response['Content-Disposition'] = f'attachment; filename="{fname}"'
        response.write('\ufeff')  # UTF-8 BOM for Excel compatibility
        writer = csv.writer(response)
        writer.writerow(CSV_HEADERS)
        writer.writerow(_family_to_csv_row(family))
        return response





class ExportPoster(View):
    """Render the 1080×1920 Islamic-themed JPG poster for a single Family record."""

    def get(self, request, pk):
        from .poster import render_family_poster
        family = get_object_or_404(Family, pk=pk)
        
        data = family.family_json
        if not request.user.is_authenticated:
            data = _mask_family_data(data)
            
        jpg_bytes = render_family_poster(data)
        response = HttpResponse(jpg_bytes, content_type='image/jpeg')
        head_name = data.get('ഗൃഹനാഥന്റെ പേര്', 'family')
        # Safe ASCII filename
        safe_name = f"poster_{family.pk}.jpg"
        response['Content-Disposition'] = f'attachment; filename="{safe_name}"'
        return response


class ExportPreview(DetailView):
    """HTML preview for family data with export options."""
    model = Family
    template_name = 'family/export_preview.html'
    context_object_name = 'family'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.object.family_json
        context['family_name'] = data.get('ഗൃഹനാഥന്റെ പേര്', 'Unknown')
        context['form_no'] = data.get('ഫോം നമ്പർ', '')
        return context

class PosterPreview(DetailView):
    """HTML preview for family poster with image export options."""
    model = Family
    template_name = 'family/poster_preview.html'
    context_object_name = 'family'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.object.family_json
        context['family_name'] = data.get('ഗൃഹനാഥന്റെ പേര്', 'Unknown')
        context['form_no'] = data.get('ഫോം നമ്പർ', '')
        
        # Calculate total children below 5 for members
        total_makkal_below_5 = 0
        makkal_list = data.get('മക്കളുടെ വിവരം', [])
        for m in makkal_list:
            inner_child_data = m.get('കുട്ടികൾ', {})
            count = inner_child_data.get('5 വയസിനു താഴെ', 0)
            try:
                total_makkal_below_5 += int(count)
            except (ValueError, TypeError):
                pass
        context['total_makkal_below_5'] = total_makkal_below_5

        # Calculate total children below 5 for sisters
        total_sisters_below_5 = 0
        sisters_list = data.get('സഹോദരിമാരുടെ വിവരങ്ങൾ', [])
        for s in sisters_list:
            inner_child_data = s.get('കുട്ടികൾ', {})
            count = inner_child_data.get('5 വയസിനു താഴെ', 0)
            try:
                total_sisters_below_5 += int(count)
            except (ValueError, TypeError):
                pass
        context['total_sisters_below_5'] = total_sisters_below_5

        return context


class FamilyDeleteView(SuperuserRequiredMixin, View):
    """Delete a family record (POST only). Confirms via modal in the template."""

    def post(self, request, pk):
        family = get_object_or_404(Family, pk=pk)
        name = family.family_json.get('ഗൃഹനാഥന്റെ പേര്', f'#{pk}')
        family.delete()
        messages.success(request, f'"{name}" — ഫോം ഡാറ്റ ഡിലീറ്റ് ചെയ്തു.')
        return redirect('family:list')
