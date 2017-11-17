from django.views.generic.base import TemplateView


class StaticPageView(TemplateView):
    context = None

    def get_context_data(self, **kwargs):
        context = super(StaticPageView, self).get_context_data(**kwargs)
        context.update(self.context or {})
        return context
