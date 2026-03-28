from django.db import models


class Family(models.Model):
    """
    Stores an entire family data collection form submission as a PostgreSQL JSONB field.
    No normalization — the full structured JSON is stored as-is.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    family_json = models.JSONField()
    photo = models.ImageField(upload_to='family_photos/', null=True, blank=True)
    search_index = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Family'
        verbose_name_plural = 'Families'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Generate search index from Malayalam name
        from indic_transliteration import sanscript
        import re
        name = self.family_json.get('ഗൃഹനാഥന്റെ പേര്', '')
        if name:
            # 1. Pre-process chillu letters for better mapping in ISO
            replacements = {
                'ൻ': 'n',
                'ർ': 'r',
                'ൽ': 'l',
                'ൾ': 'l',
                'ക്': 'k',
            }
            processed_name = name
            for k, v in replacements.items():
                processed_name = processed_name.replace(k, v)

            # 2. Transliterate Malayalam to ISO (Latin)
            iso = sanscript.transliterate(processed_name, sanscript.MALAYALAM, sanscript.ISO).lower()

            # 3. Custom mappings for common English representations
            mappings = {
                'ṣ': 'sh', 
                'ś': 'sh', 
                'ā': 'a',
                'ī': 'i',
                'ū': 'u',
                'ē': 'e',
                'ō': 'o',
                'ḷ': 'l',
                'ṛ': 'r',
                'ṟ': 'r', # For words like Ashraf
                'ṇ': 'n',
                'ñ': 'n',
                'ṅ': 'n',
                'ph': 'f', # For words like Ashraf
                't‌': 't', # handles the half-u or chandrakkala at end
            }
            for k, v in mappings.items():
                iso = iso.replace(k, v)

            # 4. Final normalization: remove any remaining non-ascii chars
            normalized = re.sub(r'[^a-z\s]', '', iso)
            self.search_index = normalized
        super().save(*args, **kwargs)

    def __str__(self):
        name = self.family_json.get('ഗൃഹനാഥന്റെ പേര്', 'Unknown')
        form_no = self.family_json.get('ഫോം നമ്പർ', '')
        return f"{name} (Form #{form_no})"
