#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鸣潮账号分析规划 AI Agent
"""

import os
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class ElementType(Enum):
    """属性类型"""
    SPECTRO = "衍射"
    HAVOC = "湮灭"
    ELECTRO = "导电"
    FROST = "冷凝"
    FUSION = "热熔"
    AERO = "气动"

class CharacterRole(Enum):
    """角色定位"""
    MAIN_DPS = "主C"
    SUB_DPS = "副C"
    SUPPORT = "辅助"
    HEALER = "奶"

@dataclass
class Character:
    """角色信息"""
    name: str
    element: ElementType
    role: CharacterRole
    constellation: int = 0  # 共鸣链数
    weapon_rank: int = 0    # 专武精炼等级
    
    def __str__(self):
        weapon_str = f"+{self.weapon_rank}专" if self.weapon_rank > 0 else ""
        if self.constellation > 0:
            return f"{self.constellation}{self.name}{weapon_str}"
        return f"{self.name}{weapon_str}"

@dataclass
class Team:
    """队伍配置"""
    element: ElementType
    characters: List[Character]
    
    def __str__(self):
        chars_str = "+".join([str(c) for c in self.characters])
        return f"{self.element.value}: {chars_str}"

@dataclass
class AccountInfo:
    """账号信息"""
    uid: str
    star_sounds: int = 0        # 星声数量
    tuners: int = 0             # 调谐器数量
    tuners_device: int = 0      # 调频仪数量
    coral: int = 0              # 珊瑚数量
    
    # 氪金预算
    monthly_card: bool = False  # 月卡
    big_monthly: bool = False   # 大月卡
    weekly_card: bool = False   # 周卡
    budget: str = ""            # 额外预算描述
    
    # 偏好
    preferences: str = ""       # 偏好描述
    avoid_male: bool = False    # 不抽男角色
    
    # 配队
    teams: List[Team] = None
    
    # 问题
    questions: str = ""         # 咨询问题
    
    def __post_init__(self):
        if self.teams is None:
            self.teams = []

class WuWaAgent:
    """鸣潮账号分析Agent"""
    
    def __init__(self):
        self.account = None
        self.analysis_result = {}
        
    def collect_input(self) -> AccountInfo:
        """交互式收集账号信息"""
        print("=" * 60)
        print("鸣潮账号分析规划系统")
        print("=" * 60)
        
        # 基本信息
        uid = input("\n请输入UID: ").strip()
        
        print("\n--- 资源情况 ---")
        star_sounds = int(input("星声数量: ") or "0")
        tuners = int(input("调谐器数量: ") or "0")
        tuners_device = int(input("调频仪数量: ") or "0")
        coral = int(input("珊瑚数量: ") or "0")
        
        print("\n--- 氪金情况 ---")
        monthly = input("是否有月卡? (y/n): ").lower() == 'y'
        big_monthly = input("是否有大月卡? (y/n): ").lower() == 'y'
        weekly = input("是否有周卡? (y/n): ").lower() == 'y'
        budget = input("其他预算描述 (直接回车跳过): ").strip()
        
        print("\n--- 偏好设置 ---")
        avoid_male = input("是否不抽男角色? (y/n): ").lower() == 'y'
        preferences = input("其他偏好 (如: 喜欢少女角色/偏向强度等): ").strip()
        
        # 配队信息
        print("\n--- 配队信息 ---")
        print("属性列表: 1.衍射 2.湮灭 3.导电 4.冷凝 5.热熔 6.气动")
        teams = []
        
        for i, elem in enumerate(ElementType, 1):
            print(f"\n{elem.value}队配置 (直接回车表示无此队伍):")
            team_input = input(f"  格式示例: 61椿+00散+00守 / 01相+01吟: ").strip()
            if team_input:
                characters = self._parse_team_input(team_input)
                teams.append(Team(element=elem, characters=characters))
        
        print("\n--- 咨询问题 ---")
        questions = input("想咨询的问题 (直接回车跳过): ").strip()
        
        self.account = AccountInfo(
            uid=uid,
            star_sounds=star_sounds,
            tuners=tuners,
            tuners_device=tuners_device,
            coral=coral,
            monthly_card=monthly,
            big_monthly=big_monthly,
            weekly_card=weekly,
            budget=budget,
            avoid_male=avoid_male,
            preferences=preferences,
            teams=teams,
            questions=questions
        )
        
        return self.account
    
    def _parse_team_input(self, input_str: str) -> List[Character]:
        """解析队伍输入字符串"""
        characters = []
        parts = input_str.split('+')
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # 解析格式如: 61椿, 01相, 00散
            constellation = 0
            name = part
            weapon_rank = 0
            
            # 检查是否有共鸣链数字前缀
            if part[0].isdigit() and len(part) > 1:
                constellation = int(part[0])
                name = part[1:]
            
            # 检查是否有专武标记
            if '专' in name:
                name = name.replace('专', '')
                weapon_rank = 1  # 默认精1
            
            characters.append(Character(
                name=name,
                element=ElementType.SPECTRO,  # 临时值，会在Team中覆盖
                role=CharacterRole.MAIN_DPS,   # 临时值
                constellation=constellation,
                weapon_rank=weapon_rank
            ))
        
        return characters
    
    def analyze(self) -> Dict:
        """分析账号并生成建议"""
        if not self.account:
            raise ValueError("请先收集账号信息")
        
        analysis = {
            "uid": self.account.uid,
            "overall": self._analyze_overall(),
            "teams_analysis": self._analyze_teams(),
            "pull_suggestions": self._generate_pull_suggestions(),
            "build_suggestions": self._generate_build_suggestions(),
        }
        
        self.analysis_result = analysis
        return analysis
    
    def _analyze_overall(self) -> str:
        """整体情况分析"""
        team_count = len(self.account.teams)
        has_high_constellation = any(
            any(c.constellation >= 6 for c in team.characters)
            for team in self.account.teams
        )
        
        if team_count >= 5 and has_high_constellation:
            return "配置较好，队伍完整。"
        elif team_count >= 4:
            return "队伍较为完整，但可能有优化空间。"
        elif team_count <= 2:
            return "队伍数量较少，建议优先组建更多完整配队。"
        else:
            return "整体情况一般，需要针对性补强。"
    
    def _analyze_teams(self) -> List[Dict]:
        """逐队伍分析"""
        analyses = []
        
        for team in self.account.teams:
            analysis = {
                "element": team.element.value,
                "team_str": str(team),
                "suggestion": self._get_team_suggestion(team)
            }
            analyses.append(analysis)
        
        return analyses
    
    def _get_team_suggestion(self, team: Team) -> str:
        """获取队伍建议"""
        # 这里可以根据你的经验规则来定制
        main_dps = [c for c in team.characters if c.constellation > 0]
        
        if not main_dps:
            return "队伍缺少高链主C，建议优先补强。"
        
        highest = max(main_dps, key=lambda x: x.constellation)
        if highest.constellation >= 6:
            return f"{highest.name}配置较高，队伍核心已成型。"
        elif highest.constellation >= 3:
            return f"{highest.name}有一定配置，可视情况补链或保持现状。"
        else:
            return f"{highest.name}配置较低，建议考虑补链或更换主C。"
    
    def _generate_pull_suggestions(self) -> List[Dict]:
        """生成抽卡建议"""
        suggestions = []
        
        # 基于当前版本(3.x)的通用建议框架
        versions = [
            ("3.1下半", "陆赫斯、嘉贝莉娜", "不推荐"),
            ("3.2上半", "西格莉卡、仇远", "视情况"),
            ("3.2下半", "琳奈、赞妮、菲比", "视情况"),
            ("3.3上半", "绯雪", "推荐观望"),
            ("3.3下半", "达尼娅", "视情况"),
        ]
        
        for version, chars, default in versions:
            suggestions.append({
                "version": version,
                "characters": chars,
                "suggestion": default,
                "reason": ""
            })
        
        return suggestions
    
    def _generate_build_suggestions(self) -> List[str]:
        """生成养成建议"""
        suggestions = []
        
        if self.account.tuners < 1000:
            suggestions.append("调谐器资源紧张，建议优先给主C使用。")
        
        suggestions.append("主力主C建议刷到175-180分声骸。")
        suggestions.append("副C建议刷到150分+共鸣效率达标即可。")
        
        return suggestions
    
    def generate_latex(self) -> str:
        """生成LaTeX代码"""
        if not self.analysis_result:
            self.analyze()
        
        latex_template = r"""\documentclass[UTF8,a4paper,11pt]{{ctexart}}
\usepackage{{enumitem}}
\usepackage{{geometry}}
\usepackage{{booktabs}}
\usepackage{{amsmath}}
\usepackage{{hyperref}}
\usepackage{{setspace}}
\usepackage{{indentfirst}}

\geometry{{
	a4paper,
	left=2.54cm,
	right=2.54cm,
	top=2.54cm,
	bottom=2.54cm,
	headsep=0.5cm,
	footskip=1cm,
	showframe=false
}}

\linespread{{1.5}}
\setlength{{\parindent}}{{2em}}
\setlength{{\parskip}}{{0.2em}}

\setlist[enumerate,1]{{
	leftmargin=2em,
	labelwidth=1.5em,
	align=left,
	labelsep=0.5em,
	itemsep=0.3em,
	parsep=0.1em,
	label=\arabic{{enumi}}.
}}
\setlist[enumerate,2]{{
	leftmargin=3em,
	labelwidth=2em,
	labelsep=0.3em,
	itemsep=0.2em,
	label=(\arabic{{enumii}})
}}

\hypersetup{{
	colorlinks=true,
	linkcolor=black,
	anchorcolor=black,
	citecolor=black,
	urlcolor=blue,
	pdfborder={{0 0 0}},
	pdfstartview=FitH
}}

\pagestyle{{empty}}
\title{{\textbf{{uid: {uid} 规划}}}}
\author{{\normalsize AI Agent生成}}
\date{{}}

\begin{{document}}
	\maketitle
	\thispagestyle{{empty}}
	
	\section{{原文}}
	{original_text}
	
	\section{{整体情况}}
	{overall}
	
	\section{{配队}}
	\begin{{enumerate}}
{teams_section}
	\end{{enumerate}}
	
	\section{{逐队伍分析}}
	\begin{{enumerate}}
{team_analysis_section}
	\end{{enumerate}}
	
	\section{{逐版本抽卡建议}}
	\begin{{enumerate}}
{pull_section}
	\end{{enumerate}}
	
	\section{{养成建议}}
	\begin{{enumerate}}
{build_section}
	\end{{enumerate}}
	
\end{{document}}
"""
        
        # 构建原文部分
        original_parts = []
        original_parts.append(f"UID: {self.account.uid}")
        original_parts.append(f"资源: 星声{self.account.star_sounds}，调谐器{self.account.tuners}，调频仪{self.account.tuners_device}，珊瑚{self.account.coral}")
        
        budget_parts = []
        if self.account.monthly_card:
            budget_parts.append("月卡")
        if self.account.big_monthly:
            budget_parts.append("大月卡")
        if self.account.weekly_card:
            budget_parts.append("周卡")
        if self.account.budget:
            budget_parts.append(self.account.budget)
        
        if budget_parts:
            original_parts.append(f"氪金: {'+'.join(budget_parts)}")
        
        if self.account.preferences:
            original_parts.append(f"偏好: {self.account.preferences}")
        
        if self.account.questions:
            original_parts.append(f"咨询: {self.account.questions}")
        
        original_text = "\\\n\t".join(original_parts)
        
        # 构建配队部分
        teams_section = ""
        for team in self.account.teams:
            teams_section += f"\t\t\\item {team.element.value}: {str(team)}\n"
        
        # 构建队伍分析部分
        team_analysis_section = ""
        for analysis in self.analysis_result.get("teams_analysis", []):
            team_analysis_section += f"\t\t\\item \\textbf{{{analysis['element']}}}: {analysis['suggestion']}\n"
        
        # 构建抽卡建议部分
        pull_section = ""
        for sug in self.analysis_result.get("pull_suggestions", []):
            pull_section += f"\t\t\\item \\textbf{{{sug['version']}}} {sug['characters']}: {sug['suggestion']}\n"
        
        # 构建养成建议部分
        build_section = ""
        for sug in self.analysis_result.get("build_suggestions", []):
            build_section += f"\t\t\\item {sug}\n"
        
        return latex_template.format(
            uid=self.account.uid,
            original_text=original_text,
            overall=self.analysis_result.get("overall", ""),
            teams_section=teams_section,
            team_analysis_section=team_analysis_section,
            pull_section=pull_section,
            build_section=build_section
        )
    
    def save_latex(self, filename: str = None) -> str:
        """保存LaTeX文件"""
        if not filename:
            filename = f"{self.account.uid}_规划.tex"
        
        latex_code = self.generate_latex()
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(latex_code)
        
        print(f"LaTeX文件已保存: {filepath}")
        return filepath
    
    def compile_pdf(self, tex_path: str = None) -> str:
        """编译生成PDF"""
        if not tex_path:
            tex_path = self.save_latex()
        
        # 使用xelatex编译
        cmd = ['xelatex', '-interaction=nonstopmode', tex_path]
        
        try:
            # 编译两次以解决交叉引用
            for _ in range(2):
                result = subprocess.run(
                    cmd,
                    cwd=os.path.dirname(tex_path),
                    capture_output=True,
                    text=True
                )
            
            pdf_path = tex_path.replace('.tex', '.pdf')
            if os.path.exists(pdf_path):
                print(f"PDF已生成: {pdf_path}")
                return pdf_path
            else:
                print("PDF生成失败")
                return None
                
        except Exception as e:
            print(f"编译错误: {e}")
            return None
    
    def run(self):
        """运行完整流程"""
        self.collect_input()
        self.analyze()
        
        print("\n" + "=" * 60)
        print("分析完成！")
        print("=" * 60)
        
        print("\n请选择输出方式:")
        print("1. 仅生成LaTeX代码")
        print("2. 生成LaTeX并编译PDF")
        print("3. 两者都生成")
        
        choice = input("选择 (1/2/3): ").strip()
        
        if choice in ['1', '3']:
            tex_path = self.save_latex()
            print(f"\nLaTeX代码预览:")
            print("-" * 60)
            with open(tex_path, 'r', encoding='utf-8') as f:
                print(f.read()[:1000] + "...")
        
        if choice in ['2', '3']:
            pdf_path = self.compile_pdf()
            if pdf_path:
                print(f"\nPDF文件位置: {pdf_path}")

def main():
    agent = WuWaAgent()
    agent.run()

if __name__ == "__main__":
    main()
