from django.shortcuts import render

def render_template(request, template_name, context={}):
    language = request.GET.get('language', 'en')
    localized_template_name = f"{template_name[:-5]}_{language}.html"
    print(f'Rendering {localized_template_name}')
    return render(request, localized_template_name, context)
