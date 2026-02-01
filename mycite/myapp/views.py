import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone  # MANA SHU QATORNI QO'SHING
from django.db.models import Count, Q
# Modellarni import qilish
from .models import Lead, Teacher,Note,Group
from django.db.models.functions import ExtractMonth, ExtractDay


@login_required
def statistics_view(request):
    # 1. Oylik lidlar soni (Mavjud kod)
    monthly_stats = Lead.objects.filter(created_at__year=2026).annotate(
        month=ExtractMonth('created_at')
    ).values('month').annotate(count=Count('id')).order_by('month')
    monthly_data = [0] * 12
    for stat in monthly_stats:
        monthly_data[stat['month'] - 1] = stat['count']

    # 2. Kurslar (Guruhlar) bo'yicha tahlil (YANGILANDI)
    # Endi 'course' o'rniga 'group__name' ishlatamiz (model o'zgargani uchun)
    course_stats = Lead.objects.values('group__name').annotate(count=Count('id')).order_by('-count')
    course_labels = [c['group__name'] if c['group__name'] else "Tanlanmagan" for c in course_stats]
    course_counts = [c['count'] for c in course_stats]

    # 3. O'qituvchilar tahlili (KPI - YANGI QISM)
    teachers_kpi = Teacher.objects.annotate(
        total_leads=Count('lead'),
        trial_leads=Count('lead', filter=Q(lead__has_trial=True)),
        no_trial_leads=Count('lead', filter=Q(lead__has_trial=False))
    )
    
    teachers_data = []
    for t in teachers_kpi:
        percentage = (t.trial_leads / t.total_leads * 100) if t.total_leads > 0 else 0
        teachers_data.append({
            'name': t.name,
            'total': t.total_leads,
            'attended': t.trial_leads,
            'missed': t.no_trial_leads,
            'percentage': round(percentage, 1)
        })

    # Mini kartalar uchun (Mavjud kod)
    current_month = timezone.now().month
    total_month_leads = Lead.objects.filter(created_at__month=current_month, created_at__year=2026).count()
    weekly_growth = Lead.objects.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7)).count()
    total_leads_count = Lead.objects.count()

    context = {
        'monthly_data': json.dumps(monthly_data),
        'course_labels': json.dumps(course_labels),
        'course_counts': json.dumps(course_counts),
        'teachers_data': teachers_data, # KPI uchun ma'lumot
        'total_month_leads': total_month_leads,
        'weekly_growth': weekly_growth,
        'total_leads_count': total_leads_count,
    }
    return render(request, 'statistics.html', context)



# Eslatmalar sahifasini ochish (agar alohida sahifa bo'lsa)
@login_required(login_url='login')
def notes_view(request):
    notes = Note.objects.all().order_by('-created_at')
    teachers = Teacher.objects.all()
    return render(request, 'eslatma.html', {'notes': notes, 'teachers': teachers})

# Eslatma qo'shish API
@csrf_exempt
def add_note_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            teacher_id = data.get('teacher_id')
            note_text = data.get('text')
            
            teacher = get_object_or_404(Teacher, id=teacher_id)
            Note.objects.create(teacher=teacher, text=note_text)
            
            return JsonResponse({'status': 'success', 'message': 'Eslatma saqlandi'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
# --- LOGIN QISMI ---


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(username=u_name, password=p_word)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Login yoki parol xato!")
            
    return render(request, 'index.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# --- SAHIFALAR ---

# HOME (O'QITUVCHILAR)
@login_required(login_url='login')
def home_view(request):
    # Bazadagi barcha o'qituvchilarni olish
    teachers = Teacher.objects.all().order_by('-id')
    return render(request, 'home.html', {'teachers': teachers})

def teachers_list(request):
    teachers = Teacher.objects.all().order_by('-id')
    return render(request, 'home.html', {'teachers': teachers})

def save_teacher(request):
    if request.method == "POST":
        t_id = request.POST.get('edit_id')
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        phone = request.POST.get('phone')
        groups = request.POST.get('groups') or 0

        if t_id and t_id != "-1": # Tahrirlash
            teacher = get_object_or_404(Teacher, id=t_id)
            teacher.name = name
            teacher.subject = subject
            teacher.phone = phone
            teacher.groups_count = groups
            teacher.save()
        else: # Yangi qo'shish
            Teacher.objects.create(
                name=name, subject=subject, phone=phone, groups_count=groups
            )
    return redirect('teachers_list')

def delete_teacher(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    teacher.delete()
    return redirect('teachers_list')


@csrf_exempt
def add_lead_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # O'qituvchi va Guruhni aniqlaymiz
            teacher_name = data.get('teacher')
            group_id = data.get('group_id')
            
            teacher_obj = Teacher.objects.filter(name=teacher_name).first()
            group_obj = Group.objects.filter(id=group_id).first()

            Lead.objects.create(
                name=data.get('name'),
                age=data.get('age'),
                phone=data.get('phone'), # School o'rniga Phone
                group=group_obj,         # Course o'rniga Group obyekti
                teacher=teacher_obj,
                source=data.get('source'),
                has_trial=(data.get('trial') == 'ha')
            )
            return JsonResponse({'status': 'success', 'message': 'Lid saqlandi'}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
def delete_lead_api(request, pk):
    if request.method == 'DELETE':
        # get_object_or_404 xatolik bo'lsa avtomatik 404 qaytaradi
        lead = get_object_or_404(Lead, pk=pk)
        lead.delete()
        return JsonResponse({'status': 'success', 'message': 'Lid o\'chirildi'})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=400)

@login_required(login_url='login')
def lid_view(request):
    leads = Lead.objects.select_related('group', 'teacher').all().order_by('-created_at')
    teachers = Teacher.objects.all()
    groups = Group.objects.select_related('teacher').all()
    
    # Statistika uchun
    total_leads = leads.count()
    trial_leads = leads.filter(has_trial=True).count() # Modeldagi field nomiga qarang (has_trial yoki trial)

    context = {
        'leads': leads,
        'teachers': teachers,
        'groups': groups,
        'total_leads': total_leads,
        'trial_leads': trial_leads,
    }
    return render(request, 'lid.html', context)
# --- API ---


@csrf_exempt
def edit_lead_api(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lead = get_object_or_404(Lead, pk=pk)
            
            lead.name = data.get('name', lead.name)
            lead.age = data.get('age', lead.age)
            lead.phone = data.get('phone', lead.phone) # School -> Phone
            lead.source = data.get('source', lead.source)
            lead.has_trial = (data.get('trial') == 'ha')
            
            # O'qituvchini yangilash
            teacher_name = data.get('teacher')
            if teacher_name:
                lead.teacher = Teacher.objects.filter(name=teacher_name).first()
            
            # Guruhni yangilash
            group_id = data.get('group_id')
            if group_id:
                lead.group = Group.objects.filter(id=group_id).first()
                
            lead.save()
            return JsonResponse({'status': 'success', 'message': 'Lid yangilandi'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)