"""LangGraph orchestrator for the analytics agent pipeline."""

from langgraph.graph import END, START, StateGraph

from app.agents.analyzer_agent import AnalyzerAgent
from app.agents.intent_agent import IntentAgent
from app.agents.retriever_agent import RetrieverAgent
from app.agents.schema_agent import SchemaAgent
from app.agents.sql_generator_agent import SQLGeneratorAgent
from app.agents.sql_validator_agent import SQLValidatorAgent
from app.agents.summarizer_agent import SummarizerAgent
from app.agents.query_rewriter_agent import QueryRewriterAgent
from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.schemas.state import AnalyticsStateModel,GraphState,initial_state


from app.services.ollama_service import OllamaService
from app.services.sql_executor_service import SQLExecutorService
from app.services.sql_validator_service import SQLValidatorService

logger = get_logger("orchestrator")

class AgentOrchestrator:
    """Coordinates the analytics workflow using LangGraph."""

    def __init__(self,settings: Settings | None = None,) -> None:
        self._settings = settings or get_settings()

        # Shared Services
        self._ollama = OllamaService(self._settings)
        self._sql_executor = SQLExecutorService(self._settings)
        self._sql_validator_service = (SQLValidatorService())

        # Agents
        self._query_rewriter = QueryRewriterAgent(self._ollama)
        self._intent_agent = IntentAgent(self._ollama)
        self._schema_agent = SchemaAgent(self._ollama)
        self._sql_generator_agent =SQLGeneratorAgent(self._ollama)
        self._sql_validator_agent = SQLValidatorAgent(self._sql_validator_service)
        self._retriever_agent = RetrieverAgent(self._sql_executor)
        self._analyzer_agent = AnalyzerAgent(self._ollama,self._sql_executor)
        self._summarizer_agent = (SummarizerAgent(self._ollama) )
        self._compiled_graph = (self._build_graph().compile())

    def _build_graph( self) -> StateGraph:
        """Create LangGraph workflow."""
        graph = StateGraph(GraphState)
        graph.add_node("query_rewriter",self._query_rewriter.run)
        graph.add_node("intent",self._intent_agent.run)
        graph.add_node("schema",self._schema_agent.run)
        graph.add_node("sql_generator",self._sql_generator_agent.run)
        graph.add_node("sql_validator",self._sql_validator_agent.run)
        graph.add_node("retriever",self._retriever_agent.run)
        graph.add_node("analyzer",self._analyzer_agent.run)
        graph.add_node("summarizer",self._summarizer_agent.run)

        # Workflow
        graph.add_edge(START,"query_rewriter")
        graph.add_edge("query_rewriter","intent")
        graph.add_edge("intent","schema")
        graph.add_edge("schema","sql_generator")
        graph.add_edge("sql_generator","sql_validator")
        graph.add_edge("sql_validator","retriever")
        graph.add_edge("retriever","analyzer")
        graph.add_edge("analyzer","summarizer")
        graph.add_edge("summarizer",END)
        return graph

    def invoke(self,question: str,) -> AnalyticsStateModel:
        """Execute complete workflow."""

        logger.info("Starting workflow for question: %s",question[:80])

        state = initial_state(question)
        result: GraphState = (self._compiled_graph.invoke(state))
        response = AnalyticsStateModel(**result)

        if response.error:
            logger.error("Workflow failed: %s",response.error)
        else:
            logger.info("Workflow completed successfully")

        return response

    def process_query(self,question: str) -> AnalyticsStateModel:
        """Backward compatibility wrapper."""
        return self.invoke(question)