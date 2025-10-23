import os
import warnings
from dotenv import load_dotenv
from agent import graph
from langchain_core.messages import AIMessage

load_dotenv()

def main():
    print("Customer Support AI Agent")
    print("Type 'quit' to exit\n")
    
    state = {
        "messages": [],
        "customer_query": None,
        "order_id": None,
        "customer_id": None,
        "product_id": None,
        "next_action": None
    }
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        
        state["customer_query"] = user_input
        
        print("Agent: ", end="", flush=True)
        
        try:
            for event in graph.stream(state):
                for value in event.values():
                    if 'messages' in value and value['messages']:
                        last_msg = value['messages'][-1]
                        if isinstance(last_msg, AIMessage) and last_msg.content:
                            if not last_msg.tool_calls and 'ESCALATE_TO_HUMAN' not in last_msg.content:
                                print(last_msg.content)
                    state.update(value)
                    
        except Exception as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    main()