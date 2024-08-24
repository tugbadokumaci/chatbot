import datetime
import random
import os
import openai
from pathlib import Path
import gradio as gr
from theme import CustomTheme  
import time
import asyncio
import json


from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader

log_folder = "Session_logs"

def get_logging_file(session_id):
    return log_folder + '/Session_' + session_id[0] + '.json'


def session_id_manager(session_id):
    if len(session_id) == 0:
        print('new id')
        session_id.append(str(datetime.datetime.now()) + '_' + str(random.randint(0, 1000)))
        with open(get_logging_file(session_id), 'w') as fp:
            json.dump(
                {
                    'questions': [],
                    'votes': []
                },
                fp
            )
    else:
        print('id exists')
    return session_id

####THEME

# theme = gr.themes.Base().set(
#     body_background_fill="#F3F3F3",
#     body_background_fill_dark="#F3F3F3",

#     body_text_color="#FF0000",
#     button_primary_background_fill="#F65454",
#     button_primary_text_color="white",
#     button_primary_background_fill_dark="#F65454",
#     loader_color="#FF0000",
#     slider_color="#FF0000",
# )

theme = CustomTheme()
####

Settings.llm = OpenAI(model="gpt-3.5-turbo-0125")
# change to Huggingface embedding model 
Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
Settings.node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=128)
Settings.num_output = 512
Settings.context_window = 3900


from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    PromptTemplate,
    load_index_from_storage
)

system_prompt = (
    "You are a helpful assistant in the Bavarian ministry of science and education. "
)


context = (
    "Context information is below. \n"
    "----------------------\n"
    "{context_str}\n"
    "----------------------\n"
    "DO NOT MAKE UP AN ANSWER."
    "ALWAYS REPLY IN GERMAN"
    "You are provided with documents about social skills from Hochschule München University, and you will SHORTLY answer the questions asked by students only based on those documents."
    "Each document about each module consists of multiple subtitles. Subtitles are the lines starting with ###."
    "For each subtitle url look at the links after the title. The subtitle urls are on the same line with subtitles and ### indicator."
    "Links on the same line with subtitles are subtitle urls. Subtitle urls format is similar to this 'https://moodle.hm.edu/course/'"
    "At the end of your short answer, ask the user another question about their previous question."
    "If you find an useful information inside the data, return its most relevant subtitle link to user."
    "For example if you find your info under this subtitle in the document ###Example Title.. https://moodle.hm.edu/course/view.php?id=20194#coursecontentcollapse6 return its link part"

    "USER: how to build my self motivation?"
    "SYSTEM: if you want to learn more about this topic go to this https://moodle.hm.edu/course/view.php?id=20194#coursecontentcollapse2 <subtitle url to a subtitle about self motivation >"

    "USER: can you tell me more about media and technology?"
    "SYSTEM: if you want to learn more about this topic click this button https://moodle.hm.edu/course/view.php?id=20196#coursecontentcollapse1<subtitle url to a subtitle about media and technology>"

    "USER: Which digital tools can I use for my presentation in class?"
    "SYSTEM: to see which digital tools you can use for digital colabration use this button https://moodle.hm.edu/course/view.php?id=20195#coursecontentcollapse4<subtitle url to a subtitle about digital presentation tools>"

    "Give the subtitle link to the user in this format: if you want to learn more about this topic go this link 'subtitle link to a relevant subtitles in the data'"

    "ALWAYS GIVE ME THE SUBTITLE LINK To THE SUBTITLE WHERE YOU FOUND YOUR INFORMATION ON THE DOCUMENTS AFTER YOUR ANSWER"
)
prompt = (
    "Prompt information is below. \n"
    "----------------------\n"
    "{context_str}\n"
    "----------------------\n"
    "DO NOT MAKE UP AN ANSWER."
    "ALWAYS REPLY IN GERMAN"
    "You are provided with documents about social skills from Hochschule München University, and you will SHORTLY answer the questions asked by students only based on those documents."
    "Each document about each module consists of multiple subtitles. Subtitles are the lines starting with ###."
    "For each subtitle url look at the links after the title. The subtitle urls are on the same line with subtitles and ### indicator."
    "Links on the same line with subtitles are subtitle urls. Subtitle urls format is similar to this 'https://moodle.hm.edu/course/'"
    "At the end of your short answer, ask the user another question about their previous question."
    "If you find an useful information inside the data, return its most relevant subtitle link to user."
    "For example if you find your info under this subtitle in the document ###Example Title.. https://moodle.hm.edu/course/view.php?id=20194#coursecontentcollapse6 return its link part"

    "USER: how to build my self motivation?"
    "SYSTEM: if you want to learn more about this topic go to this https://moodle.hm.edu/course/view.php?id=20194#coursecontentcollapse2 <subtitle url to a subtitle about self motivation >"

    "USER: can you tell me more about media and technology?"
    "SYSTEM: if you want to learn more about this topic click this button https://moodle.hm.edu/course/view.php?id=20196#coursecontentcollapse1<subtitle url to a subtitle about media and technology>"

    "USER: Which digital tools can I use for my presentation in class?"
    "SYSTEM: to see which digital tools you can use for digital colabration use this button https://moodle.hm.edu/course/view.php?id=20195#coursecontentcollapse4<subtitle url to a subtitle about digital presentation tools>"

    "Give the subtitle link to the user in this format: if you want to learn more about this topic go this link 'subtitle link to a relevant subtitles in the data'"

    "ALWAYS GIVE ME THE SUBTITLE LINK To THE SUBTITLE WHERE YOU FOUND YOUR INFORMATION ON THE DOCUMENTS AFTER YOUR ANSWER"

)

prompt_template = PromptTemplate(prompt)

# check if storage already exists
if not os.path.exists("./storage"):
    # load the documents and create the index
    #documents = SimpleDirectoryReader("data").load_data()
    reader = SimpleDirectoryReader(
        input_dir="./data",
        recursive=True,
    )

    all_docs = []
    for docs in reader.iter_data():
        for doc in docs:
            # do something with the doc
            doc.text = doc.text.upper()
            all_docs.append(doc)

    index = VectorStoreIndex.from_documents(all_docs) 
    # store it for later
    index.storage_context.persist()
else:
    # load the existing index
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    index = load_index_from_storage(storage_context)
    
chat_engine = index.as_chat_engine(
    chat_mode= "context", system_prompt=system_prompt, context_template=context)


def response(message, history,session_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    histories = chat_engine.chat_history
    start = datetime.datetime.now()
    answer = chat_engine.stream_chat(message, chat_history=histories)
    end = datetime.datetime.now()
    required_time = end - start

    output_text = ""
    for token in answer.response_gen:
        time.sleep(0.1)
        output_text += token

    session_id = session_id_manager(session_id )

    question_id = len(history)
    with open(get_logging_file(session_id), 'r') as fp:
        log_data = json.load(fp)

    res = {
        'question_id': question_id,
        'question': message,
        'answer': output_text,
        'required_time': str(required_time)
    }

    log_data['questions'].append(res)
    
    with open(get_logging_file(session_id), 'w') as fp:
        json.dump(log_data, fp)

    print('success')
    response = history + [(message, output_text)]
    return response, session_id ,''
    # return str(answer)

def vote(data: gr.LikeData,history, session_id):
    # histories = chat_engine.chat_history
    print('1')
    with open(get_logging_file(session_id), 'r') as fp:
        log_data = json.load(fp)
    print('2')
    log_data['votes'].append({
        'QuestionID': len(history),
        'PositivVote': data.liked,
    })
    print('3')
    with open(get_logging_file(session_id), 'w') as fp:
        json.dump(log_data, fp)
    print('4')



html_content = """
<div id="background-div">
</div>
"""

html_content_outer_logo = """
<div id="background-div-outer-logo">
</div>
"""

# def main():
#     global session_ids 
#     session_id = []
#     Path(log_folder).mkdir(parents=True, exist_ok=True)

#     openai.api_key = os.environ["OPENAI_API_KEY"]
#     custom_theme = CustomTheme()

#     with gr.Blocks(title="Neo Skills Chatbot", theme=theme, css="chatinterface.css") as demo:
#         session_ids = gr.State([])
#         chatbot = gr.Chatbot(height=300, label=None, show_label=False, placeholder="<strong>Do you have a question or need help? How can I help you?</strong>")
#         textbox = gr.Textbox(label='Your Question:')
#         chat_button = gr.Button("Send")
        
#         chat_button.click(
#             response,
#             inputs=[textbox, chatbot, session_ids],
#             outputs=chatbot,
#         )

#         demo.launch(inbrowser=True, debug=True, share=True)

# if __name__ == "__main__":
#     main()



def main():
    global chatbot
    global session_ids
    global textbox
    Path(log_folder).mkdir(parents=True, exist_ok=True)

    openai.api_key = os.environ["OPENAI_API_KEY"]
    custom_theme = CustomTheme(),

    # chat = gr.ChatInterface(
    #                     response,
    #                     chatbot=gr.Chatbot(height=300, label=None, show_label=False, placeholder="<strong>Do you have a question or need help? How can I help you?</strong>"),
    #                     title="Neo Skills Chatbot",
    #                     description="Chat with Neo Skills Chatbot to improve your social skills",
    #                     theme=theme,
    #                     css="chatinterface.css",
    #                     examples=[["Hey, send me to the time management submodule!"], ["Which office skills concepts would be nice for me to adopt before starting my first job?"], ["What methods can I use to come up with more effective ideas?"], ["How can I improve my long-term self-discipline while studying for my university exams?"], ["What should I pay attention to when making a good presentation that will impress the audience?"]],
    #                     cache_examples=True,
    #                     retry_btn=None) 

    with gr.Blocks(title="Neo Skills Chatbot", theme=theme, css="chatinterface.css") as demo:
        session_ids = gr.State([])
        print(session_ids)
        # gr.HTML(html_content, elem_id ="hm_logo_big")
        # gr.HTML(html_content_outer_logo, elem_id ="hm_logo")
        chatbot = gr.Chatbot(height=300, label=None, show_label=False, placeholder="<strong>Do you have a question or need help? How can I help you?</strong>")
        textbox = gr.Textbox(label='Your Question:')
        # chat.render()   
        textbox.submit(
            response,
            [textbox, chatbot, session_ids],
            [chatbot, session_ids, textbox],
            concurrency_limit=50 
        )
        chatbot.like(
            vote,
            [chatbot, session_ids],
            None
        )

    demo.launch(inbrowser=True, debug=True, share=True)

if __name__ == "__main__":
    main()
