# simple-antispam-telegram-bot

Simple anti-spam Telegram bot. Allows to check a user on group joining.

## Technology stack

- Python 3.13
- Docker/PodMan
- uv

## Setup for development

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Install Docker/PodMan with compose ([podman](https://podman-desktop.io))
3. Run `uv sync` to create virtual environment
4. Create `.env` file from `.env.template` and populate variables (use [ngrok](#useful-links) for proxy localhost to temporary `webhook_base_url`)
5. Start bot using `uv run python -m sastb start`

## Setup for production

On linux server:

1. Install Docker/PodMan with compose (preferred [podman](https://podman-desktop.io))
2. Create `.env` file from `.env.template`
3. Run `docker compose -f compose.prod.yml up`

## Customization

### Application settings

Settings can be changed using environment variables.

``` dotenv
sastb_default_settings__remove_user_after=5  # Delay for button click
sastb_default_settings__additional_delay_for_permissions=2  # Delay for restrictions of user permissions, if 0 user will not be restricted
sastb_administrators=123456789,  # use @userinfobot to get your id

```

### Text templates

Texts can be changed using environment variables.

List of variables with default text templates (variables in brackets `{}` should be saved in updated templates):

``` dotenv
sastb_text_templates__welcome_message_text="Welcome {user}!\nPlease click button below ⤵️"
sastb_text_templates__confirm_button_text="I'm not a bot"
sastb_text_templates__confirmed_member_text="Welcome {user}!\nYou are now a member."
sastb_text_templates__user_left_text="User {user} has left the group."
sastb_text_templates__kicked_user_text="{user} have been kicked from the group."
sastb_text_templates__kick_user_error_text="Failed to kick {user} from the group."
sastb_text_templates__additional_text_for_permissions="\n\n<i><b>NOTE:</b>\nAccess to the group will be granted after {access_dt}</i>"
sastb_text_templates__button_click_user_id_mismatch_text="It seems you are not the one who should confirm this action."
sastb_text_templates__button_click_confirmed_member_text="You have confirmed your membership."
sastb_text_templates__invited_not_by_admin_text="I can't start to work in this group, because I was invited by someone who is not an administrator. 😢"
sastb_text_templates__invited_by_admin_text="I will start to work in this group. 😊"

```

## Useful links

- [ngrok](https://ngrok.com) - allows to proxy local app for development purposes

## Support

If you find this project useful, please consider donating to [support the Ukrainian army](https://war.ukraine.ua), as this software was created during wartime in Ukraine.
Additionally, if you’d like to support the author, you can do so via [Buy Me a Coffee](https://buymeacoffee.com/dmytrohoi) or [Monobank](https://send.monobank.ua/2iXxdPt2Rf).
