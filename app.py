
import streamlit as st
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 網站設定
st.set_page_config(
    page_title="我的零用錢記帳本",
    page_icon="💰",
    layout="wide"
)

# 中文字型設定
plt.rcParams['font.sans-serif'] = [
    'Microsoft JhengHei',
    'Noto Sans CJK TC',
    'Arial Unicode MS',
    'DejaVu Sans'
]
plt.rcParams['axes.unicode_minus'] = False

FILE = Path("records.json")


# 讀取紀錄
def load_records():
    if not FILE.exists():
        return []

    try:
        with open(FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        st.error("紀錄檔格式不正確，請檢查 records.json")
        return []

    except (json.JSONDecodeError, OSError):
        st.error("讀取紀錄失敗，請檢查 records.json")
        return []


# 儲存紀錄
def save_records(records):
    try:
        with open(FILE, 'w', encoding='utf-8') as f:
            json.dump(
                records,
                f,
                ensure_ascii=False,
                indent=2
            )
        return True

    except OSError as e:
        st.error(f"儲存失敗：{e}")
        return False


# 標題
st.title('💰 我的零用錢記帳本')
st.write('記錄每天的收入與支出，掌握自己的小金庫！')

# 讀取資料
records = load_records()

# 清空紀錄
if st.button('🗑️ 清空所有紀錄'):
    if FILE.exists():
        try:
            FILE.unlink()
        except OSError as e:
            st.error(f"清空失敗：{e}")
        else:
            st.success("紀錄已清空！")
            st.rerun()
    else:
        st.info("目前沒有任何紀錄")

st.divider()

# 新增紀錄
st.subheader('📝 新增記帳紀錄')

with st.form('add_form', clear_on_submit=True):

    date = st.date_input('日期')

    kind = st.radio(
        '收入還是支出？',
        ['支出', '收入'],
        horizontal=True
    )

    category = st.selectbox(
        '類別',
        ['飲食', '交通', '娛樂', '文具', '零用錢', '吃答辯', '購買男童']
    )

    item = st.text_input(
        '項目',
        placeholder='例如：珍奶'
    )

    amount = st.number_input(
        '金額',
        min_value=0,
        step=10
    )

    submitted = st.form_submit_button('記下來')

if submitted:

    if item.strip() == '' or amount <= 0:
        st.error('項目和金額都要填喔！')

    else:
        new_record = {
            '日期': str(date),
            '收支': kind,
            '類別': category,
            '項目': item.strip(),
            '金額': int(amount)
        }

        records.append(new_record)

        if save_records(records):
            st.success(f'已記下：{item} {amount} 元')
            st.rerun()

st.divider()

# 統計收入和支出
income = sum(
    r['金額'] for r in records
    if r['收支'] == '收入'
)

expense = sum(
    r['金額'] for r in records
    if r['收支'] == '支出'
)

balance = income - expense

# 顯示統計
st.subheader('📊 我的財務統計')

col1, col2, col3 = st.columns(3)

col1.metric('💵 總收入', f'{income:,} 元')
col2.metric('💸 總支出', f'{expense:,} 元')
col3.metric('💰 目前餘額', f'{balance:,} 元')

st.divider()

# 記帳明細
st.subheader('📋 記帳明細')

if records:
    st.dataframe(
        records,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info('目前還沒有記帳紀錄，快來新增第一筆吧！')

st.divider()

# 圖一：各類別支出圓餅圖
st.subheader('🥧 錢都花到哪裡去了？')

totals = {}

for r in records:
    if r['收支'] == '支出':
        category = r['類別']
        totals[category] = (
            totals.get(category, 0) + r['金額']
        )

if totals and sum(totals.values()) > 0:

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.pie(
        list(totals.values()),
        labels=list(totals.keys()),
        autopct='%1.1f%%',
        startangle=90
    )

    ax.set_title('各類別支出比例')

    st.pyplot(fig)
    plt.close(fig)

else:
    st.info('還沒有支出記錄')

st.divider()

# 圖二：餘額變化折線圖
st.subheader('📈 餘額變化')

if records:

    records_sorted = sorted(
        records,
        key=lambda r: r['日期']
    )

    changes = []

    for r in records_sorted:

        if r['收支'] == '收入':
            changes.append(r['金額'])
        else:
            changes.append(-r['金額'])

    balance_history = np.cumsum(changes)

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(
        range(1, len(balance_history) + 1),
        balance_history,
        marker='o',
        color='blue',
        linewidth=2
    )

    ax.axhline(
        0,
        color='red',
        linewidth=1
    )

    ax.set_title('每筆記帳後的餘額')
    ax.set_xlabel('第幾筆')
    ax.set_ylabel('餘額（元）')
    ax.grid(True, alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)

else:
    st.info('新增紀錄後，就會顯示餘額變化！')

# 頁尾
st.divider()
st.caption('💰 我的零用錢記帳本｜每天記帳，學會理財！')
