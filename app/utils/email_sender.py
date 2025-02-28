from flask_mail import Message
from flask import current_app
import logging
import smtplib

def send_invitation_email(email, token, role):
    """
    Envoie un email d'invitation à un nouvel utilisateur.
    
    Args:
        email (str): Email du destinataire
        token (str): Token d'invitation unique
        role (str): Rôle de l'utilisateur ('membre' ou 'artiste')
    """
    try:
        # Construire l'URL d'acceptation de l'invitation
        # Utiliser l'URL de base et ajouter le préfixe admin
        base_url = current_app.config['BASE_URL'].rstrip('/')
        invitation_url = f"{base_url}/admin/accept_invitation/{token}"
        
        # Personnaliser le message selon le rôle
        role_label = 'Membre' if role == 'membre' else 'Artiste'
        
        msg = Message(
            f'Invitation à rejoindre Art Cartel - {role_label}',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        
        msg.body = f'''
Bonjour,

Vous avez été invité à rejoindre Art Cartel en tant que {role_label.lower()}.

Pour accepter cette invitation, veuillez cliquer sur le lien suivant :
{invitation_url}

Ce lien expirera dans 7 jours.

Cordialement,
L'équipe Art Cartel
'''
        
        # Configuration détaillée pour le débogage
        mail_config = current_app.config
        logging.info(f"Configuration email : {mail_config}")
        
        try:
            # Utiliser l'extension mail de l'application courante
            current_app.extensions['mail'].send(msg)
            logging.info(f"Email d'invitation envoyé à {email}")
            logging.info(f"URL d'invitation : {invitation_url}")
        except Exception as mail_error:
            # Tentative d'envoi direct via smtplib pour plus de détails
            logging.error(f"Erreur via Flask-Mail : {mail_error}")
            
            try:
                with smtplib.SMTP_SSL(mail_config['MAIL_SERVER'], mail_config['MAIL_PORT']) as server:
                    server.login(mail_config['MAIL_USERNAME'], mail_config['MAIL_PASSWORD'])
                    server.sendmail(
                        mail_config['MAIL_DEFAULT_SENDER'], 
                        [email], 
                        msg.body
                    )
                logging.info(f"Email envoyé avec succès via SMTP direct")
            except Exception as smtp_error:
                logging.error(f"Erreur lors de l'envoi SMTP direct : {smtp_error}")
                raise
    
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi de l'email d'invitation : {str(e)}")
        raise
