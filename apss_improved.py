import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import difflib
from knowledge import symptom_to_diseases, disease_to_symptoms, disease_info
from chatbot import MedicalChatbot
import matplotlib.pyplot as plt   # << ADDED

class SymptomCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🩺 Advanced AI Symptom Checker")
        self.root.geometry("1400x750")
        self.root.configure(bg="#e9edf2")

        # Data
        self.all_symptoms = sorted(list(symptom_to_diseases.keys()))
        self.selected_symptoms = []
        self.chatbot = MedicalChatbot()

        # Styles
        self.setup_styles()

        # Layout
        self.create_header()
        self.create_main_layout()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Colors
        self.primary_color = "#4CAF50"
        self.secondary_color = "#1565C0"
        self.bg_color = "#e9edf2"
        self.card_bg = "#ffffff"
        self.text_color = "#333333"
        self.highlight_color = "#f5f5f5"

        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Helvetica", 11))
        style.configure("Header.TLabel", background=self.primary_color, foreground="white", font=("Helvetica", 22, "bold"))
        style.configure("TButton", font=("Helvetica", 11, "bold"), padding=6)
        style.map("TButton", background=[("active", "#45a049")])

    def create_header(self):
        header_frame = tk.Frame(self.root, bg=self.primary_color, pady=20)
        header_frame.pack(fill="x")

        title = tk.Label(header_frame, text="🩺 Advanced AI Symptom Checker", 
                         bg=self.primary_color, fg="white", font=("Helvetica", 22, "bold"))
        title.pack()

        subtitle = tk.Label(header_frame, text="Chat with AI assistant for follow-up questions", 
                            bg=self.primary_color, fg="#e0f2f1", font=("Helvetica", 12, "italic"))
        subtitle.pack(pady=(5,0))

    def create_main_layout(self):
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # LEFT SIDE - Symptom Checker (70% width)
        left_container = tk.Frame(main_frame, bg=self.bg_color)
        left_container.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.create_symptom_checker(left_container)

        # RIGHT SIDE - AI Chatbot (compact sidebar)
        right_container = tk.Frame(main_frame, bg=self.bg_color)
        right_container.pack(side="right", fill="both", expand=False, padx=(10, 0))
        right_container.pack_propagate(False)
        right_container.config(width=320, height=700)
        self.create_chatbot(right_container)

    def create_symptom_checker(self, parent):
        # Top Area: Symptoms Selection
        top_area = tk.Frame(parent, bg=self.bg_color)
        top_area.pack(fill="x", pady=(0, 15))

        # Left: Symptom List
        symptom_section = tk.Frame(top_area, bg=self.card_bg, relief="raised", bd=2)
        symptom_section.pack(side="left", fill="both", expand=True, padx=(0,10))
        symptom_section.configure(highlightbackground="#ccc", highlightthickness=1)

        tk.Label(symptom_section, text="1. Select Your Symptoms",
                 bg=self.highlight_color, fg="#333", font=("Helvetica", 13, "bold"), pady=8).pack(fill="x")

        content = tk.Frame(symptom_section, bg=self.card_bg, padx=15, pady=15)
        content.pack(fill="both", expand=True)

        tk.Label(content, text="Search Symptoms:", bg=self.card_bg, fg="#555").pack(anchor="w")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)
        search_entry = tk.Entry(content, textvariable=self.search_var, font=("Helvetica", 11), bd=1, relief="solid")
        search_entry.pack(fill="x", pady=(5,10))

        list_frame = tk.Frame(content, bg=self.card_bg)
        list_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.symptom_listbox = tk.Listbox(list_frame, font=("Helvetica", 11),
                                          selectmode="single", yscrollcommand=scrollbar.set,
                                          bd=0, relief="flat", bg="#f9f9f9", activestyle="dotbox")
        self.symptom_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.symptom_listbox.yview)

        self.symptom_listbox.bind('<<ListboxSelect>>', self.on_select_symptom)
        self.update_list()

        # Right: Selected Symptoms
        selected_section = tk.Frame(top_area, bg=self.card_bg, relief="raised", bd=2)
        selected_section.pack(side="right", fill="y", padx=(10,0))
        selected_section.configure(highlightbackground="#ccc", highlightthickness=1)

        tk.Label(selected_section, text="2. Your Selected Symptoms",
                 bg=self.highlight_color, fg="#333", font=("Helvetica", 13, "bold"), pady=8).pack(fill="x")

        selected_content = tk.Frame(selected_section, bg=self.card_bg, padx=15, pady=15)
        selected_content.pack(fill="both", expand=True)

        self.selected_listbox = tk.Listbox(selected_content, font=("Helvetica", 11), height=10,
                                           bg="#f9f9f9", fg="#333", bd=0, relief="flat")
        self.selected_listbox.pack(fill="both", expand=True, pady=(0,10))

        btn_frame = tk.Frame(selected_content, bg=self.card_bg)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Remove", command=self.remove_symptom).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side="right", padx=3)

        # Analyze Button
        self.diagnose_btn = tk.Label(parent, text="🔍 Analyze Symptoms", 
                                bg=self.secondary_color, fg="white", font=("Helvetica", 14, "bold"),
                                pady=10, cursor="hand2")
        self.diagnose_btn.pack(fill="x", pady=(0, 15))
        self.diagnose_btn.bind("<Button-1>", lambda e: self.diagnose())
        self.diagnose_btn.bind("<Enter>", lambda e: self.diagnose_btn.config(bg="#0D47A1"))
        self.diagnose_btn.bind("<Leave>", lambda e: self.diagnose_btn.config(bg=self.secondary_color))

        # -------------------- ADDED RECOVERY GRAPH BUTTON --------------------
        self.graph_btn = tk.Label(parent, text="📈 Show Recovery Graph",
                                  bg="#4CAF50", fg="white", font=("Helvetica", 14, "bold"),
                                  pady=10, cursor="hand2")
        self.graph_btn.pack(fill="x", pady=(0, 15))
        self.graph_btn.bind("<Button-1>", lambda e: self.show_recovery_graph())
        self.graph_btn.bind("<Enter>", lambda e: self.graph_btn.config(bg="#43A047"))
        self.graph_btn.bind("<Leave>", lambda e: self.graph_btn.config(bg="#4CAF50"))
        # ---------------------------------------------------------------------

        # Bottom: Results
        results_section = tk.Frame(parent, bg=self.card_bg, relief="raised", bd=2)
        results_section.pack(fill="both", expand=True)
        results_section.configure(highlightbackground="#ccc", highlightthickness=1)

        tk.Label(results_section, text="3. Analysis Results", bg=self.highlight_color, fg="#333",
                 font=("Helvetica", 13, "bold"), pady=8).pack(fill="x")

        results_content = tk.Frame(results_section, bg=self.card_bg, padx=15, pady=15)
        results_content.pack(fill="both", expand=True)

        self.results_text = tk.Text(results_content, font=("Helvetica", 11), wrap="word", 
                                   bg="#f9f9f9", fg="#333333", state="disabled", height=8, bd=0, relief="flat")
        self.results_text.pack(fill="both", expand=True)

    # ---------------- Chatbot ----------------
    def create_chatbot(self, parent):
        chat_container = tk.Frame(parent, bg=self.card_bg, relief="raised", bd=2)
        chat_container.pack(fill="both", expand=True)
        chat_container.configure(highlightbackground="#ccc", highlightthickness=1)

        tk.Label(chat_container, text="💬 AI Assistant", bg=self.highlight_color, fg="#333",
                 font=("Helvetica", 13, "bold"), pady=8).pack(fill="x")

        chat_content = tk.Frame(chat_container, bg=self.card_bg, padx=15, pady=15)
        chat_content.pack(fill="both", expand=True)

        tk.Label(chat_content, text="Ask follow-up questions", bg=self.card_bg, fg="#757575", font=("Helvetica", 9)).pack(anchor="w", pady=(0,5))

        self.chat_display = scrolledtext.ScrolledText(chat_content, font=("Helvetica", 10), 
                                                      wrap="word", bg="#f9f9f9", fg="#333333",
                                                      state="disabled", height=20, bd=0, relief="flat")
        self.chat_display.pack(fill="both", expand=True, pady=(0,10))
        self.chat_display.tag_config("user", foreground="#1565C0", font=("Helvetica", 10, "bold"))
        self.chat_display.tag_config("bot", foreground="#2e7d32", font=("Helvetica", 10, "bold"))

        input_frame = tk.Frame(chat_content, bg=self.card_bg)
        input_frame.pack(fill="x")

        self.chat_input = tk.Entry(input_frame, font=("Helvetica", 10), bg="white", fg="#333",
                                   insertbackground="#333", relief="solid", bd=1)
        self.chat_input.pack(fill="x", pady=(0,8), ipady=4)
        self.chat_input.bind("<Return>", lambda e: self.send_message())

        send_btn = tk.Label(input_frame, text="Send 📤", bg=self.primary_color, fg="white",
                            font=("Helvetica", 11, "bold"), pady=6, cursor="hand2")
        send_btn.pack(fill="x")
        send_btn.bind("<Button-1>", lambda e: self.send_message())
        send_btn.bind("<Enter>", lambda e: send_btn.config(bg="#45a049"))
        send_btn.bind("<Leave>", lambda e: send_btn.config(bg=self.primary_color))

        self.add_chat_message("bot", "Hi! I'm your AI assistant. Ask me anything about symptoms or conditions!")

    # ---------------- METHODS ----------------
    def send_message(self):
        user_message = self.chat_input.get().strip()
        if not user_message:
            return
        self.add_chat_message("user", user_message)
        self.chat_input.delete(0, tk.END)
        try:
            bot_response = self.chatbot.get_response(user_message)
        except Exception as e:
            bot_response = f"Sorry, error: {str(e)}"
        self.add_chat_message("bot", bot_response)

    def add_chat_message(self, sender, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"You: " if sender=="user" else "AI: ", sender)
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.config(state="disabled")
        self.chat_display.see(tk.END)

    def update_list(self, *args):
        search_term = self.search_var.get().lower()
        self.symptom_listbox.delete(0, tk.END)
        if not search_term:
            items = self.all_symptoms
        else:
            items = [s for s in self.all_symptoms if search_term in s.lower()]
            if len(items) < 3:
                close_matches = difflib.get_close_matches(search_term, self.all_symptoms, n=5, cutoff=0.5)
                items = list(set(items + close_matches))
                items.sort()
        for item in items:
            self.symptom_listbox.insert(tk.END, item)

    def on_select_symptom(self, event):
        selection = self.symptom_listbox.curselection()
        if selection:
            symptom = self.symptom_listbox.get(selection[0])
            if symptom not in self.selected_symptoms:
                self.selected_symptoms.append(symptom)
                self.selected_listbox.insert(tk.END, symptom)

    def remove_symptom(self):
        selection = self.selected_listbox.curselection()
        if selection:
            index = selection[0]
            symptom = self.selected_listbox.get(index)
            self.selected_symptoms.remove(symptom)
            self.selected_listbox.delete(index)

    def clear_all(self):
        self.selected_symptoms = []
        self.selected_listbox.delete(0, tk.END)
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state="disabled")

    def diagnose(self):
        if not self.selected_symptoms:
            messagebox.showwarning("No Symptoms", "Please select at least one symptom.")
            return
        matches = self.match_symptoms(self.selected_symptoms)
        if not matches:
            self.display_results("No matching conditions found.", [])
            return
        scores = self.compute_certainty(matches)
        top3 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        severity = self.get_severity(len(self.selected_symptoms))
        self.chatbot.set_diagnosis_context(top3, self.selected_symptoms, severity)
        self.add_chat_message("bot", f"✅ Analysis complete! Ask me about your results.")
        self.display_results(top3, self.selected_symptoms)

    def match_symptoms(self, user_symptoms):
        matches = {}
        for s in user_symptoms:
            if s in symptom_to_diseases:
                for illness in symptom_to_diseases[s]:
                    matches[illness] = matches.get(illness, 0) + 1
        return matches

    def compute_certainty(self, matches):
        scores = {}
        for disease, match_count in matches.items():
            total = len(disease_to_symptoms.get(disease, []))
            if total > 0:
                score = (match_count / total) * 100
                scores[disease] = round(score, 1)
        return scores

    def get_severity(self, num_symptoms):
        if num_symptoms <= 2:
            return "Mild — Home care recommended."
        elif 3 <= num_symptoms <= 4:
            return "Moderate — You should see a doctor."
        else:
            return "Severe — Seek medical attention."

    def display_results(self, top_matches, user_symptoms):
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        if isinstance(top_matches, str):
            self.results_text.insert(tk.END, top_matches)
            self.results_text.config(state="disabled")
            return
        self.results_text.insert(tk.END, "🔎 Top Possible Conditions:\n\n")
        for disease, score in top_matches:
            desc = disease_info.get(disease, "No description available.")
            score_tag = "high" if score > 70 else "med" if score > 40 else "low"
            self.results_text.tag_config("high", foreground="#d32f2f")
            self.results_text.tag_config("med", foreground="#f57c00")
            self.results_text.tag_config("low", foreground="#388e3c")
            self.results_text.tag_config("bold", font=("Helvetica", 11, "bold"))
            self.results_text.insert(tk.END, f"• {disease}", "bold")
            self.results_text.insert(tk.END, f" ({score}% match)\n", score_tag)
            self.results_text.insert(tk.END, f"  {desc}\n\n")
        severity = self.get_severity(len(user_symptoms))
        self.results_text.insert(tk.END, "⚠️ Severity Estimate: ", "bold")
        self.results_text.insert(tk.END, f"{severity}\n")
        self.results_text.config(state="disabled")

    # -------------------- ADDED RECOVERY GRAPH METHOD --------------------
    def show_recovery_graph(self):
        if not self.selected_symptoms:
            messagebox.showwarning("No Data", "Analyze symptoms first to view recovery graph.")
            return

        days = [1, 2, 3, 4, 5, 6, 7]
        recovery = [20, 35, 50, 65, 75, 85, 95]

        plt.figure()
        plt.plot(days, recovery, marker='o')
        plt.title("Estimated Recovery Progress")
        plt.xlabel("Days")
        plt.ylabel("Recovery (%)")
        plt.grid(True)
        plt.show()
    # ---------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = SymptomCheckerApp(root)
    root.mainloop()