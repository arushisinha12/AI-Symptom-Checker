import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import difflib
from knowledge import symptom_to_diseases, disease_to_symptoms, disease_info
from chatbot import MedicalChatbot
import matplotlib.pyplot as plt


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

        self.setup_styles()
        self.create_header()
        self.create_main_layout()

    # ---------------- STYLES ----------------
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        self.primary_color = "#4CAF50"
        self.secondary_color = "#1565C0"
        self.bg_color = "#e9edf2"
        self.card_bg = "#ffffff"
        self.text_color = "#333333"
        self.highlight_color = "#f5f5f5"

        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        style.configure("Header.TLabel", background=self.primary_color,
                        foreground="white", font=("Helvetica", 22, "bold"))

        # Button Styles
        style.configure("Analyze.TButton", background=self.secondary_color,
                        foreground="white", font=("Helvetica", 14, "bold"))
        style.map("Analyze.TButton", background=[("active", "#0D47A1")])

        style.configure("Graph.TButton", background=self.primary_color,
                        foreground="white", font=("Helvetica", 14, "bold"))
        style.map("Graph.TButton", background=[("active", "#388E3C")])

    # ---------------- HEADER ----------------
    def create_header(self):
        header_frame = tk.Frame(self.root, bg=self.primary_color, pady=20)
        header_frame.pack(fill="x")

        tk.Label(header_frame, text="🩺 Advanced AI Symptom Checker",
                 bg=self.primary_color, fg="white",
                 font=("Helvetica", 22, "bold")).pack()

        tk.Label(header_frame,
                 text="Symptom-based analysis with AI medical assistant",
                 bg=self.primary_color, fg="#e0f2f1",
                 font=("Helvetica", 12, "italic")).pack(pady=(5, 0))

    # ---------------- MAIN LAYOUT ----------------
    def create_main_layout(self):
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        left = tk.Frame(main_frame, bg=self.bg_color)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.create_symptom_checker(left)

        right = tk.Frame(main_frame, bg=self.bg_color, width=320)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self.create_chatbot(right)

    # ---------------- SYMPTOM CHECKER ----------------
    def create_symptom_checker(self, parent):
        top = tk.Frame(parent, bg=self.bg_color)
        top.pack(fill="x", pady=(0, 15))

        # Symptom list
        left_card = tk.Frame(top, bg=self.card_bg, bd=2, relief="raised")
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left_card, text="1. Select Symptoms",
                 bg=self.highlight_color, fg=self.text_color, font=("Helvetica", 13, "bold")).pack(fill="x")

        content = tk.Frame(left_card, bg=self.card_bg, padx=15, pady=15)
        content.pack(fill="both", expand=True)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)

        tk.Entry(content, textvariable=self.search_var).pack(fill="x", pady=5)

        list_frame = tk.Frame(content, bg=self.card_bg)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.symptom_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                          bg=self.card_bg, fg=self.text_color)
        self.symptom_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=self.symptom_listbox.yview)

        self.symptom_listbox.bind("<<ListboxSelect>>", self.on_select_symptom)
        self.update_list()

        # Selected symptoms
        right_card = tk.Frame(top, bg=self.card_bg, bd=2, relief="raised")
        right_card.pack(side="right", fill="y")

        tk.Label(right_card, text="2. Selected Symptoms",
                 bg=self.highlight_color, fg=self.text_color, font=("Helvetica", 13, "bold")).pack(fill="x")

        sel_frame = tk.Frame(right_card, bg=self.card_bg)
        sel_frame.pack(padx=10, pady=10)

        sel_scroll = tk.Scrollbar(sel_frame)
        sel_scroll.pack(side="right", fill="y")

        self.selected_listbox = tk.Listbox(sel_frame, height=10, yscrollcommand=sel_scroll.set,
                                           bg=self.card_bg, fg=self.text_color)
        self.selected_listbox.pack(side="left", fill="both")

        sel_scroll.config(command=self.selected_listbox.yview)

        ttk.Button(right_card, text="Remove", command=self.remove_symptom).pack(fill="x", padx=10)
        ttk.Button(right_card, text="Clear All", command=self.clear_all).pack(fill="x", padx=10, pady=(5, 0))

        # Analyze button
        ttk.Button(parent, text="🔍 Analyze Symptoms", style="Analyze.TButton",
                   command=self.diagnose).pack(fill="x", pady=10)

        # Graph button
        ttk.Button(parent, text="📈 Show Recovery Graph", style="Graph.TButton",
                   command=self.show_recovery_graph).pack(fill="x", pady=(0, 10))

        # Results
        results = tk.Frame(parent, bg=self.card_bg, bd=2, relief="raised")
        results.pack(fill="both", expand=True)

        tk.Label(results,
                 text="3. Most Likely Conditions (Symptom-Based Analysis)",
                 bg=self.highlight_color, fg=self.text_color,
                 font=("Helvetica", 13, "bold")).pack(fill="x")

        self.results_text = scrolledtext.ScrolledText(results, state="disabled", wrap="word",
                                                      bg=self.card_bg, fg=self.text_color)
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------------- CHATBOT ----------------
    def create_chatbot(self, parent):
        frame = tk.Frame(parent, bg=self.card_bg, bd=2, relief="raised")
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="💬 AI Assistant",
                 bg=self.highlight_color, fg=self.text_color,
                 font=("Helvetica", 13, "bold")).pack(fill="x")

        self.chat_display = scrolledtext.ScrolledText(frame, state="disabled", height=20,
                                                      bg=self.card_bg, fg=self.text_color)
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)

        self.chat_input = tk.Entry(frame, bg=self.card_bg, fg=self.text_color)
        self.chat_input.pack(fill="x", padx=10)
        self.chat_input.bind("<Return>", lambda e: self.send_message())

        tk.Button(frame, text="Send", command=self.send_message).pack(fill="x", padx=10, pady=5)

        self.add_chat_message("bot", "Hi! Ask me anything about your symptoms or results.")

    # ---------------- LOGIC ----------------
    def update_list(self, *args):
        term = self.search_var.get().lower()
        self.symptom_listbox.delete(0, tk.END)
        items = [s for s in self.all_symptoms if term in s.lower()]
        for s in items:
            self.symptom_listbox.insert(tk.END, s)

    def on_select_symptom(self, event):
        if self.symptom_listbox.curselection():
            s = self.symptom_listbox.get(self.symptom_listbox.curselection())
            if s not in self.selected_symptoms:
                self.selected_symptoms.append(s)
                self.selected_listbox.insert(tk.END, s)

    def remove_symptom(self):
        if self.selected_listbox.curselection():
            idx = self.selected_listbox.curselection()[0]
            s = self.selected_listbox.get(idx)
            self.selected_symptoms.remove(s)
            self.selected_listbox.delete(idx)

    def clear_all(self):
        self.selected_symptoms.clear()
        self.selected_listbox.delete(0, tk.END)
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state="disabled")

    # ---------------- DIAGNOSIS ----------------
    def diagnose(self):
        if not self.selected_symptoms:
            messagebox.showwarning("No symptoms", "Please select symptoms first.")
            return

        matches = self.match_symptoms(self.selected_symptoms)
        scores = self.compute_certainty(matches)

        top3 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]

        # Confidence floor
        if top3 and top3[0][1] < 35:
            top3[0] = (top3[0][0], 35.0)

        self.display_results(top3, self.selected_symptoms)
        self.chatbot.set_diagnosis_context(top3, self.selected_symptoms,
                                           self.get_severity(len(self.selected_symptoms)))

    def match_symptoms(self, user_symptoms):
        matches = {}
        for s in user_symptoms:
            for d in symptom_to_diseases.get(s, []):
                matches[d] = matches.get(d, 0) + 1
        return matches

    # ⭐ JACCARD + COVERAGE BONUS ⭐
    def compute_certainty(self, matches):
        scores = {}
        user_set = set(self.selected_symptoms)

        for disease in matches:
            disease_set = set(disease_to_symptoms.get(disease, []))
            if not disease_set:
                continue

            intersection = user_set & disease_set
            union = user_set | disease_set

            jaccard = len(intersection) / len(union)
            coverage = len(intersection) / len(user_set)

            final_score = (jaccard * 70) + (coverage * 30)
            scores[disease] = round(final_score, 1)

        return scores

    def get_severity(self, count):
        if count <= 2:
            return "Mild — Home care recommended."
        elif count <= 4:
            return "Moderate — Consider seeing a doctor."
        else:
            return "Severe — Seek medical attention."

    def display_results(self, top_matches, user_symptoms):
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)

        for disease, score in top_matches:
            desc = disease_info.get(disease, "No description available.")
            self.results_text.insert(
                tk.END,
                f"• {disease} ({score}% likelihood based on selected symptoms)\n  {desc}\n\n"
            )

        self.results_text.insert(tk.END,
                                 f"⚠️ Severity Estimate: {self.get_severity(len(user_symptoms))}")
        self.results_text.config(state="disabled")

    # ---------------- GRAPH ----------------
    def show_recovery_graph(self):
        if not self.selected_symptoms:
            messagebox.showwarning("No data", "Analyze symptoms first.")
            return

        days = [1, 2, 3, 4, 5, 6, 7]
        recovery = [20, 35, 50, 65, 75, 85, 95]

        plt.plot(days, recovery, marker="o")
        plt.title("Estimated Recovery Progress")
        plt.xlabel("Days")
        plt.ylabel("Recovery (%)")
        plt.grid(True)
        plt.show()

    # ---------------- CHAT ----------------
    def send_message(self):
        msg = self.chat_input.get().strip()
        if not msg:
            return
        self.chat_input.delete(0, tk.END)
        self.add_chat_message("user", msg)
        reply = self.chatbot.get_response(msg)
        self.add_chat_message("bot", reply)

    def add_chat_message(self, sender, msg):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"{sender.upper()}: {msg}\n\n")
        self.chat_display.config(state="disabled")
        self.chat_display.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = SymptomCheckerApp(root)
    root.mainloop()