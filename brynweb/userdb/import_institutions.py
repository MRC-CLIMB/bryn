import csv
from userdb.models import Institution


def load_institution_data(file_path):
    """clear and reload Institution data from csv"""
    Institution.objects.all().delete()
    reader = csv.DictReader(open(file_path))
    for row in reader:
        if len(row["name"]):
            institution = Institution(name=row["name"])
            institution.save()
