# A Telegram ChatGPT Bot

This is a project to integrate ChatGPT into your life more conveniently - by having it right where you talk to your friends.
This bot supports speech-to-text and text-to-speech, so you can talk to it like you would to a human.

You can find the bot running at [@tobis_openai_bot](https://t.me/tobis_openai_bot).

I'm currently hosting my instance of the bot in an AWS free tier t2.micro EC2 instance.
You can also host your own version of the bot if you like.

## Adaptability

This bot is really silly. It supports TTS with several celebrity voices. However, I do think the general architecture of it is solid. It supports:

- Session Management with persistence to MongoDB
- A System Prompt that is retained across a session and determines the behaviour of the ChatGPT backend
- Text-to-Speech and Speech-to-Text integration

I've written it to be as flexible as possible, and I do hope that it might prove useful to someone.

## Setting up your own bot

### Prerequisites

- Python 3.8
- ffmpeg/ffprobe installed [help](https://help.ftrack.com/en/articles/1040538-installing-ffmpeg-and-ffprobe)
- A MongoDB Installation
- A Telegram bot token
- An OpenAI API key
- An elevenlabs API key (optional, for text-to-speech)

### Install and Run

Clone this repository.

    git clone git@github.com:thought-tobi/openai-telegram-bot.git
    cd openai-telegram-bot

Run build.sh to create virtual environment, install dependencies and create

    ./scripts/build.sh

Create the .env file and populate it. It should look like this:

    OPENAI_API_KEY=your-openai-api-key
    TELEGRAM_TOKEN=your-telegram-bot-token
    ELEVENLABS_API_KEY=your-elevenlabs-api-key

Run it!

    ./scripts/run.sh

## Contributing

This whole project is free and open source. If you want to contribute, please do so! I'm happy to accept pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
