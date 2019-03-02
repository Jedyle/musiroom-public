# from django.contrib import messages
# from django.http import HttpResponseRedirect
# from django.shortcuts import render
#
# from feedback.forms import AnonymousFeedbackForm, FeedbackForm
#
#
# def leave_feedback(request, template_name='feedback/feedback_form.html'):
#     if request.user.is_authenticated:
#         form = FeedbackForm(request.POST or None)
#     else:
#         form = AnonymousFeedbackForm(request.POST or None)
#     if form.is_valid():
#         feedback = form.save(commit=False)
#         if request.user.is_anonymous:
#             feedback.user = None
#         else:
#             feedback.user = request.user
#         feedback.save()
#         messages.add_message(request, messages.SUCCESS,
#                              'Votre feedback a bien été envoyé.', extra_tags="feedback")
#         return HttpResponseRedirect(request.POST.get('next',
#                                                      request.META.get('HTTP_REFERER', '/')))
#     return render(request, template_name, {'feedback_form': form})
