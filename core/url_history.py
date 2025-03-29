import os
import json
from datetime import datetime

class PlaylistURLManager:
    """مدير روابط قوائم التشغيل لحفظ وإدارة الروابط المستخدمة"""
    
    def __init__(self, history_file="playlist_urls.json"):
        self.history_file = history_file
        self.urls = []
        self.load_history()
    
    def load_history(self):
        """تحميل سجل الروابط من ملف"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.urls = data
            except Exception as e:
                print(f"خطأ في تحميل سجل الروابط: {e}")
    
    def save_history(self):
        """حفظ سجل الروابط إلى ملف"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.urls, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"خطأ في حفظ سجل الروابط: {e}")
    
    def add_url(self, url):
        """إضافة رابط جديد إلى السجل"""
        # تجنب التكرار - إذا كان الرابط موجود فإزالته أولاً ثم إضافته من جديد في المقدمة
        if url in self.urls:
            self.urls.remove(url)
        
        # إضافة الرابط في بداية القائمة (الأحدث أولاً)
        self.urls.insert(0, url)
        
        # الاحتفاظ بآخر 20 رابط فقط
        self.urls = self.urls[:20]
        
        # حفظ التغييرات
        self.save_history()
    
    def get_urls(self):
        """استرجاع قائمة الروابط المحفوظة"""
        return self.urls
    
    def clear_history(self):
        """مسح سجل الروابط"""
        self.urls = []
        self.save_history()
