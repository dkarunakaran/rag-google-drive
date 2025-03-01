import numpy as np
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
import gradio as gr

class GradioInterface:
    def __init__(self, config, chroma):
        self.config = config
        self.chroma = chroma
        self.chat_setup()

    def chat_setup(self):
        # create a new Chat with OpenAI
        llm = ChatOpenAI(temperature=0.7, model_name=self.config.model)

        # Alternative - if you'd like to use Ollama locally, uncomment this line instead
        # llm = ChatOpenAI(temperature=0.7, model_name='llama3.2', base_url='http://localhost:11434/v1', api_key='ollama')

        # set up the conversation memory for the chat
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

        # the retriever is an abstraction over the VectorStore that will be used during RAG
        retriever = self.chroma.db.as_retriever()

        # putting it together: set up the conversation chain with the GPT 3.5 LLM, the vector store and memory
        self.conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, memory=memory)

    def chat(self, question, history):
        result = self.conversation_chain.invoke({"question": question})
        return result["answer"]
    
    def run(self):
        view = gr.ChatInterface(self.chat, type="messages").launch(inbrowser=True)