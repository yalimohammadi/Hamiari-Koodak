from django.db import models
from datetime import datetime
from madadkar.models import *
from modir.models import *
from karbar.models import *

# Create your models here


class Madadju(User):
    madadkar_init = models.ForeignKey(Madadkar, on_delete=models.PROTECT,related_name='Madadkar_Moaref')  # madadkari ke ezafash karde
    madadkar = models.ForeignKey(Madadkar, default=None, blank=True,
                                 null=True, on_delete=models.SET_NULL)  # madadkari ke hemaiat mikone azash mitune nabashe
    ekhtar = models.BooleanField(default=False)
    termination_date = models.DateField(null=True,
                                    blank=True)  # age delete kard acountesho kolan hazfesh nemikonim. inja minevisim
    start_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=False)  # modir activesh mikone


class sharhe_tahsil(models.Model):
    madadju = models.ForeignKey(Madadju, on_delete=models.CASCADE)
    madadkar = models.ForeignKey(Madadkar, on_delete=models.PROTECT)  # madadkari ke sharho minvise
    sharh = models.CharField(max_length=1000)
    onvan = models.CharField(max_length=50)
    Type = (
        ('GD', 'تغییر مثبت'),
        ('BD', 'تغییر منفی'))
    Field_Taghir = (
        ('gpa', 'تغییر چشمگیر در معدل'),
        ('olamp', 'شرکت در المپیاد دانش آموزی'),
        ('konkoor', 'شرکت در کنکور'),
        ('teacher', 'گزارش از معلم دانش آموز یا کادر مدرسه'),
        ('finals', 'گزارش امتحانات پایان سال')
    )


class taghire_madadkar(models.Model):
    madadju = models.ForeignKey(Madadju, on_delete=models.CASCADE)
    # az ro object madadju madadkar ham dar miad
    sharh = models.CharField(max_length=1000)
    Taieed = models.BooleanField(default=False)


class Niaz(models.Model):
    niazmand = models.ForeignKey(Madadju, on_delete=models.CASCADE)
    onvan = models.CharField(max_length=50)
    mablagh = models.PositiveIntegerField()
    mablagh_taminshodeh = models.PositiveIntegerField()
    hemaiatshod = models.BooleanField(default=False)
    Type = (
        ('yr', 'Salaneh'),
        ('mo', 'Mahaneh'))
    niazFori = models.BooleanField(default=False)

    class Meta:
        unique_together = (("niazmand", "onvan"),)


class hadie_gheire_naghdi(models.Model):
    hamiar = models.ForeignKey('hamiar.Hamiar', on_delete=models.PROTECT)
    niazmand = models.ForeignKey(Madadju, on_delete=models.PROTECT)
    onvan = models.CharField(max_length=50)



