import pandas as pd
from django.shortcuts import render
import matplotlib.pyplot as plt
import seaborn as sns
from django_excel import xlsx

def upload_file(request):
    if request.method == 'POST':
        file = request.FILES['file']
        df = pd.read_excel(file)
        # Do some analysis with pandas
        # ...
        return render(request, 'result.html', {'data': df})
    return render(request, 'upload.html')



def display_graph(request):
    # Load data from Excel file
    df = pd.read_excel('path/to/file.xlsx')

    # Create graph using matplotlib and seaborn
    sns.countplot(x='column_name', data=df)
    plt.savefig('static/graph.png')

    return render(request, 'graph.html')



@xlsx('my_file.xlsx')
def export_to_excel(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="my_file.xlsx"'

    wb = openpyxl.load_workbook(response)
    ws = wb.active

    # Write data to Excel file
    ws.append(['Column 1', 'Column 2', 'Column 3'])
    for row in df.values:
        ws.append(row)

    wb.save(response)
    return response