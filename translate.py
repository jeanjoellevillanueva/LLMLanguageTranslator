import getpass
import os

from dotenv import load_dotenv
from IPython.display import display
from IPython.display import Image
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph import START
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode

from .tools import add
from .tools import divide
from .tools import multiply

# Load .env file
load_dotenv()
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()

# Access the variables
langchain_tracing = os.getenv('LANGCHAIN_TRACING_V2')
langchain_api_key = os.getenv('LANGCHAIN_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

input_language = os.getenv('INPUT_LANGUAGE')


def assistant(state: MessagesState):
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


if __name__ == '__main__':
    tools = [add, multiply, divide]
    llm = ChatOpenAI(model='gpt-4o-mini', openai_api_key=openai_api_key)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    import pdb; pdb.set_trace()
    llm_with_tools = llm.bind_tools(tools)

    sys_msg = SystemMessage(content='You are a helpful assistant tasked with performing arithmetic on a set of inputs.')

    # Graph
    builder = StateGraph(MessagesState)

    # Define nodes: these do the work
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))

    # Define edges: these determine how the control flow moves
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
        # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
        tools_condition,
    )
    builder.add_edge("tools", "assistant")
    react_graph = builder.compile()

    # Show
    display(Image(react_graph.get_graph(xray=True).draw_mermaid_png()))

    messages = [HumanMessage(content="Add 3 and 4.")]
    import pdb; pdb.set_trace()
    messages = react_graph.invoke({"messages": messages})
    for m in messages['messages']:
        m.pretty_print()

    messages = [HumanMessage(content="Multiply that by 2.")]
    messages = react_graph.invoke({"messages": messages})
    for m in messages['messages']:
        m.pretty_print()

    memory = MemorySaver()
    react_graph_memory = builder.compile(checkpointer=memory)

    # Specify a thread
    config = {"configurable": {"thread_id": "1"}}

    # Specify an input
    messages = [HumanMessage(content="Add 3 and 4.")]

    # Run
    messages = react_graph_memory.invoke({"messages": messages},config)
    for m in messages['messages']:
        m.pretty_print()

    messages = [HumanMessage(content="Multiply that by 2.")]
    messages = react_graph_memory.invoke({"messages": messages}, config)
    for m in messages['messages']:
        m.pretty_print()
