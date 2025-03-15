from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def poisson_transform_main_html(value):
    # Cuts of the last two lines (i.e. </body> and </html>) so they can later be re-added after a {% block %} django template (see index.html template)
    return '\n'.join(value.split('\n')[:-2])
