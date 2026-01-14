import logging
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail

from .models import User, EmailVerification, PasswordReset
from .validators import send_verification_email, send_password_reset_email

logger = logging.getLogger(__name__)


class UserService:
    
    @staticmethod
    @transaction.atomic
    def _create_and_send_verification(user: User) -> EmailVerification:
        token = EmailVerification.objects.create(user=user)
        
        send_verification_email(user, token)
        
        logger.info(f'Email verification sent to {user.email}')
        
        return token
    
    @staticmethod
    @transaction.atomic
    def verify_email(token_value: str) -> User:
        
        try:
            token = EmailVerification.objects.get(token=token_value)
        except EmailVerification.DoesNotExist:
            logger.warning(f'Invalid email verification token: {token_value}')
            raise ValueError('Invalid token')

        if not token.is_valid:
            logger.warning(f'Expired or used email verification token: {token_value}')
            raise ValueError('Token is expired or already used')
        
        user = token.user
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        
        token.is_used = True
        token.save(update_fields=['is_used'])
        
        logger.info(f'Email verified for user {user.email}')
        
        return user
    
    @staticmethod
    @transaction.atomic
    def reset_password(token_value: str, new_password: str) -> User:
        
        try:
            token = PasswordReset.objects.get(token=token_value)
        except PasswordReset.DoesNotExist:
            logger.warning(f'Invalid password reset token: {token_value}')
            raise ValueError('Invalid token')

        if not token.is_valid:
            logger.warning(f'Expired or used password reset token: {token_value}')
            raise ValueError('Token is expired or already used')
        
        user = token.user
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        token.is_used = True
        token.save(update_fields=['is_used'])
        
        logger.info(f'Password reset for user {user.email}')
        
        return user
    
    @staticmethod
    @transaction.atomic
    def change_password(user: User, old_password: str, new_password: str) -> User:
        
        if not user.check_password(old_password):
            logger.warning(f'Incorrect old password for user {user.email}')
            raise ValueError('Old password is incorrect')
        
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        logger.info(f'Password changed for user {user.email}')
        
        return user
    
    @staticmethod
    def resend_verification_email(user: User) -> None:

        if user.is_verified:
            logger.info(f'User {user.email} is already verified')
            raise ValueError('User is already verified')
        
        EmailVerification.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)
        
        UserService._create_and_send_verification(user)
        
        logger.info(f'Resent email verification to {user.email}')
        
    @staticmethod
    def request_password_reset(email: str) -> bool:

        try:
            user = User.objects.get(email=email)

            token = PasswordReset.objects.create(user=user)

            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token.token}"

            send_mail(
                subject='Сброс пароля',
                message=f'Для сброса пароля перейдите по ссылке: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            logger.info(f'Password reset email sent to {email}')
            return True
        except User.DoesNotExist:
            logger.warning(f'Password reset requested for non-existent email: {email}')
            return False
        except Exception as e:
            logger.error(f'Error sending password reset email to {email}: {e}')
            return False
