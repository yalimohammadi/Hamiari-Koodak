from django.db import models
from madadju.models import *
from modir.models import *
from hamiar.models import *
from karbar.models import *
from datetime import datetime

from modir.models import *


class Madadkar(staff_members):
    termination_date = models.DateField(null=True,
                                        blank=True)  # age delete kard acountesho kolan hazfesh nemikonim. inja minevisim
    start_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=False)  # modir activesh mikone
    ekhtar = models.BooleanField(default=False)
    hoghugh = models.PositiveIntegerField()


class hoghugh_dariafti(models.Model):
    maddadkar = models.ForeignKey('Madadkar', on_delete=models.CASCADE)
    mablagh = models.PositiveIntegerField()
    zaman = models.DateTimeField(default=datetime.now, blank=True)

