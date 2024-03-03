from django.shortcuts import render

def render_template(request, template_name, context={}):
    language = request.GET.get('language', 'en')
    localized_template_name = f"{template_name[:-5]}_{language}.html"
    return render(request, localized_template_name, context)