"""
邮件工具：封装邮件发送功能
"""
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime

from config import settings
from .base_tool import BaseTool


class EmailTool(BaseTool):
    """邮件工具：封装邮件发送功能"""
    
    def __init__(self):
        super().__init__()
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_use_tls = settings.SMTP_USE_TLS
        self.sender_email = settings.SENDER_EMAIL
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        template: str = None
    ) -> bool:
        """
        发送邮件
        
        Args:
            to: 收件人邮箱
            subject: 邮件主题
            body: 邮件正文
            template: 模板名称（可选）
        
        Returns:
            是否成功
        """
        logger.info(f"邮件工具发送邮件: to={to}, subject={subject[:50]}...")
        
        if not self.smtp_host or not self.smtp_user or not self.smtp_password:
            logger.warning("邮件配置未完成，跳过发送")
            return False
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # 构建邮件
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to
            msg['Subject'] = subject
            
            # 添加正文
            msg.attach(MIMEText(body, 'html' if '<html>' in body else 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"邮件发送成功: to={to}")
            return True
        
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False
    
    def send_notification(self, notification_type: str, data: Dict[str, Any]) -> bool:
        """
        发送通知
        
        Args:
            notification_type: 通知类型
            data: 通知数据
        
        Returns:
            是否成功
        """
        logger.info(f"邮件工具发送通知: type={notification_type}")
        
        templates = {
            'news_digest': {
                'subject': '每日新闻摘要',
                'body_template': """<html>
<head><title>每日新闻摘要</title></head>
<body>
<h1>每日新闻摘要</h1>
<p>尊敬的用户，以下是今日新闻摘要：</p>
<ul>
{% for news in news_list %}
<li><a href="{{ news.url }}">{{ news.title }}</a></li>
{% endfor %}
</ul>
<p>发送时间：{{ timestamp }}</p>
</body>
</html>"""
            },
            'system_alert': {
                'subject': '系统告警',
                'body_template': """<html>
<head><title>系统告警</title></head>
<body>
<h1>系统告警</h1>
<p>告警类型：{{ alert_type }}</p>
<p>告警信息：{{ message }}</p>
<p>时间：{{ timestamp }}</p>
</body>
</html>"""
            },
            'user_notification': {
                'subject': '用户通知',
                'body_template': """<html>
<head><title>用户通知</title></head>
<body>
<h1>用户通知</h1>
<p>{{ message }}</p>
<p>时间：{{ timestamp }}</p>
</body>
</html>"""
            }
        }
        
        template = templates.get(notification_type)
        if not template:
            logger.error(f"不支持的通知类型: {notification_type}")
            return False
        
        # 渲染模板
        try:
            from jinja2 import Template
            
            body = Template(template['body_template']).render(
                **data,
                timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            return self.send_email(
                to=data.get('to', ''),
                subject=template['subject'],
                body=body
            )
        
        except ImportError:
            # 降级为简单文本
            body = f"{template['subject']}\n\n{data.get('message', '')}"
            return self.send_email(
                to=data.get('to', ''),
                subject=template['subject'],
                body=body
            )
        except Exception as e:
            logger.error(f"发送通知失败: {e}")
            return False
    
    def send_report(self, to: str, report_data: Dict[str, Any], format: str = 'html') -> bool:
        """
        发送报告
        
        Args:
            to: 收件人邮箱
            report_data: 报告数据
            format: 报告格式 (html/text)
        
        Returns:
            是否成功
        """
        logger.info(f"邮件工具发送报告: to={to}, format={format}")
        
        subject = report_data.get('title', '报告')
        
        if format == 'html':
            body = f"""<html>
<head><title>{subject}</title></head>
<body>
<h1>{subject}</h1>
<p>{report_data.get('summary', '')}</p>
<h2>详细数据</h2>
<pre>{report_data.get('details', '')}</pre>
<p>生成时间：{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</p>
</body>
</html>"""
        else:
            body = f"{subject}\n\n{report_data.get('summary', '')}\n\n详细数据:\n{report_data.get('details', '')}"
        
        return self.send_email(to=to, subject=subject, body=body)
    
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        action = kwargs.get('action', 'send_email')
        
        if action == 'send_email':
            return self.send_email(
                to=kwargs['to'],
                subject=kwargs['subject'],
                body=kwargs['body'],
                template=kwargs.get('template')
            )
        elif action == 'send_notification':
            return self.send_notification(
                notification_type=kwargs['type'],
                data=kwargs['data']
            )
        elif action == 'send_report':
            return self.send_report(
                to=kwargs['to'],
                report_data=kwargs['report_data'],
                format=kwargs.get('format', 'html')
            )
        
        return {"error": f"不支持的操作: {action}"}
