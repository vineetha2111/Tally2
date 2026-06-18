"""LangGraph orchestrator for the analytics agent pipeline."""

from langgraph.graph import END, START, StateGraph

from app.agents.analyzer_agent import AnalyzerAgent
from app.agents.intent_agent import IntentAgent
from app.agents.retriever_agent import RetrieverAgent
from app.agents.schema_agent import SchemaAgent
from app.agents.sql_generator_agent import SQLGeneratorAgent
from app.agents.sql_validator_agent import SQLValidatorAgent
from app.agents.summarizer_agent import SummarizerAgent
from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.schemas.state import GraphState, AnalyticsStateModel, initial_state
from app.services.ollama_service import OllamaService
from app.services.sql_executor_service import SQLExecutorService
from app.services.sql_validator_service import SQLValidatorService

logger = get_logger("orchestrator")


class AgentOrchestrator:
    """Coordinates the full analytics workflow via LangGraph."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        ollama = OllamaService(self._settings)
        sql_executor = SQLExecutorService(self._settings)
        validator = SQLValidatorService()

        self._intent_agent = IntentAgent(ollama)
        self._schema_agent = SchemaAgent(ollama, self._settings)
        self._sql_generator = SQLGeneratorAgent(ollama, self._settings)
        self._sql_validator = SQLValidatorAgent(validator)
        self._retriever = RetrieverAgent(sql_executor)
        self._analyzer = AnalyzerAgent(ollama, sql_executor)
        self._summarizer = SummarizerAgent(ollama)

        self._graph = self._build_graph()
        self._compiled = self._graph.compile()

    def _build_graph(self) -> StateGraph:
        graph: StateGraph = StateGraph(GraphState)

        graph.add_node("intent", self._intent_agent.run)
        graph.add_node("schema", self._schema_agent.run)
        graph.add_node("sql_generator", self._sql_generator.run)
        graph.add_node("sql_validator", self._sql_validator.run)
        graph.add_node("retriever", self._retriever.run)
        graph.add_node("analyzer", self._analyzer.run)
        graph.add_node("summarizer", self._summarizer.run)

        graph.add_edge(START, "intent")
        graph.add_edge("intent", "schema")
        graph.add_edge("schema", "sql_generator")
        graph.add_edge("sql_generator", "sql_validator")
        graph.add_edge("sql_validator", "retriever")
        graph.add_edge("retriever", "analyzer")
        graph.add_edge("analyzer", "summarizer")
        graph.add_edge("summarizer", END)

        return graph

    def invoke(self, question: str) -> AnalyticsStateModel:
        """Run the full analytics pipeline for a user question."""
        logger.info("Starting workflow for question: %s", question[:80])
        state = initial_state(question)
        result: GraphState = self._compiled.invoke(state)
        model = AnalyticsStateModel(**result)
        if model.error:
            logger.error("Workflow completed with error: %s", model.error)
        else:
            logger.info("Workflow completed successfully")
        return model

    def process_query(self, question: str) -> AnalyticsStateModel:
        """Alias for invoke — backward compatible with existing design."""
        return self.invoke(question)
