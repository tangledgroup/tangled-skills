# Mem0 Framework Integrations

Integrate Mem0 with popular AI frameworks including LangChain, LlamaIndex, CrewAI, AutoGen, and Vercel AI SDK.

## LangChain Integration

Add persistent memory to LangChain chains and agents.

### Basic Integration

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from mem0 import Memory
from langchain_core.messages import HumanMessage, AIMessage

memory = Memory()

def search_memory_tool(query: str, user_id: str):
    """Search for relevant memories."""
    results = memory.search(query=query, user_id=user_id)
    return "\n".join([f"- {r['memory']}" for r in results["results"]])

def add_memory_tool(conversation: str, user_id: str):
    """Add new memories from conversation."""
    messages = [{"role": "user", "content": conversation}]
    memory.add(messages, user_id=user_id)
    return "Memory added"

# Create tools
from langchain_core.tools import tool

@tool
def search_memories(query: str, user_id: str):
    """Search for relevant user memories."""
    results = memory.search(query=query, user_id=user_id)
    return "\n".join([r['memory'] for r in results["results"]])

@tool
def get_user_preferences(user_id: str):
    """Get user preferences and facts."""
    results = memory.search(query="preferences", user_id=user_id, top_k=5)
    return "\n".join([r['memory'] for r in results["results"]])

# Create agent with memory tools
llm = ChatOpenAI(model="gpt-4.1-mini")
tools = [search_memories, get_user_preferences]

agent = create_tool_calling_agent(llm, tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run with memory context
response = agent_executor.invoke({
    "input": "What are my dietary preferences?",
    "user_id": "alice"
})
```

### LangChain ChatWithHistory

```python
from langchain.memory import ConversationBufferMemory
from mem0 import Memory

class Mem0LangChainMemory:
    """Custom memory that integrates with LangChain."""
    
    def __init__(self, user_id: str):
        self.memory = Memory()
        self.user_id = user_id
    
    def load_memory_variables(self, inputs):
        """Load relevant memories into conversation context."""
        query = inputs.get("input", "")
        results = self.memory.search(query=query, user_id=self.user_id, top_k=3)
        
        memory_text = "\n".join([r['memory'] for r in results["results"]])
        return {"history": f"User memories:\n{memory_text}" if memory_text else ""}
    
    def save_context(self, inputs, outputs):
        """Save conversation to Mem0."""
        messages = [
            {"role": "user", "content": inputs["input"]},
            {"role": "assistant", "content": outputs["output"]}
        ]
        self.memory.add(messages, user_id=self.user_id)

# Usage
mem0_memory = Mem0LangChainMemory(user_id="alice")
```

### RAG with Memory

```python
from langchain.retrievers import ContextualCompressionRetriever
from mem0 import Memory

class Mem0EnhancedRAG:
    """RAG system enhanced with user memory."""
    
    def __init__(self, retriever, memory: Memory):
        self.retriever = retriever
        self.memory = memory
    
    def retrieve(self, query: str, user_id: str):
        # Get document context
        doc_context = self.retriever.invoke(query)
        
        # Get user memory context
        mem_context = self.memory.search(query=query, user_id=user_id, top_k=3)
        memories = [r['memory'] for r in mem_context["results"]]
        
        # Combine contexts
        full_context = f"""Document Context:
{doc_context}

User Memory:
{" ".join(memories)}"""
        
        return full_context

# Usage
rag = Mem0EnhancedRAG(retriever=document_retriever, memory=Memory())
context = rag.retrieve("How does this relate to my project?", user_id="alice")
```

## LlamaIndex Integration

Add memory to LlamaIndex agents and RAG pipelines.

### Basic Integration

```python
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.agent import ReActAgent
from mem0 import Memory

memory = Memory()

def memory_retriever(query: str, user_id: str):
    """Custom retriever that fetches from Mem0."""
    results = memory.search(query=query, user_id=user_id, top_k=3)
    from llama_index.core import Document
    
    docs = [
        Document(text=r['memory'], metadata={"source": "user_memory"})
        for r in results["results"]
    ]
    return docs

# Create agent with memory tool
from llama_index.core.tools import FunctionTool

@FunctionTool
def retrieve_user_memories(query: str, user_id: str) -> str:
    """Retrieve relevant user memories."""
    retriever_results = memory_retriever(query, user_id)
    return "\n".join([doc.text for doc in retriever_results])

agent = ReActAgent.from_tools(
    [retrieve_user_memories],
    llm=Settings.llm,
    verbose=True
)

# Query with memory
response = agent.chat("Based on my preferences, what should I do?")
```

### RAG Pipeline with Memory

```python
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from mem0 import Memory

# Load documents
documents = SimpleDirectoryReader("docs").load_data()
index = VectorStoreIndex.from_documents(documents)

class Mem0QueryEngine:
    """Query engine that incorporates user memory."""
    
    def __init__(self, index, memory: Memory):
        self.index = index
        self.memory = memory
    
    def query(self, query_str: str, user_id: str):
        # Get document responses
        base_engine = self.index.as_query_engine()
        doc_response = base_engine.query(query_str)
        
        # Get memory context
        mem_results = self.memory.search(query=query_str, user_id=user_id, top_k=3)
        memory_context = "\n".join([r['memory'] for r in mem_results["results"]])
        
        # Refine with memory
        refine_prompt = f"""Original query: {query_str}
Document answer: {doc_response.response}
User memories: {memory_context}

Provide a more personalized answer considering the user's memories."""
        
        refined_response = Settings.llm.complete(refine_prompt)
        return refined_response.response

# Usage
mem0_engine = Mem0QueryEngine(index, Memory())
response = mem0_engine.query("What would work for my use case?", user_id="alice")
```

### Multi-Document with Memory

```python
from llama_index.core import SummaryIndex
from mem0 import Memory

class Mem0SummaryIndex:
    """Summary index enhanced with user memory."""
    
    def __init__(self, documents, memory: Memory):
        self.index = SummaryIndex.from_documents(documents)
        self.memory = memory
    
    def query(self, query: str, user_id: str):
        # Get summary
        base_response = self.index.query(query)
        
        # Enhance with memory
        mem_context = self.memory.search(query=query, user_id=user_id, top_k=2)
        memories = [r['memory'] for r in mem_context["results"]]
        
        # Personalize response
        personalized = f"""{base_response.response}

Based on your background:
{"; ".join(memories)}"""
        
        return personalized
```

## CrewAI Integration

Add shared memory to CrewAI agents and tasks.

### Basic Integration

```python
from crewai import Agent, Task, Crew
from mem0 import Memory

memory = Memory()

def get_user_context(user_id: str) -> str:
    """Get user context for agent."""
    results = memory.search(query="preferences history", user_id=user_id, top_k=5)
    return "\n".join([r['memory'] for r in results["results"]])

# Create agents with memory context
researcher = Agent(
    role='Research Analyst',
    goal='Find relevant information based on user preferences',
    backstory=f"""You are a research analyst. 
User context: {get_user_context('alice')}""",
    verbose=True,
    allow_delegation=False
)

writer = Agent(
    role='Content Writer',
    goal='Write personalized content',
    backstory=f"""You are a writer who personalizes content.
User context: {get_user_context('alice')}""",
    verbose=True,
    allow_delegation=False
)

# Create tasks
research_task = Task(
    description='Research topics relevant to the user',
    agent=researcher,
    expected_output='Research findings'
)

write_task = Task(
    description='Write personalized article',
    agent=writer,
    expected_output='Personalized article'
)

# Execute crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=True
)

result = crew.kickoff()

# Store results in memory
memory.add(
    messages=[{"role": "user", "content": result}],
    user_id="alice"
)
```

### Shared Memory Across Agents

```python
from crewai import Process
from mem0 import Memory

class Mem0Crew:
    """Crew with shared memory across all agents."""
    
    def __init__(self, user_id: str):
        self.memory = Memory()
        self.user_id = user_id
    
    def get_agent_backstory(self, role: str) -> str:
        """Generate agent backstory with memory context."""
        results = self.memory.search(
            query=f"context for {role}",
            user_id=self.user_id,
            top_k=3
        )
        memories = "\n".join([r['memory'] for r in results["results"]])
        return f"You are a {role}. User context:\n{memories}"
    
    def save_crew_output(self, output: str):
        """Save crew output to memory."""
        self.memory.add(
            messages=[{"role": "assistant", "content": output}],
            user_id=self.user_id
        )

# Usage
crew_manager = Mem0Crew(user_id="alice")

researcher = Agent(
    role='Researcher',
    goal='Research topics',
    backstory=crew_manager.get_agent_backstory('researcher'),
    verbose=True
)

crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    process=Process.sequential
)

result = crew.kickoff()
crew_manager.save_crew_output(result)
```

## AutoGen Integration

Add memory to AutoGen conversational agents.

### Basic Integration

```python
from autogen import ConversableAgent, UserProxyAgent
from mem0 import Memory

memory = Memory()

# Create assistant with memory tool
assistant = ConversableAgent(
    name="assistant",
    llm_config={
        "config_list": [{"model": "gpt-4.1-mini", "api_key": os.getenv("OPENAI_API_KEY")}]
    },
    function_map={
        "search_memory": lambda query, user_id: memory.search(query=query, user_id=user_id),
        "add_memory": lambda conversation, user_id: memory.add(
            messages=[{"role": "user", "content": conversation}],
            user_id=user_id
        )
    }
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE"
)

# Conversation with memory
user_proxy.initiate_chat(
    assistant,
    message="What do you remember about my preferences?",
    additional_args={"user_id": "alice"}
)
```

### Function Calling with Memory

```python
import json
from autogen import AssistantAgent

def search_memories(query: str, user_id: str) -> str:
    """Search for relevant memories."""
    results = memory.search(query=query, user_id=user_id, top_k=3)
    return json.dumps([{
        "memory": r['memory'],
        "score": r.get('score', 0)
    } for r in results["results"]])

# Define function schema
memory_functions = [
    {
        "name": "search_memories",
        "description": "Search user memories for relevant information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "user_id": {
                    "type": "string",
                    "description": "User identifier"
                }
            },
            "required": ["query", "user_id"]
        }
    }
]

assistant = AssistantAgent(
    name="assistant",
    llm_config={
        "config_list": [{"model": "gpt-4.1-mini"}],
        "functions": memory_functions
    },
    function_map={"search_memories": search_memories}
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    code_execution_mode="none"
)

user_proxy.initiate_chat(
    assistant,
    message="Search my memories for travel preferences",
    additional_args={"user_id": "alice"}
)
```

## Vercel AI SDK Integration

Add memory to Vercel AI SDK streams and chat.

### StreamChat with Memory

```python
from ai import stream_chat, Message
from mem0 import Memory

memory = Memory()

async def chat_with_memory(messages: list[Message], user_id: str):
    """Stream chat with memory context."""
    
    # Get memory context
    last_message = messages[-1].content
    mem_results = await memory.search(query=last_message, user_id=user_id, top_k=3)
    memories = "\n".join([r['memory'] for r in mem_results["results"]])
    
    # Add memory to system prompt
    system_prompt = f"""You are a helpful assistant.
User memories: {memories}"""
    
    # Stream response
    result = await stream_chat(
        model="openai:gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            *messages
        ]
    )
    
    # Save conversation to memory
    await memory.add(
        messages=[
            {"role": "user", "content": last_message},
            {"role": "assistant", "content": result}
        ],
        user_id=user_id
    )
    
    return result

# Usage in Next.js API route
from ai import convertToCoreMessages

export async function POST(request: Request) {
    const { messages, userId } = await request.json()
    
    const result = await chat_with_memory(
        convertToCoreMessages(messages),
        userId
    )
    
    return result.toAIStreamResponse()
}
```

### UseChat Hooks with Memory

```typescript
// React component with memory
import { useChat } from 'ai/react';
import { MemoryClient } from 'mem0ai';

const memoryClient = new MemoryClient({ apiKey: process.env.MEM0_API_KEY });

function ChatWithMemory({ userId }: { userId: string }) {
    const { messages, input, handleSubmit, isLoading } = useChat({
        body: { userId },
        fetcher: async (url: string, options: any) => {
            // Get memory context before request
            const lastMessage = messages[messages.length - 1]?.content;
            const memResults = await memoryClient.search(lastMessage || '', {
                filters: { user_id: userId }
            });
            
            const memories = memResults.results.map(r => r.memory).join('\n');
            
            // Add memory to request
            const response = await fetch(url, {
                ...options,
                body: JSON.stringify({
                    ...options.body,
                    memories
                })
            });
            
            return response;
        }
    });

    return (
        <div>
            {messages.map(m => (
                <div key={m.id}>{m.content}</div>
            ))}
            <form onSubmit={handleSubmit}>
                <input value={input} onChange={e => setInput(e.target.value)} />
                <button type="submit" disabled={isLoading}>Send</button>
            </form>
        </div>
    );
}
```

## LangGraph Integration

Add memory to LangGraph state machines.

```python
from langgraph.graph import StateGraph, END
from mem0 import Memory

memory = Memory()

class AgentState(TypedDict):
    messages: list[Message]
    user_id: str
    memory_context: str

def load_memory_context(state: AgentState) -> AgentState:
    """Load relevant memories into state."""
    last_message = state["messages"][-1].content if state["messages"] else ""
    results = memory.search(query=last_message, user_id=state["user_id"], top_k=3)
    
    return {
        "memory_context": "\n".join([r['memory'] for r in results["results"]])
    }

def agent_node(state: AgentState) -> AgentState:
    """Agent processing with memory context."""
    # Use memory_context in generation
    ...
    return {"messages": [new_message]}

def save_memory(state: AgentState) -> AgentState:
    """Save conversation to memory."""
    messages = [
        {"role": m.role, "content": m.content}
        for m in state["messages"][-2:]  # Last exchange
    ]
    memory.add(messages, user_id=state["user_id"])
    return state

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("load_memory", load_memory_context)
workflow.add_node("agent", agent_node)
workflow.add_node("save_memory", save_memory)

workflow.set_entry_point("load_memory")
workflow.add_edge("load_memory", "agent")
workflow.add_edge("agent", "save_memory")
workflow.add_edge("save_memory", END)

app = workflow.compile()

# Run with memory
result = app.invoke({
    "messages": [HumanMessage(content="What do you know about me?")],
    "user_id": "alice"
})
```

## Integration Best Practices

1. **Scope memories correctly** - Always use `user_id` to prevent cross-contamination
2. **Cache memory results** - Memoize frequent searches within a session
3. **Batch memory operations** - Use async for multiple framework integrations
4. **Handle errors gracefully** - Catch memory failures without breaking main flow
5. **Respect rate limits** - Throttle memory calls in high-volume scenarios
6. **Use metadata** - Tag memories by framework/integration for better filtering
