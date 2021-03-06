from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.urls import reverse
from karbar.models import Payam_Madadju, Payam, events
from madadkar.forms import taghireNiazForm, afzoodanNiazForm, SignUpForm, VirayeshTahsilForm
from django.contrib.auth.models import User
import datetime
# Create your views here.
import karbar
import madadju
from hamiar.models import hemaiatNiaz, Hamiar
from karbar import moshtarak
from madadju.models import Madadju, Niaz, Madadkar, UserKarbar, staff_members, sharhe_tahsil


def is_madadkar(user):
    if not UserKarbar.objects.filter(user=user).exists():
        return False
    else:
        userKarbar = UserKarbar.objects.get(user=user)
        if not staff_members.objects.filter(stafID=userKarbar).exists():
            return False
        else:
            staffMember = staff_members.objects.get(stafID=userKarbar)
            return Madadkar.objects.filter(staffID=staffMember).exists()


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_afzoudan_niaz(request):
    template = 'madadkar/afzoudan_niaz.html'
    if request.method == "GET":
        form = afzoodanNiazForm()
        return render(request, template, {'progress': karbar.darbare_ma.progress(),
                                          'username': request.user, 'madadju_un': request.GET.get('madadju_un')
            , 'form': form})
    if request.method == "POST":
        form = afzoodanNiazForm(request.POST)
        if form.is_valid():
            madadju_un = request.GET.get('madadju_un')
            madadju_user = User.objects.get(username=madadju_un)
            madadju_uk = UserKarbar.objects.get(user=madadju_user)
            madadju_our = Madadju.objects.get(user=madadju_uk)
            mablagh = form.cleaned_data['mablagh']
            onvan = form.cleaned_data['onvan']
            Type = form.cleaned_data['Type']
            niazFori = form.cleaned_data['niazFori']
            if Niaz.objects.filter(onvan=onvan).exists():
                return render(request, template, {'progress': karbar.darbare_ma.progress(),
                                                  'username': request.user, 'madadju_un': request.GET.get('madadju_un')
                    , 'form': form,
                                                  'message': 'نیازی به این نام برای مددجو وجود دارد.در صورتی که می‌خواهید مبلغ آن را تغییر دهید به ویرایش نیاز مراجعه کنید.'
                                                  })
            Niaz.objects.create(niazmand=madadju_our, onvan=onvan, mablagh=mablagh,  Type=Type, niazFori=niazFori, mablagh_taminshodeh=0)
            events.objects.create(onvan='افزودن نیاز',
                                  matn='مددکار محترم، نیاز مربوط به مددجوی '+madadju_our.username()+' افزوده شد.',
                                  user=request.user, zaman=datetime.datetime.now())
            events.objects.create(onvan='افزودن نیاز',
                                  matn='مددجوی عزیز! نیازی به نیازهای شما افزوده شد.',
                                  user=madadju_user, zaman=datetime.datetime.now())

            return moshtarak.show_amaliat_movafagh(request, 'madadkar')
        else:
            return render(request, template, {'progress': karbar.darbare_ma.progress(),
                                              'username': request.user, 'madadju_un': request.GET.get('madadju_un')
                , 'form': form})


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_moshahede_madadjuyan_taht_kefalat(request):
    template = 'madadkar/moshahede_madadjuyan_taht_kefalat.html'
    user = request.user
    userKarbar = UserKarbar.objects.get(user=request.user)
    staffMember = staff_members.objects.get(stafID=userKarbar)
    madadkar = Madadkar.objects.get(staffID=staffMember)

    return render(request, template, {'username': request.user,
                                      'progress': karbar.darbare_ma.progress(),
                                      'madadjuyan': [(m.user.user.username, m.user.user.first_name,
                                                      m.user.user.last_name, m.ekhtar) for m in
                                                     Madadju.objects.filter(madadkar=madadkar)]
                                      # filter(user_user_id = user.id)]
                                      # Madadju.objects.filter(madadkar!=Null)
                                      # todo link moshahede profile madadju
                                      })


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_niaz_haye_madadju(request):
    template = 'madadkar/niaz_haye_madadju.html'
    virayesh = request.GET.get('virayesh')
    madadju_un = request.GET.get('madadju_un')
    user = User.objects.get(username=madadju_un)
    userKarbar = UserKarbar.objects.get(user=user)
    madadju = Madadju.objects.get(user=userKarbar)
    niazha = []
    for niaz in Niaz.objects.all():
        if niaz.niazmand == madadju:
            niazha.append(niaz)
    return render(request, template, {'username': request.user,
                                      'progress': karbar.darbare_ma.progress(),
                                      'niazha': [(n.id, n.onvan, n.mablagh - n.mablagh_taminshodeh,
                                                  n.mablagh_taminshodeh, n.niazFori) for n in niazha],
                                      # [ (type(n.niazmand),1,1,1) for n in Niaz.objects.all()],#= 'Madadju object (1)')],
                                      'madadju_un': madadju_un,
                                      'madadju_alarm': madadju.ekhtar
                                      ,'virayesh': virayesh
                                      })


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_niaz_haye_tamin_nashode(request):
    template = 'madadkar/niaz_haye_tamin_nashode.html'
    niazha = []
    for niaz in Niaz.objects.all():
        if niaz.hemaiatshod == False:
            niazha.append(niaz)
    return render(request, template, {'username': request.user,
                                      'progress': karbar.darbare_ma.progress(),
                                      'niazha': [(n.niazmand.username, n.onvan, n.mablagh_taminshodeh, n.mablagh-n.mablagh_taminshodeh, n.niazFori) for n in niazha],
                                      })


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_niaz_haye_tamin_nashode_fori(request):
    template = 'madadkar/niaz_haye_tamin_nashode_fori.html'
    niazha = []
    for niaz in Niaz.objects.all():
        if niaz.hemaiatshod == False:
            if niaz.niazFori:
                niazha.append(niaz)
    return render(request, template, {'username': request.user,
                                      'progress': karbar.darbare_ma.progress(),
                                      'niazha': [(n.niazmand.username, n.onvan, n.mablagh_taminshodeh,n.mablagh-n.mablagh_taminshodeh, n.niazFori) for n in niazha],
                                      })

def accPayam(request):
    payam=request.GET.get('payam')
    payamak=Payam_Madadju.objects.filter(pk= payam)
    payamak.update(taieed=True)
    payam1 = Payam_Madadju.objects.get(pk= payam)
    events.objects.create(onvan='پذیرش پیام',
                          matn='مددجوی عزیز! پیام شما به'+payam1.reciever.username()+' تایید و ارسال شد.',
                          user=payam1.sender.user.user, zaman=datetime.datetime.now())

    return HttpResponseRedirect(reverse( "movafaghshodim"))

def delPayam(request):
    payam =request.GET.get('payam')
    payam1 = Payam_Madadju.objects.get(pk= payam)
    events.objects.create(onvan='رد پیام',
                          matn='مددجوی عزیز! متاسفانه ارسال پیام شما به'+payam1.reciever.username()+' رد شد.',
                          user=payam1.sender.user.user, zaman=datetime.datetime.now())
    Payam_Madadju.objects.filter(pk=payam).delete()
    return HttpResponseRedirect(reverse( "movafaghshodim"))

@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_payam_entezar(request):
    template = 'madadkar/payam_entezar.html'
    upayam = request.GET.get('payam')
    payam1 = Payam.objects.get(pk=upayam)
    payam = Payam_Madadju.objects.get(payam=payam1)
    sender = payam.sender.username
    receiver = payam.reciever.username

    return render(request, template, {'utype': 'madadkar'
        , 'progress': karbar.darbare_ma.progress()
        , 'username': request.user
        , 'onvan': payam1.onvan
        , 'text': payam1.matn
        , 'sender': sender
        , 'receiver': receiver
        , 'date': payam1.zaman
        , 'payam':payam.pk})


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_profile(request):
    template = 'madadkar/profile.html'
    userKarbar = UserKarbar.objects.get(user=request.user)
    staffMember = staff_members.objects.get(stafID=userKarbar)
    # madadkar = Madadkar.objects.get(staffID=staffMember)
    return render(request, template, {'username': request.user,
                                      'progress': karbar.darbare_ma.progress(),
                                      'first_name': request.user.first_name,
                                      'last_name': request.user.last_name,
                                      'etebar': userKarbar.mojudi
                                      })


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_profile_madadju(request):
    template = 'madadkar/profile_madadju.html'
    virayesh = request.GET.get('virayesh')
    madadju_un = request.GET.get('madadju_un')
    user = User.objects.get(username=madadju_un)
    userKarbar = UserKarbar.objects.get(user=user)
    madadju = Madadju.objects.get(user=userKarbar)
    niazha = []
    for niaz in hemaiatNiaz.objects.all():
        if niaz.niaz.niazmand == madadju:
            niazha.append(niaz)
    hamiarha = []
    for niaz in niazha:
        if not hamiarha.__contains__(niaz.hamiar.username()):
            hamiarha.append(niaz.hamiar.staffID.stafID.user.username)
    shoruh = [ s.sharh for s in sharhe_tahsil.objects.filter(madadju=madadju)]
    shoruh_text = ''
    for s in shoruh :
        shoruh_text = shoruh_text + s + ' - '

    return render(request, template, {'username': request.user,
                                      'alarm': madadju.ekhtar,
                                      'progress': karbar.darbare_ma.progress(),
                                      'madadju_un': request.GET.get('madadju_un'),
                                      'madadju_fn': user.first_name,
                                      'madadju_ln': user.last_name,
                                      'hamiars': hamiarha,
                                      'sharh': shoruh_text,
                                      'virayesh' : virayesh
                                      # 'sharh_kh': (madadju.sharhe_tahsil.Field_Taghir, madadju.sharhe_tahsil.ُType)
                                      })


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_sandoghe_payamhaye_entezar(request):
    template = 'madadkar/sandoghe_payamhaye_entezar.html'
    payamha = []
    for payam in Payam_Madadju.objects.all():
        if (payam.sender.madadkar.username() == request.user.username) & (payam.taieed == False):
            payamha.append(
                (payam.payam.pk, payam.sender.username, payam.reciever.username, payam.payam.zaman, payam.payam.onvan))

    return render(request, template, {'utype': 'madadkar'
        , 'progress': karbar.darbare_ma.progress()
        , 'username': request.user
        , 'payamha': payamha})


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_sabte_naam_madadju(request):
    template = 'madadkar/sabte_naam_madadju.html'
    Umadadkar = UserKarbar.objects.get(user=request.user)
    Staffmadadkar = staff_members.objects.get(stafID=Umadadkar)
    Mymadadkar = Madadkar.objects.get(staffID=Staffmadadkar)

    if request.method == "GET":
        form = SignUpForm()
        return render(request, template, {'username': request.user,
                                          'progress': karbar.darbare_ma.progress(), 'form': form})
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            mGPA = form.cleaned_data['GPA']
            mEmail = form.cleaned_data['email']
            mFirstName = form.cleaned_data['first_name']
            mFamilyName = form.cleaned_data['last_name']
            mPhone = form.cleaned_data['phone_number']
            mAddress = form.cleaned_data['address']
            mSchool = form.cleaned_data['school']
            if User.objects.filter(username=mEmail).exists():
                return render(request, template, {'form': form, 'username': request.user,
                                                  'progress': karbar.darbare_ma.progress(),
                                                  'message': 'این ایمیل قبلا استفاده شده است.'})
            user = User.objects.create_user(username=mEmail, password="sabzipolo", email=mEmail, first_name=mFirstName,
                                            last_name=mFamilyName)
            user.save()
            ukarbar = UserKarbar.objects.create(user=user, phone_number=mPhone, address=mAddress, is_madadju=True)
            new_madadju = Madadju.objects.create(user=ukarbar, school=mSchool, GPA=mGPA, madadkar_init=Mymadadkar,
                                                 start_date=datetime.datetime.now())

            events.objects.create(onvan='ثبت نام مددجو',
                                  matn='مددجوی عزیز !‌خوش آمدید. ثبت نام شما توسط '+request.user.username+' با موفقیت انجام شد.',
                                  user=user, zaman=datetime.datetime.now())
            events.objects.create(onvan='ثبت نام مددجو',
                                  matn='مددکار گرامی، مددجوی '+user.username+' با موفقیت ثبت نام شد.',
                                  user=request.user, zaman=datetime.datetime.now())
            template = 'karbar/amaliat_movafagh.html'
            return render(request, template, {'utype': 'madadkar'
                , 'progress': karbar.darbare_ma.progress()
                , 'username': request.user})
        else:
            return render(request, template, {'username': request.user,
                                              'progress': karbar.darbare_ma.progress(), 'form': form})


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_virayesh_niaz(request):
    template = 'madadkar/virayesh_niaz.html'
    virayesh = request.GET.get('virayesh')
    madadju_user = request.GET.get('madadju_un')
    niaz = Niaz.objects.get(id=request.GET.get('niaz'))
    if request.method == 'GET':
        form = taghireNiazForm()
        return render(request, template, {'username': request.user,
                                          'progress': karbar.darbare_ma.progress(),
                                          'form': form, 'madadju': request.GET.get('madadju'),
                                          'niaz': niaz,
                                          'virayesh' : virayesh,
                                          'madadju_un' : madadju_user})
    if request.method == 'POST':
        niazID = request.GET.get('niaz')
        mNiaz = Niaz.objects.get(id=niazID)
        form = taghireNiazForm(request.POST)
        if form.is_valid():
            new_mablagh = form.cleaned_data['mablagh']
            mNiaz.mablagh = new_mablagh
            mNiaz.save()
            events.objects.create(onvan='ویرایش نیاز',
                                  matn='مددجوی عزیز، نیاز ' + mNiaz.onvan + ' شما تغییر یافت.',
                                  user=mNiaz.niazmand.user.user, zaman=datetime.datetime.now())
            template = 'karbar/amaliat_movafagh.html'
            return render(request, template, {'utype': 'madadkar'
                , 'progress': karbar.darbare_ma.progress()
                , 'username': request.user})
        else:
            return render(request, template, {'username': request.user,
                                              'progress': karbar.darbare_ma.progress(),
                                              'form': form, 'niaz_id': request.GET.get('niaz')
                                              ,'niaz' : niaz
                                              , 'virayesh' : virayesh
                                              ,'madadju_un' : madadju_user})


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_vaziat_tahsili(request):
    template = 'madadkar/vaziat_tahsili.html'
    virayesh = request.GET.get('virayesh')
    if request.method == "GET":
        form = VirayeshTahsilForm()
        return render(request, template, {'username': request.user,
                                          'madadju_un': request.GET.get('madadju_un'),
                                          'progress': karbar.darbare_ma.progress(), 'form': form
                                          ,'virayesh' : virayesh})
    if request.method == "POST":
        form = VirayeshTahsilForm(request.POST)
        madadju_u = User.objects.get(username=request.GET.get('madadju_un'))
        madadju_uk = UserKarbar.objects.get(user=madadju_u)
        madadju_ma = Madadju.objects.get(user=madadju_uk)
        madadkar_uk = UserKarbar.objects.get(user=request.user)
        madadkar_st = staff_members.objects.get(stafID=madadkar_uk)
        madadkar_ma = Madadkar.objects.get(staffID=madadkar_st)
        if form.is_valid():
            Field_Taghir = form.cleaned_data['Field_Taghir']
            sharh = form.cleaned_data['sharh']
            onvan = form.cleaned_data['onvan']
            Type = form.cleaned_data['Type']
            sharhe_tahsil.objects.create(madadju=madadju_ma, madadkar=madadkar_ma, onvan=onvan, Type=Type, sharh=sharh,
                                         Field_Taghir=Field_Taghir)
            return moshtarak.show_amaliat_movafagh(request, 'madadkar')
        else:
            return render(request, template, {'username': request.user,
                                              'madadju_un': request.GET.get('madadju_un'),
                                              'progress': karbar.darbare_ma.progress(), 'form': form,
                                              'virayesh':virayesh})


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_moshahede_madadjuyan_dar_entezar_madadkar(request):
    template = 'madadkar/moshahede_madadjuyan_dar_entezar_madadkar.html'
    return render(request, template, {'progress': karbar.darbare_ma.progress(),
                                      'madadjuyan': [(m.username, m.user.user.first_name, m.user.user.last_name) for m
                                                     in Madadju.objects.filter(madadkar=None)],
                                      #    Madadju.objects.filter(madadkar='Null')
                                      'username': request.user
                                      })


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def ekhtar(request):
    madadju_un = request.GET.get('madadju_un')
    madadju_user = User.objects.get(username=madadju_un)
    madadju_uk = UserKarbar.objects.get(user=madadju_user)
    madadju_our = Madadju.objects.get(user=madadju_uk)
    if madadju_our.ekhtar == True:
        madadju_our.ekhtar = False
    else:
        events.objects.create(onvan='اخطار!',
                              matn='مددجوی گرامی! چراغ اخطار شما روشن شد !',
                              user=madadju_user, zaman=datetime.datetime.now())
        madadju_our.ekhtar = True
    madadju_our.save()
    return HttpResponseRedirect(reverse("movafaghshodim"))


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def hazfNiaz(request):
    niaz = Niaz.objects.get(id=request.GET.get('niaz'))
    events.objects.create(onvan='حذف نیاز',
                              matn='مددجوی گرامی! نیاز'+niaz.onvan+' شما حذف شد.',
                              user=niaz.niazmand.user.user, zaman=datetime.datetime.now())
    Niaz.objects.filter(id=request.GET.get('niaz')).delete()
    return HttpResponseRedirect(reverse("movafaghshodim"))


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_profile_madadju_bi_kefalat(request):
    template = 'madadkar/profile_madadju_bi_kefalat.html'
    madadju_un = request.GET.get('madadju_un')
    user = User.objects.get(username=madadju_un)
    userKarbar = UserKarbar.objects.get(user=user)
    madadju = Madadju.objects.get(user=userKarbar)
    niazha = []
    for niaz in hemaiatNiaz.objects.all():
        if niaz.niaz.niazmand == madadju:
            niazha.append(niaz)
    hamiarha = []
    for niaz in niazha:
        if not hamiarha.contains(niaz.hamiar):
            hamiarha.append(niaz.hamiar.staffID.stafID.user.username)

    return render(request, template, {'username': request.user,
                                      'alarm': madadju.ekhtar,
                                      'progress': karbar.darbare_ma.progress(),
                                      'madadju_un': request.GET.get('madadju_un'),
                                      'madadju_fn': user.first_name,
                                      'madadju_ln': user.last_name,
                                      'hamiars': hamiarha,
                                      'sharh': "onvan" + "-" + "sharh"
                                      })


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_niaz_haye_madadju_bi_kefalat(request):
    template = 'madadkar/niaz_haye_madadju_bi_kefalat.html'
    madadju_un = request.GET.get('madadju_un')
    user = User.objects.get(username=madadju_un)
    userKarbar = UserKarbar.objects.get(user=user)
    madadju = Madadju.objects.get(user=userKarbar)
    niazha = []
    for niaz in Niaz.objects.all():
        if niaz.niazmand == madadju:
            niazha.append(niaz)
    return render(request, template, {'username': request.user,
                                      'progress': karbar.darbare_ma.progress(),
                                      'niazha': [(n.onvan, n.mablagh - n.mablagh_taminshodeh, n.mablagh_taminshodeh,
                                                  n.niazFori) for n in niazha],
                                      'madadju_un': madadju_un,
                                      'madadju_alarm': madadju.ekhtar
                                      })


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_madadkar(request):
    return moshtarak.show_user(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_afzayesh_etebar(request):
    return moshtarak.show_afzayesh_etebar(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_ersal_payam(request):
    return moshtarak.show_ersal_payam(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_moshahede_tarakonesh_haye_mali(request):
    return moshtarak.show_moshahede_tarakonesh_haye_mali(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_payam_daryafti(request):
    return moshtarak.show_payam_daryafti(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_payam_ersali(request):
    return moshtarak.show_payam_ersali(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_roydadha(request):
    return moshtarak.show_roydadha(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_sandoghe_payamhaye_daryafti(request):
    return moshtarak.show_sandoghe_payamhaye_daryafti(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_sandoghe_payamhaye_ersali(request):
    return moshtarak.show_sandoghe_payamhaye_ersali(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_amaliat_movafagh(request):
    return moshtarak.show_amaliat_movafagh(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_ahdaf(request):
    return moshtarak.show_ahdaf(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_ashnai(request):
    return moshtarak.show_ashnai(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_sakhtar_sazmani(request):
    return moshtarak.show_sakhtar_sazmani(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_moshahede_list_koodakan(request):
    return moshtarak.show_moshahede_list_koodakan(request, 'madadkar')


@login_required(login_url='/permission/')
@user_passes_test(is_madadkar, login_url='/permission/')
def show_moshahede_list_niazhaye_fori_taminnashode(request):
    return moshtarak.show_moshahede_list_niazhaye_fori_taminnashode(request, 'madadkar')

@login_required(login_url='/permission/')
@user_passes_test(is_madadkar,login_url='/permission/')
def edit_profile(request):
    return moshtarak.edit_profile(request,'madadkar')
