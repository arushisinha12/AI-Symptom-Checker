"""
Simple AI Chatbot for Medical Symptom Assistance
Uses pattern matching and knowledge base for responses
"""

import random
import re
import difflib
from knowledge import symptom_to_diseases, disease_to_symptoms, disease_info, disease_treatments

class MedicalChatbot:
    def __init__(self):
        # Memory to store the current thread of conversation
        # 'last_disease': The specific disease currently being discussed
        # 'mentioned_symptoms': List of symptoms user has typed in chat
        self.context = {"mentioned_symptoms": [], "last_disease": None, "last_diagnosis": None, "severity": None}
        
        # Mapping slang terms to the official dataset symptom names
        self.synonyms = {
            "belly ache": "pain abdominal", "stomach ache": "pain abdominal", "stomach pain": "pain abdominal",
            "head hurts": "headache", "puking": "vomiting", "throw up": "vomiting", 
            "high temp": "fever", "hot": "fever", "shaking": "tremor", "cant sleep": "sleeplessness",
            "hard to breathe": "shortness of breath", "cant breathe": "shortness of breath",
            "runny nose": "snuffle", "stuffy nose": "snuffle"
        }

        # Mapping common disease names to official dataset names
        self.disease_aliases = {
            "flu": "Influenza",
            "cold": "Common Cold",
            "piles": "Dimorphic hemmorhoids(piles)",
            "heart attack": "Heart attack",
        }

    def get_response(self, text):
        """Main routing function: Decides which logic to use based on user input"""
        text = text.lower().strip()

        # 1. Direct Disease Info (Priority)
        # Allows user to ask "What is Malaria?" at any time, overriding context.
        match = re.search(r"(?:what is|tell me about|info(?:rmation)? (?:on|about)) (.+)", text)
        if match:
            q = match.group(1).strip()
            # Ensure they aren't referring to 'it' (the current context disease)
            curr = (self.context.get("last_disease") or "").lower()
            if q not in ["it", "this", "the condition"] and q != curr:
                return self.get_disease_info(q)

        # 2. Context-Aware Commands
        # Only runs if we have a diagnosis from the main app or previous chat analysis
        if self.context["last_diagnosis"]:
            patterns = [
                # Regex for Severity questions -> calls get_severity_advice
                (r"serious|severe|bad|dangerous|worry", self.get_severity_advice),
                # Regex for Treatment questions -> calls get_treatment_advice
                (r"treat|cure|remedy|medicine", self.get_treatment_advice),
                # Regex for Action questions -> calls get_action_advice
                (r"what (?:should|do) i do|next steps|help", self.get_action_advice),
                # Regex for Explanation questions -> calls explain_diagnosis
                (r"what is|explain|more info", self.explain_diagnosis)
            ]
            for p, func in patterns:
                # 'p' is the regex string (e.g., "treat|cure")
                # 'func' is the actual function object (e.g., self.get_treatment_advice)
                
                # re.search checks if the pattern 'p' exists anywhere in 'text'
                if re.search(p, text): 
                    # If match found, execute the stored function immediately and return its result
                    return func()

        # 3. General Conversation (Social)
        if re.search(r"hi|hello|hey", text): return "Hello! I'm your medical assistant. How can I help?"
        if re.search(r"bye|quit", text): return "Take care! Consult a doctor for serious concerns."
        if re.search(r"thank", text): return "You're welcome! Stay healthy."
        
        # 4. Analyze Symptoms from text
        # If no other command matched, check if the user is describing symptoms
        symptoms = self.extract_symptoms(text)
        if symptoms: return self.analyze_symptoms(symptoms)

        return "I can help explain results, suggest treatments, or analyze symptoms. Try 'I have a headache' or 'What is Flu?'"

    def extract_symptoms(self, text):
        """Finds symptom keywords in text, using synonyms and fuzzy matching"""
        found = set()
        # Replace slang with official terms first
        for slang, medical in self.synonyms.items(): 
            text = text.replace(slang, medical)
        
        # Scan for every known symptom
        for s in symptom_to_diseases:
            readable = s.replace("_", " ")
            # Check exact match
            if readable in text or s in text: 
                found.add(s)
            # Check fuzzy match (handle typos like 'hedache')
            for word in text.split():
                if difflib.get_close_matches(word, [readable], n=1, cutoff=0.85):
                    found.add(s)
        
        # Update memory with found symptoms            
        if found: 
            self.context["mentioned_symptoms"] = list(set(self.context["mentioned_symptoms"]) | found)
        return list(found)

    def analyze_symptoms(self, symptoms):
        """Mini-diagnosis engine for chat-based extraction"""
        matches = {}
        # Count "votes" for each disease based on symptoms
        for s in symptoms:
            for d in symptom_to_diseases.get(s, []): 
                matches[d] = matches.get(d, 0) + 1
        
        if not matches: return "I couldn't identify a condition. Please describe more symptoms."

        # Calculate scores: (matched_symptoms / total_symptoms_for_disease) * 100
        scores = {d: round((c / len(disease_to_symptoms[d])) * 100, 1) for d, c in matches.items() if disease_to_symptoms.get(d)}
        top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Update context so follow-up questions work
        self.context["last_disease"] = top[0][0]
        self.context["last_diagnosis"] = top 
        
        res = f"Based on {', '.join([s.replace('_',' ') for s in symptoms])}:\n\n"
        for d, sc in top: 
            res += f"• {d} ({sc}%)\n  {disease_info.get(d, '')[:150]}...\n\n"
        return res + "⚠️ Consult a healthcare professional."

    def get_disease_info(self, query):
        """Lookup specific disease description in database"""
        # 1. Check aliases first
        clean_query = query.lower().strip()
        target_disease = self.disease_aliases.get(clean_query)
        
        if target_disease:
             # If alias matched, verify we have info for it
             if target_disease in disease_info:
                 return self._format_disease_response(target_disease)

        # 2. Search in database with stricter matching
        for d in disease_info.keys():
            # Check for exact case-insensitive match
            if d.lower() == clean_query:
                return self._format_disease_response(d)
            
            # Check for word boundary match (so "flu" matches "Bird Flu" but NOT "Reflux")
            # re.escape(clean_query) ensures special regex chars in query don't break things
            pattern = r'\b' + re.escape(clean_query) + r'\b'
            if re.search(pattern, d.lower()):
                 return self._format_disease_response(d)

        return f"I don't have information on '{query}'."

    def _format_disease_response(self, disease_name):
        """Helper to format the output string"""
        desc = disease_info.get(disease_name, "No description available.")
        symptoms = ", ".join([x.replace("_", " ") for x in disease_to_symptoms.get(disease_name, [])[:5]])
        return f"**{disease_name}**\n{desc}\n\nCommon Symptoms: {symptoms}..."

    def set_diagnosis_context(self, diseases, symptoms, severity):
        """Called by main App to sync results to Chatbot"""
        self.context.update({"last_diagnosis": diseases, "symptoms": symptoms, "severity": severity, "last_disease": diseases[0][0] if diseases else None})

    def get_severity_advice(self):
        """Returns advice string based on severity level"""
        sev, d = self.context.get("severity", ""), self.context.get("last_disease", "this condition")
        if "Severe" in sev: return f"⚠️ URGE: Seek medical attention for {d} immediately."
        if "Moderate" in sev: return f"Caution: {d} may require a doctor. Monitor closely."
        return f"{d} appears mild. Rest and hydration recommended."

    def get_treatment_advice(self):
        """Returns treatment steps from usage of disease_precaution.csv"""
        d = self.context.get("last_disease")
        treats = disease_treatments.get(d, {}).get("precautions", ["Rest", "Hydrate", "Consult doctor"])
        return f"💊 Treatment for {d}:\n" + "\n".join([f"• {t}" for t in treats])

    def get_action_advice(self):
        """Wrapper to provide general action advice"""
        return f"For {self.context.get('last_disease')}: \n" + self.get_treatment_advice()

    def explain_diagnosis(self):
        """Explains why a specific diagnosis was given"""
        d = self.context.get("last_disease")
        score = self.context["last_diagnosis"][0][1]
        return f"Diagnosis: {d} ({score}% match)\n{disease_info.get(d, 'No details.')}\n\nSymptoms: {', '.join([x.replace('_',' ') for x in disease_to_symptoms.get(d, [])])}"
