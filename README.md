# 简介
基于ChatGLM3-6B，从零开始做一个你的微信克隆人！小白也能跟着做的教程～

本教程包含一系列资源，包含微信聊天记录转出、清理、服务器租赁、大模型微调、部署等步骤。

# 鸣谢
本教程使用了以下项目:
* [WechatExporter](https://github.com/BlueMatthew/WechatExporter.git)
* [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory.git)

本教程参考了以下项目：
* [chat4u](https://github.com/li-plus/chat4u.git)
* [王登科 - 我用我的微信聊天记录和 280 篇博客文章，做了我自己的数字克隆AI](https://greatdk.com/1908.html)

# 0.0 
本教程将采用MacOS视角进行讲述

首先，将这个仓库克隆/下载到本地
```commandline
git clone https://github.com/codeboyphilo/ChatWithYou.git 
```

# 1.0 微信聊天记录导出

网上有众多导出微信聊天记录的攻略，包含获取本地聊天记录存储的数据库密钥等。尝试了数种方法后，我认为目前最方便的方案还是[WechatExporter](https://github.com/BlueMatthew/WechatExporter.git)。

*Prerequisite*：
- MacOS
- iPhone

**具体操作流程**：

1. 将手机进行备份。老版本使用iTune进行备份，新版本在`Finder`中，左侧菜单栏找到你的手机名称，请勿勾选加密备份
2. 备份完成后，打开下载好的WechatExporter，输入备份文件的路径和聊天记录导出的路径。为方便起见，建议直接将导出路径设定为`ChatWithYou`
3. 勾选需要导出的聊天记录，导出`txt`格式

# 2.0 聊天记录处理

我采用的聊天记录处理主要分为两部分；1. 将聊天记录按照alpaca的Instruction，Input，Output的格式进行重新排版并转换成json格式；2.将多个json
文件合并成为一个总数据集。

## 2.1 聊天记录格式转换

首先，在`scripts/get_data.sh`中，将`path_to_chats`处改为存放了导出的聊天记录(`txt`文件）的文件夹。默认情况下，脚本会在当前目录中新建一个`cleaned_chats`
文件夹，用于存放处理好的聊天记录。非特别需要，不建议更改此项。

接下来，请在`clean_chat.py`中，将变量`you`的值改为你的微信名。

之后，在`Terminal`中执行：

```commandline
cd ChatWithYou
sh scripts/get_data.sh
```

`get_data.sh`将会循环执行`clean_chat.py`，以依次清洗聊天记录。该脚本的主要功能有：
1. 将聊天记录中没有导出的语音、图片、表情、音视频通话……等非文字项的标记清除。因为这些项通常被包含在`[ ]`中，所以脚本默认将剔除所有在方括号中的内容
2. 将聊天记录‘压缩’并排版。

    *例如：*

    你和好友A的聊天记录中，脚本会将你的第一条回复之前，好友A发送的所有信息合并成一句话。同理，在好友A对你发送的消息进行回复前，将你发送的所有消息合并成一句话。
    之后，好友A的消息将被当成Instruction，而你的回复将被当成Output。这里的Input默认为空。

这样处理主要是为了符合我个人和我的大部分好友在聊天对话中，喜欢将一句话分成多段发送的习惯。当然，这种处理方法十分的naive，并且会造成很多问题。比如，如果在某次对话中，你并不是结束聊天的人，
那么脚本将会把好友A在两次聊天中发送的信息链接起来，导致最终的Instruction逻辑混乱。同样的问题也存在于当你是某次聊天的最后回复者且同时是下一次聊天的开启者的情况。
类似问题的处理方法其实也比较简单，就是引入聊天记录中关于时间的因素，并新增一些判断语句。如果你有更好的处理方法，欢迎PR～
3. 输出处理好的聊天记录为`.json`格式

## 2.2 聊天记录合并
在当前路径中，在终端中运行：
```commandline
sh scripts/combine_chat.sh
```
这里，`combine_chat`脚本将会进入到之前`get_data`新建的`cleaned_chats`文件夹中，对其中的`json`文件进行合并。如果对之前`get_data`的输出目录进行了更改，
请在运行前对`combine_chat`的`output_dir`处进行同样的更改。`combine_chat`将会默认将聊天记录合并为一个`data.json`文件，并储存在当前目录下

## 2.3 Data Integrity检查

当前`combine_chat`脚本的逻辑可能会造成以下SyntaxError，所以建议在生成`data.json`后，在当前路径下执行多次
```python
python check_data_format.py data.json
```
以对data.json进行检查。这些小错误经常是由多一个逗号导致的，直接将多余的逗号删掉即可

# 3.0 模型微调

在本教程中，我将会使用lora对ChatGLM3-6B进行参数微调

## 3.1 云容器租赁（Optional）

随便在网上租一个即可，我租的是一个1卡的V100-32GB，供参考。

## 3.2 微调

这里默认已经通过某种方式与云容器建立了链接。

关于ChatGLM的微调，我参照的是[LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory.git)。这个项目目前可对许多主流大模型进行微调，
十分推荐。具体流程在LLaMA-Factory的README里已经介绍的比较清晰了，我这里仅做关键流程的提取。强烈建议阅读下原文

首先将项目克隆/下载至本地
```commandline
git clone https://github.com/hiyouga/LLaMA-Factory.git
```

1. **填写CustomDataset的信息**

在`LLaMA-Factory/data/dataset_info.json`中，手动填写上我们的聊天记录数据的信息。如果你是按照我的流程执行的，那么在最后新加一个
```json
  "data": {
  "file_name": "data.json",
  "ranking": "false",
  "formatting": "alpaca"
  }
```
即可。之后，我们需要把之前创建的`data.json`放到`LLaMA-Factory/data/`路径下

2. **环境搭建（Recommended）**

将重新整理好的LLaMA-Factory上传到云实例后，建议大家创建一个新的环境并安装依赖包，例如：
```commandline
virtualenv chatglm-fine-tune #创建虚拟环境
source chatglm-fine-tune/bin/activate #启动虚拟环境
```
之后，我们进入到LLaMA-Factory中，安装其所需要的库
```
pip install -r requirements.txt
```

3. **开始微调**

这里，我们需要进行单卡SFT任务，以下是对sample command进行调整后的例子：
```commandline
HF_ENDPOINT=https://hf-mirror.com CUDA_VISIBLE_DEVICES=0 python src/train_bash.py \
    --stage sft \
    --do_train \
    --model_name_or_path THUDM/chatglm3-6b \
    --dataset data \
    --template default \
    --finetuning_type lora \
    --lora_target q_proj,v_proj \
    --output_dir model-checkpoints \
    --overwrite_cache \
    --per_device_train_batch_size 4 \
    --gradient_accumulation_steps 4 \
    --lr_scheduler_type cosine \
    --logging_steps 10 \
    --save_steps 1000 \
    --learning_rate 5e-5 \
    --num_train_epochs 3.0 \
    --plot_loss \
    --fp16
```
因为某些原因我个人无法连接到Hugging Face，所以需要使用一个Hugging Face的镜像，在最开始设置变量`HF_ENDPOINT=https://hf-mirror.com`

`--model_name_or_path` 处需填我们想要进行微调的大模型的名称。本示例中使用的是[ChatGLM3-6B](https://huggingface.co/THUDM/chatglm3-6b)

`--data`处填写我们之前创建的数据的名称

`--output_dir`处填写你想要储存模型checkpoints的路径

建议先用默认参数跑一下之后，视情况进行调整

4. **CLI测试**

在训练完成后，可现在命令行进行体验。这里，我们需要在当前目录运行：
```python
python src/cli_demo.py \
    --model_name_or_path THUDM/chatglm3-6b \
    --adapter_name_or_path model-checkpoints \
    --template default \
    --finetuning_type lora
```
`--model_name_or_path`和`--adapter_name_or_path`的值同上

# 4.0 部署
## TODO
