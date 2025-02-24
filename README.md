<div align=center>
<img src="https://raw.githubusercontent.com/1UHD/harmony-v2/refs/heads/main/assets/github_banner.png">
<h3>a self-hosted, feature-rich discord music bot using yt-dlp</h3>
</div>

> [!Note]
> This is a continuation of the [Harmony project](https://github.com/1UHD/harmony), featuring a complete rewrite and numerous new features.

> [!Warning]
> Due to Google’s restrictions on bypassing YouTube Premium, the bot may occasionally stop working. Unfortunately, this is beyond my control. You will need to wait for an update to yt-dlp. Harmony includes a built-in auto-updater to keep [yt-dlp](https://github.com/yt-dlp/yt-dlp) up to date.

## Installation

Ensure you have Python installed. Once installed, you can clone this repository:

```sh
git clone https://github.com/1UHD/harmony-v2.git
```

### Setting Up the Bot

Harmony is a self-hosted bot, meaning you must create your own bot instance.

1. Open the Discord Developer Portal and create a new application.
2. Navigate to the Bot tab and customize the username, profile picture, and banner as desired. You can find the Harmony logo and banner in the /assets/ directory.
3. To add the bot to your server:
    - Go to the OAuth2 tab and select “bot” in the OAuth2 URL Generator.
    - Assign the required permissions listed below
4. Copy the generated invite link at the bottom of the OAuth2 page and paste it into your browser to add the bot to your server.
5. Once added, return to the Bot tab and click Reset Token. Copy and save the token securely.

> [!Note]
> Harmony's official banner and logo can be found in the `/assets/` directory!

### Required permissions

<ul>
<li> Read Messages/View Channels
<li> Send Messages
<li> Embed Links
<li> Connect
<li> Speak
<li> Priority Speaker (optional, for priority in voice channels)
<li> Use External Sounds
</ul>

### Starting the bot

Navigate to the bot’s directory:

```sh
cd harmony-v2
```

Run the bot using:

```sh
python launch.py
```

> [!Note]
> On the first launch (or if no valid bot token is detected), Harmony will guide you through the setup process.

## Features

<ul>
<li> Streams audio directly from YouTube using [yt-dlp](https://github.com/yt-dlp/yt-dlp).
<li> Supports both direct video URLs and a built-in search function that uses YouTube’s search algorithm to fetch the first recommended result.
<li> Can play MP3 files stored on your computer.
<li> Includes playlist functionality for a seamless listening experience.
</ul>

### CLI / Launching options

**General usage:**

```sh
python launch.py [-h] [--mp3 MP3] [--debug] [--test] [--no-update]
```

**Options:**

```
-h / --help     Show help message.
--mp3 MP3       Specify the path to an MP3 directory.
--debug         Enable debug mode.
--test          Runs tests.
--no-update     Skip updating dependencies before launch.
--update        Update the bot.
```

### Running with MP3

To run MP3 files, use the launch argument `--mp3`:

```sh
python launch.py --mp3 /path/to/mp3/folder/
```

Harmony will add all MP3 files inside of the specified folder to the queue in alphabetical order after launch.

## Development

Harmony is a side project, meaning updates may be infrequent. Future plans include, but are not limited to:

<ul>
<li> Full command documentation
<li> Spotify integration
<li> Improved MP3 handling
<li> And more…
</ul>
