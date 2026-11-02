from email_validator import EmailNotValidError, validate_email


def verify_email_syntax(email: str) -> bool:
    try:
        valid = validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


# يفضل لو نحذف التحقق دا بالكامل و نخلية لية انترفيس و نقدمة في طبقة الابليكيشن او الفاليديشن عشان النظام يكون خفيف اما الي بنعملو دا هيخلي كل جلب من قاعدة البيانات تعمل تشيك على الايميل تاني فا حرفيا هدر ملوش داعي
# لكن هنكمل مع الديزاين دا لتوضيح بس الفاليو اوبجكت
