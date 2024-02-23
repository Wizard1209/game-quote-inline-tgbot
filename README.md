# game-quote-inline-tgbot

## Contributing to quotes.json

Follow these steps to set up JSON schema validation in VSCode for contributing to `quotes.json`:

1. Press `Ctrl+,` to open VSCode settings.
2. Search for `json`.
3. Ensure `JSON > Format` is enabled
4. Click `Edit in settings.json` under `JSON: Schemas`.
5. Add the following schema configuration:
```json
"json.schemas": [
    {
        "fileMatch": [
            "*quotes.json"
        ],
        "url": "https://raw.githubusercontent.com/Wizard1209/game-quote-inline-tgbot/main/quotes_schema.json"
    }
]
```