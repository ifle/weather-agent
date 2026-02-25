"""Agent Executor

Handles incoming A2A requests and manages task state through the execution lifecycle.
Integrates with WeatherAgent to process user queries and stream responses.
"""

import logging

from a2a.server.agent_execution import AgentExecutor as A2AAgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import InternalError, Part, TaskState, TextPart, UnsupportedOperationError
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError

from agent import WeatherAgent

logger = logging.getLogger(__name__)


class AgentExecutor(A2AAgentExecutor):
    """
    Executor for the Weather Agent.
    
    Handles request processing, task management, and response streaming.
    """
    
    def __init__(self):
        self.agent = WeatherAgent()
        logger.info("AgentExecutor initialized")
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Execute the agent for an incoming request.
        
        Args:
            context: Request context with user input and task information
            event_queue: Event queue for streaming responses
        """
        # Extract user input
        query = context.get_user_input()
        logger.info(f"Executing agent for query: {query}")
        
        # Get or create task
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        
        # Initialize task updater for streaming
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        
        try:
            # Get conversation context (previous messages)
            context_messages = []
            if hasattr(context, 'conversation_history'):
                context_messages = context.conversation_history
            
            # Stream agent responses
            async for item in self.agent.stream(query, task.context_id, context_messages):
                if not item["is_task_complete"] and not item["require_user_input"]:
                    # Working state - show progress
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(item["content"], task.context_id, task.id),
                    )
                elif item["require_user_input"]:
                    # Need user input
                    await updater.update_status(
                        TaskState.input_required,
                        new_agent_text_message(item["content"], task.context_id, task.id),
                        final=True,
                    )
                    break
                else:
                    # Task complete - add artifact and complete
                    await updater.add_artifact(
                        [Part(root=TextPart(text=item["content"]))],
                        name="agent_result"
                    )
                    await updater.complete()
                    break
                    
        except Exception as e:
            logger.exception("Agent execution error")
            raise ServerError(error=InternalError()) from e
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Cancel an ongoing task.
        
        Note: Cancellation is not currently supported.
        
        Args:
            context: Request context
            event_queue: Event queue
            
        Raises:
            ServerError: Always raises UnsupportedOperationError
        """
        logger.warning("Cancel operation requested but not supported")
        raise ServerError(error=UnsupportedOperationError())
