#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鸣潮账号规划文档编辑器 - Web版本
使用Flask提供Web界面
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import subprocess
import os
import tempfile

app = Flask(__name__)

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>鸣潮账号规划文档编辑器</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
        }
        .content {
            padding: 30px;
        }
        .section {
            margin-bottom: 25px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }
        .section-title {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        .section-title::before {
            content: "";
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #667eea;
            border-radius: 50%;
            margin-right: 10px;
        }
        .form-row {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .form-group {
            flex: 1;
            min-width: 200px;
        }
        .form-group.full-width {
            flex: 100%;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input[type="text"],
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus,
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        .teams-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .btn-secondary {
            background: #e0e0e0;
            color: #333;
        }
        .btn-secondary:hover {
            background: #d0d0d0;
        }
        .btn-danger {
            background: #ff6b6b;
            color: white;
        }
        .btn-danger:hover {
            background: #ff5252;
        }
        .list-container {
            background: white;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
            max-height: 200px;
            overflow-y: auto;
        }
        .list-item {
            padding: 10px;
            background: #f0f0f0;
            border-radius: 6px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .list-item:hover {
            background: #e8e8e8;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal.active {
            display: flex;
        }
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 16px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        .modal-header {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .actions {
            display: flex;
            gap: 10px;
            justify-content: center;
            padding: 20px;
            background: #f8f9fa;
        }
        .hint {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }
        .preview-box {
            background: #f4f4f4;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            font-family: monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>鸣潮账号规划文档编辑器</h1>
            <p>引导式输入，自动生成 LaTeX 和 PDF</p>
        </div>
        
        <div class="content">
            <!-- 基本信息 -->
            <div class="section">
                <div class="section-title">基本信息</div>
                <div class="form-row">
                    <div class="form-group">
                        <label>UID</label>
                        <input type="text" id="uid" placeholder="例如: 117515024">
                    </div>
                    <div class="form-group">
                        <label>作者</label>
                        <input type="text" id="author" value="鬼神莫能窥">
                    </div>
                </div>
            </div>
            
            <!-- 原文 -->
            <div class="section">
                <div class="section-title">1. 原文（用户提供的原始信息）</div>
                <textarea id="original" placeholder="资源情况、氪金预算、偏好、咨询问题等..."></textarea>
                <div class="hint">提示: 现有150抽，调谐器1500... 大小月卡... 偏向强度...</div>
            </div>
            
            <!-- 配队 -->
            <div class="section">
                <div class="section-title">2. 配队情况</div>
                <div class="teams-grid">
                    <div class="form-group">
                        <label>衍射</label>
                        <input type="text" id="team_衍射" placeholder="21赞+20菲+41守">
                    </div>
                    <div class="form-group">
                        <label>湮灭</label>
                        <input type="text" id="team_湮灭" placeholder="41椿+散+41守">
                    </div>
                    <div class="form-group">
                        <label>导电</label>
                        <input type="text" id="team_导电" placeholder="01相+吟+维">
                    </div>
                    <div class="form-group">
                        <label>冷凝</label>
                        <input type="text" id="team_冷凝" placeholder="61珂+00折+31守">
                    </div>
                    <div class="form-group">
                        <label>热熔</label>
                        <input type="text" id="team_热熔" placeholder="65爱+00琳+10莫">
                    </div>
                    <div class="form-group">
                        <label>气动</label>
                        <input type="text" id="team_气动" placeholder="21卡+00夏+01千">
                    </div>
                </div>
                <div class="hint">格式: 链数+角色名，如 61椿 表示6链椿，00守 表示0链守岸人</div>
            </div>
            
            <!-- 整体情况 -->
            <div class="section">
                <div class="section-title">3. 整体情况/现状分析</div>
                <textarea id="overall" placeholder="配置较好，队伍完整。/ 队伍数量较少，建议优先组建更多完整配队。"></textarea>
            </div>
            
            <!-- 逐队伍分析 -->
            <div class="section">
                <div class="section-title">4. 逐队伍分析</div>
                <div class="list-container" id="team_analysis_list"></div>
                <button class="btn btn-secondary" onclick="openModal('team_analysis')">添加分析</button>
            </div>
            
            <!-- 专题模块 -->
            <div class="section">
                <div class="section-title">5. 专题模块（可自定义专题名）</div>
                <div class="list-container" id="topics_list"></div>
                <button class="btn btn-secondary" onclick="openModal('topic')">添加专题</button>
                <div class="hint">例如: 聚爆爱or震谐爱、西格莉卡vs绯雪、复刻补链等</div>
            </div>
            
            <!-- 未来规划 -->
            <div class="section">
                <div class="section-title">6. 逐版本抽卡建议</div>
                <div class="list-container" id="future_list"></div>
                <button class="btn btn-secondary" onclick="openModal('future')">添加版本建议</button>
            </div>
            
            <!-- 最终结论 -->
            <div class="section">
                <div class="section-title">7. 最终推荐方案/结论</div>
                <textarea id="conclusion" placeholder="抽一个中金/高金的绯雪，然后补绯雪队友。除此之外全跳。"></textarea>
            </div>
            
            <!-- 其他 -->
            <div class="section">
                <div class="section-title">8. 其他（养成建议等）</div>
                <textarea id="others" placeholder="每行一条建议...\n主力主C建议刷到175-180分声骸。\n副C建议刷到150分+共鸣效率达标即可。\n常驻球给琳奈抽满停驻之烟。"></textarea>
            </div>
        </div>
        
        <div class="actions">
            <button class="btn btn-primary" onclick="generateLaTeX()">生成 LaTeX</button>
            <button class="btn btn-primary" onclick="generatePDF()">生成 PDF</button>
            <button class="btn btn-danger" onclick="clearAll()">清空所有</button>
        </div>
    </div>
    
    <!-- 模态框 -->
    <div class="modal" id="modal">
        <div class="modal-content">
            <div class="modal-header" id="modal_title">添加</div>
            <div id="modal_body"></div>
            <div style="margin-top: 20px; text-align: right;">
                <button class="btn btn-secondary" onclick="closeModal()">取消</button>
                <button class="btn btn-primary" onclick="saveModal()">保存</button>
            </div>
        </div>
    </div>
    
    <!-- 预览模态框 -->
    <div class="modal" id="preview_modal">
        <div class="modal-content" style="max-width: 800px;">
            <div class="modal-header">生成的 LaTeX 代码</div>
            <div class="preview-box" id="preview_content"></div>
            <div style="margin-top: 20px; text-align: right;">
                <button class="btn btn-secondary" onclick="closePreview()">关闭</button>
                <button class="btn btn-primary" onclick="downloadLaTeX()">下载 .tex 文件</button>
            </div>
        </div>
    </div>

    <script>
        // 数据存储
        let data = {
            team_analysis: [],
            topics: [],
            future_plans: []
        };
        let currentModalType = '';
        let generatedLaTeX = '';
        
        // 打开模态框
        function openModal(type) {
            currentModalType = type;
            const modal = document.getElementById('modal');
            const title = document.getElementById('modal_title');
            const body = document.getElementById('modal_body');
            
            if (type === 'team_analysis') {
                title.textContent = '添加队伍分析';
                body.innerHTML = `
                    <div class="form-group">
                        <label>队伍名称</label>
                        <input type="text" id="modal_team_name" placeholder="例如: 赞菲">
                    </div>
                    <div class="form-group">
                        <label>分析内容</label>
                        <textarea id="modal_team_content" placeholder="不推荐继续补金，可以继续养成..."></textarea>
                    </div>
                `;
            } else if (type === 'topic') {
                title.textContent = '添加专题';
                body.innerHTML = `
                    <div class="form-group">
                        <label>专题名称</label>
                        <input type="text" id="modal_topic_name" placeholder="例如: 聚爆爱or震谐爱">
                    </div>
                    <div class="form-group">
                        <label>结论（可选）</label>
                        <input type="text" id="modal_topic_conclusion" placeholder="推荐继续玩震谐爱。">
                    </div>
                    <div class="form-group">
                        <label>理由/分析（每行一条）</label>
                        <textarea id="modal_topic_reasons" placeholder="若抽达尼娅组爱达千，那么琳奈莫宁将无就业...\n经我测算，65震爱不太会弱于65聚爱..."></textarea>
                    </div>
                `;
            } else if (type === 'future') {
                title.textContent = '添加版本抽卡建议';
                body.innerHTML = `
                    <div class="form-group">
                        <label>版本</label>
                        <input type="text" id="modal_future_version" placeholder="例如: 3.1下半">
                    </div>
                    <div class="form-group">
                        <label>角色</label>
                        <input type="text" id="modal_future_chars" placeholder="例如: 陆赫斯、嘉贝莉娜">
                    </div>
                    <div class="form-group">
                        <label>建议</label>
                        <textarea id="modal_future_suggestion" placeholder="全跳，不用看一眼"></textarea>
                    </div>
                `;
            }
            
            modal.classList.add('active');
        }
        
        // 关闭模态框
        function closeModal() {
            document.getElementById('modal').classList.remove('active');
        }
        
        // 保存模态框数据
        function saveModal() {
            if (currentModalType === 'team_analysis') {
                const name = document.getElementById('modal_team_name').value;
                const content = document.getElementById('modal_team_content').value;
                if (name && content) {
                    data.team_analysis.push({name, content});
                    updateTeamAnalysisList();
                }
            } else if (currentModalType === 'topic') {
                const name = document.getElementById('modal_topic_name').value;
                const conclusion = document.getElementById('modal_topic_conclusion').value;
                const reasons = document.getElementById('modal_topic_reasons').value.split('\\n').filter(r => r.trim());
                if (name) {
                    data.topics.push({name, conclusion, reasons});
                    updateTopicsList();
                }
            } else if (currentModalType === 'future') {
                const version = document.getElementById('modal_future_version').value;
                const chars = document.getElementById('modal_future_chars').value;
                const suggestion = document.getElementById('modal_future_suggestion').value;
                if (version) {
                    data.future_plans.push({version, chars, suggestion});
                    updateFutureList();
                }
            }
            closeModal();
        }
        
        // 更新列表显示
        function updateTeamAnalysisList() {
            const list = document.getElementById('team_analysis_list');
            list.innerHTML = data.team_analysis.map((item, idx) => `
                <div class="list-item">
                    <span><strong>${item.name}</strong>: ${item.content.substring(0, 50)}...</span>
                    <button class="btn btn-danger" onclick="deleteItem('team_analysis', ${idx})" style="padding: 5px 10px;">删除</button>
                </div>
            `).join('');
        }
        
        function updateTopicsList() {
            const list = document.getElementById('topics_list');
            list.innerHTML = data.topics.map((item, idx) => `
                <div class="list-item">
                    <span><strong>${item.name}</strong></span>
                    <button class="btn btn-danger" onclick="deleteItem('topics', ${idx})" style="padding: 5px 10px;">删除</button>
                </div>
            `).join('');
        }
        
        function updateFutureList() {
            const list = document.getElementById('future_list');
            list.innerHTML = data.future_plans.map((item, idx) => `
                <div class="list-item">
                    <span><strong>${item.version}</strong>: ${item.chars}</span>
                    <button class="btn btn-danger" onclick="deleteItem('future_plans', ${idx})" style="padding: 5px 10px;">删除</button>
                </div>
            `).join('');
        }
        
        // 删除项目
        function deleteItem(type, idx) {
            data[type].splice(idx, 1);
            if (type === 'team_analysis') updateTeamAnalysisList();
            else if (type === 'topics') updateTopicsList();
            else if (type === 'future_plans') updateFutureList();
        }
        
        // 收集表单数据
        function collectFormData() {
            return {
                uid: document.getElementById('uid').value,
                author: document.getElementById('author').value,
                original: document.getElementById('original').value,
                teams: {
                    衍射: document.getElementById('team_衍射').value,
                    湮灭: document.getElementById('team_湮灭').value,
                    导电: document.getElementById('team_导电').value,
                    冷凝: document.getElementById('team_冷凝').value,
                    热熔: document.getElementById('team_热熔').value,
                    气动: document.getElementById('team_气动').value
                },
                overall: document.getElementById('overall').value,
                team_analysis: data.team_analysis,
                topics: data.topics,
                future_plans: data.future_plans,
                conclusion: document.getElementById('conclusion').value,
                others: document.getElementById('others').value.split('\\n').filter(r => r.trim())
            };
        }
        
        // 生成LaTeX
        function generateLaTeX() {
            const formData = collectFormData();
            
            fetch('/generate_latex', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            })
            .then(res => res.json())
            .then(result => {
                generatedLaTeX = result.latex;
                document.getElementById('preview_content').textContent = generatedLaTeX;
                document.getElementById('preview_modal').classList.add('active');
            });
        }
        
        // 生成PDF
        function generatePDF() {
            const formData = collectFormData();
            
            fetch('/generate_pdf', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            })
            .then(res => res.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = formData.uid + '_规划.pdf';
                a.click();
            });
        }
        
        // 关闭预览
        function closePreview() {
            document.getElementById('preview_modal').classList.remove('active');
        }
        
        // 下载LaTeX
        function downloadLaTeX() {
            const blob = new Blob([generatedLaTeX], {type: 'text/plain'});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = document.getElementById('uid').value + '_规划.tex';
            a.click();
        }
        
        // 清空所有
        function clearAll() {
            if (confirm('确定要清空所有内容吗？')) {
                document.getElementById('uid').value = '';
                document.getElementById('original').value = '';
                document.getElementById('overall').value = '';
                document.getElementById('conclusion').value = '';
                document.getElementById('others').value = '';
                
                ['衍射', '湮灭', '导电', '冷凝', '热熔', '气动'].forEach(elem => {
                    document.getElementById('team_' + elem).value = '';
                });
                
                data = {team_analysis: [], topics: [], future_plans: []};
                updateTeamAnalysisList();
                updateTopicsList();
                updateFutureList();
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate_latex', methods=['POST'])
def generate_latex():
    data = request.json
    latex = build_latex(data)
    return jsonify({'latex': latex})

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    latex = build_latex(data)
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False, encoding='utf-8') as f:
        f.write(latex)
        tex_path = f.name
    
    # 编译PDF
    try:
        for _ in range(2):
            subprocess.run(
                ['xelatex', '-interaction=nonstopmode', tex_path],
                cwd=os.path.dirname(tex_path),
                capture_output=True,
                text=True
            )
        
        pdf_path = tex_path.replace('.tex', '.pdf')
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True, 
                           download_name=f"{data['uid']}_规划.pdf")
        else:
            return 'PDF生成失败', 500
    finally:
        # 清理临时文件
        if os.path.exists(tex_path):
            os.remove(tex_path)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

def build_latex(data):
    """构建LaTeX文档"""
    
    # 配队表格
    teams_table = ""
    has_teams = any(data['teams'].values())
    if has_teams:
        teams_table = r"""
\begin{center}
\begin{tabular}{p{1.8cm}p{10cm}}
\toprule
属性 & 配队 \\
\midrule
"""
        for elem in ["衍射", "湮灭", "导电", "冷凝", "热熔", "气动"]:
            val = data['teams'].get(elem, '')
            if val:
                teams_table += f"{elem} & {val} \\\\\n"
            else:
                teams_table += f"{elem} & \\\\\n"
        
        teams_table += r"""\bottomrule
\end{tabular}
\end{center}
"""
    
    # 队伍分析
    team_analysis_section = ""
    if data.get('team_analysis'):
        team_analysis_section = r"\section*{逐队伍分析}" + "\n\\begin{enumerate}\n"
        for item in data['team_analysis']:
            team_analysis_section += f"\\item \\textbf{{{item['name']}}}：{item['content']}\n"
        team_analysis_section += "\\end{enumerate}\n"
    
    # 专题模块
    topics_section = ""
    for topic in data.get('topics', []):
        topics_section += f"\\section*{{{topic['name']}}}\n"
        if topic.get('conclusion'):
            topics_section += f"结论：{topic['conclusion']}\n\n"
        if topic.get('reasons'):
            topics_section += "理由：\n\\begin{enumerate}\n"
            for r in topic['reasons']:
                topics_section += f"\\item {r}\n"
            topics_section += "\\end{enumerate}\n"
    
    # 未来规划
    future_section = ""
    if data.get('future_plans'):
        future_section = r"\section*{逐版本抽卡建议}" + "\n\\begin{enumerate}\n"
        for item in data['future_plans']:
            future_section += f"\\item \\textbf{{{item['version']}}} {item.get('chars', '')}：{item.get('suggestion', '')}\n"
        future_section += "\\end{enumerate}\n"
    
    # 结论
    conclusion_section = ""
    if data.get('conclusion'):
        conclusion_section = f"\\section*{{最终推荐方案}}\n{data['conclusion']}\n"
    
    # 其他
    others_section = ""
    if data.get('others'):
        others_section = r"\section*{其他}" + "\n\\begin{enumerate}\n"
        for item in data['others']:
            others_section += f"\\item {item}\n"
        others_section += "\\end{enumerate}\n"
    
    # 原文
    original_section = ""
    if data.get('original'):
        original_section = f"\\section*{{原文}}\n{data['original']}\n"
    
    # 整体情况
    overall_section = ""
    if data.get('overall'):
        overall_section = f"\\section*{{整体情况}}\n{data['overall']}\n"
    
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
\title{\textbf{uid: """ + data.get('uid', '') + r""" 规划}}
\author{\normalsize """ + data.get('author', '鬼神莫能窥') + r"""}
\date{}

\begin{document}
    \maketitle
    \thispagestyle{empty}
    
""" + original_section + r"""
    \section*{配队}
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

if __name__ == '__main__':
    print("启动鸣潮账号规划文档编辑器...")
    print("请在浏览器中访问: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
