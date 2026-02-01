from django.urls import path
from .views import login_view, home_view, lid_view, logout_view,add_lead_api,delete_lead_api, edit_lead_api,notes_view,add_note_api,statistics_view,teachers_list,save_teacher,delete_teacher

urlpatterns = [
    path('', login_view, name='login'),          # Asosiy sahifa - Login
    path('home/', home_view, name='home'),       # O'qituvchilar
    path('lids/', lid_view, name='lids'),        # Lidlar
    path('lids/', lid_view, name='lids'),
    path('api/add-lead/', add_lead_api, name='add_lead_api'),
    path('logout/', logout_view, name='logout'), # Tizimdan chiqish
    path('api/delete-lead/<int:pk>/', delete_lead_api, name='delete_lead_api'),
    path('api/edit-lead/<int:pk>/', edit_lead_api, name='edit_lead_api'),
    # ... boshqa url-lar
    path('notes/', notes_view, name='notes'),
    path('api/add-note/', add_note_api, name='add_note_api'),
    path('statistics/', statistics_view, name='statistics'),

    path('teachers/',teachers_list, name='teachers_list'),
    path('teachers/save/', save_teacher, name='save_teacher'),
    path('teachers/delete/<int:pk>/', delete_teacher, name='delete_teacher'),
]