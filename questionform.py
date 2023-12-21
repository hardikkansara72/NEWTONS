import logging
from typing import Any
from django import forms
from django.conf import settings
from bulwark.apps.questionnaire.models import Question, Plan, Group, Language, SurveyPlanQuestionMap, QuestionContents
from django.core.exceptions import ValidationError

LOGGER = logging.getLogger('questionnaire_handler')

class GroupForm(forms.ModelForm):
    model = Group
    
    fields = '__all__'

class PlanForm(forms.ModelForm):
    model = Plan
    fields = '__all__'


class QuestionForm(forms.Form):
    plan = forms.ModelChoiceField(queryset=Plan.objects.filter(status='A'), required=True, help_text="Select Plan", label="Plan")
    qgroup = forms.ModelChoiceField(queryset=Group.objects.all())
    language = forms.ModelChoiceField(queryset=Language.objects.all())
    code = forms.CharField(max_length=60, min_length=3)
    content = forms.CharField(widget=forms.Textarea(attrs={'name':'content', 'rows':5, 'cols':5, 'help_text':"Enter cintent"}))
    answer_type = forms.ChoiceField(choices=settings.QUESTION_ANSWER_TYPES, required=True)
    status = forms.ChoiceField(choices=settings.QUESTION_STATUS_CHOICES, required=True)
    
    
    
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        plan = Plan.objects.all()
        self.fields['plan'].queryset = plan
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     plan = cleaned_data['plan']
    #     code = cleaned_data['code']
    #     content = cleaned_data['content']
    #     if Question.objects.filter(code=code).exists():
    #         raise forms.ValidationError("Code already exists")
    #     return cleaned_data
    
    def save(self, instance=None, commit=True):
        cleaned_data = self.cleaned_data
        
        if instance:
            instance.plan = cleaned_data['plan']
            instance.language = cleaned_data['language']
            instance.code = cleaned_data['code']
            instance.content = cleaned_data['content']
            instance.answer_type = cleaned_data['answer_type']
            instance.status = cleaned_data['status']
            if commit:
                instance.save()
            return instance
        else:
            question = Question(qgroup = cleaned_data['qgroup'],
                                code = cleaned_data['code'],
                                answer_type = cleaned_data['answer_type'],
                                status = cleaned_data['status'],
                                )
            question.save()
            LOGGER.debug("Question are created")
            SurveyPlanQuestionMap.objects.create(
                plan = cleaned_data['plan'],
                question = question,
            )
            QuestionContents.objects.create(
                question_id = question,
                language_id = cleaned_data['language'],
                content = cleaned_data['content'],
            )
            if commit:
                question.save()
            return question, instance
            

# class QuestionForm(forms.ModelForm):
    
#     plan = forms.ModelChoiceField(queryset=Plan.objects.filter(status='A'), required=True, help_text="Select Plan", label="Plan")
#     language = forms.ModelChoiceField(queryset=Language.objects.filter(status='A'), required=True, help_text="Select language", )
    
#     content = forms.CharField(widget=forms.Textarea())
#     code = forms.CharField(max_length=48, help_text="Enter Code")
    
#     class Meta:
#         model = Question
#         fields = ['plan', 'qgroup', 'code' , 'language', 'content','answer_type', 'status']
#         help_texts = {
#             "answer_type": ("Select answer type."),
#             "content": ("Write a content."),
#         }
        
    
#     def __init__(self, *args, **kwargs):        
#         super(QuestionForm, self).__init__(*args, **kwargs)
        
    
#     def clean(self) -> dict[str, Any]:
#         cleaned_data = super().clean()
#         plan = cleaned_data.get('plan')
#         language = cleaned_data.get('language')
        
#         if not plan and not language:
#             raise forms.ValidationError("Please select either a Plan or Language.")
        
#         return super().clean()
