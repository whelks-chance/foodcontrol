from django.shortcuts import render

from dataimport.scripts.readraw import ReadRaw


def example(request):
    rr = ReadRaw()
    filename = '091117.json'
    user_data, feedback = rr.open_file(filename=filename)
    return render(request, 'example.html', {
        'create_tech_form': 0,
        'user_data': user_data,
        'feedback': feedback

    })