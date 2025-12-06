import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import openpyxl
from database import get_connection as get_conn


class SyllabusApp(tk.Tk):
    def __init__(self): 
        super().__init__()
        self.title("Syllabus Repository System")
        self.geometry("1000x600")

        # Search Frame
        search_frame = tk.Frame(self)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search())
        tk.Button(search_frame, text="Search", command=self.search).pack(side="left", padx=2)
        tk.Button(search_frame, text="Clear", command=self.clear_search).pack(side="left", padx=2)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add New", command=self.add_syllabus, bg="green", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Edit Selected", command=self.edit_syllabus, bg="blue", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_syllabus, bg="red", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Export to Excel", command=self.export_excel, bg="orange", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.load_data).pack(side="left", padx=5)

        # Table
        columns = ("ID", "Code", "Name", "Instructor", "Semester", "Year")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Bindings
        self.tree.bind("<Double-1>", self.open_pdf)
        self.tree.bind("<Button-3>", self.on_right_click)

        self.load_data()

    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = get_conn()
        for row in conn.execute("SELECT id, course_code, course_name, instructor, semester, year FROM syllabi"):
            self.tree.insert("", "end", values=row)
        conn.close()

    def search(self):
        term = self.search_var.get().strip()
        if not term:
            self.load_data()
            return
        
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        conn = get_conn()
        like = f"%{term}%"
        rows = conn.execute(
            "SELECT id, course_code, course_name, instructor, semester, year FROM syllabi "
            "WHERE course_code LIKE ? OR course_name LIKE ? OR instructor LIKE ? OR semester LIKE ? OR year LIKE ?",
            (like, like, like, like, like)
        ).fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        conn.close()

    def clear_search(self):
        self.search_var.set("")
        self.load_data()

    def add_syllabus(self):
        self.open_form(mode="add")

    def edit_syllabus(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a row to edit")
            return
        values = self.tree.item(selected[0])["values"]
        self.open_form(mode="edit", data=values)

    def open_form(self, mode="add", data=None):
        win = tk.Toplevel(self)
        win.title("Add Syllabus" if mode == "add" else "Edit Syllabus")
        win.geometry("400x500")

        entries = {}
        labels = ["Course Code", "Course Name", "Instructor", "Semester", "Year"]
        for i, label in enumerate(labels):
            tk.Label(win, text=label + ":").pack(pady=5)
            e = tk.Entry(win, width=40)
            e.pack()
            if mode == "edit" and data:
                e.insert(0, data[i+1])
            entries[label] = e

        def save():
            code = entries["Course Code"].get()
            name = entries["Course Name"].get()
            if not code or not name:
                messagebox.showwarning("Error", "Code and Name required")
                return

            pdf = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
            if not pdf:
                return

            os.makedirs("data/pdfs", exist_ok=True)
            new_path = f"data/pdfs/{code}_{name[:20]}.pdf"
            shutil.copy(pdf, new_path)

            conn = get_conn()
            if mode == "add":
                conn.execute("INSERT INTO syllabi (course_code,course_name,instructor,semester,year,pdf_path) VALUES (?,?,?,?,?,?)",
                             (code, name, entries["Instructor"].get(), entries["Semester"].get(),
                              entries["Year"].get(), new_path))
            else:
                conn.execute("UPDATE syllabi SET course_code=?, course_name=?, instructor=?, semester=?, year=?, pdf_path=? WHERE id=?",
                             (code, name, entries["Instructor"].get(), entries["Semester"].get(),
                              entries["Year"].get(), new_path, data[0]))
            conn.commit()
            conn.close()
            self.load_data()
            win.destroy()

        tk.Button(win, text="Save", command=save, bg="green", fg="white").pack(pady=20)

    def on_right_click(self, event):
        item = self.tree.identify("item", event.x, event.y)
        if item:
            self.tree.selection_set(item)
            self.delete_syllabus()

    def delete_syllabus(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        if messagebox.askyesno("Delete", "Delete this syllabus?"):
            id_to_delete = self.tree.item(selected[0])["values"][0]
            conn = get_conn()
            conn.execute("DELETE FROM syllabi WHERE id=?", (id_to_delete,))
            conn.commit()
            conn.close()
            self.load_data()

    def open_pdf(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        conn = get_conn()
        path = conn.execute("SELECT pdf_path FROM syllabi WHERE id=?", 
                           (self.tree.item(selected[0])["values"][0],)).fetchone()[0]
        conn.close()
        try:
            os.startfile(path)
        except:
            import subprocess
            subprocess.run(["xdg-open", path])

    def export_excel(self):
        conn = get_conn()
        rows = conn.execute("SELECT course_code,course_name,instructor,semester,year FROM syllabi").fetchall()
        conn.close()

        wb = openpyxl.Workbook()
        ws = wb.active or wb.create_sheet()
        ws.append(["Code", "Name", "Instructor", "Semester", "Year"])
        for row in rows:
            ws.append(row)
        wb.save("syllabi_export.xlsx")
        messagebox.showinfo("Done", "Exported to syllabi_export.xlsx")


if __name__ == "__main__":
    app = SyllabusApp()
    app.mainloop()