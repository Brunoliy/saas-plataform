"""Email Service using Resend API."""

import resend
from typing import List, Optional

from app.core.config import settings
from app.core.exceptions import SaaSPlatformException


class EmailService:
    """Email service for sending transactional emails."""

    def __init__(self):
        """Initialize Resend API."""
        if not settings.resend_api_key:
            raise SaaSPlatformException(
                message="Resend API key not configured",
                error_code="EMAIL_NOT_CONFIGURED"
            )

        resend.api_key = settings.resend_api_key

    def send_email(
        self,
        to: List[str],
        subject: str,
        html: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> dict:
        """
        Send email using Resend.

        Args:
            to: List of recipient email addresses
            subject: Email subject
            html: HTML email content
            from_email: Sender email (defaults to settings)
            from_name: Sender name (defaults to settings)

        Returns:
            dict with email_id and status
        """
        try:
            sender = f"{from_name or settings.from_name} <{from_email or settings.from_email}>"

            response = resend.Emails.send({
                "from": sender,
                "to": to,
                "subject": subject,
                "html": html,
            })

            return {
                "email_id": response.get("id"),
                "status": "sent"
            }

        except Exception as e:
            raise SaaSPlatformException(
                message=f"Failed to send email: {str(e)}",
                error_code="EMAIL_SEND_FAILED"
            )

    def send_welcome_email(self, to_email: str, user_name: str) -> dict:
        """Send welcome email to new user."""
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h1 style="color: #333;">Bem-vindo ao SaaS Platform, {user_name}!</h1>
                <p>Obrigado por se cadastrar na nossa plataforma.</p>
                <p>Agora você pode:</p>
                <ul>
                    <li>Explorar projetos disponíveis</li>
                    <li>Conectar-se com profissionais qualificados</li>
                    <li>Receber recomendações personalizadas com IA</li>
                </ul>
                <p>Caso tenha alguma dúvida, não hesite em nos contatar.</p>
                <p>
                    <a href="{settings.frontend_url}"
                       style="background-color: #4CAF50; color: white; padding: 10px 20px;
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Acessar Plataforma
                    </a>
                </p>
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    Este é um email automático, por favor não responda.
                </p>
            </body>
        </html>
        """

        return self.send_email(
            to=[to_email],
            subject="Bem-vindo ao SaaS Platform!",
            html=html
        )

    def send_proposal_notification(
        self,
        to_email: str,
        client_name: str,
        project_title: str,
        professional_name: str
    ) -> dict:
        """Send notification when a new proposal is received."""
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h1 style="color: #333;">Nova Proposta Recebida!</h1>
                <p>Olá {client_name},</p>
                <p>Você recebeu uma nova proposta para o projeto <strong>{project_title}</strong>.</p>
                <p><strong>Profissional:</strong> {professional_name}</p>
                <p>
                    <a href="{settings.frontend_url}/projects"
                       style="background-color: #2196F3; color: white; padding: 10px 20px;
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Ver Proposta
                    </a>
                </p>
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    Este é um email automático, por favor não responda.
                </p>
            </body>
        </html>
        """

        return self.send_email(
            to=[to_email],
            subject=f"Nova proposta para: {project_title}",
            html=html
        )

    def send_proposal_accepted_notification(
        self,
        to_email: str,
        professional_name: str,
        project_title: str,
        client_name: str
    ) -> dict:
        """Send notification when a proposal is accepted."""
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h1 style="color: #4CAF50;">Proposta Aceita! 🎉</h1>
                <p>Olá {professional_name},</p>
                <p>Sua proposta para o projeto <strong>{project_title}</strong> foi aceita!</p>
                <p><strong>Cliente:</strong> {client_name}</p>
                <p>Entre em contato com o cliente para dar início ao projeto.</p>
                <p>
                    <a href="{settings.frontend_url}/projects"
                       style="background-color: #4CAF50; color: white; padding: 10px 20px;
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Ver Projeto
                    </a>
                </p>
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    Este é um email automático, por favor não responda.
                </p>
            </body>
        </html>
        """

        return self.send_email(
            to=[to_email],
            subject=f"Proposta aceita: {project_title}",
            html=html
        )

    def send_project_completed_notification(
        self,
        to_email: str,
        recipient_name: str,
        project_title: str
    ) -> dict:
        """Send notification when a project is completed."""
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h1 style="color: #333;">Projeto Concluído!</h1>
                <p>Olá {recipient_name},</p>
                <p>O projeto <strong>{project_title}</strong> foi marcado como concluído.</p>
                <p>Não se esqueça de deixar uma avaliação para ajudar outros usuários!</p>
                <p>
                    <a href="{settings.frontend_url}/projects"
                       style="background-color: #FF9800; color: white; padding: 10px 20px;
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Deixar Avaliação
                    </a>
                </p>
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    Este é um email automático, por favor não responda.
                </p>
            </body>
        </html>
        """

        return self.send_email(
            to=[to_email],
            subject=f"Projeto concluído: {project_title}",
            html=html
        )
