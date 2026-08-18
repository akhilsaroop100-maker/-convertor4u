from django import forms

from .models import CorrectionReport


class CorrectionReportForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput, label="Leave blank")

    class Meta:
        model = CorrectionReport
        fields = ("name", "email", "page_url", "subject", "message")
        widgets = {
            "message": forms.Textarea(attrs={"rows": 7}),
            "page_url": forms.URLInput(attrs={"placeholder": "https://example.com/page/"}),
        }

    def clean_website(self):
        value = self.cleaned_data.get("website")
        if value:
            raise forms.ValidationError("Unable to submit this report.")
        return value
