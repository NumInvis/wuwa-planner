#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鸣潮账号规划文档编辑器 - GUI版本
引导式输入，生成LaTeX和PDF
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
from datetime import datetime

class WuWaEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("鸣潮账号规划文档编辑器")
        self.root.geometry("900x700")
        
        # 数据存储
        self.data = {
            "uid": "",
            "author": "鬼神莫能窥",
            "original": "",
            "teams": {},  # 属性: 配队字符串
            "overall": "",
            "team_analysis": [],  # [(队伍名, 分析内容), ...]
            "topics": [],  # [(专题名, 结论, 理由列表), ...]
            "future_plans": [],  # [(版本, 角色, 建议), ...]
            "conclusion": "",
            "others": []
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主滚动区域
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=860)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定鼠标滚轮
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # ===== 基本信息 =====
        info_frame = ttk.LabelFrame(self.scrollable_frame, text="基本信息", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text="UID:").grid(row=0, column=0, sticky=tk.W)
        self.uid_entry = ttk.Entry(info_frame, width=20)
        self.uid_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_frame, text="作者:").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.author_entry = ttk.Entry(info_frame, width=20)
        self.author_entry.insert(0, "鬼神莫能窥")
        self.author_entry.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # ===== 原文 =====
        original_frame = ttk.LabelFrame(self.scrollable_frame, text="1. 原文（用户提供的原始信息）", padding=10)
        original_frame.pack(fill=tk.X, pady=5)
        
        self.original_text = scrolledtext.ScrolledText(original_frame, height=4, wrap=tk.WORD)
        self.original_text.pack(fill=tk.X)
        ttk.Label(original_frame, text="提示: 资源情况、氪金预算、偏好、咨询问题等", 
                 foreground="gray").pack(anchor=tk.W)
        
        # ===== 配队情况 =====
        teams_frame = ttk.LabelFrame(self.scrollable_frame, text="2. 配队情况", padding=10)
        teams_frame.pack(fill=tk.X, pady=5)
        
        self.team_entries = {}
        elements = ["衍射", "湮灭", "导电", "冷凝", "热熔", "气动"]
        
        for i, elem in enumerate(elements):
            row = i // 2
            col = (i % 2) * 2
            ttk.Label(teams_frame, text=f"{elem}:").grid(row=row, column=col, sticky=tk.W, pady=2)
            entry = ttk.Entry(teams_frame, width=35)
            entry.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=2)
            self.team_entries[elem] = entry
        
        ttk.Label(teams_frame, text="格式示例: 21赞+20菲+41守 / 61椿+散+维", 
                 foreground="gray").grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=(5,0))
        
        # ===== 整体情况 =====
        overall_frame = ttk.LabelFrame(self.scrollable_frame, text="3. 整体情况/现状分析", padding=10)
        overall_frame.pack(fill=tk.X, pady=5)
        
        self.overall_text = scrolledtext.ScrolledText(overall_frame, height=3, wrap=tk.WORD)
        self.overall_text.pack(fill=tk.X)
        
        # ===== 逐队伍分析 =====
        team_analysis_frame = ttk.LabelFrame(self.scrollable_frame, text="4. 逐队伍分析", padding=10)
        team_analysis_frame.pack(fill=tk.X, pady=5)
        
        self.team_analysis_list = tk.Listbox(team_analysis_frame, height=4)
        self.team_analysis_list.pack(fill=tk.X, pady=5)
        
        btn_frame = ttk.Frame(team_analysis_frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="添加分析", command=self.add_team_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除选中", command=self.remove_team_analysis).pack(side=tk.LEFT, padx=5)
        
        # ===== 专题模块 =====
        topics_frame = ttk.LabelFrame(self.scrollable_frame, text="5. 专题模块（可自定义专题名）", padding=10)
        topics_frame.pack(fill=tk.X, pady=5)
        
        self.topics_list = tk.Listbox(topics_frame, height=4)
        self.topics_list.pack(fill=tk.X, pady=5)
        
        btn_frame2 = ttk.Frame(topics_frame)
        btn_frame2.pack(fill=tk.X)
        ttk.Button(btn_frame2, text="添加专题", command=self.add_topic).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="删除选中", command=self.remove_topic).pack(side=tk.LEFT, padx=5)
        
        # ===== 未来卡池规划 =====
        future_frame = ttk.LabelFrame(self.scrollable_frame, text="6. 逐版本抽卡建议", padding=10)
        future_frame.pack(fill=tk.X, pady=5)
        
        self.future_list = tk.Listbox(future_frame, height=4)
        self.future_list.pack(fill=tk.X, pady=5)
        
        btn_frame3 = ttk.Frame(future_frame)
        btn_frame3.pack(fill=tk.X)
        ttk.Button(btn_frame3, text="添加版本建议", command=self.add_future).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame3, text="删除选中", command=self.remove_future).pack(side=tk.LEFT, padx=5)
        
        # ===== 最终结论 =====
        conclusion_frame = ttk.LabelFrame(self.scrollable_frame, text="7. 最终推荐方案/结论", padding=10)
        conclusion_frame.pack(fill=tk.X, pady=5)
        
        self.conclusion_text = scrolledtext.ScrolledText(conclusion_frame, height=3, wrap=tk.WORD)
        self.conclusion_text.pack(fill=tk.X)
        
        # ===== 其他 =====
        others_frame = ttk.LabelFrame(self.scrollable_frame, text="8. 其他（养成建议等）", padding=10)
        others_frame.pack(fill=tk.X, pady=5)
        
        self.others_text = scrolledtext.ScrolledText(others_frame, height=4, wrap=tk.WORD)
        self.others_text.pack(fill=tk.X)
        
        # ===== 底部按钮 =====
        bottom_frame = ttk.Frame(self.scrollable_frame)
        bottom_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(bottom_frame, text="生成LaTeX", command=self.generate_latex).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="生成PDF", command=self.generate_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="清空所有", command=self.clear_all).pack(side=tk.LEFT, padx=5)
    
    def add_team_analysis(self):
        """添加队伍分析"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加队伍分析")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="队伍名称:").pack(anchor=tk.W, padx=10, pady=(10,0))
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dialog, text="分析内容:").pack(anchor=tk.W, padx=10)
        content_text = scrolledtext.ScrolledText(dialog, height=8, wrap=tk.WORD)
        content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        def save():
            name = name_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            if name and content:
                self.data["team_analysis"].append((name, content))
                self.team_analysis_list.insert(tk.END, f"{name}: {content[:30]}...")
                dialog.destroy()
        
        ttk.Button(dialog, text="保存", command=save).pack(pady=10)
    
    def remove_team_analysis(self):
        """删除队伍分析"""
        selection = self.team_analysis_list.curselection()
        if selection:
            idx = selection[0]
            self.team_analysis_list.delete(idx)
            del self.data["team_analysis"][idx]
    
    def add_topic(self):
        """添加专题"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加专题")
        dialog.geometry("500x400")
        
        ttk.Label(dialog, text="专题名称:").pack(anchor=tk.W, padx=10, pady=(10,0))
        name_entry = ttk.Entry(dialog, width=50)
        name_entry.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dialog, text="结论:").pack(anchor=tk.W, padx=10)
        conclusion_text = scrolledtext.ScrolledText(dialog, height=3, wrap=tk.WORD)
        conclusion_text.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dialog, text="理由/分析（每行一条）:").pack(anchor=tk.W, padx=10)
        reasons_text = scrolledtext.ScrolledText(dialog, height=8, wrap=tk.WORD)
        reasons_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        def save():
            name = name_entry.get().strip()
            conclusion = conclusion_text.get("1.0", tk.END).strip()
            reasons = [r.strip() for r in reasons_text.get("1.0", tk.END).strip().split("\n") if r.strip()]
            if name:
                self.data["topics"].append((name, conclusion, reasons))
                self.topics_list.insert(tk.END, name)
                dialog.destroy()
        
        ttk.Button(dialog, text="保存", command=save).pack(pady=10)
    
    def remove_topic(self):
        """删除专题"""
        selection = self.topics_list.curselection()
        if selection:
            idx = selection[0]
            self.topics_list.delete(idx)
            del self.data["topics"][idx]
    
    def add_future(self):
        """添加未来规划"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加版本抽卡建议")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="版本（如: 3.1下半）:").pack(anchor=tk.W, padx=10, pady=(10,0))
        version_entry = ttk.Entry(dialog, width=40)
        version_entry.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dialog, text="角色:").pack(anchor=tk.W, padx=10)
        chars_entry = ttk.Entry(dialog, width=40)
        chars_entry.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dialog, text="建议:").pack(anchor=tk.W, padx=10)
        suggestion_text = scrolledtext.ScrolledText(dialog, height=4, wrap=tk.WORD)
        suggestion_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        def save():
            version = version_entry.get().strip()
            chars = chars_entry.get().strip()
            suggestion = suggestion_text.get("1.0", tk.END).strip()
            if version:
                self.data["future_plans"].append((version, chars, suggestion))
                self.future_list.insert(tk.END, f"{version}: {chars}")
                dialog.destroy()
        
        ttk.Button(dialog, text="保存", command=save).pack(pady=10)
    
    def remove_future(self):
        """删除未来规划"""
        selection = self.future_list.curselection()
        if selection:
            idx = selection[0]
            self.future_list.delete(idx)
            del self.data["future_plans"][idx]
    
    def collect_data(self):
        """收集所有数据"""
        self.data["uid"] = self.uid_entry.get().strip()
        self.data["author"] = self.author_entry.get().strip() or "鬼神莫能窥"
        self.data["original"] = self.original_text.get("1.0", tk.END).strip()
        self.data["overall"] = self.overall_text.get("1.0", tk.END).strip()
        self.data["conclusion"] = self.conclusion_text.get("1.0", tk.END).strip()
        self.data["others"] = [r.strip() for r in self.others_text.get("1.0", tk.END).strip().split("\n") if r.strip()]
        
        # 收集配队
        for elem, entry in self.team_entries.items():
            val = entry.get().strip()
            if val:
                self.data["teams"][elem] = val
    
    def generate_latex(self):
        """生成LaTeX代码"""
        self.collect_data()
        
        if not self.data["uid"]:
            messagebox.showerror("错误", "请输入UID")
            return
        
        latex = self._build_latex()
        
        # 保存文件
        filename = f"{self.data['uid']}_规划.tex"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(latex)
        
        messagebox.showinfo("成功", f"LaTeX文件已保存:\n{filepath}")
        return filepath
    
    def generate_pdf(self):
        """生成PDF"""
        tex_path = self.generate_latex()
        if not tex_path:
            return
        
        try:
            # 编译两次
            for _ in range(2):
                result = subprocess.run(
                    ['xelatex', '-interaction=nonstopmode', tex_path],
                    cwd=os.path.dirname(tex_path),
                    capture_output=True,
                    text=True
                )
            
            pdf_path = tex_path.replace('.tex', '.pdf')
            if os.path.exists(pdf_path):
                messagebox.showinfo("成功", f"PDF已生成:\n{pdf_path}")
            else:
                messagebox.showerror("错误", "PDF生成失败，请检查LaTeX环境")
        except Exception as e:
            messagebox.showerror("错误", f"编译出错: {e}")
    
    def _build_latex(self) -> str:
        """构建LaTeX文档"""
        
        # 配队表格
        teams_table = ""
        if self.data["teams"]:
            teams_table = r"""
\begin{center}
\begin{tabular}{p{1.8cm}p{10cm}}
\toprule
属性 & 配队 \\
\midrule
"""
            for elem in ["衍射", "湮灭", "导电", "冷凝", "热熔", "气动"]:
                if elem in self.data["teams"]:
                    teams_table += f"{elem} & {self.data['teams'][elem]} \\\\\n"
                else:
                    teams_table += f"{elem} & \\\\\n"
            
            teams_table += r"""\bottomrule
\end{tabular}
\end{center}
"""
        
        # 队伍分析
        team_analysis_section = ""
        if self.data["team_analysis"]:
            team_analysis_section = r"\section{逐队伍分析}" + "\n\\begin{enumerate}\n"
            for name, content in self.data["team_analysis"]:
                team_analysis_section += f"\\item \\textbf{{{name}}}：{content}\n"
            team_analysis_section += "\\end{enumerate}\n"
        
        # 专题模块
        topics_section = ""
        for topic_name, conclusion, reasons in self.data["topics"]:
            topics_section += f"\\section{{{topic_name}}}\n"
            if conclusion:
                topics_section += f"结论：{conclusion}\n\n"
            if reasons:
                topics_section += "理由：\n\\begin{enumerate}\n"
                for r in reasons:
                    topics_section += f"\\item {r}\n"
                topics_section += "\\end{enumerate}\n"
        
        # 未来规划
        future_section = ""
        if self.data["future_plans"]:
            future_section = r"\section{逐版本抽卡建议}" + "\n\\begin{enumerate}\n"
            for version, chars, suggestion in self.data["future_plans"]:
                future_section += f"\\item \\textbf{{{version}}} {chars}：{suggestion}\n"
            future_section += "\\end{enumerate}\n"
        
        # 结论
        conclusion_section = ""
        if self.data["conclusion"]:
            conclusion_section = f"\\section{{最终推荐方案}}\n{self.data['conclusion']}\n"
        
        # 其他
        others_section = ""
        if self.data["others"]:
            others_section = r"\section{其他}" + "\n\\begin{enumerate}\n"
            for item in self.data["others"]:
                others_section += f"\\item {item}\n"
            others_section += "\\end{enumerate}\n"
        
        # 原文
        original_section = ""
        if self.data["original"]:
            original_section = f"\\section{{原文}}\n{self.data['original']}\n"
        
        # 整体情况
        overall_section = ""
        if self.data["overall"]:
            overall_section = f"\\section{{整体情况}}\n{self.data['overall']}\n"
        
        latex = r"""\documentclass[UTF8,a4paper,11pt]{ctexart}
\usepackage{enumitem}
\usepackage{geometry}
\usepackage{booktabs}
\usepackage{amsmath}
\usepackage{hyperref}
\usepackage{setspace}
\usepackage{indentfirst}

\geometry{
    a4paper,
    left=2.54cm,
    right=2.54cm,
    top=2.54cm,
    bottom=2.54cm,
    headsep=0.5cm,
    footskip=1cm,
    showframe=false
}

\linespread{1.5}
\setlength{\parindent}{2em}
\setlength{\parskip}{0.2em}

\setlist[enumerate,1]{
    leftmargin=2em,
    labelwidth=1.5em,
    align=left,
    labelsep=0.5em,
    itemsep=0.3em,
    parsep=0.1em,
    label=\arabic{enumi}.
}

\hypersetup{
    colorlinks=true,
    linkcolor=black,
    anchorcolor=black,
    citecolor=black,
    urlcolor=blue,
    pdfborder={0 0 0},
    pdfstartview=FitH
}

\pagestyle{empty}
\title{\textbf{uid: """ + self.data["uid"] + r""" 规划}}
\author{\normalsize """ + self.data["author"] + r"""}
\date{}

\begin{document}
    \maketitle
    \thispagestyle{empty}
    
""" + original_section + r"""
    \section{配队}
""" + teams_table + r"""
""" + overall_section + r"""
""" + team_analysis_section + r"""
""" + topics_section + r"""
""" + future_section + r"""
""" + conclusion_section + r"""
""" + others_section + r"""
\end{document}
"""
        return latex
    
    def clear_all(self):
        """清空所有数据"""
        if messagebox.askyesno("确认", "确定要清空所有内容吗？"):
            self.uid_entry.delete(0, tk.END)
            self.original_text.delete("1.0", tk.END)
            self.overall_text.delete("1.0", tk.END)
            self.conclusion_text.delete("1.0", tk.END)
            self.others_text.delete("1.0", tk.END)
            
            for entry in self.team_entries.values():
                entry.delete(0, tk.END)
            
            self.team_analysis_list.delete(0, tk.END)
            self.topics_list.delete(0, tk.END)
            self.future_list.delete(0, tk.END)
            
            self.data = {
                "uid": "",
                "author": "鬼神莫能窥",
                "original": "",
                "teams": {},
                "overall": "",
                "team_analysis": [],
                "topics": [],
                "future_plans": [],
                "conclusion": "",
                "others": []
            }

def main():
    root = tk.Tk()
    app = WuWaEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
