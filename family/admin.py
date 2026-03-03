from django.contrib import admin
from .models import Family


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_head_name', 'get_form_number', 'get_panchayath', 'created_at']
    list_filter = ['created_at']
    search_fields = ['family_json__ഗൃഹനാഥന്റെ പേര്', 'family_json__ഫോം നമ്പർ']
    readonly_fields = ['created_at', 'family_json']

    def get_head_name(self, obj):
        return obj.family_json.get('ഗൃഹനാഥന്റെ പേര്', '—')
    get_head_name.short_description = 'ഗൃഹനാഥൻ'

    def get_form_number(self, obj):
        return obj.family_json.get('ഫോം നമ്പർ', '—')
    get_form_number.short_description = 'ഫോം നമ്പർ'

    def get_panchayath(self, obj):
        return obj.family_json.get('പഞ്ചായത്ത്', '—')
    get_panchayath.short_description = 'പഞ്ചായത്ത്'
