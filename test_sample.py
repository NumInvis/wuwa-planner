#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试示例 - 非交互式快速测试
"""

from agent import WuWaAgent, AccountInfo, Team, Character, ElementType, CharacterRole

def test_quick():
    """快速测试，使用预设数据"""
    agent = WuWaAgent()
    
    # 创建测试账号数据
    agent.account = AccountInfo(
        uid="123456789",
        star_sounds=500,
        tuners=2000,
        tuners_device=10,
        coral=800,
        monthly_card=True,
        big_monthly=True,
        weekly_card=False,
        budget="礼包看情况",
        avoid_male=True,
        preferences="偏向强度，喜欢少女角色",
        questions="后续怎么抽？要不要补链？",
        teams=[
            Team(element=ElementType.HAVOC, characters=[
                Character(name="椿", element=ElementType.HAVOC, role=CharacterRole.MAIN_DPS, constellation=0, weapon_rank=0),
                Character(name="散华", element=ElementType.HAVOC, role=CharacterRole.SUB_DPS, constellation=6, weapon_rank=0),
            ]),
            Team(element=ElementType.AERO, characters=[
                Character(name="卡提", element=ElementType.AERO, role=CharacterRole.MAIN_DPS, constellation=3, weapon_rank=1),
                Character(name="夏空", element=ElementType.AERO, role=CharacterRole.SUB_DPS, constellation=0, weapon_rank=0),
                Character(name="千咲", element=ElementType.AERO, role=CharacterRole.SUPPORT, constellation=0, weapon_rank=1),
            ]),
            Team(element=ElementType.FUSION, characters=[
                Character(name="爱弥斯", element=ElementType.FUSION, role=CharacterRole.MAIN_DPS, constellation=6, weapon_rank=1),
                Character(name="琳奈", element=ElementType.FUSION, role=CharacterRole.SUB_DPS, constellation=0, weapon_rank=0),
            ]),
        ]
    )
    
    # 分析
    print("=" * 60)
    print("开始分析...")
    print("=" * 60)
    
    agent.analyze()
    
    print("\n整体情况:")
    print(agent.analysis_result['overall'])
    
    print("\n队伍分析:")
    for team in agent.analysis_result['teams_analysis']:
        print(f"  {team['element']}: {team['suggestion']}")
    
    # 生成LaTeX
    print("\n" + "=" * 60)
    print("生成LaTeX文件...")
    print("=" * 60)
    
    tex_path = agent.save_latex("test_output.tex")
    
    # 读取并显示生成的LaTeX
    with open(tex_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"\nLaTeX文件已生成，共 {len(content)} 字符")
        print("\n前1500字符预览:")
        print("-" * 60)
        print(content[:1500])
        print("...")
    
    # 尝试编译PDF
    print("\n" + "=" * 60)
    print("尝试编译PDF...")
    print("=" * 60)
    
    pdf_path = agent.compile_pdf(tex_path)
    
    if pdf_path:
        print(f"\n✅ 成功生成PDF: {pdf_path}")
    else:
        print("\n❌ PDF生成失败，但LaTeX文件已保存")
        print(f"   你可以手动编译: xelatex {tex_path}")

if __name__ == "__main__":
    test_quick()
