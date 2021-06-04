from schematics.models import Model
from schematics.types import URLType, DecimalType, StringType, DictType, ModelType, PolyModelType


class HeadHunterSalary(Model):
    value = StringType(required=True)
    range = DictType(DecimalType, required=True)


class HeadHunterCompany(Model):
    name = StringType()
    url = StringType()


class HeadHunterItem(Model):
    timestamp = DecimalType(required=True)
    vacancy_id = StringType(required=True)
    company = ModelType(HeadHunterCompany, required=True)
    title = StringType(required=True)
    url = URLType(required=True)
    salary = ModelType(HeadHunterSalary, required=True)
