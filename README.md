# chatbot-py
中文聊天机器人， 根据自己的语料训练出自己想要的聊天机器人，可以用于智能客服、在线问答、智能聊天等场景!

# 快速开始
**1. 安装**
```
pip install chatbot-py
```

**2. 基本用法**
```
from chatbot.chatbot import ChatBot


bot = ChatBot('test')
static_statement_data = {
    'question': '早上吃鸡蛋对身体好吗',
    'answer': '早餐当中吃鸡蛋，的确是对身体有很大的益处',
}
bot.learn(**static_statement_data)
print(bot.get_response('早上吃鸡蛋好吗'))
```