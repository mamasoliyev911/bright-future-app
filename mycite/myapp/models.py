from django.db import models

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    groups_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

# 1. YANGI MODEL: Guruhlar (Leadlar shu yerga birikadi)
class Group(models.Model):
    name = models.CharField(max_length=100)  # Masalan: "Elementary A1"
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='groups')
    days = models.CharField(max_length=100)  # Masalan: "Du-Chor-Jum"
    time = models.CharField(max_length=50)   # Masalan: "14:00 - 15:30"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} | {self.teacher.name}"

class Lead(models.Model):
    SOURCE_CHOICES = [
        ('Instagram', 'Instagram'),
        ('Tanish', 'Tanish orqali'),
        ('Telegram', 'Telegram'),
        ('Banner', 'Banner'),
        ('Maktab targ\'iboti', 'Maktab targ\'iboti'),
    ]
    
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    
    # 2. O'ZGARISH: School o'rniga Phone bo'ldi
    phone = models.CharField(max_length=20) 
    
    # 3. O'ZGARISH: Course (text) o'rniga Group (ForeignKey) ishlatamiz
    # related_name='leads' deb yozdik, shunda group.leads.all() qilib o'quvchilarni olamiz
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    
    # Teacher ham turavergani ma'qul (zaxira uchun yoki guruhsiz o'quvchi bo'lsa)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    
    has_trial = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Note(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='notes')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher.name} uchun eslatma"