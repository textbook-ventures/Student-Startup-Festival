from django.conf import settings
from django import forms
from django.shortcuts import render
from .forms import applicationForm
from .gmail import *

def homepage (request):
        return render(request,'landing.html')

def startupcup (request):
        return render(request,'startupcup.html')

def sponsors (request):
        return render(request,'sponsors.html')

def festival (request):
        return render(request,'festival.html')

def application (request):
    if request.method == 'POST':
        application = applicationForm(request.POST, request.FILES)
        if application.is_valid():
            name = application.cleaned_data['name']
            email_address = application.cleaned_data['email']
            pdf = application.cleaned_data['pdf']
            message = name + "\n" + email_address + "\n" + application.cleaned_data['comments']
            recipients = 'Operations@textbook.ventures'
            recipients += ',Kevinwochan@gmail.com'
            recipients += ',Clinton@textbook.ventures'
            email = create_message_with_attachment(
                                 'Operations@textbook.ventures',
                                 recipients,
                                 'SSF Application: '+ name, 
                                 message,
                                 pdf
            )
            service = initialise_gmail() 
            send_message (service, email)
            '''
            subject = 'SSF Application: '+ name, 
            email = EmailMessage(
                                subject,
                                message,
                                settings.EMAIL_HOST_USER,
                                recipients
            )
            email.attach (pdf.name,
                          pdf.file.getvalue(),
                          mimetypes.guess_type(pdf.name)[0]
            )
            email.send(fail_silently=False)
            '''
            return render(request,'application.html', {'application':application})
        else:
            return render(request,'application.html', {'application':application})

    else:
        application = applicationForm()
        return render(request,'application.html', {'application':application})


