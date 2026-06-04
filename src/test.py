from utils.myTools import *

llm=get_model("qwen-plus")

response=llm.invoke("你好")

print(response.content)