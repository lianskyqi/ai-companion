import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

# 语言配置
LANGUAGE_OPTIONS = {
    "中文": {
        "title": "AI 智能伴侣",
        "session_time": "会话时间",
        "input_placeholder": "请输入你的问题",
        "sidebar_title": "AI 控制面板",
        "partner_info": "伴侣信息",
        "nickname_label": "昵称",
        "nickname_original": "小甜甜",
        "nickname_placeholder": "请输入昵称",
        "nature_label": "性格",
        "nature_original": "一只可爱的猫娘",
        "nature_placeholder": "请输入性格",
        "new_session": "✏️新建会话",
        "history_sessions": "历史会话",
        "system_prompt": """
        你叫 %s，现在是用户的伴侣，请代入伴侣角色。
        规则：
            1. 每次只回 1 条消息
            2. 禁止任何场景或状态描述性文字
            3. 匹配用户的语言
            4. 回复简短，像聊天一样
            5. 有需要的话可以用 emoji 表情和颜文字
            6. 用符合伴侣性格的方式对话
            7. 回复的内容，要充分体现伴侣的性格特征
        伴侣性格：
            - %s
    """
    },
    "English": {
        "title": "AI Intelligent Partner",
        "session_time": "Session Time",
        "input_placeholder": "Enter your question",
        "sidebar_title": "AI Control Panel",
        "partner_info": "Partner Information",
        "nickname_label": "Nickname",
        "nickname_original": "Sweetie",
        "nickname_placeholder": "Enter nickname",
        "nature_label": "Personality",
        "nature_original": "a cute cat girl",
        "nature_placeholder": "Enter personality",
        "new_session": "✏️New Session",
        "history_sessions": "History Sessions",
        "system_prompt": """
        Your name is %s, you are now the user's partner, please play the role of a partner.
        Rules:
            1. Only send 1 message at a time
            2. No situational or descriptive text
            3. Match the user's language
            4. Keep responses brief, like a conversation
            5. Use emoji and emoticons if needed
            6. Communicate in a way that fits the partner's personality
            7. The content should fully reflect the partner's personality characteristics
        Partner Personality:
            - %s
    """
    },
    "日本語": {
        "title": "AI コンパニオン",
        "session_time": "時間",
        "input_placeholder": "質問してみましょう",
        "sidebar_title": "AI コントロールパネル",
        "partner_info": "パートナー情報",
        "nickname_label": "ニックネーム",
        "nickname_original": "あまちゃん~",
        "nickname_placeholder": "ニックネームを入力してください",
        "nature_label": "性格",
        "nature_original": "かわいい猫娘",
        "nature_placeholder": "性格を入力してください",
        "new_session": "✏️新しいチャット",
        "history_sessions": "あなたのチャット",
        "system_prompt": """
        あなたの名前は %s、あなたは現在ユーザーのパートナーです、パートナーの役割を演じてください。
        ルール：
            1. 一度に 1 つのメッセージだけを送信
            2. 状況や説明文は禁止
            3. ユーザーの言語に一致
            4. 会話のように簡潔な返信
            5. 必要に応じて絵文字や顔文字を使用
            6. パートナーの性格に合った方法で会話
            7. 返信内容はパートナーの性格特徴を十分に反映
        パートナーの性格：
            - %s
    """
    }
}

# 初始化语言
if 'language' not in st.session_state:
    st.session_state.language = "中文"

# 获取当前语言配置
current_lang = LANGUAGE_OPTIONS[st.session_state.language]

st.set_page_config(
        page_title="Your AI Partner",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

# 保存会话信息
def save_session():
    if st.session_state.current_session:
        # 构建新的会话对象
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }

        # 如果文件夹不存在，则创建
        if not os.path.exists("../session"):
            os.mkdir("../session")

        # 保存会话信息
        with open(f"session/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

# 生成会话标识
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 加载所有的会话列表信息
def load_sessions():
    session_list = []
    # 加载session目录下的文件
    if os.path.exists("../session"):
        file_list = os.listdir("../session")
        for file in file_list:
            if file.endswith(".json"):
                session_list.append(file[:-5])
    session_list.sort(reverse=True) # 降序
    return session_list

# 加载指定会话信息
def load_session(session_name):
    try:
        if os.path.exists(f"session/{session_name}.json"):
            with open(f"session/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_name
    except Exception:
        st.error('加载会话失败')

# 删除会话信息
def delete_session(session_name):
    try:
        if os.path.exists(f"session/{session_name}.json"):
            os.remove(f"session/{session_name}.json")
            # 如果删除的是当前会话，则更新当前会话标识
            if st.session_state.current_session == session_name:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
    except Exception:
        st.error('删除会话失败')

st.title(current_lang["title"])
st.logo("resource/logo.png")

# 系统提示
system_prompt = current_lang["system_prompt"]

# 初始化聊天记录
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'nick_name' not in st.session_state:
    st.session_state.nick_name = current_lang["nickname_original"]
if 'nature' not in st.session_state:
    st.session_state.nature = current_lang["nature_original"]
if 'current_session' not in st.session_state:   # 会话标识
    st.session_state.current_session = generate_session_name()

# 展示聊天记录
st.text(f'{current_lang["session_time"]}: {st.session_state.current_session}')
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# 右上角语言选择器
col1, col2 = st.columns([6, 1])
with col1:
    pass  # 占位
with col2:
    selected_language = st.selectbox(
        '',
        options=list(LANGUAGE_OPTIONS.keys()),
        index=list(LANGUAGE_OPTIONS.keys()).index(st.session_state.language),
        key="language_selector"
    )

    # 如果语言改变，更新会话状态
    if selected_language != st.session_state.language:
        st.session_state.language = selected_language
        current_lang = LANGUAGE_OPTIONS[st.session_state.language]
        # 保存当前会话信息
        save_session()
        # 更新默认昵称和性格为新语言的默认值
        st.session_state.nick_name = LANGUAGE_OPTIONS[selected_language]["nickname_original"]
        st.session_state.nature = LANGUAGE_OPTIONS[selected_language]["nature_original"]
        # 创建新的对话
        if st.session_state.messages:   # 聊天记录不为空 True
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
        st.rerun() # 重新运行当前页面

# 初始化OpenAI
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

# 侧边栏
with st.sidebar:
    st.title(current_lang["sidebar_title"])
    st.subheader(current_lang["partner_info"])
    nick_name = st.text_input(current_lang["nickname_label"], placeholder=current_lang["nickname_placeholder"], value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    nature = st.text_area(current_lang["nature_label"], placeholder=current_lang["nature_placeholder"], value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

    # 分割线
    st.divider()

    # 新建会话
    if st.button(label=current_lang["new_session"], width="stretch"):
        # 保存当前会话信息
        save_session()

        # 创建新的对话
        if st.session_state.messages:   # 聊天记录不为空 True
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun() # 重新运行当前页面

    # 历史会话
    st.text(current_lang["history_sessions"])
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            # 加载会话信息
            # 三元运算符：
            if st.button(session, width='stretch', icon='📝', key=f'load_{session}',
                         type='primary' if session == st.session_state.current_session else 'secondary'):
                load_session(session)
                st.rerun()
        with col2:
            if st.button(label='', width='stretch', icon='❌', key=f'delete_{session}'):  # 删除会话
                delete_session(session)


# 获取用户输入
prompt = st.chat_input(current_lang["input_placeholder"])
if prompt:
    st.chat_message("user").write(prompt)
    print('调用 AI 大模型，提示词：')
    # 添加用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": current_lang["system_prompt"] % (st.session_state.nick_name, st.session_state.nature)},
            *st.session_state.messages
        ],
        stream=True
    )

    # 非流式输出
    # print('大模型返回结果：', response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)

    # 流式输出
    response_message = st.empty()
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    # 添加大模型返回结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})






if __name__ == "__main__":
    print()
