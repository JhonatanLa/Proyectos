from django import forms

class ExcelUploadForm(forms.Form):
    # Campo para cargar el archivo Excel
    excel_file = forms.FileField(label='Seleccionar archivo Excel')
