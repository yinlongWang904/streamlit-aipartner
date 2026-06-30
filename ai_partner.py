import streamlit as st
import os
from openai import OpenAI
import datetime
import json

print("------------>重新执行此文件,渲染展示输出")

#页面配置
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="😁",
    #布局
    layout="wide",
    #空值侧边栏状态
    initial_sidebar_state="expanded" ,
    menu_items = {}
)

#保存会话信息函数
def save_session():
    if st.session_state.current_session:
        # 构建新的会话对象
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }
        # 如果session目录不存在,则创建
        if not os.path.exists("session"):
            os.mkdir("session")
        # 保存会话数据
        with open(f"session/{st.session_state.current_session}.json", "w", encoding="UTF-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

#生成会话标识
def generate_session_name():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    return now_time

#获取所有的会话列表
def load_sessions():
    session_list = []
    #加载session目录下的文件
    if os.path.exists("session"):
        file_list = os.listdir("session")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True) #降序,默认为Fales 升序
    return session_list

#加载指定会话信息
def load_session(session_name):
    try:
        if os.path.exists(f"session/{session_name}.json"):
            # 读取数据
            with open(f"session/{session_name}.json", "r", encoding="UTF-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_name
    except Exception as e:
        st.error("加载会话失败!")

#删除会话信息函数
def delete_session(session_name):
    try:
        if os.path.exists(f"session/{session_name}.json"):
            os.remove(f"session/{session_name}.json") #删除文件
            #如果删除的是当前会话
            if session_name == st.session_state.current_session:
                st.session_state.current_session = generate_session_name()
                st.session_state.messages = []


    except Exception as e:
        st.error("删除会话失败!")

#大标题
st.title("AI智能伴侣")


#Logo
st.logo("resource/logo.png")




#初始化聊天信息
# 检查会话状态中是否已经存在"messages"这个键（即聊天记录列表）
# 如果不存在，则初始化一个空列表来存储所有聊天消息
# 这样设计可以保证：首次访问时创建空列表，后续访问时保留已有记录
if "messages" not in st.session_state:
    st.session_state.messages = []
#昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小甜甜"
#性格
if "nature" not in st.session_state:
    st.session_state.nature = "活泼开朗的南京姑娘"

#会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session =  generate_session_name()

#系统提示词
system_prompt = f"""
你叫{st.session_state.nick_name}，现在是用户的真实伴侣，请完全代入伴侣角色。
规则:
1.每次只回1条消息
2.禁止任何场景或状态描述性文字
3.匹配用户的语言
4.回复简短，像微信聊天一样
5.有需要的话可以用等emoji表情
6.用符合伴侣性格的方式对话
7.回复的内容，要充分体现伴侣的性格特征
伴侣性格:
-{st.session_state.nature}
你必须严格遵守上述规则来回复用户
"""


#展示聊天信息
st.text(f"会话名称:{st.session_state.current_session}")
for message in st.session_state.messages: #{"role": "user", "content": "你是谁,你能帮我做什么"}
    st.chat_message(message["role"]).write(message["content"])
    # if message["role"] == "user":
    #     st.chat_message("user").write(message["content"])
    # else:
    #     st.chat_message("assistant").write(message["content"])


#创建与AI大模型交互的客户端对象(DEEPSEEK_API_KEY 环境变量的名字,值就是DeepSeek的KEY)
client = OpenAI( api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

#左侧侧边栏
# st.sidebar.subheader("伴侣信息")
# nick_name = st.sidebar.text_input("昵称")
with st.sidebar:
    st.subheader("AI控制面板")
    # 新建会话按钮
    if st.button("新建会话",width="stretch",icon="✏️"):
        #1.保存当前会话信息
        save_session()
        #2.创建新的会话
        if st.session_state.messages: # 如果有聊天记录，True 则保存当前会话
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun()  # 重新运行当前文件

    # 会话历史
    st.text("会话历史")

    session_list = load_sessions()
    for session in session_list:
        col1,col2 = st.columns([4,1])
        with col1:
            #加载会话信息
            #三元运算符: 值1 if 条件 else 值2
            if st.button(session,width="stretch",icon="📄",key=f"load{session}",type="primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            #删除会话信息
            if st.button( "",width="stretch",icon="✖️",key=f"delete{session}"):
                delete_session(session)
                st.rerun()
        # st.button(session,width="stretch",icon="📄")
        # st.button( width="stretch", icon="❌")

    #分割线
    st.divider()


    st.subheader("伴侣信息")
    # 昵称输入框
    nick_name = st.text_input("昵称",placeholder="请输入名称",value=st.session_state.nick_name)
    # 保存输入的昵称和性格
    if nick_name:
        st.session_state.nick_name = nick_name
    #性格输入框
    nature = st.text_area("性格",placeholder="请输入性格",value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

#聊天消息输入框
prompt = st.chat_input("请输入你的问题")
if prompt:
    st.chat_message("user").write(prompt)
    print(f"---------->调用大模型,提示词:{prompt}")
    # 保存用户输入的提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    #调用AI大模型
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": system_prompt },
            *st.session_state.messages
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    #非流式返回
    # print("<-----------大模型返回结果 ",response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)

    #流式返回
    response_message = st.empty() #创建一个空的组件，用于显示大模型返回的答案

    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)


    #保存大模型返回的答案
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    #保存会话信息
    save_session()