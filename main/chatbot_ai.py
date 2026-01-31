import json
import re
from datetime import datetime
from .models import ChatbotSession, ServiceInquiry

class ChatbotAI:
    def __init__(self):
        self.responses = self.load_responses()
        self.services = {
            'web development': 'it-consulting',
            'software development': 'software-development',
            'mobile app': 'software-development',
            'digital marketing': 'digital-marketing',
            'seo': 'digital-marketing',
            'social media': 'digital-marketing',
            'cloud': 'cloud-solutions',
            'aws': 'cloud-solutions',
            'azure': 'cloud-solutions',
            'security': 'cybersecurity',
            'cybersecurity': 'cybersecurity',
            'data analytics': 'data-analytics',
            'ai': 'data-analytics',
            'machine learning': 'data-analytics',
            'consulting': 'it-consulting'
        }
    
    def load_responses(self):
        return {
            'greeting': [
                "Hello! I'm Sharsh, your AI assistant at BunShai TECHNOHUB. How can I help you today?",
                "Hi there! I'm Sharsh. How can I assist you with BunShai TECHNOHUB services?",
                "Welcome! I'm Sharsh, ready to help you with all your technology needs."
            ],
            'services': {
                'intro': "We offer a wide range of IT services including:\n\n",
                'list': """• **IT Consulting** - Technology strategy and digital transformation\n• **Software Development** - Custom web and mobile applications\n• **Digital Marketing** - SEO, social media, and online advertising\n• **Cloud Solutions** - AWS, Azure, and Google Cloud services\n• **Cybersecurity** - Security audits and protection solutions\n• **Data Analytics** - Business intelligence and AI/ML solutions\n\nWhich service are you interested in?""",
                'follow_up': "Would you like me to connect you with our {service} specialist?"
            },
            'pricing': {
                'general': "Our pricing depends on project requirements. We offer:\n• Hourly rates from $25-$75\n• Project-based pricing\n• Monthly retainers\n• Custom enterprise solutions\n\nWould you like a free consultation?",
                'budget': "What's your budget range for this project?"
            },
            'contact': {
                'info': """You can reach us through:\n📧 Email: team.bunshailogicloop@gmail.com\n📞 Phone: +91 8091401208\n💬 WhatsApp: +91 8091401208\n📍 Address: Global Remote Operations\n\nWould you like me to connect you directly?""",
                'hours': "We're available 24/7 for urgent matters. Regular business hours: Mon-Fri, 9AM-6PM IST."
            },
            'hours': "We operate 24/7 for critical support. Regular business hours are Monday to Friday, 9AM to 6PM Indian Standard Time.",
            'team': "Our team consists of 50+ experienced professionals including software developers, designers, cloud architects, security experts, and data scientists.",
            'portfolio': "We've delivered 50+ successful projects across various industries. Check our website for case studies and client testimonials.",
            'default': "I'm not sure I understand. Could you please rephrase? Or you can ask about:\n• Our services\n• Pricing\n• Contact information\n• Portfolio\n• Team"
        }
    
    def get_response(self, message, session):
        """Get appropriate chatbot response based on user message"""
        message_lower = message.lower().strip()
        
        # Check for greetings
        if self.is_greeting(message_lower):
            return self.get_random_response('greeting')
        
        # Check for services inquiry
        service_match = self.check_service_inquiry(message_lower)
        if service_match:
            return self.handle_service_inquiry(service_match, session)
        
        # Check for pricing
        if any(word in message_lower for word in ['price', 'cost', 'rate', 'budget', 'how much']):
            return self.handle_pricing_inquiry(message_lower)
        
        # Check for contact information
        if any(word in message_lower for word in ['contact', 'email', 'phone', 'call', 'reach']):
            return self.responses['contact']['info']
        
        # Check for business hours
        if any(word in message_lower for word in ['hour', 'time', 'available', 'open', 'close']):
            return self.responses['hours']
        
        # Check for team information
        if any(word in message_lower for word in ['team', 'people', 'staff', 'employee']):
            return self.responses['team']
        
        # Check for portfolio
        if any(word in message_lower for word in ['portfolio', 'project', 'work', 'case study', 'client']):
            return self.responses['portfolio']
        
        # Default response
        return self.responses['default']
    
    def is_greeting(self, message):
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in message for greeting in greetings)
    
    def check_service_inquiry(self, message):
        """Check if user is asking about specific services"""
        for service_key in self.services.keys():
            if service_key in message:
                return service_key
        return None
    
    def handle_service_inquiry(self, service, session):
        """Handle service-specific inquiries"""
        service_name = service.title()
        response = f"We offer comprehensive {service_name} services. "
        
        # Add service-specific details
        if service in ['web development', 'software development', 'mobile app']:
            response += "Our development team specializes in:\n• Custom web applications\n• Mobile apps (iOS/Android)\n• E-commerce solutions\n• API development\n• Progressive Web Apps"
        elif service in ['digital marketing', 'seo', 'social media']:
            response += "Our marketing services include:\n• SEO optimization\n• Social media management\n• PPC advertising\n• Content marketing\n• Brand strategy"
        elif service in ['cloud', 'aws', 'azure']:
            response += "Our cloud expertise covers:\n• Cloud migration\n• Infrastructure setup\n• DevOps automation\n• Cost optimization\n• Security compliance"
        elif service in ['security', 'cybersecurity']:
            response += "Our security services provide:\n• Vulnerability assessments\n• Penetration testing\n• Security monitoring\n• Incident response\n• Compliance audits"
        elif service in ['data analytics', 'ai', 'machine learning']:
            response += "Our data services include:\n• Business intelligence\n• Predictive analytics\n• Machine learning models\n• Data visualization\n• Big data solutions"
        
        response += f"\n\nWould you like me to schedule a free consultation for {service_name}?"
        
        # Store service interest in session
        if session:
            session.service_interest = service
            session.save()
        
        return response
    
    def handle_pricing_inquiry(self, message):
        """Handle pricing-related inquiries"""
        if 'budget' in message:
            return self.responses['pricing']['budget']
        return self.responses['pricing']['general']
    
    def get_random_response(self, response_type):
        """Get random response from list"""
        responses = self.responses.get(response_type, [])
        if isinstance(responses, list) and responses:
            import random
            return random.choice(responses)
        return responses if isinstance(responses, str) else "I'm here to help!"

def get_chatbot_response(message, session):
    """Main function to get chatbot response"""
    chatbot = ChatbotAI()
    return chatbot.get_response(message, session)