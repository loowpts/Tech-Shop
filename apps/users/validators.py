import logging
import re
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail


logger = logging.getLogger(__name__)


def send_verification_email(user, token):
    """
    Отправляет письмо с ссылкой для верификации email.
    
    Пример: send_verification_email(user, verification_token)
    """
    subject = 'Подтвердите ваш email'
    
    verification_link = f'{settings.FRONTEND_URL}/verify-email/{token.token}'
    
    message = f"""
    Здравствуйте, {user.get_short_name()}!
    
    Спасибо за регистрацию. Пожалуйста, подтвердите ваш email адрес, перейдя по ссылке:
    
    {verification_link}
    
    Ссылка действительна в течение 24 часов.
    
    Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.
    
    С уважением,
    Команда сайта.
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f'Письмо верификации отправлено на: {user.email}')
    except Exception as e:
        logger.error(f'Ошибка отправки письма верификации на {user.email}: {e}')
        raise
    

def send_password_reset_email(user, token):
    """
    Отправляет письмо со ссылкой для сброса пароля.
    
    Пример: send_password_reset_email(user, reset_token)
    """
    
    subject = 'Сброс пароля'
    
    # Формируем ссылку для сброса пароля
    reset_link = f'{settings.FRONTEND_URL}/reset-password/{token.token}'
    
    message = f"""
    Здравствуйте, {user.get_short_name()}!
    
    Вы запросили сброс пароля. Перейдите по ссылке для установки нового пароля:
    
    {reset_link}
    
    Ссылка действительная в течение 1 часа.
    
    Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.
    
    С уважением,
    Команда сайта
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f'Письмо сброса пароля отправлено на: {user.email}')
    except Exception as e:
        logger.error(f'Ошибка отправки письма сброса пароля на {user.email}: {e}')
        raise
    
def send_welcome_email(user):
    """
    Отправляет приветственное письмо после верификации.
    
    send_welcome_email(user)
    """
    
    subject = 'Добро пожаловать'
    
    message = f"""
    Здравствуйте, {user.get_short_name()}!
    
    Спасибо за подтверждение email адреса!
    
    Теперь вы можете пользоваться всеми возможностями нашего сервиса.
    
    С уважением,
    Команда сайта
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f'Приветственное письмо отправлено на: {user.email}')
    except Exception as e:
        logger.error(f'Ошибка отправки приветственного письма на {user.email}: {e}')
        pass
    

def validate_phone_number(value):
    """
    Проверяет корректность номер телефона.
    
    Пример: phone = serializers.CharField(validators=[validate_phone_number])
    """

    if not value:
        return
    
    # Убираем все кроме цифр и +
    cleaned = re.sub(r'[^\d+]', '', value)
    
    pattern = r'^\+?[78][\d]{10}$'
    if not re.match(pattern, cleaned):
        raise ValidationError(
            _('Некорректный формат номер телефона. Используйте формат: +79991234567'),
            code='invalid_phone'
        )

def validate_password_strength(password):
    """
    Проверяет надежность пароля.
    
    Пример:
    validate_password_strength('MyPass123) # Ok
    validate_password_strength('weak) # ValidationError
    """
    
    if len(password) < 8:
        raise ValidationError(
            _('Пароль должен содержать минимум 8 символов.'),
            code='password_too_short'
        )
        
    if not re.search(r'[A-Z]', password):
        raise ValidationError(
            _('Пароль должен содержать хотя бы одну заглавную букву'),
            code='password_no_upper'
        )
        
    if not re.search(r'[a-z]', password):
        raise ValidationError(
            _('Пароль должен содержать хотя бы одну строчную букву'),
            code='password_no_lower'
        )
    
    if not re.search(r'\d', password):
        raise ValidationError(
            _('Пароль должен содержать хотя бы одну цифру'),
            code='password_no_digit'
        )
        
def validate_password(value):
    validate_password_strength(value)
    return value
    