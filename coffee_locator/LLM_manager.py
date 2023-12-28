from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class LLMHandler:
    def __init__(self, openai_api_key, model):
        # Инициализация модели Language Model (LLM) с ключом API и указанной моделью.
        self.llm = ChatOpenAI(openai_api_key=openai_api_key, model=model)

        # Инициализация парсера для обработки выходных данных от LLM.
        self.output_parser = StrOutputParser()

        # Словарь для хранения истории взаимодействий для каждого пользователя.
        self.user_memories = {}

        # Создание шаблона запроса (промпта) для LLM, включая логику обработки запросов.
        self.prompt = ChatPromptTemplate.from_template(
            "{context} Определите город из сообщения. Если город не ясен, "
            "запросите уточнение. Иначе, предложите топ-3 кофейни в городе "
            "с информацией перечисленной через перенос строки с дефисами: "
            "Название кофейни со встроенный в нее ссылкой(формат "
            "ссылки:https://www.google.com/maps/search/'<кофейня>+<город>'),"
            "Средний чек, "
            "Особенности кофейни."
            "Дополнительно отвечайте на вопросы, основываясь на истории:"
            "{history}. "
            "Ответ:"
        )

        # Создание цепочки обработки запросов, включая логику обработки контекста и истории.
        self.chain = (
                {"context": RunnablePassthrough(), "history": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | self.output_parser
        )

    async def get_response(self, user_id, context):
        # Получение истории общения с пользователем или инициализация новой, если истории нет.
        memory = self.user_memories.get(user_id, [])

        # Добавление текущего контекста в историю пользователя.
        memory.append(context)

        # Создание промпта, включая всю историю общения с пользователем.
        memory_str = self._create_prompt_with_memory(memory)

        # Выполнение запроса к LLM с использованием сформированного промпта.
        response = await self.chain.ainvoke({"history": memory_str, "context": context})

        # Добавление ответа LLM в историю пользователя и обновление истории в словаре.
        memory.append(response)
        # Ограничение размера истории, чтобы избежать чрезмерного накопления данных.
        if len(memory) > 4:
            memory = memory[1:]
        self.user_memories[user_id] = memory

        return response

    def _create_prompt_with_memory(self, memory):
        # Формирование единого промпта из всех элементов истории.
        return " ".join(memory)
