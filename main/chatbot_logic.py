import json
import re
from datetime import datetime
from .models import ServiceInquiry, ContactMessage

class ChatbotEngine:
    def __init__(self, session):
        self.session = session
        self.knowledge_base = self.load_knowledge_base()
        
    def load_knowledge_base(self):
        """Load chatbot knowledge base"""
        return {
            'greetings': ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening'],
            'farewells': ['bye', 'goodbye', 'see you', 'talk to you later'],
            'services': {
                'web development': 'We offer custom web development services using latest technologies like React, Django, Node.js',
                'mobile app': 'We develop iOS and Android applications using React Native, Flutter, and native technologies',
                'ai solutions': 'We provide AI/ML solutions including chatbots, predictive analytics, and computer vision',
                'cloud services': 'We offer cloud migration, AWS/Azure/GCP setup, and cloud optimization services',
                'cybersecurity': 'We provide security audits, penetration testing, and security implementation',
                'consulting': 'We offer IT consulting, digital transformation, and technology strategy services'
            },
            'company_info': {
                'about': 'BunShai TECHNOHUB is an IT consulting and services company delivering cutting-edge solutions since 2025.',
                'contact': 'You can contact us at +91 8091700280 or email at info@bunshai.com',
                'location': 'We are a remote-first company serving clients worldwide',
                'team': 'We have a team of 50+ experts with deep experience across various technologies'
            },
            'pricing': 'Our pricing depends on project requirements. Would you like a custom quote?',
            'process': 'Our process includes Discovery, Design, Development, Testing, and Deployment phases.',
            'faq': {
                'timeline': 'Project timelines vary from 2 weeks to 6 months depending on complexity',
                'support': 'We provide 24/7 technical support for all our clients',
                'payment': 'We accept various payment methods including bank transfer, cards, and UPI'
            }
        }
    
    def get_response(self, user_message):
        """Get chatbot response based on user message"""
        user_message_lower = user_message.lower().strip()
        
        # Check for greetings
        if any(greet in user_message_lower for greet in self.knowledge_base['greetings']):
            return self.get_greeting_response()
        
        # Check for farewells
        if any(farewell in user_message_lower for farewell in self.knowledge_base['farewells']):
            return "Thank you for chatting with me! Have a great day. If you have more questions, I'm always here to help."
        
        # Check for service inquiries
        service_response = self.check_services(user_message_lower)
        if service_response:
            return service_response
        
        # Check for company info
        company_response = self.check_company_info(user_message_lower)
        if company_response:
            return company_response
        
        # Check for pricing
        if any(word in user_message_lower for word in ['price', 'cost', 'budget', 'how much']):
            return self.knowledge_base['pricing']
        
        # Check for process
        if any(word in user_message_lower for word in ['process', 'how it works', 'procedure', 'steps']):
            return self.knowledge_base['process']
        
        # Check for FAQ
        faq_response = self.check_faq(user_message_lower)
        if faq_response:
            return faq_response
        
        # Check for contact information
        if any(word in user_message_lower for word in ['contact', 'email', 'phone', 'number', 'call']):
            return "You can contact us at:\n📞 Phone: +91 8091700280\n📧 Email: info@bunshai.com\n💬 WhatsApp: +91 8091401208\nWe're available 24/7!"
        
        # Check for proposal request
        if any(word in user_message_lower for word in ['proposal', 'quote', 'estimate', 'project details']):
            return "I can help you get a proposal! Please provide:\n1. Your name\n2. Contact details\n3. Project requirements\nOr you can fill our proposal form for faster response."
        
        # Check if user wants to submit a form
        if any(word in user_message_lower for word in ['submit', 'form', 'application', 'apply']):
            return "I can guide you to the right form:\n📋 Contact Form: For general inquiries\n💼 Service Inquiry: For specific service requests\n📄 Proposal Request: For detailed project quotes\n👨‍💼 Career Application: For job opportunities\nWhich one would you like to fill?"
        
        # Default response
        return self.get_default_response(user_message_lower)
    
    def get_greeting_response(self):
        """Get personalized greeting response"""
        if self.session.name:
            return f"Hello {self.session.name}! I'm Sharsh, your AI assistant at BunShai TECHNOHUB. How can I help you today?"
        elif self.session.email:
            return f"Welcome back! I'm Sharsh, your AI assistant. How can I assist you today?"
        else:
            return "Hello! I'm Sharsh, your AI assistant at BunShai TECHNOHUB. How can I help you today?"
    
    def check_services(self, message):
        """Check if user is asking about services"""
        for service, description in self.knowledge_base['services'].items():
            if service in message:
                return f"{description}\n\nWould you like more details about this service or want to discuss a specific project?"
        
        if any(word in message for word in ['service', 'services', 'what do you offer', 'offerings']):
            services_list = "\n".join([f"• {service.title()}" for service in self.knowledge_base['services'].keys()])
            return f"We offer the following services:\n\n{services_list}\n\nWhich service are you interested in?"
        
        return None
    
    def check_company_info(self, message):
        """Check if user is asking about company info"""
        for keyword, response in self.knowledge_base['company_info'].items():
            if keyword in message:
                return response
        
        if any(word in message for word in ['who are you', 'about company', 'about bunshai']):
            return self.knowledge_base['company_info']['about']
        
        return None
    
    def check_faq(self, message):
        """Check if user is asking FAQ questions"""
        for question, answer in self.knowledge_base['faq'].items():
            if question in message:
                return answer
        
        if 'timeline' in message or 'how long' in message or 'duration' in message:
            return self.knowledge_base['faq']['timeline']
        
        if 'support' in message or 'help' in message:
            return self.knowledge_base['faq']['support']
        
        if 'payment' in message or 'pay' in message or 'methods' in message:
            return self.knowledge_base['faq']['payment']
        
        return None
    
    def get_default_response(self, message):
        """Get default response for unknown queries"""
        default_responses = [
            "I'm not sure I understand. Could you rephrase that?",
            "That's an interesting question! Could you provide more details?",
            "I'm here to help with information about our services, pricing, and company details. What would you like to know?",
            "I'm still learning! Could you ask me about our services, pricing, or contact information?",
            "I'd be happy to help! Could you tell me what specific information you're looking for?"
        ]
        
        # Use session context for personalized responses
        if self.session.email:
            # Check if this user has submitted forms before
            user_forms = ContactMessage.objects.filter(email=self.session.email).count()
            if user_forms > 0:
                return f"Welcome back! I see you've contacted us before. How can I assist you today?"
        
        # Return random default response
        import random
        return random.choice(default_responses)