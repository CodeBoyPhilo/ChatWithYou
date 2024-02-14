# 👉 [中文版README](README-ZH.md) 👈

> :warning: **AI Translation**: Some contents in this README file is AI translated with adaption.

# Introduction
Create your own WeChat bot from scratch with ChatGLM3-6B! This tutorial is designed to be easy to follow for beginners.

This tutorial includes a series of resources, covering steps such as exporting and cleaning WeChat chat histories, renting cloud servers, fine-tuning LLMs, and deployment.

# Acknowledgement
This project used the following projects:
* [WechatExporter](https://github.com/BlueMatthew/WechatExporter.git)
* [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory.git)

This project was inspired by the following project and blog post:
* [chat4u](https://github.com/li-plus/chat4u.git)
* [王登科 - 我用我的微信聊天记录和 280 篇博客文章，做了我自己的数字克隆AI](https://greatdk.com/1908.html)

# 0.0
The tutorial is presented from a MacOS perspective.

First, clone/download this repository to your local machine:
```commandline
git clone https://github.com/codeboyphilo/ChatWithYou.git 
```

# 1.0 Exporting the WeChat Chat History
There are many guides online for exporting WeChat chat histories, including obtaining the local chat history storage database key. After trying several methods, WechatExporter is currently considered the most convenient solution for me.

*Prerequisite*:
- MacOS
- iPhone

**Detailed process**:

1. Back up your iPhone. Use iTunes for older versions of macOS. For newer versions, please navigate to `Finder`, finding your phone name on the left menu bar. Do not check "Encrypt backup".
2. After backup, open the downloaded WechatExporter, input the path of the backup file, and the path where the chat histories will be exported. For convenience, it is recommended to set the export path directly to `ChatWithYou`.
3. Check the chat histories you want to export and export them in `txt` format.

# 2.0 Clean the Chat Histories
The process I used for chat histories cleaning mainly consists of two parts: 
1. Reformatting the chat histories according to alpaca's Instruction, Input, Output format and converting them into json format; 
2. Merging multiple json files into a one dataset.

## 2.1 Convert File Format
First, in `scripts/get_data.sh`, change the `path_to_chats` to the folder containing the exported chat histories (`txt` files). 
By default, the script will create a `cleaned_chats` folder under the current directory to store the processed chat histories.
It's not recommended to change this default output path unless necessary.

Next, in `clean_chat.py`, change the value of the variable `you` to your WeChat name.

Then, execute in `Terminal`:
```commandline
cd ChatWithYou
sh scripts/get_data.sh
```

`get_data.sh` will execute `clean_chat.py` to iteratively clean the chat histories. The main functions of the script include:

1. Removing markers of non-text items such as voice messages, pictures, emojis, voice and video calls, etc., from the chat histories. Since these items are usually enclosed in [ ], the script by default removes all content within square brackets.

2. "Compressing" and formatting the chat logs.

    *For example:*

    In your chat with friend A, the script will merge all messages sent by friend A before your first reply into one sentence. Similarly, before friend A replies to your message, all messages you sent will be merged into one sentence.
    Afterwards, friend A's message will be treated as Instruction, and your reply as Output. Here, Input is assumed to be empty.

This processing is mainly to accommodate the habit of most people and their friends in chat conversations of sending a sentence in multiple parts. However, this method is quite naive and can cause many problems. For example, if you were not the one to end a conversation, the script will link friend A's messages from two conversations together, leading to confusion in the final Instruction logic. The same problem exists when you are the last to reply in a conversation and also the one to start the next conversation.
Solving such problems is relatively simple, involving the introduction of time factors from the chat logs and adding some judgment statements. If you have a better processing method, PRs are welcomed~

3. Outputting the processed chat histories in `.json` format.

## 2.2 Merging Chat Histories
Under the current directory, execute in `Terminal`:
```commandline
sh scripts/combine_chat.sh
```
Here, the `combine_chat` script will enter the `cleaned_chats` folder created by `get_data` earlier and merge the `json` files inside. If you changed the output directory of `get_data`, please make the same change to `combine_chat`'s `output_dir` before running. `combine_chat` will by default merge the chat histories into a `data.json` file and store it in the current directory.

## 2.3 Checking Data Integrity
The logic of the current `combine_chat` script may cause SyntaxError, so it's recommended to execute multiple times after generating data.json:
```commandline
python check_data_format.py data.json
```
to check `data.json`. These minor errors are often caused by an extra comma, which can be directly deleted.

# 3.0 Fine-tuning LLM
In this tutorial, I will use lora to fine-tune parameters of ChatGLM3-6B.
## 3.1 Cloud Instance Leasing (Optional)
You can lease any online cloud container you liked. I leased a 1-card V100-32GB for reference. Just make sure the GPU RAM is suitable.
## 3.2 Supervised Fine-Tuning
Assuming a connection has already been established with the cloud container.

For fine-tuning ChatGLM, I referred to [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory.git). This project currently allows fine-tuning of many mainstream LLMs, highly recommended. The specific process is clearly introduced in LLaMA-Factory's README, and I only extract the key processes here. It's strongly advised to read the original file.

First, clone/download the project to your local machine:
```commandline
git clone https://github.com/hiyouga/LLaMA-Factory.git
```

1. **Insert the Custom Dataset Info**

In `LLaMA-Factory/data/dataset_info.json`, manually enter the information of our chat history data. If you followed my procedure, adding these following at the end
```json
  "data": {
  "file_name": "data.json",
  "ranking": "false",
  "formatting": "alpaca"
  }
```
is sufficient. 
After this, we need to place the `data.json` we created earlier into `LLaMA-Factory/data/`.

2. **Virtual Environment (Recommended)**

After uploading the reorganised LLaMA-Factory to the cloud instance, it's recommended to create a new environment and install the necessary packages, for example:
```commandline
virtualenv chatglm-fine-tune #创建虚拟环境
source chatglm-fine-tune/bin/activate #启动虚拟环境
```
Then, install the necessary dependencies:
```
pip install -r requirements.txt
```

3. **Start fine-tuning**

Here, we begin SFT on a single core of GPU. Here are example of adaptations made to the sample command:
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
For some reasons I could not connect to Hugging Face, therefore I have used a Hugging Face mirror and set the environment variable `HF_ENDPOINT=https://hf-mirror.com`

`--model_name_or_path` should place the name of LLM we wish to fine-tune. This tutorial has used [ChatGLM3-6B](https://huggingface.co/THUDM/chatglm3-6b)

`--data` should place the name of the data we created earlier

`--output_dir`should place the desired path to output directory you wish to store the model checkpoints

I suggest you fine-tune a round using the default hyperparameters, and adjust later. 

4. **CLI experimenting**

When fine-tune is finished, you could play around with the model via command line. Here, we run the following:
```python
python src/cli_demo.py \
    --model_name_or_path THUDM/chatglm3-6b \
    --adapter_name_or_path model-checkpoints \
    --template default \
    --finetuning_type lora
```

`--model_name_or_path` and `--adapter_name_or_path` have values as mentioned before.

# 4.0 Deployment
## TODO 
