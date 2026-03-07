from django.urls import path
from . import views

app_name = 'family'

urlpatterns = [
    path('', views.LandingView.as_view(), name='landing'),
    path('records/', views.FamilyListView.as_view(), name='list'),
    path('new/', views.FamilyCreateView.as_view(), name='create'),
    path('<int:pk>/', views.FamilyDetailView.as_view(), name='detail'),
    path('success/', views.SuccessView.as_view(), name='success'),

    # Bulk exports
    path('export/json/', views.ExportAllJSON.as_view(), name='export_all_json'),
    path('export/csv/', views.ExportAllCSV.as_view(), name='export_all_csv'),

    # Single record exports
    path('<int:pk>/export/json/', views.ExportSingleJSON.as_view(), name='export_json'),
    path('<int:pk>/export/csv/', views.ExportSingleCSV.as_view(), name='export_csv'),
    path('<int:pk>/export/poster/', views.ExportPoster.as_view(), name='export_poster'),
    path('<int:pk>/export/preview/', views.ExportPreview.as_view(), name='export_preview'),
    path('<int:pk>/poster/preview/', views.PosterPreview.as_view(), name='poster_preview'),

    # Delete
    path('<int:pk>/delete/', views.FamilyDeleteView.as_view(), name='delete'),

    # Edit
    path('<int:pk>/edit/', views.FamilyEditView.as_view(), name='edit'),
]
