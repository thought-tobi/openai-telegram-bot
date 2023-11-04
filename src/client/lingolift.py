import asyncio
import aiohttp
import requests
from typing import List


async def get_translation(session, sentence: str) -> str:
    async with session.post("http://localhost:5001/translate", json={"sentence": sentence}) as response:
        return await response.json()


async def get_suggestions(session, sentence: str) -> List[str]:
    async with session.post("http://localhost:5001/responses", json={"sentence": sentence}) as response:
        return await response.json()


async def get_literal_translation(session, sentence: str) -> List[dict]:
    async with session.post("http://localhost:5001/literal-translation",
                            json={"sentence": sentence, "language": "russian"}) as response:
        return await response.json()


async def get_all(sentence: str) -> dict:
    async with aiohttp.ClientSession() as session:
        translation_task = asyncio.create_task(get_translation(session, sentence))
        suggestions_task = asyncio.create_task(get_suggestions(session, sentence))
        literal_translation_task = asyncio.create_task(get_literal_translation(session, sentence))

        # Await the completion of all tasks
        translation_result = await translation_task
        suggestions_result = await suggestions_task
        literal_translation_result = await literal_translation_task

        return {
            "translation": translation_result["translation"],
            "response_suggestions": suggestions_result["response_suggestions"],
            "words": literal_translation_result["words"]
        }


# To execute the get_all function and print results
if __name__ == "__main__":
    sentence_to_translate = "Хорошо, как твои дела?"
    result = asyncio.run(get_all(sentence_to_translate))
    print(result)
