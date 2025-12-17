"""
Simple AI Chatbot for Medical Symptom Assistance
Uses pattern matching and knowledge base for responses
"""

import random
import re
from knowledge import symptom_to_diseases, disease_to_symptoms, disease_info

class MedicalChatbot:
    def __init__(self):
        self.context = {
            "mentioned_symptoms": [],
            "last_disease": None,
            "severity": None 
        }
        
        
        # Greeting patterns
        self.greetings = {
            "patterns": r"hi|hello|hey|greetings|good morning|good afternoon|good evening",
            "responses": [
                "Hello! I'm your medical assistant. How can I help you today?",
                "Hi there! Tell me about your symptoms and I'll try to help.",
                "Hello! I'm here to assist with symptom analysis. What's bothering you?"
            ]
        }
        
        # Symptom inquiry patterns
        self.symptom_patterns = {
            "feeling": r"i (?:feel|have|am feeling|experiencing) (.+)",
            "symptom": r"(?:my|i have) (.+) (?:hurts?|aches?|is (?:painful|sore))",
            "general": r"(?:what (?:could|might) (?:cause|be causing)) (.+)"
        }
        
    def get_response(self, user_input):
        """Generate a response based on user input"""
        user_input = user_input.lower().strip()
        
        # Check for greetings
        if re.search(self.greetings["patterns"], user_input):
            return random.choice(self.greetings["responses"])
        
        # Check for goodbye
        if re.search(r"bye|goodbye|see you|exit|quit", user_input):
            return "Take care! Remember to consult a healthcare professional for serious concerns. Goodbye!"
        
        # Check for thanks
        if re.search(r"thank|thanks|appreciate", user_input):
            return "You're welcome! Feel free to ask if you have more questions. Stay healthy!"
        
        # Check for help request
        if re.search(r"help|how (?:do|can) (?:i|you)|what can you do", user_input):
            return ("I can help you with:\n"
                   "• Explaining your diagnosis results\n"
                   "• Answering questions about conditions\n"
                   "• Providing general health advice\n"
                   "• Clarifying symptoms and severity\n\n"
                   "Just ask me anything about your results!")
        
        # Context-aware responses about diagnosis
        if self.context.get("last_diagnosis"):
            # Questions about severity
            if re.search(r"serious|severe|bad|dangerous|worry|worried|concer|die", user_input):
                return self.get_severity_advice()
            
            # Questions about treatment
            if re.search(r"treatment|treat|cure|remedy|remedies|medicine|medication|how to treat|get better|heal|solve", user_input):
                return self.get_treatment_advice()
            
            # Questions about what to do
            if re.search(r"what (?:should|do) i do|next steps|help", user_input):
                return self.get_action_advice()
            
            # Questions about specific disease
            if re.search(r"what is|tell me (?:about|more)|explain", user_input):
                return self.explain_diagnosis()
        
        # Extract symptoms from input
        symptoms = self.extract_symptoms(user_input)
        
        if symptoms:
            return self.analyze_symptoms(symptoms)
        
        # Check for disease information request
        disease_match = re.search(r"(?:what is|tell me about|info(?:rmation)? (?:on|about)) (.+)", user_input)
        if disease_match:
            disease_query = disease_match.group(1).strip()
            return self.get_disease_info(disease_query)
        
        # Default response
        if self.context.get("last_diagnosis"):
            return ("I'm here to help explain your diagnosis. You can ask:\n"
                   "• 'Is this serious?'\n"
                   "• 'What should I do?'\n"
                   "• 'Tell me more about [condition]'\n"
                   "• 'What are the symptoms?'")
        else:
            return ("Please use the symptom checker on the left to get a diagnosis first.\n"
                   "Then I can help answer questions about your results!")
    
    def extract_symptoms(self, text):
        """Extract known symptoms from user input"""
        found_symptoms = []
        
        # Check each known symptom
        for symptom in symptom_to_diseases.keys():
            # Create pattern for symptom (handle underscores)
            symptom_readable = symptom.replace("_", " ")
            
            if symptom_readable in text or symptom in text:
                found_symptoms.append(symptom)
                self.context["mentioned_symptoms"].append(symptom)
        
        return found_symptoms
    
    def analyze_symptoms(self, symptoms):
        """Analyze symptoms and provide diagnosis"""
        if not symptoms:
            return "I didn't catch any specific symptoms. Could you describe what you're experiencing?"
        
        # Find matching diseases
        matches = {}
        for symptom in symptoms:
            if symptom in symptom_to_diseases:
                for disease in symptom_to_diseases[symptom]:
                    matches[disease] = matches.get(disease, 0) + 1
        
        if not matches:
            return "I couldn't find any conditions matching those symptoms. Please try describing them differently."
        
        # Calculate certainty scores
        scores = {}
        for disease, match_count in matches.items():
            total = len(disease_to_symptoms.get(disease, []))
            if total > 0:
                score = (match_count / total) * 100
                scores[disease] = round(score, 1)
        
        # Get top 3
        top_matches = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Build response
        response = f"Based on the symptoms you mentioned ({', '.join([s.replace('_', ' ') for s in symptoms])}), here are the possible conditions:\n\n"
        
        for disease, score in top_matches:
            desc = disease_info.get(disease, "No description available.")
            response += f"• {disease} ({score}% match)\n  {desc}\n\n"
        
        response += "\n⚠️ This is not a diagnosis. Please consult a healthcare professional for proper medical advice."
        
        self.context["last_disease"] = top_matches[0][0] if top_matches else None
        
        return response
    
    def get_disease_info(self, disease_query):
        """Get information about a specific disease"""
        # Try to find matching disease
        for disease in disease_info.keys():
            if disease.lower() in disease_query or disease_query in disease.lower():
                info = disease_info[disease]
                symptoms = disease_to_symptoms.get(disease, [])
                symptom_list = ", ".join([s.replace("_", " ") for s in symptoms])
                
                return (f"**{disease}**\n\n"
                       f"{info}\n\n"
                       f"Common symptoms: {symptom_list}\n\n"
                       f"Remember to consult a doctor for proper diagnosis.")
        return f"I don't have information about '{disease_query}'. Try asking about common conditions like flu, cold, or migraine."
    
    
    def set_diagnosis_context(self, diseases, symptoms, severity):
        """Set the current diagnosis context for follow-up questions"""
        self.context["last_diagnosis"] = diseases
        self.context["symptoms"] = symptoms
        self.context["severity"] = severity
    
    def get_severity_advice(self):
        """Provide advice about severity"""
        severity = self.context.get("severity", "")
        diseases = self.context.get("last_diagnosis", [])
        
        if not diseases:
            return "I don't have diagnosis information yet. Please run the analysis first."
        
        top_disease = diseases[0][0] if diseases else "the condition"
        
        if "Severe" in severity:
            return (f"Based on your symptoms, this appears to be a {severity.lower()} situation.\n\n"
                   f"⚠️ IMPORTANT: You should seek medical attention promptly. "
                   f"{top_disease} can be serious and requires professional evaluation.\n\n"
                   f"Consider visiting a doctor or urgent care clinic soon.")
        elif "Moderate" in severity:
            return (f"Your symptoms suggest a {severity.lower()} condition.\n\n"
                   f"I recommend scheduling an appointment with your doctor to discuss {top_disease}. "
                   f"While not an emergency, it's best to get professional medical advice.\n\n"
                   f"Monitor your symptoms and seek immediate care if they worsen.")
        else:
            return (f"Your symptoms appear to be {severity.lower()}\n\n"
                   f"Home care and rest may help with {top_disease}. However, if symptoms persist "
                   f"for more than a few days or worsen, consult a healthcare provider.\n\n"
                   f"Stay hydrated and get plenty of rest.")
    
    def get_action_advice(self):
        """Provide actionable advice"""
        diseases = self.context.get("last_diagnosis", [])
        severity = self.context.get("severity", "")
        
        if not diseases:
            return "Please run the symptom analysis first so I can provide specific advice."
        
        top_disease, score = diseases[0]
        
        advice = f"For {top_disease}, here's what you can do:\n\n"
        
        # General advice based on disease type
        if "Flu" in top_disease or "Cold" in top_disease:
            advice += ("• Rest and stay hydrated\n"
                      "• Take over-the-counter pain relievers if needed\n"
                      "• Use a humidifier\n"
                      "• Gargle with salt water for sore throat\n")
        elif "Fever" in str(self.context.get("symptoms", [])):
            advice += ("• Monitor your temperature regularly\n"
                      "• Stay hydrated with water and clear fluids\n"
                      "• Rest in a cool environment\n"
                      "• Take fever-reducing medication if needed\n")
        else:
            advice += ("• Rest and avoid strenuous activity\n"
                      "• Stay well-hydrated\n"
                      "• Monitor your symptoms\n"
                      "• Keep track of any changes\n")
        
        if "Severe" in severity or score > 70:
            advice += "\n⚠️ Given the severity, please consult a doctor soon."
        else:
            advice += "\n💡 If symptoms worsen or persist, consult a healthcare professional."
        
        return advice
    
    
    def get_treatment_advice(self):
        """Provide detailed treatment recommendations"""
        from knowledge import disease_treatments
        
        diseases = self.context.get("last_diagnosis", [])
        
        if not diseases:
            return "Please run the symptom analysis first so I can provide treatment advice."
        
        top_disease, score = diseases[0]
        
        # Check if we have treatment data for this disease
        if top_disease not in disease_treatments:
            return (f"💊 Treatment for {top_disease}:\n\n"
                   "**General Treatment:**\n"
                   "• Rest and adequate sleep\n"
                   "• Stay well-hydrated\n"
                   "• Over-the-counter pain relievers if needed\n"
                   "• Monitor symptoms closely\n\n"
                   "**When to See a Doctor:**\n"
                   "• Symptoms worsen or don't improve\n"
                   "• High fever (over 103°F)\n"
                   "• Severe pain\n"
                   "• Difficulty breathing\n\n"
                   "For specific treatment, please consult a healthcare professional.\n\n"
                   "⚠️ **Disclaimer:** This is general information. Always consult a healthcare provider.")
        
        # Get treatment data
        treatment_data = disease_treatments[top_disease]
        treatment = f"💊 Treatment for {top_disease}:\n\n"
        
        # Build treatment response from data
        for category, items in treatment_data.items():
            # Format category name
            category_name = category.replace("_", " ").title()
            
            if isinstance(items, list):
                treatment += f"**{category_name}:**\n"
                for item in items:
                    treatment += f"• {item}\n"
                treatment += "\n"
            else:
                # Single string value (like "important" or "duration")
                treatment += f"**{category_name}:** {items}\n\n"
        
        treatment += "⚠️ **Disclaimer:** This is general information. Always consult a healthcare provider for personalized medical advice and treatment."
        
        return treatment
    
    
    def explain_diagnosis(self):
        """Explain the top diagnosis in detail"""
        diseases = self.context.get("last_diagnosis", [])
        
        
        top_disease, score = diseases[0]
        
        # Get detailed info
        desc = disease_info.get(top_disease, "No description available.")
        symptoms = disease_to_symptoms.get(top_disease, [])
        symptom_list = ", ".join([s.replace("_", " ") for s in symptoms])
        
        explanation = f"📋 About {top_disease}:\n\n"
        explanation += f"{desc}\n\n"
        explanation += f"Common symptoms include: {symptom_list}\n\n"
        explanation += f"Your match: {score}%\n\n"
        
        if score > 70:
            explanation += "This is a strong match based on your symptoms."
        elif score > 40:
            explanation += "This is a moderate match. Other conditions are also possible."
        else:
            explanation += "This is a possible match, but other conditions should also be considered."
        
        return explanation
    
    def reset_context(self):
        """Reset conversation context"""
        self.context = {
            "last_diagnosis": None,
            "symptoms": [],
            "severity": None
        }
