from django.db import models


class Family(models.Model):
    """
    Stores an entire family data collection form submission as a PostgreSQL JSONB field.
    No normalization — the full structured JSON is stored as-is.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    family_json = models.JSONField()
    photo = models.ImageField(upload_to='family_photos/', null=True, blank=True)

    class Meta:
        verbose_name = 'Family'
        verbose_name_plural = 'Families'
        ordering = ['-created_at']

    def __str__(self):
        name = self.family_json.get('ഗൃഹനാഥന്റെ പേര്', 'Unknown')
        form_no = self.family_json.get('ഫോം നമ്പർ', '')
        return f"{name} (Form #{form_no})"
