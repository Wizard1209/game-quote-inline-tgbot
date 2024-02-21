build:
  docker build -t game_quote_bot_image:{git rev-parse --abbrev-ref HEAD} .
run:
  docker run -v src:/app/src -v api_key.txt:/app/api_key.txt --name game_quote_bot game_quote_bot_image:{git rev-parse --abbrev-ref HEAD}
stop:
  docker stop game_quote_bot && docker rm game_quote_bot
