import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from compiler import Lexer, Parser, TokenType

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Camel Compiler")
        self.root.geometry("1000x900")
        
        self.setup_scrollable_container()
        
        self.setup_input_area()
        
        self.setup_analyze_button()
        
        self.setup_results_area()
        
        self.main_frame.columnconfigure(1, weight=1)

    def setup_scrollable_container(self):
        self.canvas = tk.Canvas(self.root, borderwidth=0, background="#f0f0f0")
        self.v_scroll = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)
        
        self.v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.main_frame = ttk.Frame(self.canvas, padding="10")
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def setup_input_area(self):
        self.input_label = ttk.Label(self.main_frame, text="Enter your code:", font=("Arial", 12))
        self.input_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.input_text = scrolledtext.ScrolledText(
            self.main_frame, 
            width=60, 
            height=10,
            font=("Consolas", 12),
            wrap=tk.WORD
        )
        self.input_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.input_text.insert(tk.END, "x = y + 5;") 

    def setup_analyze_button(self):
        self.analyze_button = ttk.Button(
            self.main_frame, 
            text="Analyze Code", 
            command=self.analyze_code,
            style="Accent.TButton"
        )
        self.analyze_button.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 11))

    def setup_results_area(self):
        self.create_transition_table()
        self.create_lexical_analysis_area()
        self.create_parser_area()

    def create_transition_table(self):
        self.dynamic_table_frame = ttk.LabelFrame(
            self.main_frame, 
            text="State Transitions", 
            padding="10"
        )
        self.dynamic_table_frame.grid(
            row=3, 
            column=0, 
            columnspan=2, 
            sticky=(tk.W, tk.E), 
            pady=(0, 10)
        )
        
        columns = ("Current State", "Input Type", "Next State", "Token Value", "Final State?")
        self.dynamic_table = ttk.Treeview(
            self.dynamic_table_frame, 
            columns=columns, 
            show="headings", 
            height=7
        )
        
        for col in columns:
            self.dynamic_table.heading(col, text=col)
            self.dynamic_table.column(col, anchor=tk.CENTER, width=120)
        
        self.dynamic_table.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def create_lexical_analysis_area(self):
        self.phase1_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Lexical Analysis", 
            padding="5"
        )
        self.phase1_frame.grid(
            row=4, 
            column=0, 
            columnspan=2, 
            sticky=(tk.W, tk.E, tk.N, tk.S), 
            pady=(0, 10)
        )
        
        columns = ("Token", "TokenType", "Position")
        self.phase1_table = ttk.Treeview(
            self.phase1_frame, 
            columns=columns, 
            show="headings", 
            height=6
        )
        
        for col in columns:
            self.phase1_table.heading(col, text=col)
            self.phase1_table.column(col, anchor=tk.CENTER, width=120)
        
        self.phase1_table.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.phase1_frame.columnconfigure(0, weight=1)
        self.phase1_frame.rowconfigure(0, weight=1)

    def create_parser_area(self):
        self.phase3_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Parser Output", 
            padding="5"
        )
        self.phase3_frame.grid(
            row=6, 
            column=0, 
            columnspan=2, 
            sticky=(tk.W, tk.E, tk.N, tk.S)
        )
        
        self.phase3_text = tk.Text(
            self.phase3_frame, 
            width=60, 
            height=8, 
            font=("Consolas", 12),
            wrap=tk.WORD
        )
        self.phase3_text.grid(
            row=0, 
            column=0, 
            sticky=(tk.W, tk.E, tk.N, tk.S), 
            padx=5, 
            pady=5
        )
        self.phase3_text.config(
            state=tk.DISABLED, 
            bg="#f8f8ff", 
            relief=tk.SOLID, 
            bd=2
        )
        
        self.phase3_frame.columnconfigure(0, weight=1)
        self.phase3_frame.rowconfigure(0, weight=1)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def analyze_code(self):
        self.clear_results()
        
        code = self.input_text.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "Please enter some code to analyze!")
            return
        
        try:
            self.perform_lexical_analysis(code)
            
            self.perform_syntax_analysis(code)
            
            self.perform_parsing(code)
            
        except Exception as e:
            self.show_error(f"Analysis failed: {str(e)}")

    def clear_results(self):
        for row in self.phase1_table.get_children():
            self.phase1_table.delete(row)
        
        self.phase3_text.config(state=tk.NORMAL)
        self.phase3_text.delete(1.0, tk.END)
        self.phase3_text.config(state=tk.DISABLED)
        
        for row in self.dynamic_table.get_children():
            self.dynamic_table.delete(row)

    def perform_lexical_analysis(self, code):
        lexer = Lexer(code)
        pos = 0
        
        while True:
            token = lexer.get_next_token()
            if token.type == TokenType.EOF:
                break
                
            ttype = self.get_token_type_display(token.type)
            
            idx = code.find(token.value, pos)
            if idx == -1:
                idx = pos
                
            self.phase1_table.insert("", tk.END, values=(token.value, ttype, idx))
            pos = idx + len(token.value)

    def perform_syntax_analysis(self, code):
        lexer = Lexer(code)
        current_token = lexer.get_next_token()
        
        transition_table = {
            'q0': {'letter': 'q1'},
            'q1': {'=': 'q2'},
            'q2': {'letter': 'q3'},
            'q3': {'operator': 'q4', 'special': 'q_accept'},
            'q4': {'letter': 'q3'},
        }
        
        state = 'q0'
        transitions = []
        
        while current_token.type != TokenType.EOF:
            input_type = self.get_input_type(current_token)
            
            if state not in transition_table or input_type not in transition_table[state]:
                transitions.append((state, input_type, 'qErr', current_token.value, 'No'))
                state = 'qErr'
                break
                
            next_state = transition_table[state][input_type]
            is_final = 'Yes' if next_state in ['q1', 'q3', 'q_accept'] else 'No'
            transitions.append((state, input_type, next_state, current_token.value, is_final))
            
            state = next_state
            current_token = lexer.get_next_token()
            
        for t in transitions:
            self.dynamic_table.insert("", tk.END, values=t)
            
        return state == 'q_accept'

    def perform_parsing(self, code):
        self.phase3_text.config(state=tk.NORMAL)
        self.phase3_text.delete(1.0, tk.END)
        
        try:
            lexer = Lexer(code)
            parser = Parser(lexer)
            result = parser.program()
            self.phase3_text.insert(tk.END, result)
        except Exception as e:
            self.phase3_text.insert(tk.END, f"Parsing failed: {str(e)}\n")
        finally:
            self.phase3_text.config(state=tk.DISABLED)

    def get_token_type_display(self, token_type):
        type_map = {
            TokenType.IDENTIFIER: "Identifier",
            TokenType.KEYWORD: "Keyword",
            TokenType.OPERATOR: "Operator",
            TokenType.SPECIAL_CHAR: "SpecialChar",
            TokenType.NUMBER: "Number"
        }
        return type_map.get(token_type, str(token_type))

    def get_input_type(self, token):
        if token.type in (TokenType.IDENTIFIER, TokenType.NUMBER):
            return 'letter'
        elif token.type == TokenType.OPERATOR:
            return '=' if token.value == '=' else 'operator'
        elif token.type == TokenType.SPECIAL_CHAR and token.value == ';':
            return 'special'
        return 'other'

    def show_error(self, message):
        self.phase3_text.config(state=tk.NORMAL)
        self.phase3_text.delete(1.0, tk.END)
        self.phase3_text.insert(tk.END, f"Error: {message}\n")
        self.phase3_text.config(state=tk.DISABLED)
        messagebox.showerror("Error", message)

def main():
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
