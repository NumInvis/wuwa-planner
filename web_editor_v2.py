#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鸣潮账号规划文档编辑器 - Web版本 V2
新增功能：数据持久化、历史记录管理、语料导出
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import subprocess
import os
import tempfile
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# 数据存储目录
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

# 历史记录文件
HISTORY_FILE = DATA_DIR / 'history.json'
CORPUS_DIR = DATA_DIR / 'corpus'
CORPUS_DIR.mkdir(exist_ok=True)

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>鸣潮账号规划文档编辑器 V2</title>
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
            max-width: 1000px;
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
        .nav-tabs {
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #e0e0e0;
        }
        .nav-tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            border: none;
            background: transparent;
            font-size: 14px;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
        }
        .nav-tab:hover {
            background: #e8e8e8;
        }
        .nav-tab.active {
            color: #667eea;
            border-bottom: 3px solid #667eea;
        }
        .content {
            padding: 30px;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
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
            justify-content: space-between;
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
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input[type="text"],
        textarea,
        select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus,
        textarea:focus,
        select:focus {
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
        .btn-success {
            background: #51cf66;
            color: white;
        }
        .btn-warning {
            background: #ffd43b;
            color: #333;
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
        .history-item {
            padding: 15px;
            background: white;
            border-radius: 8px;
            margin-bottom: 10px;
            border: 2px solid #e0e0e0;
            cursor: pointer;
            transition: all 0.3s;
        }
        .history-item:hover {
            border-color: #667eea;
            box-shadow: 0 2px 10px rgba(102, 126, 234, 0.2);
        }
        .history-item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .history-item-title {
            font-weight: bold;
            color: #333;
        }
        .history-item-date {
            font-size: 12px;
            color: #888;
        }
        .history-item-preview {
            font-size: 13px;
            color: #666;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
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
            flex-wrap: wrap;
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
        .save-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: #51cf66;
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            display: none;
            z-index: 2000;
        }
        .save-status.show {
            display: block;
            animation: fadeInOut 2s ease;
        }
        @keyframes fadeInOut {
            0% { opacity: 0; transform: translateY(-20px); }
            20% { opacity: 1; transform: translateY(0); }
            80% { opacity: 1; transform: translateY(0); }
            100% { opacity: 0; transform: translateY(-20px); }
        }
        .corpus-info {
            background: #e7f5ff;
            border: 1px solid #74c0fc;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .corpus-info h3 {
            color: #1864ab;
            margin-bottom: 10px;
        }
        .corpus-info p {
            color: #495057;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>鸣潮账号规划文档编辑器 V2</h1>
            <p>引导式输入，自动生成 LaTeX 和 PDF | 数据自动保存</p>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="switchTab('editor')">编辑器</button>
            <button class="nav-tab" onclick="switchTab('history')">历史记录</button>
            <button class="nav-tab" onclick="switchTab('corpus')">语料管理</button>
        </div>
        
        <!-- 编辑器标签 -->
        <div id="editor-tab" class="tab-content active">
            <div class="content">
                <!-- 基本信息 -->
                <div class="section">
                    <div class="section-title">
                        <span>基本信息</span>
                        <button class="btn btn-secondary" onclick="saveToHistory()" style="padding: 8px 16px; font-size: 12px;">保存到历史</button>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>UID</label>
                            <input type="text" id="uid" placeholder="例如: 117515024" onchange="autoSave()">
                        </div>
                        <div class="form-group">
                            <label>作者</label>
                            <input type="text" id="author" value="鬼神莫能窥" onchange="autoSave()">
                        </div>
                    </div>
                </div>
                
                <!-- 原文 -->
                <div class="section">
                    <div class="section-title">1. 原文（用户提供的原始信息）</div>
                    <textarea id="original" placeholder="资源情况、氪金预算、偏好、咨询问题等..." onchange="autoSave()"></textarea>
                </div>
                
                <!-- 配队 -->
                <div class="section">
                    <div class="section-title">2. 配队情况</div>
                    <div class="teams-grid">
                        <div class="form-group">
                            <label>衍射</label>
                            <input type="text" id="team_衍射" placeholder="21赞+20菲+41守" onchange="autoSave()">
                        </div>
                        <div class="form-group">
                            <label>湮灭</label>
                            <input type="text" id="team_湮灭" placeholder="41椿+散+41守" onchange="autoSave()">
                        </div>
                        <div class="form-group">
                            <label>导电</label>
                            <input type="text" id="team_导电" placeholder="01相+吟+维" onchange="autoSave()">
                        </div>
                        <div class="form-group">
                            <label>冷凝</label>
                            <input type="text" id="team_冷凝" placeholder="61珂+00折+31守" onchange="autoSave()">
                        </div>
                        <div class="form-group">
                            <label>热熔</label>
                            <input type="text" id="team_热熔" placeholder="65爱+00琳+10莫" onchange="autoSave()">
                        </div>
                        <div class="form-group">
                            <label>气动</label>
                            <input type="text" id="team_气动" placeholder="21卡+00夏+01千" onchange="autoSave()">
                        </div>
                    </div>
                </div>
                
                <!-- 整体情况 -->
                <div class="section">
                    <div class="section-title">3. 整体情况/现状分析</div>
                    <textarea id="overall" placeholder="配置较好，队伍完整。" onchange="autoSave()"></textarea>
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
                    <textarea id="conclusion" placeholder="抽一个中金/高金的绯雪..." onchange="autoSave()"></textarea>
                </div>
                
                <!-- 其他 -->
                <div class="section">
                    <div class="section-title">8. 其他（养成建议等）</div>
                    <textarea id="others" placeholder="每行一条建议..." onchange="autoSave()"></textarea>
                </div>
            </div>
            
            <div class="actions">
                <button class="btn btn-primary" onclick="generateLaTeX()">生成 LaTeX</button>
                <button class="btn btn-primary" onclick="generatePDF()">生成 PDF</button>
                <button class="btn btn-success" onclick="exportJSON()">导出 JSON</button>
                <button class="btn btn-warning" onclick="document.getElementById('import-file').click()">导入 JSON</button>
                <input type="file" id="import-file" style="display:none" accept=".json" onchange="importJSON(this)">
                <button class="btn btn-danger" onclick="clearAll()">清空所有</button>
            </div>
        </div>
        
        <!-- 历史记录标签 -->
        <div id="history-tab" class="tab-content">
            <div class="content">
                <div class="section">
                    <div class="section-title">
                        <span>历史记录</span>
                        <button class="btn btn-danger" onclick="clearAllHistory()" style="padding: 8px 16px; font-size: 12px;">清空历史</button>
                    </div>
                    <div id="history-list"></div>
                </div>
            </div>
        </div>
        
        <!-- 语料管理标签 -->
        <div id="corpus-tab" class="tab-content">
            <div class="content">
                <div class="corpus-info">
                    <h3>📚 语料库功能</h3>
                    <p>所有保存的历史记录都会自动转换为训练语料，存储在 data/corpus/ 目录下。<br>
                    语料格式包含完整的输入-输出对，适合用于训练AI模型。</p>
                </div>
                
                <div class="section">
                    <div class="section-title">语料统计</div>
                    <div id="corpus-stats">
                        <p>加载中...</p>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">语料操作</div>
                    <div class="actions" style="background: transparent; padding: 0;">
                        <button class="btn btn-primary" onclick="exportCorpus()">导出全部语料</button>
                        <button class="btn btn-secondary" onclick="viewCorpusSample()">查看样例</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 保存状态提示 -->
    <div class="save-status" id="save-status">已自动保存</div>
    
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
        let autoSaveTimer = null;
        
        // 切换标签
        function switchTab(tab) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
            
            if (tab === 'history') {
                loadHistoryList();
            } else if (tab === 'corpus') {
                loadCorpusStats();
            }
        }
        
        // 自动保存
        function autoSave() {
            if (autoSaveTimer) {
                clearTimeout(autoSaveTimer);
            }
            autoSaveTimer = setTimeout(() => {
                saveToServer();
            }, 1000);
        }
        
        // 保存到服务器
        function saveToServer() {
            const formData = collectFormData();
            fetch('/autosave', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            }).then(() => {
                showSaveStatus();
            });
        }
        
        // 显示保存状态
        function showSaveStatus() {
            const status = document.getElementById('save-status');
            status.classList.add('show');
            setTimeout(() => {
                status.classList.remove('show');
            }, 2000);
        }
        
        // 保存到历史
        function saveToHistory() {
            const formData = collectFormData();
            if (!formData.uid) {
                alert('请先输入UID');
                return;
            }
            
            fetch('/save_history', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            }).then(res => res.json())
            .then(result => {
                alert('已保存到历史记录');
            });
        }
        
        // 加载历史列表
        function loadHistoryList() {
            fetch('/get_history')
                .then(res => res.json())
                .then(history => {
                    const container = document.getElementById('history-list');
                    if (history.length === 0) {
                        container.innerHTML = '<p style="text-align: center; color: #888;">暂无历史记录</p>';
                        return;
                    }
                    
                    container.innerHTML = history.map((item, idx) => `
                        <div class="history-item" onclick="loadHistoryItem(${idx})">
                            <div class="history-item-header">
                                <span class="history-item-title">UID: ${item.uid}</span>
                                <span class="history-item-date">${item.timestamp}</span>
                            </div>
                            <div class="history-item-preview">${item.preview || '无预览'}</div>
                            <div style="margin-top: 10px;">
                                <button class="btn btn-secondary" onclick="event.stopPropagation(); deleteHistoryItem(${idx})" style="padding: 5px 10px; font-size: 12px;">删除</button>
                            </div>
                        </div>
                    `).join('');
                });
        }
        
        // 加载历史项
        function loadHistoryItem(idx) {
            fetch('/get_history')
                .then(res => res.json())
                .then(history => {
                    if (history[idx]) {
                        loadFormData(history[idx]);
                        switchTab('editor');
                        document.querySelector('.nav-tab').click();
                    }
                });
        }
        
        // 删除历史项
        function deleteHistoryItem(idx) {
            if (!confirm('确定删除这条记录吗？')) return;
            
            fetch('/delete_history', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({index: idx})
            }).then(() => {
                loadHistoryList();
            });
        }
        
        // 清空所有历史
        function clearAllHistory() {
            if (!confirm('确定清空所有历史记录吗？此操作不可恢复！')) return;
            
            fetch('/clear_history', {method: 'POST'})
                .then(() => {
                    loadHistoryList();
                });
        }
        
        // 加载语料统计
        function loadCorpusStats() {
            fetch('/corpus_stats')
                .then(res => res.json())
                .then(stats => {
                    document.getElementById('corpus-stats').innerHTML = `
                        <p><strong>总记录数:</strong> ${stats.total_records}</p>
                        <p><strong>总字数:</strong> ${stats.total_chars}</p>
                        <p><strong>存储位置:</strong> ${stats.corpus_dir}</p>
                    `;
                });
        }
        
        // 导出语料
        function exportCorpus() {
            window.location.href = '/export_corpus';
        }
        
        // 查看语料样例
        function viewCorpusSample() {
            fetch('/corpus_sample')
                .then(res => res.json())
                .then(sample => {
                    document.getElementById('preview_content').textContent = JSON.stringify(sample, null, 2);
                    document.getElementById('preview_modal').classList.add('active');
                });
        }
        
        // 导出JSON
        function exportJSON() {
            const formData = collectFormData();
            const blob = new Blob([JSON.stringify(formData, null, 2)], {type: 'application/json'});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = (formData.uid || 'unnamed') + '_data.json';
            a.click();
        }
        
        // 导入JSON
        function importJSON(input) {
            const file = input.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const data = JSON.parse(e.target.result);
                    loadFormData(data);
                    alert('导入成功');
                } catch (err) {
                    alert('导入失败: ' + err.message);
                }
            };
            reader.readAsText(file);
            input.value = '';
        }
        
        // 加载表单数据
        function loadFormData(data) {
            document.getElementById('uid').value = data.uid || '';
            document.getElementById('author').value = data.author || '鬼神莫能窥';
            document.getElementById('original').value = data.original || '';
            document.getElementById('overall').value = data.overall || '';
            document.getElementById('conclusion').value = data.conclusion || '';
            document.getElementById('others').value = data.others ? data.others.join('\\n') : '';
            
            const teams = data.teams || {};
            ['衍射', '湮灭', '导电', '冷凝', '热熔', '气动'].forEach(elem => {
                document.getElementById('team_' + elem).value = teams[elem] || '';
            });
            
            window.data = {
                team_analysis: data.team_analysis || [],
                topics: data.topics || [],
                future_plans: data.future_plans || []
            };
            
            updateTeamAnalysisList();
            updateTopicsList();
            updateFutureList();
        }
        
        // 其他原有函数...
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
                        <textarea id="modal_team_content" placeholder="不推荐继续补金..."></textarea>
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
                        <textarea id="modal_topic_reasons" placeholder="理由1...\\n理由2..."></textarea>
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
        
        function closeModal() {
            document.getElementById('modal').classList.remove('active');
            editingIndex = null;
            editingType = null;
        }
        
        function updateTeamAnalysisList() {
            const list = document.getElementById('team_analysis_list');
            list.innerHTML = data.team_analysis.map((item, idx) => `
                <div class="list-item">
                    <span><strong>${item.name}</strong>: ${item.content.substring(0, 50)}...</span>
                    <div>
                        <button class="btn btn-secondary" onclick="editItem('team_analysis', ${idx})" style="padding: 5px 10px; margin-right: 5px;">编辑</button>
                        <button class="btn btn-danger" onclick="deleteItem('team_analysis', ${idx})" style="padding: 5px 10px;">删除</button>
                    </div>
                </div>
            `).join('');
        }
        
        function updateTopicsList() {
            const list = document.getElementById('topics_list');
            list.innerHTML = data.topics.map((item, idx) => `
                <div class="list-item">
                    <span><strong>${item.name}</strong></span>
                    <div>
                        <button class="btn btn-secondary" onclick="editItem('topics', ${idx})" style="padding: 5px 10px; margin-right: 5px;">编辑</button>
                        <button class="btn btn-danger" onclick="deleteItem('topics', ${idx})" style="padding: 5px 10px;">删除</button>
                    </div>
                </div>
            `).join('');
        }
        
        function updateFutureList() {
            const list = document.getElementById('future_list');
            list.innerHTML = data.future_plans.map((item, idx) => `
                <div class="list-item">
                    <span><strong>${item.version}</strong>: ${item.chars}</span>
                    <div>
                        <button class="btn btn-secondary" onclick="editItem('future_plans', ${idx})" style="padding: 5px 10px; margin-right: 5px;">编辑</button>
                        <button class="btn btn-danger" onclick="deleteItem('future_plans', ${idx})" style="padding: 5px 10px;">删除</button>
                    </div>
                </div>
            `).join('');
        }
        
        let editingIndex = null;
        let editingType = null;
        
        function editItem(type, idx) {
            editingIndex = idx;
            editingType = type;
            const item = data[type][idx];
            
            const modal = document.getElementById('modal');
            const title = document.getElementById('modal_title');
            const body = document.getElementById('modal_body');
            
            if (type === 'team_analysis') {
                title.textContent = '编辑队伍分析';
                body.innerHTML = `
                    <div class="form-group">
                        <label>队伍名称</label>
                        <input type="text" id="modal_team_name" value="${item.name}">
                    </div>
                    <div class="form-group">
                        <label>分析内容</label>
                        <textarea id="modal_team_content">${item.content}</textarea>
                    </div>
                `;
            } else if (type === 'topics') {
                title.textContent = '编辑专题';
                body.innerHTML = `
                    <div class="form-group">
                        <label>专题名称</label>
                        <input type="text" id="modal_topic_name" value="${item.name}">
                    </div>
                    <div class="form-group">
                        <label>结论（可选）</label>
                        <input type="text" id="modal_topic_conclusion" value="${item.conclusion || ''}">
                    </div>
                    <div class="form-group">
                        <label>理由/分析（每行一条）</label>
                        <textarea id="modal_topic_reasons">${item.reasons ? item.reasons.join('\\n') : ''}</textarea>
                    </div>
                `;
            } else if (type === 'future_plans') {
                title.textContent = '编辑版本抽卡建议';
                body.innerHTML = `
                    <div class="form-group">
                        <label>版本</label>
                        <input type="text" id="modal_future_version" value="${item.version}">
                    </div>
                    <div class="form-group">
                        <label>角色</label>
                        <input type="text" id="modal_future_chars" value="${item.chars || ''}">
                    </div>
                    <div class="form-group">
                        <label>建议</label>
                        <textarea id="modal_future_suggestion">${item.suggestion || ''}</textarea>
                    </div>
                `;
            }
            
            modal.classList.add('active');
        }
        
        function deleteItem(type, idx) {
            data[type].splice(idx, 1);
            if (type === 'team_analysis') updateTeamAnalysisList();
            else if (type === 'topics') updateTopicsList();
            else if (type === 'future_plans') updateFutureList();
            autoSave();
        }
        
        function saveModal() {
            if (editingIndex !== null && editingType) {
                // 编辑模式
                if (editingType === 'team_analysis') {
                    const name = document.getElementById('modal_team_name').value;
                    const content = document.getElementById('modal_team_content').value;
                    if (name && content) {
                        data.team_analysis[editingIndex] = {name, content};
                        updateTeamAnalysisList();
                    }
                } else if (editingType === 'topics') {
                    const name = document.getElementById('modal_topic_name').value;
                    const conclusion = document.getElementById('modal_topic_conclusion').value;
                    const reasons = document.getElementById('modal_topic_reasons').value.split('\\n').filter(r => r.trim());
                    if (name) {
                        data.topics[editingIndex] = {name, conclusion, reasons};
                        updateTopicsList();
                    }
                } else if (editingType === 'future_plans') {
                    const version = document.getElementById('modal_future_version').value;
                    const chars = document.getElementById('modal_future_chars').value;
                    const suggestion = document.getElementById('modal_future_suggestion').value;
                    if (version) {
                        data.future_plans[editingIndex] = {version, chars, suggestion};
                        updateFutureList();
                    }
                }
                editingIndex = null;
                editingType = null;
            } else {
                // 新增模式
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
            }
            closeModal();
            autoSave();
        }
        
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
        
        function closePreview() {
            document.getElementById('preview_modal').classList.remove('active');
        }
        
        function downloadLaTeX() {
            const blob = new Blob([generatedLaTeX], {type: 'text/plain'});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = document.getElementById('uid').value + '_规划.tex';
            a.click();
        }
        
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
                autoSave();
            }
        }
        
        // 页面加载时恢复自动保存的数据
        window.onload = function() {
            fetch('/get_autosave')
                .then(res => res.json())
                .then(data => {
                    if (data && data.uid) {
                        loadFormData(data);
                    }
                });
        };
    </script>
</body>
</html>
'''


def build_latex(data):
    """构建LaTeX文档"""
    
    def escape_latex(text):
        """转义LaTeX特殊字符"""
        if not text:
            return ""
        replacements = [
            ('\\', '\\textbackslash{}'),
            ('&', '\\&'),
            ('%', '\\%'),
            ('$', '\\$'),
            ('#', '\\#'),
            ('_', '\\_'),
            ('{', '\\{'),
            ('}', '\\}'),
            ('~', '\\textasciitilde{}'),
            ('^', '\\textasciicircum{}'),
        ]
        for old, new in replacements:
            text = text.replace(old, new)
        return text
    
    # 配队表格
    teams_table = ""
    has_teams = any(data.get('teams', {}).values())
    if has_teams:
        teams_table = r"""
\begin{center}
\begin{tabular}{p{1.8cm}p{10cm}}
\toprule
属性 & 配队 \\
\midrule
"""
        for elem in ["衍射", "湮灭", "导电", "冷凝", "热熔", "气动"]:
            val = data.get('teams', {}).get(elem, '')
            if val:
                teams_table += f"{elem} & {escape_latex(val)} \\\\\n"
            else:
                teams_table += f"{elem} & \\\\\n"
        
        teams_table += r"""\bottomrule
\end{tabular}
\end{center}
"""
    
    # 构建各部分
    sections = []
    
    # 原文
    if data.get('original'):
        sections.append(f"\\section*{{原文}}\n{escape_latex(data['original'])}")
    
    # 配队
    sections.append("\\section*{配队}\n" + teams_table)
    
    # 整体情况
    if data.get('overall'):
        sections.append(f"\\section*{{整体情况}}\n{escape_latex(data['overall'])}")
    
    # 逐队伍分析
    if data.get('team_analysis'):
        content = r"\section*{逐队伍分析}" + "\n\\begin{enumerate}\n"
        for item in data['team_analysis']:
            content += f"\\item \\textbf{{{escape_latex(item['name'])}}}：{escape_latex(item['content'])}\n"
        content += "\\end{enumerate}"
        sections.append(content)
    
    # 专题模块
    for topic in data.get('topics', []):
        content = f"\\section*{{{escape_latex(topic['name'])}}}\n"
        if topic.get('conclusion'):
            content += f"结论：{escape_latex(topic['conclusion'])}\n\n"
        if topic.get('reasons'):
            content += "理由：\n\\begin{enumerate}\n"
            for r in topic['reasons']:
                content += f"\\item {escape_latex(r)}\n"
            content += "\\end{enumerate}"
        sections.append(content)
    
    # 未来规划
    if data.get('future_plans'):
        content = r"\section*{逐版本抽卡建议}" + "\n\\begin{enumerate}\n"
        for item in data['future_plans']:
            content += f"\\item \\textbf{{{escape_latex(item['version'])}}} {escape_latex(item.get('chars', ''))}：{escape_latex(item.get('suggestion', ''))}\n"
        content += "\\end{enumerate}"
        sections.append(content)
    
    # 结论
    if data.get('conclusion'):
        sections.append(f"\\section*{{最终推荐方案}}\n{escape_latex(data['conclusion'])}")
    
    # 其他
    if data.get('others'):
        content = r"\section*{其他}" + "\n\\begin{enumerate}\n"
        for item in data['others']:
            content += f"\\item {escape_latex(item)}\n"
        content += "\\end{enumerate}"
        sections.append(content)
    
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
\title{\textbf{uid: """ + escape_latex(data.get('uid', '')) + r""" 规划}}
\author{\normalsize """ + escape_latex(data.get('author', '鬼神莫能窥')) + r"""}
\date{}

\begin{document}
    \maketitle
    \thispagestyle{empty}
    
""" + "\n\n".join(sections) + r"""
\end{document}
"""
    return latex


# 自动保存文件
AUTOSAVE_FILE = DATA_DIR / 'autosave.json'


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/autosave', methods=['POST'])
def autosave():
    """自动保存"""
    data = request.json
    with open(AUTOSAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({'status': 'ok'})


@app.route('/get_autosave')
def get_autosave():
    """获取自动保存的数据"""
    if AUTOSAVE_FILE.exists():
        with open(AUTOSAVE_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({})


@app.route('/save_history', methods=['POST'])
def save_history():
    """保存到历史记录"""
    data = request.json
    
    # 添加时间戳和预览
    data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data['preview'] = data.get('overall', '')[:50] + '...' if data.get('overall') else '无预览'
    
    # 读取现有历史
    history = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
    
    # 添加到开头
    history.insert(0, data)
    
    # 限制历史记录数量（保留最近50条）
    history = history[:50]
    
    # 保存
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    # 同时保存为语料
    save_to_corpus(data)
    
    return jsonify({'status': 'ok'})


def save_to_corpus(data):
    """保存为训练语料"""
    corpus_item = {
        'input': {
            'uid': data.get('uid'),
            'teams': data.get('teams'),
            'original': data.get('original'),
        },
        'output': {
            'overall': data.get('overall'),
            'team_analysis': data.get('team_analysis'),
            'topics': data.get('topics'),
            'future_plans': data.get('future_plans'),
            'conclusion': data.get('conclusion'),
            'others': data.get('others'),
        },
        'metadata': {
            'timestamp': data.get('timestamp'),
            'author': data.get('author'),
        }
    }
    
    # 生成文件名
    filename = f"{data.get('uid', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = CORPUS_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(corpus_item, f, ensure_ascii=False, indent=2)


@app.route('/get_history')
def get_history():
    """获取历史记录"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify([])


@app.route('/delete_history', methods=['POST'])
def delete_history():
    """删除历史记录"""
    idx = request.json.get('index')
    
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if 0 <= idx < len(history):
            history.pop(idx)
            
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
    
    return jsonify({'status': 'ok'})


@app.route('/clear_history', methods=['POST'])
def clear_history():
    """清空历史记录"""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    return jsonify({'status': 'ok'})


@app.route('/corpus_stats')
def corpus_stats():
    """获取语料统计"""
    corpus_files = list(CORPUS_DIR.glob('*.json'))
    total_records = len(corpus_files)
    total_chars = 0
    
    for f in corpus_files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            total_chars += len(content)
    
    return jsonify({
        'total_records': total_records,
        'total_chars': total_chars,
        'corpus_dir': str(CORPUS_DIR)
    })


@app.route('/corpus_sample')
def corpus_sample():
    """获取语料样例"""
    corpus_files = list(CORPUS_DIR.glob('*.json'))
    if corpus_files:
        with open(corpus_files[0], 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({'error': 'No corpus available'})


@app.route('/export_corpus')
def export_corpus():
    """导出全部语料"""
    import zipfile
    import io
    
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for corpus_file in CORPUS_DIR.glob('*.json'):
            zf.write(corpus_file, corpus_file.name)
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='wuwa_corpus.zip'
    )


@app.route('/generate_latex', methods=['POST'])
def generate_latex():
    data = request.json
    latex = build_latex(data)
    return jsonify({'latex': latex})


@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    latex = build_latex(data)
    
    tex_path = None
    pdf_path = None
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False, encoding='utf-8') as f:
            f.write(latex)
            tex_path = f.name
        
        pdf_path = tex_path.replace('.tex', '.pdf')
        
        for _ in range(2):
            subprocess.run(
                ['xelatex', '-interaction=nonstopmode', tex_path],
                cwd=os.path.dirname(tex_path),
                capture_output=True,
                text=True,
                timeout=60
            )
        
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True, 
                           download_name=f"{data.get('uid', 'unnamed')}_规划.pdf")
        else:
            return jsonify({'error': 'PDF生成失败'}), 500
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'PDF生成超时'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        for path in [tex_path, pdf_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass


if __name__ == '__main__':
    print("=" * 60)
    print("鸣潮账号规划文档编辑器 V2")
    print("=" * 60)
    print(f"数据存储目录: {DATA_DIR}")
    print(f"语料存储目录: {CORPUS_DIR}")
    print("=" * 60)
    print("请在浏览器中访问: http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
