import tkinter as tk
from tkinter import ttk
import requests
from io import BytesIO

class Rule:
    def __init__(self, conditions, conclusions, image_urls):
        self.conditions = conditions
        self.conclusions = conclusions
        self.image_urls = image_urls

class RuleBase:
    def __init__(self, rules):
        self.rules = rules

def read_rules_from_file(file_path):
    rules = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                conditions_str, conclusions_str = line.split("=>")
                conditions = [condition.strip() for condition in conditions_str.split(",")]
                conclusions_with_images = conclusions_str.split(", image=")
                conclusions = [conclusion.strip() for conclusion in conclusions_with_images[0].split(",")]
                images = [image.strip() for image in conclusions_with_images[1:]]
                rule = Rule(conditions, conclusions, images)
                rules.append(rule)
    return rules

def forward_chaining(rule_base, symptoms):
    known_facts = set(symptoms)
    inferred_facts = set()

    while True:
        newly_inferred = False
        for rule in rule_base.rules:
            if set(rule.conditions).issubset(known_facts.union(inferred_facts)):
                for conclusion in rule.conclusions:
                    if conclusion not in known_facts:
                        known_facts.add(conclusion)
                        inferred_facts.add(conclusion)
                        newly_inferred = True

                if len(rule.conditions) == 1 and rule.conditions[0] not in known_facts:
                    missing_condition = rule.conditions[0]
                    user_input = input(f"Additional condition needed for rule '{rule.conditions}': {missing_condition} - (y/n): ")
                    if user_input.lower() == 'y':
                        known_facts.add(missing_condition)
                        newly_inferred = True

        if not newly_inferred:
            break

    return known_facts, inferred_facts

def backward_chaining(rule_base, hypothesis):
    supporting_facts = []

    def find_supporting_facts(hypo):
        facts = []
        for rule in rule_base.rules:
            if hypo in rule.conclusions:
                facts.append((rule.conclusions, rule.conditions, rule.image_urls))
        return facts

    def explore_hypotheses(hypotheses):
        while hypotheses:
            hypo = hypotheses.pop()
            facts = find_supporting_facts(hypo)
            for fact in facts:
                supporting_facts.append(fact)
                for cond in fact[1]:
                    if cond not in known_facts:
                        known_facts.append(cond)
                        hypotheses.append(cond)

    known_facts = []
    hypotheses = [hypothesis]

    explore_hypotheses(hypotheses)

    return supporting_facts

class ExpertSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Motor Fault Diagnosis Expert System")

        label = ttk.Label(root, text="Enter symptoms (comma-separated):")
        label.pack(pady=10)

        self.symptoms_entry = ttk.Entry(root, width=50)
        self.symptoms_entry.pack(pady=10)

        diagnose_button = ttk.Button(root, text="Diagnose", command=self.diagnose)
        diagnose_button.pack(pady=10)

        self.results_text = tk.Text(root, wrap=tk.WORD)
        self.results_text.pack(pady=10)

    def Support_ref(self, image_urls):
        if image_urls:
            for i, image_url in enumerate(image_urls, start=1):
                self.results_text.insert(tk.END, f"{i}. {image_url}\n")
            self.results_text.insert(tk.END, "\n")

    def diagnose(self):
        symptoms_input = self.symptoms_entry.get().split(', ')
        symptoms = [symptom.strip() for symptom in symptoms_input]

        rules = read_rules_from_file("rules.txt")
        rule_base = RuleBase(rules)

        known_facts, inferred_facts = forward_chaining(rule_base, symptoms)
        forward_chaining_result = f"Inferred facts: {inferred_facts}\n"

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, forward_chaining_result)

        if inferred_facts:
            supporting_facts = backward_chaining(rule_base, list(inferred_facts)[0])

            for fact in supporting_facts:
                conclusion = fact[0][0]
                image_urls = fact[2]

                self.results_text.insert(tk.END, f"\nSupporting facts for {conclusion}:")

                self.Support_ref(image_urls)

                self.results_text.insert(tk.END, "\n")
        else:
            self.results_text.insert(tk.END, "\nNo specific diagnosis could be made based on the provided symptoms.\n")
            
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")
    app = ExpertSystemApp(root)
    root.mainloop()