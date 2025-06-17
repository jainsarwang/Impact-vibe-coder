import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Union
import jinja2

class Mailer:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True
    ):
        """
        Initialize the mailer with SMTP server details.
        
        Args:
            host (str): SMTP server host
            port (int): SMTP server port
            username (str): SMTP username/email
            password (str): SMTP password
            use_tls (bool): Whether to use TLS for secure connection
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.template_env = jinja2.Environment()

    def _render_template(self, template_content: str, template_data: Optional[dict] = None) -> str:
        """
        Render a template string with the provided data.
        
        Args:
            template_content (str): Raw template content (HTML or text)
            template_data (Optional[dict]): Data to render in the template
            
        Returns:
            str: Rendered template content
        """
        template = self.template_env.from_string(template_content)
        return template.render(**(template_data or {}))

    def send_mail(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        template_content: Optional[str] = None,
        template_data: Optional[dict] = None,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email using either a template or direct content.
        
        Args:
            to_emails (Union[str, List[str]]): Recipient email(s)
            subject (str): Email subject
            template_content (Optional[str]): Raw template content (HTML or text)
            template_data (Optional[dict]): Data to render in the template
            html_content (Optional[str]): Direct HTML content
            text_content (Optional[str]): Direct text content
            from_email (Optional[str]): Sender email (defaults to username)
            cc (Optional[List[str]]): CC recipients
            bcc (Optional[List[str]]): BCC recipients
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Convert single email to list
            if isinstance(to_emails, str):
                to_emails = [to_emails]

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email or self.username
            msg['To'] = ', '.join(to_emails)
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)

            # Prepare content
            if template_content:
                rendered_content = self._render_template(template_content, template_data)
                
                # Try to detect if template is HTML
                if '<html' in rendered_content.lower():
                    html_content = rendered_content
                else:
                    text_content = rendered_content

            # Add content parts
            if html_content:
                msg.attach(MIMEText(html_content, 'html'))
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))

            # Connect to SMTP server
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                
                # Send email
                all_recipients = to_emails + (cc or []) + (bcc or [])
                server.sendmail(
                    msg['From'],
                    all_recipients,
                    msg.as_string()
                )
                
            return True

        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False



if __name__ == "__main__":
    # Example usage
    mailer = Mailer(
        host="smtp.gmail.com",
        port=587,
        username="your-email@gmail.com", 
        password="your-app-specific-password",
        use_tls=True
    )

    # Example 1: Send simple text email
    mailer.send_mail(
        to_emails="recipient@example.com",
        subject="Test Email",
        text_content="This is a test email sent from Python."
    )

    # Example 2: Send HTML email
    html_content = """
    <html>
        <body>
            <h1>Hello!</h1>
            <p>This is a test HTML email.</p>
        </body>
    </html>
    """
    mailer.send_mail(
        to_emails=["recipient1@example.com", "recipient2@example.com"],
        subject="HTML Test Email",
        html_content=html_content,
        cc=["cc@example.com"],
        bcc=["bcc@example.com"]
    )

    # Example 3: Send email using template
    template_content = """
    Hello {{ name }},
    
    Thank you for {{ action }}.
    
    Best regards,
    {{ sender }}
    """
    template_data = {
        "name": "John",
        "action": "subscribing to our newsletter",
        "sender": "The Team"
    }
    
    mailer.send_mail(
        to_emails="recipient@example.com",
        subject="Template Test",
        template_content=template_content,
        template_data=template_data
    )

