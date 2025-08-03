from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


# error handling 
def error_404_view(request, exception):
    return render(request, "error_handling/404.html", status=404)

def custom_500_view(request):
    return render(request, "error_handling/500.html", status=500)

def custom_403_view(request, exception):
    return render(request, "error_handling/403.html", status=403)

def custom_400_view(request, exception):
    return render(request, "error_handling/400.html", status=400)