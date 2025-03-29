# Modern IPTV Player

مشغل IPTV حديث مبني باستخدام Python وواجهة PyQt6 ومشغل VLC.

## الميزات

- تشغيل القنوات من روابط M3U
- البحث في القنوات وتصنيفها
- إنشاء قوائم تشغيل مخصصة
- دعم اللغة العربية والإنجليزية
- واجهة مستخدم حديثة وأنيقة

## متطلبات النظام

- Python 3.8+
- PyQt6
- python-vlc
- requests
- VLC Media Player (إصدار 64 بت موصى به)

## هام: توافق البنية مع VLC

لكي يعمل التطبيق بشكل صحيح، يجب أن تتطابق بنية VLC مع بنية Python:

- **ينصح باستخدام Python 64-bit مع VLC 64-bit** المثبت في "C:\Program Files\VideoLAN\VLC"
- **يمكن أيضاً استخدام Python 32-bit مع VLC 32-bit** المثبت في "C:\Program Files (x86)\VideoLAN\VLC"

للتحقق من بنية Python لديك، قم بتشغيل:
```python
python -c "import sys; print('64-bit' if sys.maxsize > 2**32 else '32-bit')"
```

## التثبيت

1. قم بتنزيل وتثبيت إصدار 64 بت من VLC من [videolan.org](https://www.videolan.org/vlc/)

2. قم بتثبيت حزم Python المطلوبة:
   ```
   pip install -r requirements.txt
   ```

3. قم بتكوين مسار VLC:
   ```
   python force_vlc_path.py
   ```
   سيساعدك هذا في اختيار تثبيت VLC الصحيح.

4. قم بتشغيل التطبيق:
   ```
   python main.py
   ```

## استكشاف أخطاء VLC وإصلاحها

إذا واجهت مشكلات:

1. قم بتثبيت إصدار 64 بت من VLC في المسار الافتراضي: `C:\Program Files\VideoLAN\VLC`

2. قم بتشغيل أداة تكوين مسار VLC:
   ```
   python force_vlc_path.py
   ```

3. إذا استمرت المشكلة، جرب:
   ```
   python setup_vlc.py
   ```

## الاستخدام

1. قم بتشغيل التطبيق:
   ```
   python main.py
   ```

2. قم بتحميل قائمة تشغيل IPTV:
   - فتح ملف M3U محلي: File > Open Playlist...
   - فتح من URL: File > Open Playlist from URL...

3. تصفح القنوات:
   - استخدم مربع البحث للعثور على قنوات محددة
   - قم بتصفية القنوات حسب الفئة باستخدام القائمة المنسدلة
   - انقر نقراً مزدوجاً على قناة لتشغيلها

4. قوائم التشغيل المخصصة:
   - انقر على زر "+" في منطقة علامات التبويب
   - قم بتسمية قائمة التشغيل الخاصة بك
   - انقر بزر الماوس الأيمن على القنوات وحدد "Add to Playlist"

