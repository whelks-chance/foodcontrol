from django.shortcuts import render


def example(request):
    return render(request, 'example.html', {'create_tech_form': 0})