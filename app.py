import os
import openai
from pathlib import Path
import gradio as gr
from theme import CustomTheme  
import time
import asyncio


from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader

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

def upload_file(filepath):
    name = Path(filepath).name
    return [gr.UploadButton(visible=False), gr.DownloadButton(label=f"Download {name}", value=filepath, visible=True)]

def download_file():
    return [gr.UploadButton(visible=True), gr.DownloadButton(visible=False)]

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


def response(message, history):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    histories = chat_engine.chat_history
    answer = chat_engine.stream_chat(message, chat_history=histories)

    output_text = ""
    for token in answer.response_gen:
        time.sleep(0.1)

        output_text += token
        yield output_text

    #return str(answer)



html_content = """
<div id="background-div">
</div>
"""

html_content_outer_logo = """
<div id="background-div-outer-logo">
</div>
"""

chat = gr.ChatInterface(
                    response,
                    chatbot=gr.Chatbot(height=300, label=None, show_label=False, placeholder="<strong>Do you have a question or need help? How can I help you?</strong>"),
                    title="Neo Skills Chatbot",
                    description="Chat with Neo Skills Chatbot to improve your social skills",
                    theme=theme,
                    css="chatinterface.css",
                    examples=["Hey, send me to the time management submodule!","Which office skills concepts would be nice for me to adopt before starting my first job?", "What methods can I use to come up with more effective ideas ?","How can I improve my long-term self-discipline while studying for my university exams?", "What should I pay attention to when making a good presentation that will impress the audience?" ],
                    cache_examples=True,
                    retry_btn=None) 

with gr.Blocks(title="Neo Skills Chatbot", theme=theme, css="chatinterface.css") as demo:
    # gr.Image("./img/hm_logo.png",elem_id="hm-logo")
    # gr.Blocks(css="chatinterface.css")
    gr.HTML(html_content, elem_id ="hm_logo_big")
    gr.HTML(html_content_outer_logo, elem_id ="hm_logo")
    # gr.Markdown("New generation learning assistant chatbot developed by Neo Skills", elem_id="markdown") 
    chat.render()
    # with gr.Column():
    #         with gr.Row():
    #             u = gr.UploadButton("Upload a file", file_count="single")
    #             d = gr.DownloadButton("Download the file", visible=False)

    #         u.upload(upload_file, u, [u, d])
    #         d.click(download_file, None, [u, d])
   



def main():
    openai.api_key = os.environ["OPENAI_API_KEY"]
    custom_theme = CustomTheme(),

    demo.launch(inbrowser=True, debug=True, share=False)

if __name__ == "__main__":
    main()
