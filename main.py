from langgraph.graph import StateGraph
from agents import alex, sam, mira, jordan, sam_decision, taylor, alex_summary

workflow = StateGraph()
workflow.add_node("alex", alex.run)
workflow.add_node("sam", sam.run)
workflow.add_node("mira", mira.run)
workflow.add_node("jordan", jordan.run)
workflow.add_node("sam_decision", sam_decision.run)
workflow.add_node("taylor", taylor.run)
workflow.add_node("alex_summary", alex_summary.run)

workflow.set_entry_node("alex")
workflow.set_conditional("sam", lambda state: ["mira", "jordan"])
workflow.set_conditional("mira", lambda state: ["sam_decision"])
workflow.set_conditional("jordan", lambda state: ["sam_decision"])
workflow.set_conditional("sam_decision", lambda state: ["taylor"])
workflow.set_conditional("taylor", lambda state: ["alex_summary"])
workflow.set_exit_node("alex_summary")

graph = workflow.compile()