from flask_mail import Mail, Message
from flask import url_for

class NotificationService:
    @staticmethod
    def send_verification_email(user_email, mail_instance, frontend_url, token):
        """Envía un correo electrónico de verificación al usuario"""
        try:

            link = f"{frontend_url}/verify-email?token={token}"

            msg = Message("Verificación de correo electrónico",
                          subject="Verificación de correo electrónico",
                          sender=user_email,
                          recipients=[user_email])
            msg.body = f"Por favor, verifica tu correo electrónico haciendo clic en el siguiente enlace: {link}"
            
            mail_instance.send(msg)
            print(f"Correo de verificación enviado a {user_email}")
        except Exception as e:  
            print(f"Error al enviar el correo de verificación a {user_email}: {str(e)}")
