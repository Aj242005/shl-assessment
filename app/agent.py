import json
import logging
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.catalog_store import CatalogStore
from app.catalog_retriever import CatalogRetriever
from app.models import Message, ChatResponse, Recommendation
from app.prompts import SYSTEM_PROMPT
from app.config import settings

logger = logging.getLogger(__name__)

class SHLAgent:
    def __init__(self, catalog_store: CatalogStore, retriever: CatalogRetriever):
        self.catalog = catalog_store
        self.retriever = retriever
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            model=settings.OPENROUTER_MODEL,
            temperature=0.2,
            model_kwargs={
                "response_format": {"type": "json_object"}
            }
        )

    def process(self, messages: list[Message]) -> ChatResponse:
        last_user_msg = next((m.content for m in reversed(messages) if m.role == "user"), "")

        if len(messages) >= 2:
            prev_msg = messages[-2].content
            query = f"{prev_msg} {last_user_msg}"
        else:
            query = last_user_msg

        retrieved_items = self.retriever.retrieve(query)

        opq = self.catalog.get_by_name("Occupational Personality Questionnaire OPQ32r")
        if opq and not any(i.name == opq.name for i in retrieved_items):
            retrieved_items.append(opq)

        verify = self.catalog.get_by_name("SHL Verify Interactive G+")
        if verify and not any(i.name == verify.name for i in retrieved_items):
            retrieved_items.append(verify)

        context_str = "\n---\n".join([item.to_context_string() for item in retrieved_items])

        lc_messages = [
            SystemMessage(content=SYSTEM_PROMPT.format(context=context_str))
        ]

        for msg in messages:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))

        logger.info("Calling LLM via OpenRouter...")
        response = self.llm.invoke(lc_messages)

        try:
            raw_data = json.loads(response.content)

            raw_recs = raw_data.get("recommendations")
            clean_recs = self._validate_recommendations(raw_recs)

            return ChatResponse(
                reply=raw_data.get("reply", "I'm sorry, I couldn't process that."),
                recommendations=clean_recs,
                end_of_conversation=raw_data.get("end_of_conversation", False)
            )

        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response as JSON: {response.content}")
            return ChatResponse(
                reply="I encountered an internal error formatting my response. Please try again.",
                recommendations=None,
                end_of_conversation=False
            )

    def _validate_recommendations(self, recs: list[dict] | None) -> list[Recommendation] | None:
        if not recs:
            return None

        valid_recs = []
        for rec in recs:
            url = rec.get("url")
            if url and self.catalog.validate_url(url):
                catalog_item = self.catalog.get_by_url(url)
                test_type = rec.get("test_type", catalog_item.test_type_codes)

                valid_recs.append(Recommendation(
                    name=catalog_item.name,
                    url=url,
                    test_type=test_type
                ))
            else:
                logger.warning(f"Filtered out hallucinated or invalid recommendation URL: {url}")

        return valid_recs if valid_recs else None
