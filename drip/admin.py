import base64
import simplejson

from django.contrib import admin
from django.contrib.auth.models import User

from drip.models import Drip, SentDrip, QuerySetRule


class QuerySetRuleInline(admin.TabularInline):
    model = QuerySetRule

class DripAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled')
    inlines = [
        QuerySetRuleInline,
    ]

    av = lambda self, view: self.admin_site.admin_view(view)
    def timeline(self, request, drip_id, into_past, into_future):
        """
        Return a list of people who should get emails.
        """
        from django.shortcuts import render, get_object_or_404

        drip = get_object_or_404(Drip, id=drip_id)

        shifted_drips = []
        for shifted_drip in drip.drip.walk(into_past=int(into_past), into_future=int(into_future)+1):
            shifted_drips.append({
                'drip': shifted_drip,
                'qs': shifted_drip.get_queryset()
            })

        return render(request, 'drip/timeline.html', locals())

    def view_drip_email(self, request, drip_id, into_past, into_future, user_id):
        from django.shortcuts import render, get_object_or_404
        from django.http import HttpResponse
        drip = get_object_or_404(Drip, id=drip_id)
        user = get_object_or_404(User, id=user_id)

        html = ''
        for body, mime in drip.drip.build_email(user).alternatives:
            if mime == 'text/html':
                html = body

        return HttpResponse(html)

    def change_view(self, request, object_id, extra_context=None):
        from drip.utils import get_fields, get_simple_fields
        extra_context = extra_context or {}
        extra_context['field_data'] = simplejson.dumps(get_simple_fields(User))
        return super(DripAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(DripAdmin, self).get_urls()
        my_urls = patterns('',
            url(
                r'^(?P<drip_id>[\d]+)/timeline/(?P<into_past>[\d]+)/(?P<into_future>[\d]+)/$',
                self.av(self.timeline),
                name='drip_timeline'
            ),
            url(
                r'^(?P<drip_id>[\d]+)/timeline/(?P<into_past>[\d]+)/(?P<into_future>[\d]+)/(?P<user_id>[\d]+)/$',
                self.av(self.view_drip_email),
                name='view_drip_email'
            )
        )
        return my_urls + urls
admin.site.register(Drip, DripAdmin)


class SentDripAdmin(admin.ModelAdmin):
    list_display = [f.name for f in SentDrip._meta.fields]
    ordering = ['-id']
admin.site.register(SentDrip, SentDripAdmin)
